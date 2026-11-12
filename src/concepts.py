"""Bước 1.6 (giai đoạn A): gạch cụm trong chữ luật theo bốn vai (chủ thể, điều kiện, ngoại lệ, kết luận), kèm tham số, nguồn và đích dẫn chiếu.

Chạy: python -I src/concepts.py [--doc <doc_id>] [--llm off|replay|live] [--max-batches N]     (mặc định: BLLĐ; cần các bước parse, refs, article_type, exceptions_general)
Đầu ra (data/processed/concepts/):
  concepts_spans_<doc_id>.jsonl     bảng cụm {unit, span, role, source, predicate, params, targets, how, flags}; predicate còn null (giai đoạn B đặt tên và tái dùng)
  concepts_rejected_<doc_id>.jsonl  cụm LLM đề xuất bị loại kèm lý do
  concepts_uncovered_<doc_id>.jsonl từ báo hiệu mà chưa có cụm phủ hoặc kề (chỉ BÁO, không chặn)
Báo cáo: docs/bao_cao_chay/concepts/concepts_report_<doc_id>.txt. Thẻ bước: docs/pipeline_moi.md (mục "THẺ BƯỚC 1.6"), quyết định A25 đến A31.

Việc của máy và của LLM tách rạch ròi (đề cương: LLM chỉ làm phần cần hiểu, mọi đầu ra phải qua cổng máy):
  - LLM chỉ trả: chữ của cụm, vai, tham số. Nó KHÔNG đặt tên, KHÔNG nói cụm lấy từ đâu, KHÔNG nói dẫn chiếu trỏ đi đâu.
  - Máy tính `source` (own, rồi chapeau, rồi heading, lấy chỗ khớp đầu tiên), ghi lại `span` bằng đoạn NGUYÊN VĂN cắt từ chữ gốc (không dùng chuỗi LLM trả,
    nên span luôn là chuỗi con của chữ gốc), điền `targets` từ cạnh refers_to đã giải của 1.2, và thêm cụm ngoại lệ từ nút điều kiện của 1.5 (how=cond_node).
Cổng CHẶN (cụm bị loại, ghi vào rejected): cụm không là chuỗi từ liền nhau của ngữ cảnh (tiêu đề Điều + chữ khoản cha + chữ đơn vị); vai ngoài bốn vai; tham số
ngoài W E C J G D A. So khớp theo TỪ (không theo ký tự) nên một mảnh giữa chừng của một từ không khớp. Cổng BÁO: từ báo hiệu chưa có cụm phủ hoặc kề; nút điều kiện
1.5 mà LLM không gạch cụm ngoại lệ nào trùng hoặc chứa nó; dẫn chiếu nằm vắt qua biên cụm (không tính vào targets).

LLM (`--llm`): off = chỉ phần máy (cụm từ nút 1.5 và targets), kết quả tất định; replay = đọc cache, lô nào thiếu cache thì giữ kết quả như off cho các đơn vị của lô đó và
báo rõ trong báo cáo (không chạm mạng); live = thiếu cache thì gọi API (vai trich = Claude, A34; mỗi lô một lượt). Lô cố định (mỗi lô là một Điều, Điều dài hơn BATCH_SIZE đơn vị thì cắt theo thứ tự tài liệu) và lời nhắc
cố định theo PROMPT_VERSION: sửa lời nhắc mà không đổi PROMPT_VERSION vẫn không dùng nhầm cache cũ (khoá cache gồm cả chữ lời nhắc), nhưng sửa lời nhắc sau khi đã chạy live
là bỏ phí các lượt đã gọi.
"""
import argparse
import collections
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import parse as l1
import refs as l2
import corpus
import llm_client
from textutil import TONE

DIR_NAME = "concepts"
TASK, PROMPT_VERSION, BATCH_SIZE = "concepts_spans", "concepts-1", 20
ROLES = ("chu_the", "dieu_kien", "ngoai_le", "ket_luan")
PARAMS = ("W", "E", "C", "J", "G", "D", "A")
IN_SCOPE_LABELS = ("substantive", "definition")
UNIT_TYPES = ("dieu", "khoan", "diem")
# Từ báo hiệu (thẻ 1.6): dãy từ đã chuẩn hoá. "trường hợp" và "không áp dụng" gồm nhiều từ.
SIGNALS = (("nếu",), ("khi",), ("trường", "hợp"), ("trừ",), ("không", "áp", "dụng"), ("phải",), ("được",), ("bị", "coi", "là"))

