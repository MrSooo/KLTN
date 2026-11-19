"""web demo hỏi đáp trên KB thích nghi theo ngày (A45). Chạy trên máy, chỉ mở ở 127.0.0.1. Không phải một bước của pipeline.

Mỗi câu hỏi (chữ + ngày sự việc τ):
  1. Dữ kiện: lời nhắc 1.9 `answering.SYSTEM` (hoi-dap-2) đổi câu hỏi thành φ và dữ kiện, qua `answering.gate`. Câu của bộ dev đã có trả lời
     hợp lệ (cùng lời nhắc, cùng từ vựng) thì dùng lại, không gọi LLM. Cổng trượt thì dừng, không suy luận.
  2. Suy luận: Π_τ từ R của 2.6 (`update_rules.jsonl`), `answering.classify` trên s(CASP): kết quả, căn cứ, mô hình.
  3. Cây chứng minh dựng từ mô hình (quy tắc đã chạy, quy tắc bị chặn, dữ kiện); chữ căn cứ là chữ của đơn vị tại τ trong kho phiên bản.
  4. Câu mở đầu (kết luận) do MÁY viết từ kết quả và nghĩa của φ. [THÊM, A45] LLM (lời nhắc `tra-loi-1`) chỉ viết phần diễn giải tiếp theo;
     cổng: đúng hình, `can_cu_dung` thuộc căn cứ, mọi "Điều N" và số hiệu văn bản nêu ra phải có trong căn cứ hoặc trong chữ căn cứ. Trượt cổng
     thì dùng diễn giải dựng sẵn từ cây. Cổng không kiểm được độ trung thành của câu chữ: trang ghi rõ là "diễn giải".

LLM: tạm dùng `claude -p` (phiên Claude Code, như lúc chạy thử; không công cụ, thư mục tạm rỗng, lời nhắc qua stdin). Đổi sang API thì chỉ
thay `claude_code`. Kết quả LLM của demo ghi ở data/processed[_subset]/demo/demo_cache.json (không đụng data/llm_cache/).

Chạy (ở gốc repo):
  KLTN_TAP_CON=lldnn python -X utf8 -I utils/demo/qa_server.py [--port 8765] [--llm claude|off]
  KLTN_TAP_CON=lldnn python -X utf8 -I utils/demo/qa_server.py hoi "<câu hỏi>" <YYYY-MM-DD> [--llm off]   (một câu, in JSON)
"""
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "src"))  # -I không tự thêm thư mục script
import answering as A  # noqa: E402
import corpus  # noqa: E402
import knowledge_units as KU  # noqa: E402
import rules  # noqa: E402

EXPLAIN_VERSION = "tra-loi-1"
CLAUDE = "/opt/homebrew/bin/claude"
LLM_TIMEOUT = 180
PROXY_VARS = ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY")
MAX_EXPLAIN = 1500

SYSTEM_EXPLAIN = """Bạn viết phần diễn giải cho câu trả lời của một hệ hỏi đáp pháp luật lao động Việt Nam. Kết luận ĐÃ do bộ suy luận logic quyết; bạn không quyết lại.

ĐẦU VÀO (JSON): cau_hoi, ngay (ngày sự việc), ket_luan (câu kết luận của máy, đã hiển thị trước phần của bạn), du_kien (điều câu hỏi nêu, kèm trích), can_cu (các quy định: id, ten, chu = nguyên văn tại ngày đó), lap_luan (các bước suy luận của máy).

VIẾT: 2 đến 6 câu tiếng Việt dễ hiểu cho người không học luật, giải thích VÌ SAO có kết luận đó, theo đúng lap_luan: quy định chung nào áp dụng, điều kiện nào đã thoả theo dữ kiện, ngoại lệ nào làm quy định chung không áp dụng, hoặc còn thiếu dữ kiện gì.
- Không viết lại hay đảo kết luận; không mở đầu bằng "Có" hay "Không".
- Chỉ dựa vào can_cu và lap_luan. Không thêm quy định, điều khoản, văn bản, con số hay hiểu biết nào ngoài đầu vào. Chỉ nêu Điều, văn bản có trong ten hoặc chu của can_cu.
- Nêu quy định bằng ten của nó (ví dụ "điểm d khoản 1 Điều 151 Bộ luật Lao động 45/2019/QH14").

ĐẦU RA: chỉ JSON {"giai_thich": "...", "can_cu_dung": ["id", ...]} (can_cu_dung: id của các can_cu bạn đã dựa vào)."""

