"""Bước 1.9: hỏi đáp theo ngày (docs/reference/method.md, mục hỏi đáp). Câu hỏi có/không + ngày sự việc τ -> một trong bốn kết quả, kèm căn cứ.

Cách làm:
  1. LLM (phiên Claude Code ngoài repo, A36) đổi câu hỏi thành: phi = một đầu quy tắc của KB (φ), su_kien = dữ kiện về MỘT đối tượng p1, mỗi
     dữ kiện kèm trích nguyên văn từ câu hỏi. LLM chỉ thấy chữ câu hỏi và từ vựng (vị từ và đầu quy tắc kèm chữ Việt), không thấy ngày,
     φ chuẩn hay đáp án. Không đầu nào khớp thì phi = null: câu hỏi ngoài phạm vi (quyết bằng máy, không có trường trong/ngoài riêng).
  2. Cổng: phi là đầu có thật; vị từ dữ kiện có trong sổ 1.6B; trích là chuỗi con của câu hỏi; không có cặp p và -p.
  3. Π_τ: quy tắc không bị cô lập mà MỌI đơn vị nguồn (`source_units`) có một phiên bản đang hiệu lực tại τ với đúng chữ 1.6A đã đọc
     (so text_norm). Đơn vị bị sửa sau đó thì quy tắc cũ hết dùng từ ngày sửa (chờ 2.6 trích lại); đơn vị do văn bản sau chèn (D154.K8a)
     chưa có quy tắc.
  4. s(CASP) chạy φ(p1) và -φ(p1), chỉ khi đầu tương ứng có định nghĩa trong chương trình (truy vấn vị từ không tồn tại trả rỗng, không
     phải "không"). Đầu ra lạ hay rỗng là LỖI, không bao giờ coi là "không".
  5. Phân loại (A41): φ chứng minh được -> ket_luan_duoc; -φ -> bi_bac; [THÊM] mọi quy tắc kết luận φ trong Π_τ đều có một điều kiện bị dữ
     kiện nói ngược -> bi_bac (Q10, chủ đề tài chốt 18/11); có quy tắc bị cô lập đang hiệu lực mà đầu là φ, -φ hoặc đầu chặn của một quy
     tắc φ (xét một bước) -> khong_tra_loi (co_lap); còn lại chua_du_can_cu. phi = null -> khong_tra_loi (ngoai_pham_vi) [THÊM: method.md
     tách "ngoài phạm vi" khỏi bốn kết quả, bộ câu hỏi dev xếp nó vào khong_tra_loi]. Dữ kiện mâu thuẫn hoặc chương trình không có mô hình
     -> lỗi riêng (s(CASP) không có mô hình thì mọi truy vấn đều "không", dễ đọc nhầm thành chưa đủ căn cứ).
  6. Căn cứ: mô hình s(CASP) của truy vấn thắng; quy tắc "đã chạy" là quy tắc có đầu và mọi literal dương của thân nằm trong mô hình; căn
     cứ là `source_units` của chúng. Chạy hai lần: có và không có cạnh 1.7 `llm_proposed` (steps_1_6_to_1_8.md mục 5).

Chạy (kho con thì đặt KLTN_TAP_CON; mặc định bộ câu hỏi data/eval_dev/<tập con>_questions.json):
  python -X utf8 -I src/answering.py                  đầu ra bước (đọc kết quả LLM đã nhập)
  python -X utf8 -I src/answering.py xuat <thư mục>   dựng thư mục làm việc
  python -X utf8 -I src/answering.py nhap <thư mục>   kiểm từng lô rồi ghi data/llm_cache/answering/<bộ câu hỏi>[.<tập con>].json
"""
import collections
import datetime
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus  # noqa: E402
import implicit_exceptions  # noqa: E402  (dùng lại HUONG_DAN của hộp cát)
import parse  # noqa: E402
import propositions  # noqa: E402
import rules  # noqa: E402
import textutil  # noqa: E402
import versions  # noqa: E402

