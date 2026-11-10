"""L4: gắn mỗi Điều một nhãn để biết nó đi tiếp tới bước nào (trích quy tắc, chỉ thị hiệu lực, chỉ giữ chữ ...).

Chạy: python -I src/l4_classify.py [--llm off|replay|live]       (cả kho; cần l1)
Đầu ra: data/processed/l4/l4_labels.jsonl  {id, label, how, heading, flags}; docs/bao_cao_chay/l4/l4_report.txt.

Nhãn: substantive (điều có điều kiện, quyền, nghĩa vụ, mức, thời hạn, ngoại lệ, chế tài) | definition | effect_transition (hiệu lực,
chuyển tiếp, bãi bỏ, và các Điều "Sửa đổi, bổ sung ..." của văn bản sửa đổi: nguồn câu chỉ thị cho L6) | procedural (hồ sơ, trình tự,
thủ tục) | authority (trách nhiệm, thẩm quyền cơ quan) | appendix (phụ lục) .
Mọi Điều vẫn nằm trong KB, vẫn có phiên bản và là đích sửa đổi được; nhãn chỉ quyết định Điều đó có được dịch thành quy tắc không.

Cách xếp: regex trên tiêu đề trước (how=regex). Điều không khớp mẫu nào mang nhãn TẠM substantive (an toàn hơn: không bỏ sót quy tắc), how=default_pending_llm,
cờ llm_pending. Với --llm replay / live, các Điều đó được phân loại theo lô bằng model chính (llm_config.md), và KHÔNG áp thẳng:
  - đầu ra phải đúng lược đồ, đủ và không thừa khoá của lô, nhãn thuộc tập cho phép; lô sai bị loại cả lô (Điều vẫn nhãn tạm; số lô bị loại và lý do ở báo cáo; phản hồi sai nằm ở data/llm_cache/l4_classify/_rejected/ và KHÔNG vào cache chính nên chạy lại sẽ gọi lại);
  - nhãn đẩy một Điều RA KHỎI substantive (procedural, authority, effect_transition) phải được model kiểm (model khác) phân loại độc lập ra cùng nhãn; khác nhau hoặc
    chưa kiểm được thì Điều trả về nhãn tạm (cờ llm_disagree / llm_unverified), vì nhãn sai ở hướng này làm mất quy tắc của một điều có điều kiện thật.
Điều trùng tiêu đề và đoạn đầu (bản hợp nhất giống BLLĐ) chỉ hỏi một lần. Hết hạn mức thì dừng gọn; chạy lại hôm sau đọc phần đã lưu từ cache.
"""
import argparse
import collections
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import l1_parse as l1
import l6_versions as l6v
import corpus
import llm_client

L4_DIR_NAME = "l4"
TASK, PROMPT_VERSION, BATCH = "l4_classify", "l4-1", 40
LABELS = ("substantive", "definition", "effect_transition", "procedural", "authority")
VERIFY_LABELS = ("effect_transition", "procedural", "authority")  # nhãn đẩy Điều ra khỏi substantive: cần model kiểm duyệt lại

RULES = [  # (nhãn, regex trên tiêu đề, theo thứ tự ưu tiên)
    ("definition", re.compile(r"^Giải thích từ ngữ", re.I)),
    ("effect_transition", re.compile(r"^(?:Hiệu lực(?: thi hành)?|Quy định chuyển tiếp|Điều khoản chuyển tiếp|Điều khoản thi hành|Bãi bỏ|"
                                      r"Sửa đổi, bổ sung|Sửa đổi|Bổ sung|Thay thế|Hết hiệu lực|Áp dụng pháp luật)", re.I)),
    # "Trách nhiệm" chỉ là authority khi chủ thể là cơ quan, tổ chức nhà nước; "Trách nhiệm khi chấm dứt hợp đồng lao động" là nghĩa vụ của các bên.
    ("authority", re.compile(r"^(?:Trách nhiệm của (?:các )?(?:Bộ|cơ quan|Ủy ban|Sở|Chính phủ|Thủ tướng|Tổng liên đoàn|UBND|tổ chức có thẩm quyền)|"
                             r"Trách nhiệm (?:thi hành|quản lý nhà nước)|Thẩm quyền|Nhiệm vụ|Quyền hạn|Tổ chức thực hiện|Cơ quan)", re.I)),
    ("procedural", re.compile(r"^(?:Hồ sơ|Trình tự|Thủ tục|Cách thức|Tiếp nhận|Nộp hồ sơ|Thời hạn giải quyết|Quy trình)", re.I)),
]