SYSTEM = """Bạn đọc từng đơn vị của một văn bản pháp luật lao động Việt Nam (khoản, điểm hoặc Điều có chữ) và gạch ra các CỤM theo bốn vai:
- chu_the: ai bị quy tắc nói tới (ví dụ "Hai bên", "người lao động").
- dieu_kien: khi nào quy tắc áp dụng.
- ngoai_le: trừ khi nào (chữ sau "trừ", "ngoại trừ", "không áp dụng" ...).
- ket_luan: hệ quả của quy tắc (được, không được, phải, bị cấm, hưởng ...).
Mỗi đơn vị được cho kèm ngữ cảnh gồm ba phần: chu_don_vi (chữ của chính đơn vị), khoan_cha (chữ khoản cha, chỉ có khi đơn vị là điểm) và tieu_de_dieu (tiêu đề Điều).
Cụm có thể lấy từ BẤT KỲ phần nào trong ba phần, vì chủ thể hoặc kết luận nhiều khi nằm ở tiêu đề Điều hay khoản cha chứ không nằm trong chữ của đơn vị.
Quy tắc bắt buộc:
1. Mỗi cụm phải là chuỗi chữ LIỀN NHAU chép NGUYÊN VĂN từ một trong ba phần. Không viết lại, không diễn giải, không dịch, không bỏ chữ ở giữa.
2. Chỉ gạch cụm có nghĩa trong quy tắc của đơn vị đó. Đơn vị không nêu quy tắc nào (ví dụ chỉ nêu tên cơ quan) thì trả mảng spans rỗng.
3. params: chữ cái của thực thể mà cụm nói tới, chọn trong W (người lao động), E (người sử dụng lao động), C (hợp đồng lao động), J (nghề, công việc), G (vùng),
   D (ngày, mốc thời gian), A (số tiền, số lượng). Cụm không nói tới thực thể nào thì params rỗng.
4. Không đặt tên cho cụm và không phân loại gì thêm.
5. Mỗi đơn vị trong đầu vào có đúng một mục trong kết quả, ghi đúng unit_id.
Ví dụ cho đơn vị chu_don_vi = "Hai bên có thể giao kết hợp đồng lao động bằng lời nói đối với hợp đồng có thời hạn dưới 01 tháng, trừ trường hợp quy định tại khoản 2 Điều 18 của Bộ luật này.":
  chu_the "Hai bên" (params []); ket_luan "giao kết hợp đồng lao động bằng lời nói" (params ["C"]); dieu_kien "hợp đồng có thời hạn dưới 01 tháng" (params ["C"]);
  ngoai_le "quy định tại khoản 2 Điều 18 của Bộ luật này" (params []).
Trả về JSON đúng lược đồ."""

SCHEMA = {"type": "object", "additionalProperties": False, "required": ["units"],
          "properties": {"units": {"type": "array", "items": {
              "type": "object", "additionalProperties": False, "required": ["unit_id", "spans"],
              "properties": {"unit_id": {"type": "string"},
                             "spans": {"type": "array", "items": {
                                 "type": "object", "additionalProperties": False, "required": ["span", "role", "params"],
                                 "properties": {"span": {"type": "string"}, "role": {"type": "string", "enum": list(ROLES)},
                                                "params": {"type": "array", "items": {"type": "string", "enum": list(PARAMS)}}}}}}}}}}


# ---- chữ và vị trí từ ----

def norm_token(w):
    w = w.casefold()
    for a, b in TONE:
        w = w.replace(a, b)
    return w