PROMPT_VERSION = "hoi-dap-2"  # 2 (A44): ket_luan kèm vị từ chủ thể (canh của quy tắc); hoi-dap-1 không cho LLM biết φ cần chủ thể nào
MODEL, EFFORT, ALIAS = implicit_exceptions.MODEL, implicit_exceptions.EFFORT, implicit_exceptions.ALIAS  # cùng hộp cát với 1.7 (khoá hop_cat.*, A46)
LOT_SIZE = 5
DIR_NAME = "answering"
CACHE_DIR = corpus.ROOT / "data" / "llm_cache" / DIR_NAME
ENTITY = "p1"
MODE_GLOSS = (("must_neg_", "phải không"), ("must_", "phải"), ("may_", "được"), ("forbidden_", "cấm"), ("not_applicable_", "không thuộc diện"))

SYSTEM = """Bạn chuyển câu hỏi có/không về pháp luật lao động Việt Nam thành dữ kiện cho một bộ suy luận logic. Bạn KHÔNG trả lời câu hỏi.

ĐẦU VÀO: {"tu_vung": {"ket_luan": [{"ten", "nghia"}], "vi_tu": [{"ten", "nghia"}]}, "cau_hoi": [{"id", "cau_hoi"}]}.
- ket_luan: các kết luận bộ suy luận chứng minh được (ví dụ "phải: có giấy phép lao động"). Mục có "chu_the" là danh sách vị từ chỉ NHÓM ĐỐI TƯỢNG mà kết luận đó áp cho (kết luận chỉ chứng minh được khi đối tượng thuộc nhóm).
- vi_tu: các vị từ dùng làm dữ kiện; "nghia" là chữ trong luật.

Với mỗi câu hỏi:
- phi: "ten" của MỘT mục trong ket_luan diễn đạt đúng điều câu hỏi hỏi. Không mục nào diễn đạt đúng thì null. Không chọn mục chỉ gần nghĩa.
- su_kien: dữ kiện câu hỏi nêu về đối tượng. Chỉ có MỘT đối tượng: dữ kiện về bên liên quan (cơ quan, doanh nghiệp, hồ sơ) cũng ghi cho đối tượng này.
  Mỗi dữ kiện {"vi_tu": "ten" trong vi_tu, "phu_dinh": true|false, "trich": chuỗi chép NGUYÊN VĂN, liền, từ cau_hoi}.
  - Không dùng "ten" của ket_luan làm dữ kiện.
  - phu_dinh = true chỉ khi câu hỏi nói rõ hoặc hàm ý rõ là KHÔNG (ví dụ "không có giấy phép"). Câu hỏi không nhắc thì KHÔNG ghi dữ kiện đó.
  - Chỉ ghi điều câu hỏi nêu; không suy thêm từ hiểu biết pháp luật, không đoán điều câu hỏi im lặng.
  - Chủ thể: nếu ket_luan của phi có "chu_the" và câu hỏi mô tả đối tượng thuộc đúng một nhóm trong đó (đối tượng có đủ các đặc điểm mà "nghia" của nhóm nêu), ghi dữ kiện vị từ nhóm đó, "trich" là cụm của câu hỏi mô tả đối tượng. Câu hỏi không đủ để biết đối tượng thuộc nhóm thì không ghi.
  - Ngưỡng số: chỉ ghi dữ kiện so ngưỡng khi "nghia" của vị từ nêu ngưỡng và con số trong câu hỏi đủ để quyết; "trich" phải chứa con số đó.

ĐẦU RA: chỉ JSON {"cau_hoi": [{"id": "...", "phi": "..." | null, "su_kien": [...]}]}. Mỗi câu hỏi đúng một mục. Mỗi câu hỏi xét riêng."""


# ---- từ vựng, quy tắc, phiên bản ----

def rule_docs():
    """Văn bản đã có quy tắc 1.8 (giai đoạn 1: chỉ BLLĐ; 2.6 thêm văn bản khác)."""
    d = corpus.out_dir(rules.DIR_NAME)
    return sorted(p.name[len("rules_"):-len(".jsonl")] for p in d.glob("rules_*.jsonl") if not p.name.startswith("rules_isolated_"))


def update_rules_path():
    return corpus.out_dir("update") / "update_rules.jsonl"