SYSTEM = """Bạn phân loại các Điều của văn bản pháp luật lao động Việt Nam (bộ luật, nghị định, thông tư) để quyết định Điều nào được dịch thành quy tắc.
Mỗi mục có: k (mã), loại văn bản, tiêu đề Điều, đoạn đầu của Điều. Với MỖI mục chọn đúng một nhãn:
- substantive: Điều có điều kiện, quyền, nghĩa vụ, mức, thời hạn, ngoại lệ, chế tài mà từ đó trả lời được câu hỏi có/không về việc áp dụng pháp luật.
- definition: Điều giải thích từ ngữ, định nghĩa khái niệm.
- effect_transition: Điều về hiệu lực thi hành, quy định chuyển tiếp, bãi bỏ, sửa đổi bổ sung văn bản khác.
- procedural: Điều chỉ nói hồ sơ, trình tự, thủ tục, biểu mẫu, không có điều kiện áp dụng thực chất.
- authority: Điều chỉ nói trách nhiệm, nhiệm vụ, thẩm quyền của cơ quan, tổ chức nhà nước (không phải nghĩa vụ của người lao động / người sử dụng lao động).
Không chắc thì chọn substantive. Chỉ dựa vào tiêu đề và đoạn đầu được cho. Trả về JSON đúng lược đồ, đủ mọi mã k, mỗi mã một lần."""

SCHEMA = {"type": "object", "additionalProperties": False, "required": ["labels"],
          "properties": {"labels": {"type": "array", "items": {
              "type": "object", "additionalProperties": False, "required": ["k", "label"],
              "properties": {"k": {"type": "string"}, "label": {"type": "string", "enum": list(LABELS)}}}}}}


def classify_heading(heading):
    """-> (nhãn, how). Không khớp mẫu nào thì nhãn tạm substantive, how=default_pending_llm."""
    for label, rx in RULES:
        if rx.match(heading or ""):
            return label, "regex"
    return "substantive", "default_pending_llm"


# ---- nhánh LLM ----

def snippet(units, dieu_id, n=160):
    """Đoạn chữ đầu của Điều (chính nó, không có thì con đầu có chữ), cắt n ký tự."""
    for uid, u in units.items():
        if (uid == dieu_id or uid.startswith(dieu_id + ".")) and (u.get("text") or "").strip():
            return re.sub(r"\s+", " ", u["text"]).strip()[:n]
    return ""


def collect_items(rows, units_by_doc, docs):
    """Gom các Điều còn nhãn tạm thành mục duy nhất theo (tiêu đề, đoạn đầu): bản hợp nhất trùng chữ với BLLĐ chỉ hỏi một lần. -> list mục có khoá k."""
    items = collections.OrderedDict()
    for r in rows:
        if r["how"] != "default_pending_llm":
            continue
        doc_id = r["id"].split(".")[0]
        snip = snippet(units_by_doc[doc_id], r["id"])
        key = (l6v.text_norm(r["heading"]), l6v.text_norm(snip))
        it = items.setdefault(key, {"heading": r["heading"], "snippet": snip, "doc_type": docs[doc_id].loai, "ids": []})
        it["ids"].append(r["id"])
    out = list(items.values())
    for i, it in enumerate(out, 1):
        it["k"] = f"k{i}"
    return out