def tokenize(text):
    """[(từ chuẩn hoá, bắt đầu, kết thúc)] trên chữ đã NFC. Vị trí là vị trí trong NFC(text), nên cắt đoạn nguyên văn theo vị trí đó được (chuẩn hoá từng từ không đổi độ dài)."""
    t = unicodedata.normalize("NFC", text or "")
    t = re.sub(r"\[\d+\]", lambda m: " " * len(m.group()), t)  # dấu chú thích [n] không phải chữ luật; thay bằng khoảng trắng để giữ nguyên vị trí
    return [(norm_token(m.group()), m.start(), m.end()) for m in re.finditer(r"\w+", t)], unicodedata.normalize("NFC", text or "")


def find_all(hay, needle):
    """Mọi vị trí bắt đầu (chỉ số từ) của dãy từ needle trong dãy từ hay."""
    n = len(needle)
    return [i for i in range(len(hay) - n + 1) if hay[i:i + n] == needle] if n else []


# ---- ngữ cảnh và lô ----

def dieu_of(uid):
    return ".".join(uid.split(".")[:2])


def unit_contexts(units, labels):
    """[{id, heading, chapeau, text}] của mọi đơn vị có chữ dưới Điều nhãn substantive hoặc definition, theo thứ tự tài liệu.
    chapeau = chữ khoản cha với điểm (thẻ 1.6, A26), và (A35) câu dẫn của chính Điều với khoản đứng dưới Điều có chữ trực tiếp
    (vd Điều 108: "Người sử dụng lao động có quyền yêu cầu ... trong trường hợp sau đây:" rồi K1, K2). Lần chạy đầu 13/11 thiếu câu dẫn này ở 46 khoản
    thuộc 10 Điều và 18/46 khoản không ra cụm chủ thể (39%, so với 16% ở phần còn lại). heading = tiêu đề Điều."""
    out = []
    for uid, u in units.items():
        if u["type"] not in UNIT_TYPES or not (u.get("text") or "").strip() or u.get("scope") == "out_of_scope":
            continue
        dieu = dieu_of(uid)
        if labels.get(dieu) not in IN_SCOPE_LABELS:
            continue
        parent = units.get(u.get("parent"))
        lead_in = parent if parent is not None and (u["type"] == "diem" or (u["type"] == "khoan" and parent["type"] == "dieu")) else None
        out.append({"id": uid, "heading": (units.get(dieu, {}).get("heading") or ""), "chapeau": (lead_in or {}).get("text") or "", "text": u["text"]})
    return out


def make_batches(contexts, size=BATCH_SIZE):
    """Mỗi lô là các đơn vị của MỘT Điều, theo thứ tự tài liệu; Điều dài hơn `size` đơn vị thì cắt thành lô liên tiếp. Chia theo Điều (không đóng gói đều theo thứ tự)
    để khoá cache của lô chỉ đổi khi chính Điều đó đổi: phạm vi đổi ở một Điều (như A21 đổi nhãn 6 Điều) không làm dịch ranh giới của mọi lô sau nó và bỏ phí cả lượt live."""
    by_dieu = collections.OrderedDict()
    for c in contexts:
        by_dieu.setdefault(dieu_of(c["id"]), []).append(c)
    return [units[i:i + size] for units in by_dieu.values() for i in range(0, len(units), size)]


def user_message(batch):
    return json.dumps({"don_vi": [{"unit_id": c["id"], "tieu_de_dieu": c["heading"], "khoan_cha": c["chapeau"], "chu_don_vi": c["text"]} for c in batch]},
                      ensure_ascii=False, indent=0)


def validate_output(output, ids):
    """Kiểm HÌNH của đầu ra (không kiểm nghĩa): sai thì ValueError và phản hồi không vào cache chính. Cụm hỏng từng cái xử lý ở gate_span, không làm hỏng cả lô."""
    items = output.get("units") if isinstance(output, dict) else None
    if not isinstance(items, list):
        raise ValueError("thiếu 'units'")
    seen = set()
    for it in items:
        if not isinstance(it, dict) or it.get("unit_id") not in ids:
            raise ValueError(f"unit_id ngoài lô: {it.get('unit_id') if isinstance(it, dict) else it!r}")
        if it["unit_id"] in seen:
            raise ValueError(f"unit_id lặp: {it['unit_id']}")
        seen.add(it["unit_id"])
        spans = it.get("spans")
        if not isinstance(spans, list) or not all(isinstance(s, dict) and isinstance(s.get("span"), str) and isinstance(s.get("role"), str)
                                                  and isinstance(s.get("params"), list) for s in spans):
            raise ValueError(f"'spans' sai hình ở {it['unit_id']}")