def load_rules():
    """Quy tắc để dựng Π_τ. Có R của 2.6 (update.py: mọi văn bản, mỗi quy tắc có khoảng hiệu lực) thì đọc R; không thì quy tắc 1.8 của KB gốc
    (giai đoạn 1, chọn theo phiên bản ở `in_force_rules`)."""
    p = update_rules_path()
    if p.exists():
        out = parse.read_jsonl(p)
        for r in out:
            r["valid_from"] = datetime.date.fromisoformat(r["valid_from"])
            r["valid_to"] = datetime.date.fromisoformat(r["valid_to"]) if r["valid_to"] else None
        return out
    out = []
    for doc in rule_docs():
        out += parse.read_jsonl(corpus.out_dir(rules.DIR_NAME) / f"rules_{doc}.jsonl")
    return out


def gloss(atom, surface):
    for prefix, word in MODE_GLOSS:
        if atom.startswith(prefix):
            return f"{word}: {surface}"
    return surface


def live_heads(all_rules):
    """Đầu đưa cho LLM chọn làm φ: bỏ đầu chỉ có ở quy tắc cô lập (A62, user duyệt 26/11). Chọn đầu đó thì chỉ ra khong_tra_loi, và
    đầu cô lập thường là tên ngắn, chung chung (D27.K1 `terminate` thân rỗng) nên kéo bước dịch khỏi đầu đúng (`terminate_employment_contract`).
    Quy tắc cô lập vẫn ở Π_τ để _classify báo co_lap khi φ hay một ngoại lệ của nó trỏ tới."""
    return sorted({r["head"]["atom"] for r in all_rules if not r.get("isolated")})


def vocabulary(all_rules):
    """-> (từ vựng gửi LLM, tập tên vị từ, tập đầu). Đầu là atom dương của quy tắc (đầu mô tả có cực phủ định vẫn hỏi bằng atom dương)."""
    ledger = {}
    reg = corpus.out_dir("predicate_registry") / "predicate_registry_names.json"
    if update_rules_path().exists() and reg.exists():  # sổ chỉ thêm của 2.6: chữ Việt của tên là chữ của thành viên đầu (như sổ 1.6B)
        ledger = dict(json.loads(reg.read_text(encoding="utf-8"))["surface"])
    for doc in rule_docs():
        for p in parse.read_jsonl(corpus.out_dir("predicates") / f"predicates_ledger_{doc}.jsonl"):
            ledger.setdefault(p["predicate"], p["surface"][0] if p["surface"] else p["predicate"])
    heads = live_heads(all_rules)
    pred_of_head = {r["head"]["atom"]: r["head"]["pred"] for r in all_rules}
    subj = collections.defaultdict(set)  # đầu -> vị từ chủ thể (literal canh `chu_the` của các quy tắc kết luận đầu đó)
    for r in all_rules:
        for lit in r["body"]:
            if lit.get("role") == "chu_the":
                subj[r["head"]["atom"]].add(lit["atom"])

    def entry(h):
        e = {"ten": h, "nghia": gloss(h, ledger.get(pred_of_head[h], pred_of_head[h]))}
        if subj.get(h):
            e["chu_the"] = [{"ten": x, "nghia": ledger.get(x, x)} for x in sorted(subj[h])]
        return e
    vocab = {"ket_luan": [entry(h) for h in heads],
             "vi_tu": [{"ten": n, "nghia": s} for n, s in sorted(ledger.items())]}
    return vocab, set(ledger), set(heads)