def validate_labels(output, keys):
    """Kiểm đầu ra của một lô: đúng lược đồ, nhãn thuộc LABELS, đủ và không thừa, không trùng khoá. Sai thì ValueError (loại cả lô)."""
    labels = output.get("labels") if isinstance(output, dict) else None
    if not isinstance(labels, list):
        raise ValueError("thiếu danh sách 'labels'")
    got = {}
    for x in labels:
        if not isinstance(x, dict) or x.get("k") not in keys or x.get("label") not in LABELS:
            raise ValueError(f"mục không hợp lệ: {x!r}")
        if x["k"] in got:
            raise ValueError(f"trùng mã {x['k']}")
        got[x["k"]] = x["label"]
    if set(got) != set(keys):
        raise ValueError(f"thiếu mã {sorted(set(keys) - set(got))}")
    return got


def ask_batch(client, batch, role, label=None):
    user = json.dumps([{"k": it["k"], "loai_van_ban": it["doc_type"], "tieu_de": it["heading"], "doan_dau": it["snippet"]} for it in batch],
                      ensure_ascii=False, indent=0)
    keys = [it["k"] for it in batch]
    rec = client.ask(TASK, PROMPT_VERSION, SYSTEM, user, SCHEMA, role=role, validate=lambda out: validate_labels(out, keys), label=label)
    return validate_labels(rec["output"], keys)


def chunks(seq, n=None):
    n = n or BATCH  # đọc BATCH lúc gọi (không buộc lúc định nghĩa) để test đổi được kích thước lô
    return [seq[i:i + n] for i in range(0, len(seq), n)]


def run_pass(client, items, role, stats, notes):
    """Một lượt phân loại theo lô với một vai. -> {k: nhãn} cho các lô thành công. Hết hạn mức thì dừng gọn; thiếu cache (replay) bỏ qua lô."""
    got = {}
    batches = chunks(items)
    if client.log:
        client.log(f"[L4] lượt {role}: {len(items)} mục chia {len(batches)} lô (lô nào đã có trong cache thì đọc lại, không gọi API và không in dòng riêng)")
    for i, batch in enumerate(batches, 1):
        try:
            got.update(ask_batch(client, batch, role, f"lô {i}/{len(batches)}"))
        except llm_client.CacheMiss:
            stats[f"{role}_cache_miss_items"] += len(batch)
        except llm_client.QuotaReached as e:
            stats[f"{role}_quota_stop"] += 1
            notes.append(f"dừng gọn ({role}): {e}; phần còn lại chạy tiếp hôm sau, phần đã gọi nằm trong cache")
            break
        except ValueError as e:
            stats[f"{role}_batch_rejected"] += 1
            notes.append(f"lô bị loại ({role}, {len(batch)} mục): {e} (phản hồi ở data/llm_cache/{TASK}/_rejected/, chạy lại sẽ gọi lại)")
    return got


def apply_llm(rows, items, proposed, verified):
    """Áp nhãn LLM lên rows theo luật ở docstring đầu file. Trả Counter các kết cục theo số Điều."""
    by_id = {r["id"]: r for r in rows}
    out = collections.Counter()
    for it in items:
        p = proposed.get(it["k"])
        for uid in it["ids"]:
            r = by_id[uid]
            if p is None:
                out["chua_co_de_xuat"] += 1
                continue
            if p in VERIFY_LABELS and verified.get(it["k"]) != p:
                r["flags"] = ["llm_pending", "llm_disagree" if it["k"] in verified else "llm_unverified"]
                out["tra_ve_nhan_tam_disagree" if it["k"] in verified else "tra_ve_nhan_tam_unverified"] += 1
                continue
            r["label"], r["how"] = p, "llm"
            r["flags"] = ["llm_proposed"] + (["llm_verified"] if p in VERIFY_LABELS else [])
            out[f"nhan_{p}"] += 1
    return out


def llm_classify(client, rows, units_by_doc, docs):
    """-> (kết cục theo Điều, stats, notes, số mục duy nhất)."""
    stats, notes = collections.Counter(), []
    items = collect_items(rows, units_by_doc, docs)
    proposed = run_pass(client, items, "chinh", stats, notes)
    need = [it for it in items if proposed.get(it["k"]) in VERIFY_LABELS]
    verified = run_pass(client, need, "kiem", stats, notes)
    return apply_llm(rows, items, proposed, verified), stats, notes, len(items)


# ---- chạy ----