# ---- cổng ----

def locate(span, ctx):
    """(source, chỉ số từ đầu, chỉ số từ cuối + 1, đoạn nguyên văn) của lần khớp ĐẦU TIÊN trong own, rồi chapeau, rồi heading; hoặc None."""
    want = [w for w, _, _ in tokenize(span)[0]]
    if not want:
        return None
    for source, text in (("own", ctx["text"]), ("chapeau", ctx["chapeau"]), ("heading", ctx["heading"])):
        toks, nfc = tokenize(text)
        pos = find_all([w for w, _, _ in toks], want)
        if pos:
            a, b = pos[0], pos[0] + len(want)
            return source, a, b, nfc[toks[a][1]:toks[b - 1][2]]
    return None


def gate_span(item, ctx):
    """-> (ok, dict hàng hoặc lý do). item: {span, role, params} từ LLM. Hàng chưa có targets (điền sau)."""
    if item["role"] not in ROLES:
        return False, f"vai ngoài bốn vai: {item['role']!r}"
    params = [p for p in item["params"]]
    if not all(isinstance(p, str) and p in PARAMS for p in params):
        return False, f"tham số ngoài {''.join(PARAMS)}: {params!r}"
    hit = locate(item["span"], ctx)
    if hit is None:
        return False, "cụm không là chuỗi từ liền nhau của ngữ cảnh"
    source, a, b, verbatim = hit
    return True, {"unit": ctx["id"], "span": verbatim, "role": item["role"], "source": source, "predicate": None,
                  "params": list(dict.fromkeys(params)), "targets": [], "how": "llm", "flags": [], "_a": a, "_b": b}


def cond_node_rows(contexts_by_id, nodes):
    """Cụm ngoại lệ từ nút điều kiện 1.5: mỗi (nút, đơn vị nằm trong phạm vi) một hàng, how=cond_node, params []. -> (rows, rejected)."""
    rows, rejected = [], []
    for node in nodes:
        for uid in node["units"]:
            ctx = contexts_by_id.get(uid)
            if ctx is None:
                continue
            hit = locate(node["text"], ctx)
            if hit is None or hit[0] != "own":
                rejected.append({"unit": uid, "span": node["text"], "role": "ngoai_le", "reason": "nút điều kiện 1.5 không nằm trong chữ của đơn vị"})
                continue
            _, a, b, verbatim = hit
            rows.append({"unit": uid, "span": verbatim, "role": "ngoai_le", "source": "own", "predicate": None, "params": [], "targets": [],
                         "how": "cond_node", "flags": [], "_a": a, "_b": b})
    return rows, rejected


def attach_targets(rows, contexts_by_id, refs_by_unit):
    """Điền targets của cụm own từ cạnh refers_to đã giải: đích được tính khi chữ dẫn chiếu (evidence) nằm trọn trong cụm. Dẫn chiếu chỉ chồng lên biên cụm thì không tính,
    đếm lại để báo. -> số lần vắt qua biên."""
    straddle = 0
    cache = {}
    for r in rows:
        if r["source"] != "own":
            continue
        ctx = contexts_by_id[r["unit"]]
        own = cache.setdefault(r["unit"], [w for w, _, _ in tokenize(ctx["text"])[0]])
        inside, over = [], 0
        for ref in refs_by_unit.get(r["unit"], []):
            ev = [w for w, _, _ in tokenize(ref["evidence"])[0]]
            occ = [(i, i + len(ev)) for i in find_all(own, ev)]
            if any(r["_a"] <= i and j <= r["_b"] for i, j in occ):
                inside.append(ref["o"])
            elif any(i < r["_b"] and j > r["_a"] for i, j in occ):
                over += 1
        r["targets"] = list(dict.fromkeys(inside))
        straddle += over
    return straddle