HEADLINE = {
    "ket_luan_duoc": "Kết luận: «{phi}» — ĐÚNG với trường hợp trong câu hỏi, tại ngày {ngay}.",
    "bi_bac": "Kết luận: «{phi}» — KHÔNG đúng (bị bác) với trường hợp trong câu hỏi, tại ngày {ngay}.",
    "chua_du_can_cu": "Chưa đủ căn cứ để kết luận «{phi}» tại ngày {ngay}: câu hỏi chưa nêu đủ dữ kiện.",
    "ngoai_pham_vi": "Ngoài phạm vi: cơ sở tri thức hiện tại không có quy định nào diễn đạt đúng điều câu hỏi hỏi.",
    "co_lap": "Không trả lời: quy định liên quan đang bị cô lập (mâu thuẫn chưa giải quyết trong cơ sở tri thức).",
    "loi": "Lỗi suy luận: {ly_do}",
}


# ---- LLM ----

def claude_code(system, payload, timeout=LLM_TIMEOUT):
    """Một lượt `claude -p` không công cụ, chạy trong thư mục tạm rỗng; đầu vào qua stdin. -> (đối tượng JSON trong câu trả lời, mô tả lượt)."""
    env = {k: v for k, v in os.environ.items() if k not in PROXY_VARS}
    cmd = [CLAUDE, "-p", "--model", "sonnet", "--effort", "high", "--system-prompt", system, "--tools", "", "--output-format", "json",
           "--no-session-persistence", "--disable-slash-commands", "--strict-mcp-config"]
    t = time.time()
    with tempfile.TemporaryDirectory() as d:
        p = subprocess.run(cmd, input=json.dumps(payload, ensure_ascii=False), capture_output=True, text=True, encoding="utf-8",
                           cwd=d, env=env, timeout=timeout)
    meta = {"giay": round(time.time() - t, 1), "ma_thoat": p.returncode}
    try:
        out = json.loads(p.stdout)
    except ValueError:
        raise RuntimeError(f"claude -p trả đầu ra không phải JSON (mã {p.returncode}): {(p.stdout or p.stderr)[:300]}")
    if out.get("is_error"):
        raise RuntimeError(f"claude -p báo lỗi: {str(out.get('result'))[:300]}")
    meta["model"] = ",".join(sorted(out.get("modelUsage") or {})) or None
    return extract_json(out.get("result") or ""), meta


def extract_json(text):
    """Đối tượng JSON trong câu trả lời (bỏ rào ```json nếu có)."""
    s = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", s, re.S)
    if m:
        s = m.group(1).strip()
    if not s.startswith("{"):
        i, j = s.find("{"), s.rfind("}")
        s = s[i:j + 1] if i >= 0 and j > i else s
    try:
        return json.loads(s)
    except ValueError:
        raise RuntimeError(f"câu trả lời LLM không chứa JSON đọc được: {text[:300]}")


def no_llm(system, payload):
    raise RuntimeError("demo chạy với --llm off: không gọi LLM")


# ---- tên đơn vị ----