def build_rows(docs):
    rows, units_by_doc = [], {}
    for doc_id in docs:
        units = units_by_doc[doc_id] = l1.load_units(doc_id)
        for uid, u in units.items():
            if u["type"] == "dieu":
                label, how = classify_heading(u.get("heading", ""))
                rows.append({"id": uid, "label": label, "how": how, "heading": u.get("heading", ""),
                             "flags": ["llm_pending"] if how == "default_pending_llm" else []})
            elif u["type"] == "pl":
                rows.append({"id": uid, "label": "appendix", "how": "type", "heading": u.get("heading") or "", "flags": []})
    return rows, units_by_doc


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--llm", choices=("off", "replay", "live"), default="off", help="off: chỉ regex (mặc định); replay: đọc cache; live: gọi API khi thiếu cache")
    args = ap.parse_args(argv)
    if args.llm == "live" and not llm_client.key_is_set():
        raise SystemExit("--llm live nhưng không thấy GEMINI_API_KEY trong môi trường của process này (đặt khoá MỘT LẦN bằng `setx GEMINI_API_KEY` ở terminal riêng rồi mở terminal mới; xem đầu src/run_all.py)")
    docs = corpus.load_manifest()
    rows, units_by_doc = build_rows(docs)
    llm_lines = ["LLM: tắt (--llm off); các Điều chưa xếp được giữ nhãn tạm substantive"]
    if args.llm != "off":
        client = llm_client.Client(args.llm, log=llm_client.stderr_log)
        try:
            outcome, stats, notes, n_items = llm_classify(client, rows, units_by_doc, docs)
        except llm_client.LLMError as e:
            raise SystemExit(f"LỖI LLM: {e}\n(các lô đã gọi xong nằm trong data/llm_cache/{TASK}/, chạy lại sẽ đọc từ cache)")
        llm_lines = [f"LLM: --llm {args.llm}; {n_items} mục duy nhất (Điều trùng tiêu đề và đoạn đầu hỏi một lần); gọi API lần này: {client.calls}; "
                     f"đọc từ cache: {client.hits}; hôm nay đã dùng {{chinh: {client.used_today('chinh')}, kiem: {client.used_today('kiem')}}}",
                     f"kết cục theo Điều: {dict(outcome)}", f"đếm lô: {dict(stats)}"] + [f"  {n}" for n in notes]
        # L6 đọc câu chỉ thị hiệu lực chỉ từ Điều nhãn effect_transition: liệt kê các Điều do LLM đặt nhãn này để người duyệt xem
        eff = [r["id"] for r in rows if r["how"] == "llm" and r["label"] == "effect_transition"]
        llm_lines += [f"Điều do LLM đặt nhãn effect_transition (L6 sẽ đọc chỉ thị từ đây, cần duyệt): {len(eff)}"] + [f"  {i}" for i in eff]
    l1.write_jsonl(corpus.out_dir(L4_DIR_NAME) / "l4_labels.jsonl", rows)

    report = ["L4 báo cáo", f"tổng Điều/phụ lục có nhãn: {len(rows)}"]
    by_doc = collections.defaultdict(collections.Counter)
    for r in rows:
        by_doc[r["id"].split(".")[0]][r["label"]] += 1
    report.append("phân bố nhãn theo văn bản:")
    report += [f"  {d:<22} {dict(c)}" for d, c in by_doc.items()]
    how = collections.Counter(r["how"] for r in rows)
    report.append(f"cách xếp: regex {how['regex']}; LLM {how['llm']}; chưa xếp được (nhãn tạm substantive, chờ LLM): {how['default_pending_llm']}; phụ lục: {how['type']}")
    report += llm_lines
    sample = random.Random(20261109).sample([r for r in rows if r["label"] != "appendix"], 10)
    report.append("10 Điều mẫu ngẫu nhiên (hạt giống cố định):")
    report += [f"  {r['id']:<34} {r['label']:<18} {r['how']:<20} {r['heading'][:60]}" for r in sample]
    path = corpus.report_dir(L4_DIR_NAME) / "l4_report.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(report) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(report))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()