def uncovered_signals(contexts, rows):
    """[{unit, signal, sentence}] từ báo hiệu trong chữ của đơn vị mà không có cụm own nào phủ hoặc kề (cách cụm tối đa một từ)."""
    by_unit = collections.defaultdict(list)
    for r in rows:
        if r["source"] == "own":
            by_unit[r["unit"]].append((r["_a"], r["_b"]))
    out = []
    for ctx in contexts:
        toks = [w for w, _, _ in tokenize(ctx["text"])[0]]
        for sig in SIGNALS:
            for i in find_all(toks, list(sig)):
                if not any(i < b + 1 and i + len(sig) > a - 1 for a, b in by_unit.get(ctx["id"], [])):
                    out.append({"unit": ctx["id"], "signal": " ".join(sig), "sentence": ctx["text"]})
    return out


# ---- chạy một văn bản ----

def process_doc(doc_id, units, labels, nodes, refs, client, max_batches=None):
    """-> (rows, rejected, uncovered, stats, notes). client None = chế độ off."""
    contexts = unit_contexts(units, labels)
    by_id = {c["id"]: c for c in contexts}
    batches = make_batches(contexts)
    stats = collections.Counter(units_in_scope=len(contexts), batches=len(batches))
    notes = []
    llm_rows, rejected = [], []
    llm_units = set()  # đơn vị thuộc lô đã có kết quả LLM (chỉ ở đó mới so được cụm ngoại lệ LLM với nút 1.5)
    quota_hit = False
    for i, batch in enumerate(batches, 1):
        if client is None:
            stats["batches_off"] += 1
            continue
        if max_batches is not None and i > max_batches:
            stats["batches_skipped_by_option"] += 1
            continue
        if quota_hit:
            stats["batches_quota"] += 1
            continue
        ids = {c["id"] for c in batch}
        try:
            rec = client.ask(TASK, PROMPT_VERSION, SYSTEM, user_message(batch), SCHEMA, role="trich", validate=lambda out: validate_output(out, ids),
                             label=f"lô {i}/{len(batches)}")
        except llm_client.CacheMiss:
            stats["batches_cache_miss"] += 1
            continue
        except llm_client.QuotaReached as e:
            stats["batches_quota"] += 1
            quota_hit = True
            notes.append(str(e))
            continue
        except ValueError as e:  # InvalidOutput hoặc lỗi hình: lô này không có kết quả, các lô khác vẫn chạy
            stats["batches_invalid"] += 1
            notes.append(f"lô {i}: đầu ra bị loại ({e})")
            continue
        except llm_client.LLMError as e:
            raise SystemExit(f"LỖI LLM ở lô {i}/{len(batches)}: {e}\n(các lô đã gọi xong nằm trong data/llm_cache/{TASK}/, chạy lại sẽ đọc từ cache)")
        stats["batches_ok"] += 1
        llm_units |= ids
        stats["units_without_entry"] += len(ids - {it["unit_id"] for it in rec["output"]["units"]})  # LLM bỏ cả đơn vị (khác với trả mảng rỗng)
        for it in rec["output"]["units"]:
            ctx = by_id[it["unit_id"]]
            for item in it["spans"]:
                stats["spans_proposed"] += 1
                ok, res = gate_span(item, ctx)
                if ok:
                    llm_rows.append(res)
                else:
                    rejected.append({"unit": it["unit_id"], "span": item["span"], "role": item["role"], "reason": res})
    node_rows, node_rejected = cond_node_rows(by_id, nodes)
    rejected += node_rejected
    # trùng: cụm LLM cùng (đơn vị, vai, chuỗi từ) với cụm khác chỉ giữ một; cụm ngoại lệ LLM trùng chữ nút 1.5 thì giữ dòng cond_node (thẻ 1.6).
    # A35: "trùng" cũng gồm cụm ngoại lệ LLM chứa hoặc nằm trong chữ nút 1.5 của cùng đơn vị (so theo vị trí từ, vd D185.K5: LLM gạch "trường hợp quy định tại
    # điểm c khoản 4 Điều này", nút là "quy định tại điểm c khoản 4 Điều này"): lần chạy đầu 13/11 ghi một ngoại lệ hai lần ở 11 đơn vị. Giữ dòng nút vì nó có targets
    # (dẫn chiếu do máy nối, LLM không đụng). Cái mất: chữ LLM chứa nút mà dài hơn nút thì phần dài thêm bị bỏ.
    node_pos = collections.defaultdict(list)
    for r in node_rows:
        node_pos[r["unit"]].append((r["_a"], r["_b"]))
    rows, seen = [], set()
    for r in node_rows + llm_rows:
        key = (r["unit"], r["role"], tuple(w for w, _, _ in tokenize(r["span"])[0]))
        nested_in_node = (r["how"] == "llm" and r["role"] == "ngoai_le" and r["source"] == "own"
                          and any(a <= r["_a"] and r["_b"] <= b or r["_a"] <= a and b <= r["_b"] for a, b in node_pos.get(r["unit"], [])))
        if key in seen or nested_in_node:
            stats["duplicates_dropped"] += 1
            continue
        seen.add(key)
        rows.append(r)
    order = {c["id"]: i for i, c in enumerate(contexts)}
    src = {"own": 0, "chapeau": 1, "heading": 2}
    rows.sort(key=lambda r: (order[r["unit"]], src[r["source"]], r["_a"], r["_b"], r["role"]))
    stats["straddling_refs"] = attach_targets(rows, by_id, collections.defaultdict(list, refs))
    uncovered = uncovered_signals(contexts, rows)
    # G4 (báo): nút 1.5 mà LLM không gạch cụm ngoại lệ nào trùng hoặc chứa nó (chỉ xét đơn vị thuộc lô đã có kết quả LLM)
    llm_exc = collections.defaultdict(list)
    for r in llm_rows:
        if r["role"] == "ngoai_le" and r["source"] == "own":
            llm_exc[r["unit"]].append([w for w, _, _ in tokenize(r["span"])[0]])
    for r in node_rows:
        if r["unit"] in llm_units:
            node = [w for w, _, _ in tokenize(r["span"])[0]]
            if not any(find_all(s, node) or find_all(node, s) for s in llm_exc.get(r["unit"], [])):
                stats["node_without_matching_llm_span"] += 1
    stats["rows_total"] = len(rows)
    for r in rows:
        stats[f"rows_{r['how']}"] += 1
        stats[f"role_{r['role']}"] += 1
        stats["rows_with_targets"] += bool(r["targets"])
    stats["units_with_span"] = len({r["unit"] for r in rows})
    for r in rows:
        del r["_a"], r["_b"]
    return rows, rejected, uncovered, stats, notes