def unit_name(uid, docs):
    """BLLD_45-2019.D151.K1.d -> 'điểm d khoản 1 Điều 151 Bộ luật 45/2019/QH14'. Mã lạ thì trả nguyên mã."""
    doc_id, *parts = uid.split(".")
    doc = docs.get(doc_id)
    words = []
    for p in parts:
        m = re.fullmatch(r"D(\d+[a-z]?)", p)
        if m:
            words.append(f"Điều {m.group(1)}")
            continue
        m = re.fullmatch(r"K(\d+[a-z]?)", p)
        if m:
            words.append(f"khoản {m.group(1)}")
            continue
        if re.fullmatch(r"[a-zđ]", p):
            words.append(f"điểm {p}")
            continue
        return uid
    where = (f"{'Bộ luật Lao động' if doc.loai == 'Bộ luật' else doc.loai} {doc.so_hieu}") if doc else doc_id
    return " ".join(reversed(words)) + (" " if words else "") + where


# ---- KB ----

class KB:
    def __init__(self, llm=claude_code):
        self.llm = llm
        self.rules = A.load_rules()
        if not self.rules or "valid_from" not in self.rules[0]:
            raise SystemExit("chưa có R của 2.6 (update_rules.jsonl): chạy run_all --tap-con <tên> --llm replay trước")
        self.vocab, self.preds, self.heads = A.vocabulary(self.rules)
        self.vhash = A.vocab_hash(self.vocab)
        self.meaning = {x["ten"]: x["nghia"] for x in self.vocab["vi_tu"]}
        self.meaning.update({x["ten"]: x["nghia"] for x in self.vocab["ket_luan"]})
        self.docs = corpus.load_manifest()
        self.store = KU.Store.load()
        self.labels = KU.load_labels()
        self.examples, self.dev = [], {}
        qp = A.questions_path()
        if qp and qp.exists():
            self.examples = [{"id": q["id"], "cau_hoi": q["cau_hoi"], "ngay": q["ngay"]} for q in A.load_questions(qp)]
            cp = A.cache_path(qp)
            c = json.loads(cp.read_text(encoding="utf-8")) if cp.exists() else {}
            if c.get("prompt_version") == A.PROMPT_VERSION and c.get("tu_vung") == self.vhash:  # như answering.run
                self.dev = {a["cau_hoi"]: a for a in c["answers"].values()}
        self.cache_file = corpus.out_dir("demo") / "demo_cache.json"
        self.cache = json.loads(self.cache_file.read_text(encoding="utf-8")) if self.cache_file.exists() else {}
        self.lock = threading.Lock()

    # cache của demo: khoá gồm phiên bản lời nhắc và mọi đầu vào LLM thấy
    def _key(self, *parts):
        return hashlib.sha256(json.dumps(parts, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:24]

    def _put(self, key, value):
        with self.lock:
            self.cache[key] = value
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.cache_file.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.cache, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            tmp.replace(self.cache_file)

    def nghia(self, lit):
        """Chữ đọc được của literal: 'phải: có giấy phép' -> 'phải có giấy phép'; -p -> 'không p'."""
        neg = lit.startswith("-")
        s = self.meaning.get(lit.lstrip("-"), lit.lstrip("-")).replace(": ", " ", 1)
        s = s.replace("không thuộc diện thuộc diện", "không thuộc diện")
        s = s[:1].lower() + s[1:] if s[:2] != s[:2].upper() else s
        return ("không " + s).replace("không thuộc diện thuộc diện", "không thuộc diện") if neg else s

    def phi_text(self, phi):
        return self.meaning.get(phi, phi).replace(": ", " ", 1)

    # 1. dữ kiện
    def facts(self, question):
        """-> (mục {phi, su_kien}, nguồn, lỗi). Lỗi cổng thì mục là None."""
        q = {"id": "Q", "cau_hoi": question}
        if question in self.dev:
            item, src = self.dev[question], "cache bộ dev (1.9)"
        else:
            key = self._key("facts", A.PROMPT_VERSION, self.vhash, question)
            if key in self.cache:
                item, src = self.cache[key], "cache demo"
            else:
                out, meta = self.llm(A.SYSTEM, {"tu_vung": self.vocab, "cau_hoi": [q]})
                items = out.get("cau_hoi") if isinstance(out, dict) else None
                if not isinstance(items, list) or len(items) != 1:
                    return None, "LLM", f"đầu ra sai hình: {str(out)[:200]}"
                item = {"phi": items[0].get("phi"), "su_kien": items[0].get("su_kien")}
                src = f"LLM ({meta.get('model')}, {meta['giay']} giây)"
                if A.gate(item, q, self.preds, self.heads) is None:
                    self._put(key, item)
        err = A.gate(item, q, self.preds, self.heads)
        return (None if err else item), src, err

    # 2-3. suy luận, cây, căn cứ
    def reason(self, item, tau):
        rules_tau = A.in_force_rules(self.rules, [], {}, tau)
        iso = {r["id"] for r in rules_tau if r.get("isolated")}
        res = A.classify(item["phi"], item["su_kien"], rules_tau, iso, llm_edges=True, detail=True)
        live = [r for r in rules_tau if r["id"] not in iso]
        tree = self.tree(item, res, live)
        units = list(res["can_cu"])
        if res["ket_qua"] == "chua_du_can_cu":  # không có căn cứ đã chạy: nêu quy định kết luận φ để nói còn thiếu gì
            for r in live:
                if r["head"]["atom"] == item["phi"] and not r["head"]["neg"]:
                    units += [u for u in r["source_units"] if u not in units]
        texts = KU.contexts_at(self.store.snapshot(tau), self.labels)
        snap = self.store.snapshot(tau)
        basis = []
        for u in units:
            c = texts.get(u) or {"heading": "", "chapeau": "", "text": (snap.get(u) or {}).get("text") or ""}
            basis.append({"id": u, "ten": unit_name(u, self.docs), "tieu_de": c["heading"], "cau_dan": c["chapeau"], "chu": c["text"]})
        return res, tree, basis, len(live)

    def tree(self, item, res, live):
        """Cây chứng minh từ mô hình của truy vấn thắng. Nút: dữ kiện | quy tắc (thân là con) | bị chặn (quy tắc bị bác + đầu chặn)."""
        model = res.get("mo_hinh") or []
        if res["ket_qua"] not in ("ket_luan_duoc", "bi_bac") or not model:
            return None
        m = {x.replace(" ", "") for x in model}
        blocked, fired = A.fired_rules(live, model)
        facts = {("-" if f["phu_dinh"] else "") + f["vi_tu"]: f for f in item["su_kien"]}
        seen = set()

        def node(lit):
            base = {"lit": lit, "nghia": self.nghia(lit)}
            if lit in facts:
                return dict(base, loai="du_kien", trich=facts[lit]["trich"])
            if lit in seen:
                return dict(base, loai="lap")
            seen.add(lit)
            for r in fired:
                if rules.head_form(r) == lit:
                    kids = [node(("-" if b.get("neg") else "") + b["atom"]) for b in r["body"] if b["atom"] != "blocked" and not b.get("naf")]
                    return dict(base, loai="quy_tac", quy_tac=r["id"], don_vi=r["source_units"], ten=unit_name(r["unit"], self.docs), con=kids)
            if lit.startswith("-"):
                for r in blocked:
                    if r["head"]["atom"] == lit[1:] and not r["head"]["neg"]:
                        hs = [h for h in rules.active_blockers(r) if f"{h}({A.ENTITY})" in m]
                        return dict(base, loai="bi_chan", quy_tac=r["id"], don_vi=r["source_units"], ten=unit_name(r["unit"], self.docs),
                                    dieu_kien=[self.nghia(("-" if b.get("neg") else "") + b["atom"]) for b in r["body"] if b["atom"] != "blocked"],
                                    con=[node(h) for h in hs])
            return dict(base, loai="khac")
        root = item["phi"] if res["ket_qua"] == "ket_luan_duoc" else "-" + item["phi"]
        return node(root)

    def steps(self, item, res, tree, live_rules=None):
        """Lập luận bằng chữ (đưa cho LLM và làm diễn giải dựng sẵn)."""
        out = []

        def walk(n):
            for c in n.get("con", []):
                walk(c)
            if n["loai"] == "du_kien":
                out.append(f"Dữ kiện: {n['nghia']} (câu hỏi nêu: \"{n['trich']}\").")
            elif n["loai"] == "quy_tac":
                conds = "; ".join(c["nghia"] for c in n["con"]) or "không cần điều kiện"
                out.append(f"Theo {n['ten']}: khi {conds} thì {n['nghia']}.")
            elif n["loai"] == "bi_chan":
                out.append(f"Quy định chung {n['ten']} (khi {'; '.join(n['dieu_kien'])} thì {self.nghia(n['lit'][1:])}) không áp dụng vì có ngoại lệ: "
                           + "; ".join(c["nghia"] for c in n["con"]) + ".")
        if tree:
            walk(tree)
            if tree["loai"] == "quy_tac":  # kết luận được: ngoại lệ có trong KB mà dữ kiện không thoả
                rs = [r for r in live_rules or [] if r["id"] == tree["quy_tac"]]
                hs = sorted({self.nghia(h) for r in rs for h in rules.active_blockers(r)})
                if hs:
                    out.append(f"Ngoại lệ của quy định này ({'; '.join(hs)}) không thoả với dữ kiện câu hỏi nêu.")
        elif res["ket_qua"] in ("chua_du_can_cu", "bi_bac"):  # bị bác do điều kiện bị dữ kiện nói ngược, hoặc thiếu dữ kiện
            have = {("-" if f["phu_dinh"] else "") + f["vi_tu"] for f in item["su_kien"]}
            for r in live_rules or []:
                if r["head"]["atom"] != item["phi"] or r["head"]["neg"]:
                    continue
                conds = [("-" if b.get("neg") else "") + b["atom"] for b in r["body"] if b["atom"] != "blocked" and not b.get("naf")]
                against = [self.nghia(c) for c in conds if ("-" + c if not c.startswith("-") else c[1:]) in have]
                miss = [self.nghia(c) for c in conds if c not in have and self.nghia(c) not in against]
                out.append(f"Theo {unit_name(r['unit'], self.docs)}: cần {'; '.join(self.nghia(c) for c in conds)} thì {self.nghia(item['phi'])}."
                           + (f" Câu hỏi nêu ngược điều kiện: {'; '.join(against)}." if against else "")
                           + (f" Câu hỏi chưa nêu: {'; '.join(miss)}." if miss else ""))
        return out

    # 4. diễn giải
    def explain(self, question, tau, headline, item, basis, steps, use_llm=True):
        """-> (chữ diễn giải, nguồn, lỗi cổng hoặc None)."""
        fallback = " ".join(steps) or "Không có bước suy luận để diễn giải."
        if not use_llm or not basis:
            return fallback, "dựng sẵn từ cây chứng minh", None
        payload = {"cau_hoi": question, "ngay": tau.isoformat(), "ket_luan": headline,
                   "du_kien": [{"nghia": self.nghia(("-" if f["phu_dinh"] else "") + f["vi_tu"]), "trich": f["trich"]} for f in item["su_kien"]],
                   "can_cu": [{"id": b["id"], "ten": b["ten"], "chu": " ".join(x for x in (b["cau_dan"], b["chu"]) if x)} for b in basis],
                   "lap_luan": steps}
        key = self._key("explain", EXPLAIN_VERSION, SYSTEM_EXPLAIN, payload)
        src = "cache demo"
        if key in self.cache:
            out = self.cache[key]
        else:
            try:
                out, meta = self.llm(SYSTEM_EXPLAIN, payload)
            except (RuntimeError, subprocess.TimeoutExpired) as e:
                return fallback, "dựng sẵn từ cây chứng minh (LLM lỗi)", str(e)[:300]
            src = f"LLM ({meta.get('model')}, {meta['giay']} giây)"
        err = explain_gate(out, basis, self.docs)
        if err:
            return fallback, "dựng sẵn từ cây chứng minh (diễn giải LLM trượt cổng)", err
        if src != "cache demo":
            self._put(key, out)
        return out["giai_thich"].strip(), src, None

    def ask(self, question, tau, use_llm=True):
        t0 = time.time()
        timing = {}
        out = {"cau_hoi": question, "ngay": tau.isoformat(), "tap_con": corpus.SUBSET}
        try:
            item, src, err = self.facts(question)
        except (RuntimeError, subprocess.TimeoutExpired) as e:
            item, src, err = None, "LLM", f"không lấy được dữ kiện: {str(e)[:300]}"
        timing["du_kien"] = round(time.time() - t0, 2)
        out["nguon_du_kien"] = src
        if err:
            out.update(ket_qua="loi", ket_luan=f"Lỗi ở bước đổi câu hỏi thành dữ kiện: {err}", loi_cong=err, thoi_gian=timing)
            return out
        out.update(phi=item["phi"], phi_nghia=self.meaning.get(item["phi"]) if item["phi"] else None,
                   su_kien=[dict(f, nghia=self.nghia(("-" if f["phu_dinh"] else "") + f["vi_tu"])) for f in item["su_kien"]])
        t1 = time.time()
        res, tree, basis, n_rules = self.reason(item, tau)
        timing["suy_luan"] = round(time.time() - t1, 2)
        kind = res["ly_do"].split(":")[0] if res["ket_qua"] == "khong_tra_loi" else res["ket_qua"]
        headline = HEADLINE.get(kind, HEADLINE["loi"]).format(phi=self.phi_text(item["phi"]) if item["phi"] else "", ngay=tau.strftime("%d/%m/%Y"),
                                                               ly_do=res["ly_do"])
        live = [r for r in A.in_force_rules(self.rules, [], {}, tau) if not r.get("isolated")]
        steps = self.steps(item, res, tree, live)
        out.update(ket_qua=res["ket_qua"], ly_do=res["ly_do"], ket_luan=headline, can_cu=basis, cay=tree, lap_luan=steps, so_quy_tac_tau=n_rules)
        t2 = time.time()
        if res["ket_qua"] in ("ket_luan_duoc", "bi_bac", "chua_du_can_cu"):
            text, esrc, eerr = self.explain(question, tau, headline, item, basis, steps, use_llm)
            out.update(giai_thich=text, nguon_giai_thich=esrc, loi_cong_giai_thich=eerr)
        timing["giai_thich"] = round(time.time() - t2, 2)
        timing["tong"] = round(time.time() - t0, 2)
        out["thoi_gian"] = timing
        return out


DOC_NO = r"(?<![\d/])(\d+)/\d{4}(?!/\d)"
DOC_BARE = r"(?:Nghị định|Bộ luật|Nghị quyết|Thông tư|Luật|NĐ|NQ|TT)(?:\s+số)?\s+(\d+)(?![\d/.,])"


def explain_gate(out, basis, docs):
    """Cổng của diễn giải `tra-loi-1` -> lỗi hoặc None. Điều và số hiệu được nêu: của căn cứ, hoặc có trong chữ căn cứ (D151.K1.d nêu
    'trừ trường hợp quy định tại Điều 154')."""
    if not isinstance(out, dict) or not isinstance(out.get("giai_thich"), str) or not out["giai_thich"].strip():
        return "đầu ra sai hình (thiếu giai_thich)"
    text = out["giai_thich"]
    if len(text) > MAX_EXPLAIN:
        return f"diễn giải dài {len(text)} ký tự (> {MAX_EXPLAIN})"
    ids = {b["id"] for b in basis}
    used = out.get("can_cu_dung")
    if not isinstance(used, list) or not used or not set(used) <= ids:
        return f"can_cu_dung phải là danh sách khác rỗng, con của căn cứ: {used!r}"
    allowed_text = " ".join(" ".join((b["ten"], b.get("tieu_de", ""), b.get("cau_dan", ""), b["chu"])) for b in basis)
    articles = set(re.findall(r"Điều\s+(\d+[a-z]?)", allowed_text, re.I))
    # số hiệu văn bản: "152/2020" (không khớp "10/2025" trong ngày 01/10/2025) và số trần sau tên loại ("Nghị định 219", "NĐ 152")
    numbers = set(re.findall(DOC_NO, allowed_text))
    for b in basis:
        d = docs.get(b["id"].split(".")[0])
        if d:
            numbers |= set(re.findall(DOC_NO, d.so_hieu))
    bad_a = sorted(set(re.findall(r"Điều\s+(\d+[a-z]?)", text, re.I)) - articles)
    if bad_a:
        return f"nêu Điều ngoài căn cứ: {bad_a}"
    bad_n = sorted((set(re.findall(DOC_NO, text)) | set(re.findall(DOC_BARE, text, re.I))) - numbers)
    if bad_n:
        return f"nêu văn bản ngoài căn cứ: {bad_n}"
    if re.match(r"\s*(có|không)\b", text, re.I):
        return "diễn giải mở đầu bằng Có/Không (kết luận là của máy)"
    return None


# ---- web ----

def make_handler(kb, use_llm):
    page = (HERE / "index.html").read_bytes()

    class H(BaseHTTPRequestHandler):
        def _send(self, code, body, ctype="application/json; charset=utf-8"):
            data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                return self._send(200, page, "text/html; charset=utf-8")
            if self.path == "/api/info":
                return self._send(200, {"tap_con": corpus.SUBSET, "so_quy_tac": len(kb.rules), "vi_du": kb.examples, "llm": use_llm,
                                        "hom_nay": datetime.date.today().isoformat(),
                                        "ket_luan": [x["nghia"] for x in kb.vocab["ket_luan"]]})
            self._send(404, {"loi": "không có"})

        def do_POST(self):
            if self.path != "/api/hoi":
                return self._send(404, {"loi": "không có"})
            try:
                n = int(self.headers.get("Content-Length") or 0)
                req = json.loads(self.rfile.read(min(n, 20000)).decode("utf-8"))
                q = str(req.get("cau_hoi") or "").strip()
                tau = datetime.date.fromisoformat(req.get("ngay") or datetime.date.today().isoformat())
            except (ValueError, TypeError) as e:
                return self._send(400, {"loi": f"yêu cầu sai: {e}"})
            if not q or len(q) > 2000:
                return self._send(400, {"loi": "câu hỏi rỗng hoặc quá dài"})
            self._send(200, kb.ask(q, tau, use_llm=use_llm and req.get("giai_thich", True)))

        def log_message(self, fmt, *args):
            sys.stderr.write("demo: " + (fmt % args) + "\n")
    return H


def main(argv):
    llm = "claude"
    if "--llm" in argv:
        i = argv.index("--llm")
        llm = argv[i + 1]
        del argv[i:i + 2]
    if llm not in ("claude", "off"):
        raise SystemExit("--llm claude|off")
    kb = KB(llm=claude_code if llm == "claude" else no_llm)
    if argv[:1] == ["hoi"]:
        print(json.dumps(kb.ask(argv[1], datetime.date.fromisoformat(argv[2]), use_llm=llm == "claude"), ensure_ascii=False, indent=1))
        return
    port = int(argv[argv.index("--port") + 1]) if "--port" in argv else 8765
    srv = ThreadingHTTPServer(("127.0.0.1", port), make_handler(kb, llm == "claude"))
    print(f"demo hỏi đáp (kho {corpus.SUBSET or 'đầy đủ'}, {len(kb.rules)} quy tắc, LLM {llm}): http://127.0.0.1:{port}/")
    srv.serve_forever()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main(sys.argv[1:])