def vocab_hash(vocab):
    return hashlib.sha256(json.dumps(vocab, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def source_texts():
    """{đơn vị: text_norm của chữ 1.6A đã đọc}."""
    out = {}
    for doc in rule_docs():
        out.update({u: textutil.text_norm(c["text"]) for u, c in propositions.contexts(doc).items()})
    return out


def in_force_rules(all_rules, ver_rows, texts, tau):
    """Π_τ (kể cả quy tắc bị cô lập; người gọi tách). R của 2.6: quy tắc có khoảng hiệu lực chứa τ. Quy tắc 1.8 của KB gốc: dùng được khi
    mọi đơn vị nguồn có phiên bản hiệu lực tại τ với đúng chữ 1.6A."""
    if all_rules and "valid_from" in all_rules[0]:
        return [r for r in all_rules if r["valid_from"] <= tau and (r["valid_to"] is None or tau < r["valid_to"])]
    live = collections.defaultdict(set)
    for v in ver_rows:
        if (v["state"] == "normal" and v["effective_from"] and v["effective_from"] <= tau
                and (v["effective_to"] is None or tau < v["effective_to"])):
            live[v["id"]].add(v["text_norm"])
    return [r for r in all_rules if all(u in texts and texts[u] in live.get(u, ()) for u in r["source_units"])]


# ---- suy luận ----

def scasp_query(program, query, swipl=rules.SWIPL):
    """-> (True, mô hình [chuỗi literal]) | (False, []) | (None, đầu ra thô) khi đầu ra lạ."""
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "q.pl"
        f.write_text(program, encoding="utf-8")
        goal = (f"consult('{f.as_posix()}'), (scasp({query}, [model(M)]) -> (write('KQ:yes'), nl, forall(member(T, M), (print(T), nl))) "
                f"; (write('KQ:no'), nl)), halt")
        out = subprocess.run([swipl, "-q", "-g", goal, "-t", "halt(1)"], capture_output=True, text=True, encoding="utf-8").stdout
    lines = out.splitlines()
    marks = [i for i, x in enumerate(lines) if x.strip() in ("KQ:yes", "KQ:no")]
    if len(marks) != 1:
        return None, out
    i = marks[0]
    if lines[i].strip() == "KQ:no":
        return False, []
    return True, [x.strip() for x in lines[i + 1:] if x.strip()]


def fact_lines(facts):
    return [f"{'-' if f['phu_dinh'] else ''}{f['vi_tu']}({ENTITY})." for f in facts]


def contradicted(r, facts):
    """Quy tắc có ít nhất một điều kiện bị dữ kiện nói ngược (dương gặp -p, `-p` gặp p, `not p` gặp p)."""
    pos = {f["vi_tu"] for f in facts if not f["phu_dinh"]}
    neg = {f["vi_tu"] for f in facts if f["phu_dinh"]}
    for lit in r["body"]:
        if lit["atom"] == "blocked":
            continue
        if lit.get("naf") and lit["atom"] in pos:
            return True
        if not lit.get("naf") and (lit["atom"] in pos if lit.get("neg") else lit["atom"] in neg):
            return True
    return False


def fired_rules(rs, model):
    """-> (quy tắc bị chặn, quy tắc đã chạy): bị chặn là có blocked(r, p1) trong mô hình; đã chạy là có đầu và mọi literal dương (không
    `not`) của thân trong mô hình."""
    m = {x.replace(" ", "") for x in model}
    blocked = [r for r in rs if f"blocked({r['id']},{ENTITY})" in m]
    fired = []
    for r in rs:
        head = f"{'-' if r['head']['neg'] else ''}{r['head']['atom']}({ENTITY})"
        if head not in m:
            continue
        if all(f"{'-' if lit.get('neg') else ''}{lit['atom']}({ENTITY})" in m for lit in r["body"] if lit["atom"] != "blocked" and not lit.get("naf")):
            fired.append(r)
    return blocked, fired


def fired_units(rs, model):
    """Căn cứ: source_units của quy tắc đã chạy. Quy tắc bị chặn cũng là căn cứ của "bị bác": câu trả lời nêu cả quy định bị bác lẫn
    ngoại lệ."""
    out = []
    blocked, fired = fired_rules(rs, model)
    for r in blocked + fired:
        out += [u for u in r["source_units"] if u not in out]
    return out


def classify(phi, facts, rules_tau, iso_ids, llm_edges=True, query=scasp_query, detail=False):
    """-> {"ket_qua", "ly_do", "can_cu"}; ket_qua thuộc bốn loại hoặc "loi". detail=True (web demo) thêm "mo_hinh": mô hình s(CASP) của
    truy vấn thắng (rỗng khi không truy vấn nào thắng)."""
    out = _classify(phi, facts, rules_tau, iso_ids, llm_edges, query)
    if not detail:
        out.pop("mo_hinh", None)
    return out


def _classify(phi, facts, rules_tau, iso_ids, llm_edges, query):
    if phi is None:
        return {"ket_qua": "khong_tra_loi", "ly_do": "ngoai_pham_vi", "can_cu": []}
    pos = {f["vi_tu"] for f in facts if not f["phu_dinh"]}
    neg = {f["vi_tu"] for f in facts if f["phu_dinh"]}
    if pos & neg:
        return {"ket_qua": "loi", "ly_do": f"dữ kiện mâu thuẫn: {sorted(pos & neg)}", "can_cu": []}
    live = [r for r in rules_tau if r["id"] not in iso_ids]
    program = rules.program_text(live, (), llm_edges) + "\n".join(fact_lines(facts)) + "\n"
    has_pos = phi in pos or any(r["head"]["atom"] == phi and not r["head"]["neg"] for r in live)
    has_neg = phi in neg or any(r["head"]["atom"] == phi and (r["head"]["neg"] or rules.active_blockers(r, llm_edges)) for r in live)
    res = {}
    for key, ok, q in (("pos", has_pos, f"{phi}({ENTITY})"), ("neg", has_neg, f"-{phi}({ENTITY})")):
        res[key] = query(program, q) if ok else (False, [])
        if res[key][0] is None:
            return {"ket_qua": "loi", "ly_do": f"s(CASP) trả đầu ra lạ cho {q}: {str(res[key][1])[:200]}", "can_cu": []}
    if not res["pos"][0] and not res["neg"][0] and facts:
        ok, out = query(program, fact_lines(facts)[0][:-1])  # dữ kiện đầu tiên phải đúng; không thì chương trình không có mô hình
        if not ok:
            return {"ket_qua": "loi", "ly_do": "chương trình cộng dữ kiện không có mô hình (mâu thuẫn)", "can_cu": []}
    if res["pos"][0] and res["neg"][0]:
        return {"ket_qua": "loi", "ly_do": "chứng minh được cả φ lẫn -φ", "can_cu": []}
    if res["pos"][0]:
        return {"ket_qua": "ket_luan_duoc", "ly_do": "", "can_cu": fired_units(live, res["pos"][1]), "mo_hinh": res["pos"][1]}
    if res["neg"][0]:
        return {"ket_qua": "bi_bac", "ly_do": "", "can_cu": fired_units(live, res["neg"][1]), "mo_hinh": res["neg"][1]}
    phi_rules = [r for r in live if r["head"]["atom"] == phi and not r["head"]["neg"]]
    if phi_rules and all(contradicted(r, facts) for r in phi_rules):
        return {"ket_qua": "bi_bac", "ly_do": "dieu_kien_bi_bac", "can_cu": [u for r in phi_rules for u in r["source_units"]]}
    watch = {phi} | {h.lstrip("-") for r in phi_rules for h in rules.active_blockers(r, llm_edges)}
    iso_hit = [r for r in rules_tau if r["id"] in iso_ids and r["head"]["atom"] in watch]
    if iso_hit:
        return {"ket_qua": "khong_tra_loi", "ly_do": "co_lap: " + ", ".join(r["id"] for r in iso_hit), "can_cu": []}
    return {"ket_qua": "chua_du_can_cu", "ly_do": "", "can_cu": []}


# ---- bộ câu hỏi, hộp cát, cache ----

# [A61] Chạy bộ câu hỏi trên kho đầy đủ (so `tach` với `ckey` trên các câu chỉ cần BLLĐ): KLTN_CAU_HOI=<tên bộ trong data/eval_dev> chọn bộ khi
# không có tập con, KLTN_CAU_HOI_ID=Q04,Q06 chỉ lấy các câu đó (không sửa file gold); cache ghi riêng theo danh sách câu.
CAU_HOI = os.environ.get("KLTN_CAU_HOI", "").strip() or None
CAU_HOI_ID = [x.strip() for x in os.environ.get("KLTN_CAU_HOI_ID", "").split(",") if x.strip()]


def questions_path():
    if corpus.SUBSET:
        return corpus.ROOT / "data" / "eval_dev" / f"{corpus.SUBSET}_questions.json"
    return corpus.ROOT / "data" / "eval_dev" / f"{CAU_HOI}.json" if CAU_HOI else None


def load_questions(path):
    qs = json.loads(Path(path).read_text(encoding="utf-8"))["cau_hoi"]
    if CAU_HOI_ID:
        missing = set(CAU_HOI_ID) - {q["id"] for q in qs}
        if missing:
            raise SystemExit(f"KLTN_CAU_HOI_ID có câu không có trong {path}: {sorted(missing)}")
        qs = [q for q in qs if q["id"] in CAU_HOI_ID]
    return qs


def cache_path(path):
    stem = Path(path).stem + ("." + "_".join(CAU_HOI_ID) if CAU_HOI_ID else "")
    return CACHE_DIR / corpus.cache_name(stem)


def lots(qs, vocab):
    return [{"tu_vung": vocab, "cau_hoi": [{"id": q["id"], "cau_hoi": q["cau_hoi"]} for q in qs[k:k + LOT_SIZE]]}
            for k in range(0, len(qs), LOT_SIZE)]


def gate(item, q, preds, heads):
    """-> lỗi hoặc None."""
    phi = item.get("phi")
    if phi is not None and phi not in heads:
        return f"phi {phi!r} không phải đầu quy tắc"
    facts = item.get("su_kien")
    if not isinstance(facts, list):
        return "su_kien không phải danh sách"
    for f in facts:
        if not isinstance(f, dict) or f.get("vi_tu") not in preds or not isinstance(f.get("phu_dinh"), bool):
            return f"dữ kiện sai hình hoặc vị từ lạ: {f!r}"
        if f["vi_tu"] == phi:  # đầu mô tả (không tiền tố) cũng là vị từ của sổ: cho làm dữ kiện thì LLM tự trả lời thay bộ suy luận
            return f"dữ kiện trùng φ: {phi}"
        if not f.get("trich") or f["trich"] not in q["cau_hoi"]:
            return f"trích không nguyên văn trong câu hỏi: {f.get('trich')!r}"
    return None


def xuat(thu_muc, qpath):
    d = Path(thu_muc)
    if d.exists() and any(d.iterdir()):
        raise SystemExit(f"{d} đã có nội dung, không ghi đè")
    vocab, _, _ = vocabulary(load_rules())
    ls = lots(load_questions(qpath), vocab)
    (d / "lo").mkdir(parents=True, exist_ok=True)
    (d / "out").mkdir()
    (d / "system.txt").write_text(SYSTEM + "\n", encoding="utf-8", newline="\n")
    for i, lot in enumerate(ls, 1):
        (d / "lo" / f"{i:03d}.json").write_text(implicit_exceptions.lot_text(lot), encoding="utf-8", newline="\n")
    (d / "HUONG_DAN.md").write_text(implicit_exceptions.HUONG_DAN.replace("@N@", f"{len(ls):03d}").replace("@MODEL@", MODEL)
                                    .replace("@ALIAS@", ALIAS).replace("@EFFORT@", EFFORT), encoding="utf-8", newline="\n")
    cfg = {"model": MODEL, "effort": EFFORT, "prompt_version": PROMPT_VERSION, "tap_con": corpus.SUBSET, "cau_hoi": Path(qpath).name,
           "tu_vung": vocab_hash(vocab)}
    (d / "cau_hinh.json").write_text(json.dumps(cfg) + "\n", encoding="utf-8")
    return f"đã dựng {d}: {len(ls)} lô, {sum(len(x['cau_hoi']) for x in ls)} câu hỏi; từ vựng {len(vocab['ket_luan'])} kết luận, {len(vocab['vi_tu'])} vị từ"


def nhap(thu_muc, qpath):
    d = Path(thu_muc)
    cfg = json.loads((d / "cau_hinh.json").read_text(encoding="utf-8"))
    vocab, _, _ = vocabulary(load_rules())
    if (cfg.get("tap_con") != corpus.SUBSET or cfg.get("prompt_version") != PROMPT_VERSION or cfg.get("tu_vung") != vocab_hash(vocab)
            or (d / "system.txt").read_text(encoding="utf-8") != SYSTEM + "\n"):
        raise SystemExit("hộp cát dựng với tập con, lời nhắc hoặc từ vựng khác hiện tại: không nhập")
    if not (d / "nhat_ky.tsv").exists():
        raise SystemExit(f"{d} chưa có nhat_ky.tsv: phiên chưa chạy xong, không nhập")
    log = {int(p[0]): p[1].strip() for p in (x.split("\t") for x in (d / "nhat_ky.tsv").read_text(encoding="utf-8").splitlines())
           if len(p) >= 2 and p[0].strip().isdigit()}
    qs = load_questions(qpath)
    answers, bad = {}, []
    for n, lot in enumerate(lots(qs, vocab), 1):
        if (d / "lo" / f"{n:03d}.json").read_text(encoding="utf-8") != implicit_exceptions.lot_text(lot):
            bad.append((n, "lo/ khác đầu vào hiện tại"))
            continue
        f = d / "out" / f"{n:03d}.json"
        if not f.exists() or log.get(n) != MODEL:
            bad.append((n, f"chưa có out hoặc nhat_ky báo {log.get(n)!r}"))
            continue
        try:
            items = {it["id"]: it for it in json.loads(f.read_text(encoding="utf-8"))["cau_hoi"]}
        except (ValueError, KeyError, TypeError) as e:
            bad.append((n, f"sai hình: {e}"))
            continue
        want = {c["id"]: c for c in lot["cau_hoi"]}
        if set(items) != set(want):
            bad.append((n, f"id lệch: {sorted(set(want) ^ set(items))}"))
            continue
        # ghi kèm chữ câu hỏi: sửa câu hỏi thì câu trả lời cũ không còn dùng
        answers.update({i: {"cau_hoi": want[i]["cau_hoi"], "phi": it.get("phi"), "su_kien": it.get("su_kien")} for i, it in items.items()})
    out = cache_path(qpath)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"prompt_version": PROMPT_VERSION, "model": MODEL, "effort": EFFORT, "tu_vung": vocab_hash(vocab),
                               "answers": answers}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"ghi {out}: {len(answers)} câu có trả lời")
    for n, why in bad:
        print(f"  lô {n:03d} KHÔNG nhận: {why}")