def load_inputs(doc_id):
    docs, all_units, resolver, available = l2.load_context()
    doc = corpus.get_doc(doc_id, docs)
    lab_path = corpus.out_dir("l4") / "l4_labels.jsonl"
    nodes_path = corpus.out_dir("l5_general") / f"l5_general_conditions_{doc.doc_id}.jsonl"
    refs_path = l2.l2_dir() / f"l2_refs_{doc.doc_id}.jsonl"
    for p, step in ((lab_path, "article_type.py"), (nodes_path, "exceptions_general.py"), (refs_path, "refs.py")):
        if not p.exists():
            raise SystemExit(f"chưa có {p.name}; chạy src/{step} trước")
    labels = {r["id"]: r["label"] for r in l1.read_jsonl(lab_path)}
    refs = collections.defaultdict(list)
    for r in l1.read_jsonl(refs_path):
        if r["p"] == "refers_to":
            refs[r["s"]].append(r)
    return doc, all_units[doc.doc_id], labels, l1.read_jsonl(nodes_path), refs


def report_lines(doc_id, stats, uncovered, rejected, notes, mode):
    s = stats
    n_b = s["batches"]
    lines = [f"1.6 gạch cụm (giai đoạn A) báo cáo: {doc_id}", f"chế độ LLM: {mode}",
             f"đơn vị trong phạm vi: {s['units_in_scope']}  lô: {n_b} (mỗi lô là một Điều; Điều dài hơn {BATCH_SIZE} đơn vị thì cắt)"]
    if mode == "off":
        lines.append("LLM TẮT: chỉ có cụm ngoại lệ từ nút điều kiện 1.5 và targets; KHÔNG có cụm chủ thể, điều kiện, kết luận")
    else:
        lines.append(f"lô có kết quả LLM: {s['batches_ok']}/{n_b}  thiếu cache: {s['batches_cache_miss']}  hết hạn mức: {s['batches_quota']}  "
                     f"đầu ra bị loại: {s['batches_invalid']}  bỏ qua theo --max-batches: {s['batches_skipped_by_option']}")
        if s["batches_ok"] < n_b - s["batches_skipped_by_option"]:
            lines.append(f"!!! CHƯA ĐỦ KẾT QUẢ LLM: {n_b - s['batches_ok'] - s['batches_skipped_by_option']} lô không có cụm LLM; đơn vị của các lô đó chỉ có phần máy làm")
    if mode != "off":
        lines.append(f"đơn vị LLM KHÔNG trả mục nào (khác với trả mảng cụm rỗng; nên xem đầu tiên sau lượt chạy thử): {s['units_without_entry']}")
    lines += [f"cụm LLM đề xuất: {s['spans_proposed']}; bị loại: {len(rejected)}; trùng bỏ bớt: {s['duplicates_dropped']}",
              f"hàng trong bảng cụm: {s['rows_total']} (llm {s['rows_llm']}, cond_node {s['rows_cond_node']}); có targets: {s['rows_with_targets']}; đơn vị có ít nhất một cụm: {s['units_with_span']}/{s['units_in_scope']}",
              "theo vai: " + ", ".join(f"{r} {s['role_' + r]}" for r in ROLES),
              f"dẫn chiếu nằm vắt qua biên cụm (không tính vào targets): {s['straddling_refs']}",
              f"BÁO: từ báo hiệu chưa có cụm phủ hoặc kề: {len(uncovered)} lần ở {len({u['unit'] for u in uncovered})} đơn vị",
              f"BÁO: nút điều kiện 1.5 mà LLM không gạch cụm ngoại lệ trùng hoặc chứa nó: {s['node_without_matching_llm_span']}"]
    why = collections.Counter(r["reason"].split(":")[0] for r in rejected)
    if why:
        lines.append("lý do loại cụm: " + "; ".join(f"{n} x {r}" for r, n in why.most_common()))
    lines += [f"ghi chú: {n}" for n in notes]
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--doc", default=corpus.BASE_DOC_ID)
    ap.add_argument("--llm", choices=("off", "replay", "live"), default="off", help="off: chỉ phần máy (mặc định); replay: đọc cache; live: gọi API khi thiếu cache")
    ap.add_argument("--max-batches", type=int, default=None, help="chỉ xử lý N lô đầu (chạy thử live rẻ trước khi chạy cả bộ)")
    args = ap.parse_args(argv)
    if args.llm == "live":
        provider = llm_client.provider_of(llm_client.load_config(), "trich")  # 1.6 dùng vai trich (A34), nhà cung cấp theo docs/llm_config.md
        if not llm_client.key_is_set(provider):
            var = llm_client.PROVIDERS[provider]
            raise SystemExit(f"--llm live nhưng không thấy {var} trong môi trường của process này (đặt khoá MỘT LẦN bằng `setx {var}` ở terminal riêng rồi mở terminal mới; xem đầu src/run_all.py)")
    client = llm_client.Client(args.llm, log=llm_client.stderr_log) if args.llm != "off" else None
    doc, units, labels, nodes, refs = load_inputs(args.doc)
    rows, rejected, uncovered, stats, notes = process_doc(doc.doc_id, units, labels, nodes, refs, client, args.max_batches)
    out = corpus.out_dir(DIR_NAME)
    l1.write_jsonl(out / f"concepts_spans_{doc.doc_id}.jsonl", rows)
    l1.write_jsonl(out / f"concepts_rejected_{doc.doc_id}.jsonl", rejected)
    l1.write_jsonl(out / f"concepts_uncovered_{doc.doc_id}.jsonl", uncovered)
    lines = report_lines(doc.doc_id, stats, uncovered, rejected, notes, args.llm)
    if client is not None:
        lines.append(f"LLM: gọi API lần này: {client.calls}; đọc từ cache: {client.hits}; hôm nay đã dùng trich {client.used_today('trich')}")
    rp = corpus.report_dir(DIR_NAME) / f"concepts_report_{doc.doc_id}.txt"
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()