# ---- đầu ra bước ----

def run(qpath):
    all_rules = load_rules()
    vocab, preds, heads = vocabulary(all_rules)
    p = cache_path(qpath)
    cache = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"answers": {}}
    warns = []
    if p.exists() and (cache.get("prompt_version") != PROMPT_VERSION or cache.get("tu_vung") != vocab_hash(vocab)):
        warns.append("CẢNH BÁO: cache của lời nhắc hoặc từ vựng khác (đổi 1.6B/1.8?): mọi câu coi như chưa có trả lời, cần chạy lại phiên")
        cache = {"answers": {}}
    ver_rows = versions.load_versions(corpus.out_dir("versions") / "versions.jsonl")
    for v in ver_rows:
        for k in ("effective_from", "effective_to"):
            v[k] = datetime.date.fromisoformat(v[k]) if v[k] else None
    texts = source_texts()
    rule_doc_ids = {r["unit"].split(".")[0] for r in all_rules} if update_rules_path().exists() else set(rule_docs())
    covered = {u for r in all_rules for u in r["source_units"]}
    results = []
    for q in load_questions(qpath):
        item = cache["answers"].get(q["id"])
        row = {"id": q["id"], "ngay": q["ngay"], "chuan": q.get("dap_an"), "can_cu_chuan": q.get("can_cu", []),
               # căn cứ chuẩn chưa có quy tắc nào (văn bản chưa trích, hoặc đơn vị do văn bản sau chèn như D154.K8a): chờ 2.6
               "can_2_6": any(not any(rules.under(s, u) for s in covered) for u in q.get("can_cu", []))}
        if item is None or item["cau_hoi"] != q["cau_hoi"]:
            row.update(ket_qua="chua_hoi", ly_do="chưa có trả lời LLM cho đúng chữ câu hỏi này")
            results.append(row)
            continue
        err = gate(item, q, preds, heads)
        row.update(phi=item["phi"], su_kien=item["su_kien"])
        if err:
            row.update(ket_qua="loi", ly_do=f"cổng: {err}")
            results.append(row)
            continue
        tau = datetime.date.fromisoformat(q["ngay"])
        rules_tau = in_force_rules(all_rules, ver_rows, texts, tau)
        # R của 2.6 mang cờ cô lập theo từng khoảng (cùng mã có thể cô lập ở khoảng này, không ở khoảng khác): lấy cờ tại τ
        iso_tau = {r["id"] for r in rules_tau if r.get("isolated")}
        row["so_quy_tac_tau"] = sum(1 for r in rules_tau if r["id"] not in iso_tau)
        with_llm = classify(item["phi"], item["su_kien"], rules_tau, iso_tau, llm_edges=True)
        without = classify(item["phi"], item["su_kien"], rules_tau, iso_tau, llm_edges=False)
        row.update(with_llm, khong_canh_1_7=without["ket_qua"])
        results.append(row)
    d = corpus.out_dir(DIR_NAME)
    d.mkdir(parents=True, exist_ok=True)
    stem = Path(qpath).stem + ("." + "_".join(CAU_HOI_ID) if CAU_HOI_ID else "")  # [A61] bộ lọc câu: file riêng
    parse.write_jsonl(d / f"answering_results_{stem}.jsonl", results)
    lines = [f"1.9 hỏi đáp: {Path(qpath).name}" + (f" (kho con {corpus.SUBSET})" if corpus.SUBSET else ""),
             f"văn bản có quy tắc: {sorted(rule_doc_ids)}; câu hỏi: {len(results)}; từ vựng: {len(vocab['ket_luan'])} kết luận, {len(vocab['vi_tu'])} vị từ",
             "Không in tỉ lệ đúng chung: câu gắn 'cần 2.6' có căn cứ chuẩn ở văn bản chưa có quy tắc nên chưa thể đúng ở giai đoạn này."] + warns
    for r in results:
        mark = "ĐÚNG" if r.get("ket_qua") == r["chuan"] else "sai"
        lines.append(f"{r['id']} {r['ngay']} chuẩn={r['chuan']} ra={r.get('ket_qua')} [{mark}]" + (" (cần 2.6)" if r["can_2_6"] else "")
                     + (f" không cạnh 1.7={r['khong_canh_1_7']}" if r.get("khong_canh_1_7") not in (None, r.get("ket_qua")) else ""))
        if "phi" in r:
            lines.append(f"    φ={r['phi']}; quy tắc trong Π_τ: {r.get('so_quy_tac_tau', '-')}; dữ kiện: " + ", ".join(f"{'-' if f['phu_dinh'] else ''}{f['vi_tu']}" for f in r.get("su_kien") or []))
        if r.get("ly_do"):
            lines.append(f"    lý do: {r['ly_do']}")
        if r.get("can_cu") or r["can_cu_chuan"]:
            lines.append(f"    căn cứ: {r.get('can_cu', [])}; căn cứ chuẩn: {r['can_cu_chuan']}")
    rp = corpus.report_dir(DIR_NAME) / f"answering_report_{stem}.txt"
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))


def main():
    cmd = sys.argv[1:2]
    qpath = questions_path()
    if not propositions.full_cache_path().exists() or not rule_docs():
        print("BỎ QUA 1.9: chưa có quy tắc 1.8 (chưa có kết quả 1.6A)")
        return
    if qpath is None or not qpath.exists():
        print(f"BỎ QUA 1.9: chưa có bộ câu hỏi cho kho này ({qpath})")
        return
    if cmd == ["xuat"]:
        print(xuat(sys.argv[2], qpath))
    elif cmd == ["nhap"]:
        nhap(sys.argv[2], qpath)
    elif not cmd:
        run(qpath)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
