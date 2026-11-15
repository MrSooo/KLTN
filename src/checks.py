"""checks: kiểm tra độc lập các bước 1.1-2.4 trên cả kho; đối chiếu số đếm với đĩa và các mốc cổng đã chốt.

Chạy: python -I src/checks.py          (cần các bước trước đã chạy; thoát mã 1 nếu có vi phạm)
Báo cáo: docs/run_reports/checks/checks_report.txt.

Số đối chiếu cứng (EXPECTED) chỉ cho BLLĐ; nguồn độc lập với 1.1:
  Điều: grep -c -E '^Điều [0-9]+\\.' data/raw/labor/base/BLLD_45-2019.txt            = 220 (khớp cột so_dieu_dem_duoc của manifest)
  Khoản: grep -c -E '^[0-9]+[a-z]?\\. ' ...                                         = 645; trừ 7 dòng nằm trong 4 khối trích dẫn của Điều 219 = 638
  Điểm:  grep -c -E '^[a-zđ][0-9]?\\) ' ...                                         = 287; trừ 20 dòng trong các khối đó             = 267
Phép đếm thứ hai (independent_counts) quét file thô bằng bộ đếm nháy riêng, không dùng 1.1.
"""
import collections
import datetime
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import parse
import refs
import versions
import corpus
from textutil import text_norm


class Expect(NamedTuple):
    dieu: int
    khoan: int
    diem: int


EXPECTED = {"BLLD_45-2019": Expect(dieu=220, khoan=638, diem=267)}
D = datetime.date


def independent_counts(path):
    """Đếm Điều / Khoản / Điểm trên file thô: bỏ dòng trong khối “...” (bắt đầu ở dòng mở nháy, kết thúc khi nháy cân bằng) và dừng
    ở phụ lục đầu tiên. Cài đặt riêng, không dùng 1.1."""
    n = collections.Counter()
    depth = 0
    for raw in open(path, encoding="utf-8").read().split("\n"):
        line = raw.strip()
        if depth > 0:
            depth += line.count("“") - line.count("”")
            continue
        if line.startswith("“") and line.count("“") > line.count("”"):
            depth = line.count("“") - line.count("”")
            continue
        if re.match(r"^(PHỤ LỤC|Phụ lục)\b", line):
            break
        if re.match(r"^Điều \d+[a-z]?\.", line):
            n["dieu"] += 1
        elif re.match(r"^\d+[a-z]?\. ", line):
            n["khoan"] += 1
        elif re.match(r"^[a-zđ]\d?\) ", line):
            n["diem"] += 1
    return n


def version_problems(by):
    """Bất biến của phiên bản theo mã (by: {id: [dòng versions]}): số phiên bản liên tiếp, phiên bản kế chỉ có khi phiên bản trước đã
    đóng, khoảng hiệu lực nửa mở không chồng nhau, from không sau to."""
    p = []
    for uid, vs in by.items():
        for i, v in enumerate(vs):
            if v["version"] != i + 1 or v["previous_version"] != (i if i else None):
                p.append(f"{uid}: số phiên bản không liên tiếp")
        for a_, b_ in zip(vs, vs[1:]):
            if a_["effective_to"] is None:
                p.append(f"{uid}: phiên bản {a_['version']} chưa đóng mà đã có phiên bản kế")
            elif b_["effective_from"] is not None and b_["effective_from"] < a_["effective_to"]:
                p.append(f"{uid}: khoảng hiệu lực v{a_['version']} / v{b_['version']} chồng nhau")
        for v in vs:
            if v["effective_from"] and v["effective_to"] and not v["effective_from"] <= v["effective_to"]:
                p.append(f"{uid} v{v['version']}: effective_from sau effective_to")
    return p


# Ca "trừ" BLLĐ mà 1.5 chưa xử lý, kèm lý do (12/11). Đổi danh sách này chỉ khi đã đọc ca mới/ca bị bớt.
BLLD_UNHANDLED_KNOWN = {"D24.K3": "'không áp dụng' không kèm dẫn chiếu tới đơn vị bị loại trừ",
                        "D188.K1": "ngoại lệ liệt kê ở các đơn vị con (đoạn kết thúc bằng dấu hai chấm)"}


def residue_problems(got, known):
    """[] nếu tập ca chưa xử lý đúng bằng danh sách đã biết; không thì một dòng nêu ca thừa và ca thiếu."""
    if got == known:
        return []
    return [f"ca 'trừ' chưa xử lý của BLLĐ lệch danh sách đã biết: thừa {sorted(got - known)}, thiếu {sorted(known - got)}"]


def lead_in_text(units, u):
    """Chữ câu dẫn (chapeau) của đơn vị u theo mô tả bước 1.6, tính lại độc lập với concepts.py: chữ khoản cha của điểm, hoặc (A35) chữ của Điều
    đứng trên khoản. Lần chạy 14/11 có cụm chapeau ở khoản (D67.K1-8) bị báo lỗi vì chỗ này vẫn chỉ tính cho điểm."""
    parent = units.get(u.get("parent"))
    if parent is not None and (u["type"] == "diem" or (u["type"] == "khoan" and parent["type"] == "dieu")):
        return parent.get("text") or ""
    return ""


NAME_RE = re.compile(r"^[a-z][a-z0-9_]{2,49}$")  # mô tả bước 1.6 bước 9; chép lại (không import) để kiểm độc lập


def names_files_problems(spans, units, base):
    d = corpus.out_dir("concepts")
    pn, pl = d / f"concepts_named_{base}.jsonl", d / f"concepts_ledger_{base}.jsonl"
    if not (pn.exists() and pl.exists()):
        return [f"chưa có {pn.name} hoặc {pl.name}"]
    return names_problems(spans, units, parse.read_jsonl(pn), parse.read_jsonl(pl))


def names_problems(spans, units, named, ledger):
    """Bất biến của đầu ra 1.6B, đúng cả khi chưa có lượt nào (off, hoặc replay dừng CHƯA ĐỦ: predicate toàn null, sổ rỗng)."""
    p = []
    if len(named) != len(spans):
        return [f"bảng đặt tên có {len(named)} hàng, bảng cụm có {len(spans)}"]
    name_of_text = {}
    rows_of = collections.defaultdict(list)
    for a, b in zip(spans, named):
        if {k: v for k, v in a.items() if k not in ("predicate", "flags")} != {k: v for k, v in b.items() if k not in ("predicate", "flags")}:
            p.append(f"{b['unit']}: hàng đặt tên khác hàng bảng cụm ngoài predicate/flags")
            continue
        name = b["predicate"]
        if b["targets"]:
            if name is not None or b["flags"]:
                p.append(f"{b['unit']}: hàng có targets mà có tên hoặc cờ")
            continue
        key = text_norm(b["span"])
        if name_of_text.setdefault(key, name) != name:
            p.append(f"{b['unit']}: cùng chữ {b['span'][:40]!r} mà khác tên ({name_of_text[key]} / {name})")
        if not set(b["flags"]) <= {"reuse_llm", "param_conflict"} or (name is None and b["flags"]):
            p.append(f"{b['unit']}: cờ sai {b['flags']}")
        if name is not None:
            if not NAME_RE.match(name) or name in ("not", "non") or name.startswith(("not_", "no_", "non_")):
                p.append(f"{b['unit']}: tên sai dạng hoặc phủ định: {name}")
            rows_of[name].append(b)
    seen = [e["predicate"] for e in ledger]
    if len(seen) != len(set(seen)) or set(seen) != set(rows_of):
        p.append(f"sổ vị từ không khớp tên trong bảng: sổ {len(seen)} ({len(set(seen))} khác nhau), bảng {len(rows_of)}")
    for e in ledger:
        rs = rows_of.get(e["predicate"], [])
        if not {text_norm(s) for s in e["surface"]} <= {text_norm(r["span"]) for r in rs}:
            p.append(f"sổ {e['predicate']}: surface không phải chữ của hàng mang tên")
        if e["anchors"] != sorted({r["unit"] for r in rs if r["role"] == "ket_luan"}) or e["kind"] != ("concept" if e["anchors"] else "input"):
            p.append(f"sổ {e['predicate']}: anchors/kind không khớp hàng ket_luan")
        if any(u not in units for u in e["used_in"]):
            p.append(f"sổ {e['predicate']}: used_in trỏ đơn vị không tồn tại")
    if not any(r["how"] == "llm" for r in spans) and (rows_of or ledger):
        p.append("bảng cụm không có cụm LLM (chế độ off) mà 1.6B có tên")
    return p


def checks(docs):
    """-> list[(nhãn, [vấn đề])]."""
    out = []
    all_units = refs.load_all_units(docs)
    # 1.1
    p = []
    for d in docs.values():
        units = all_units.get(d.doc_id)
        if units is None:
            p.append(f"{d.doc_id}: chưa có a1")
            continue
        ty = collections.Counter(u["type"] for u in units.values())
        raw_dieu = sum(1 for l in open(d.path, encoding="utf-8") if re.match(r"^Điều \d+[a-z]?\.", l))
        if not (ty["dieu"] == d.so_dieu):
            p.append(f"{d.doc_id}: số Điều 1.1 {ty['dieu']} khác manifest {d.so_dieu}")
        if raw_dieu < d.so_dieu:
            p.append(f"{d.doc_id}: đếm thô {raw_dieu} ít hơn manifest {d.so_dieu}")
        exp = EXPECTED.get(d.doc_id)
        if exp:
            ind = independent_counts(d.path)
            for k in ("dieu", "khoan", "diem"):
                if not (ty[k] == getattr(exp, k) == ind[k]):
                    p.append(f"{d.doc_id}: {k} 1.1 {ty[k]}, EXPECTED {getattr(exp, k)}, đếm độc lập {ind[k]}")
    out.append(("1.1 số đơn vị = manifest / EXPECTED / đếm độc lập", p))
    # 1.2
    p = []
    for d in docs.values():
        units = all_units[d.doc_id]
        edges = [(r["s"], r["p"], r["o"]) for r in parse.read_jsonl(refs.output_dir() / f"refs_edges_{d.doc_id}.jsonl")]
        p += [f"{d.doc_id}: {e}" for e in refs.check_structure(units, edges)]
        mentions = parse.read_jsonl(refs.output_dir() / f"refs_mentions_{d.doc_id}.jsonl")
        for r in mentions:
            tdoc = r["o"].split(".")[0]
            if r["o"] not in all_units.get(tdoc, {}):
                p.append(f"{d.doc_id}: refers_to trỏ mã không tồn tại {r['o']}")
            if r["evidence"] not in (units[r["s"]].get("text") or ""):
                p.append(f"{d.doc_id}: evidence không nằm trong text của {r['s']}")
    refs152 = parse.read_jsonl(refs.output_dir() / "refs_mentions_ND_152-2020.jsonl")
    if not any(r["s"].startswith("ND_152-2020.D7") and r["o"].startswith("BLLD_45-2019.D154") for r in refs152):
        p.append("mốc: ND_152.D7 không có refers_to tới BLLD.D154")
    out.append(("1.2 cấu trúc, refers_to (hai đầu tồn tại, evidence), mốc ND_152.D7→BLLD.D154", p))
    # 1.5 tường minh + 1.5 chung
    p = []
    ex = parse.read_jsonl(corpus.out_dir("exceptions_explicit") / "exceptions_explicit_edges_BLLD_45-2019.jsonl") + parse.read_jsonl(corpus.out_dir("exceptions_general") / "exceptions_general_edges_BLLD_45-2019.jsonl")
    pairs = {(e["s"], e["o"]) for e in ex}
    B = "BLLD_45-2019."
    for s, o in [(B + "D154", B + "D151.K1.d"), (B + "D36.K1.b", B + "D37.K1"), (B + "D29", B + "D35.K2.a"), (B + "D97.K4", B + "D35.K2.b")]:
        if (s, o) not in pairs:
            p.append(f"mốc exception_of thiếu: {s} → {o}")
    for d in docs.values():
        for e in parse.read_jsonl(corpus.out_dir("exceptions_general") / f"exceptions_general_edges_{d.doc_id}.jsonl"):
            if e["o"] not in all_units[d.doc_id]:
                p.append(f"{d.doc_id}: exception_of trỏ mã không tồn tại {e['o']}")
    # Ca "trừ" chưa xử lý của BLLĐ phải đúng danh sách đã biết (12/11). Không chặn mọi ca chưa xử lý (regex không bao giờ phủ hết, kiểm sẽ đỏ vĩnh viễn);
    # chỉ chặn khi danh sách đổi mà chưa ai ghi lại: thêm ca mới hay bớt ca cũ đều đỏ.
    got = {u["unit"] for u in parse.read_jsonl(corpus.out_dir("exceptions_general") / "exceptions_general_unhandled_BLLD_45-2019.jsonl")}
    p += residue_problems(got, {B + u for u in BLLD_UNHANDLED_KNOWN})
    out.append(("1.5 tường minh/1.5 chung exception_of (mốc D154→D151.K1.d, D36.K1.b→D37.K1, D29/D97→D35; ca chưa xử lý của BLLĐ = D24.K3, D188.K1)", p))
    # 1.6 giai đoạn A: bảng cụm. Kiểm độc lập bằng text_norm (concepts.py so theo từ), không import concepts.py.
    p = []
    base = "BLLD_45-2019"
    units = all_units[base]
    labels = {r["id"]: r["label"] for r in parse.read_jsonl(corpus.out_dir("article_type") / "article_type_labels.jsonl")}
    rows = parse.read_jsonl(corpus.out_dir("concepts") / f"concepts_spans_{base}.jsonl")
    for r in rows:
        u = units.get(r["unit"])
        if u is None:
            p.append(f"cụm trỏ đơn vị không tồn tại: {r['unit']}")
            continue
        dieu = ".".join(r["unit"].split(".")[:2])
        if labels.get(dieu) not in ("substantive", "definition"):
            p.append(f"{r['unit']}: cụm của Điều ngoài phạm vi (nhãn {labels.get(dieu)})")
        if r["role"] not in ("chu_the", "dieu_kien", "ngoai_le", "ket_luan") or r["how"] not in ("llm", "cond_node") or r["source"] not in ("own", "chapeau", "heading"):
            p.append(f"{r['unit']}: vai/how/source sai: {r['role']}/{r['how']}/{r['source']}")
            continue
        src = {"own": u.get("text"), "chapeau": lead_in_text(units, u), "heading": units.get(dieu, {}).get("heading")}[r["source"]] or ""
        if text_norm(r["span"]) not in text_norm(src):
            p.append(f"{r['unit']}: cụm không nằm trong {r['source']}: {r['span'][:50]!r}")
        if r["predicate"] is not None:
            p.append(f"{r['unit']}: giai đoạn A mà predicate khác null")
        if any(x not in "WECJGDA" for x in r["params"]) or (r["how"] == "cond_node" and r["params"]):
            p.append(f"{r['unit']}: tham số sai {r['params']}")
        if r["targets"] and r["source"] != "own":
            p.append(f"{r['unit']}: cụm {r['source']} mà có targets")
        for tg in r["targets"]:
            if tg not in all_units.get(tg.split(".")[0], {}):
                p.append(f"{r['unit']}: targets trỏ mã không tồn tại {tg}")
    nodes = parse.read_jsonl(corpus.out_dir("exceptions_general") / f"exceptions_general_conditions_{base}.jsonl")
    want = sum(1 for n in nodes for uid in n["units"] if labels.get(".".join(uid.split(".")[:2])) in ("substantive", "definition"))
    got = sum(1 for r in rows if r["how"] == "cond_node")
    if got != want:
        p.append(f"số cụm cond_node {got} khác số (nút 1.5, đơn vị trong phạm vi) {want}")
    cn = {r["unit"]: r for r in rows if r["how"] == "cond_node"}
    if sorted(cn.get(base + ".D14.K2", {}).get("targets", [])) != sorted(base + "." + x for x in ("D18.K2", "D145.K1.a", "D162.K1")):
        p.append("mốc: cụm ngoại lệ của D14.K2 phải có targets D18.K2, D145.K1.a, D162.K1")
    if cn.get(base + ".D151.K1.d", {}).get("targets") != [base + ".D154"]:
        p.append("mốc: cụm ngoại lệ của D151.K1.d phải có targets D154")
    out.append(("1.6 bảng cụm (cụm nguyên văn trong ngữ cảnh, vai, nguồn, targets tồn tại; số cụm cond_node = số nút 1.5 trong phạm vi; mốc D14.K2, D151.K1.d)", p))
    # 1.6 giai đoạn B: bảng cụm đã đặt tên và sổ vị từ. Cài lại độc lập, không import concepts_names.py.
    out.append(("1.6B tên vị từ (bảng đặt tên = bảng cụm ngoài predicate/flags; cùng chữ cùng tên; hàng có targets không tên; tên đúng dạng, khẳng định; sổ khớp bảng)",
                names_files_problems(rows, units, base)))
    # 2.2
    p = []
    links = parse.read_jsonl(corpus.out_dir("links") / "links_edges.jsonl")
    for l in links:
        tdoc = l["o"].split(".")[0]
        if l["o"] not in all_units.get(tdoc, {}) and l["o"] not in docs:
            p.append(f"2.2: {l['p']} trỏ mã không tồn tại {l['o']}")
    out.append(("2.2 based_on / details trỏ đến nút có thật", p))
    # 1.4
    p = []
    labels = {r["id"] for r in parse.read_jsonl(corpus.out_dir("article_type") / "article_type_labels.jsonl")}
    for d in docs.values():
        p += [f"1.4: {k} chưa có nhãn" for k, u in all_units[d.doc_id].items() if u["type"] == "dieu" and k not in labels]
    out.append(("1.4 mọi Điều có nhãn", p))
    # 2.3-2.4
    p = []
    rows = versions.load_versions()
    by = collections.defaultdict(list)
    for r in rows:
        by[r["id"]].append(r)
    p += version_problems(by)
    for d in docs.values():  # không mất nút: mọi mã của 1.1 còn trong versions; phiên bản 1 giữ chữ của 1.1 (trừ bản hợp nhất)
        if d.is_consolidation:
            continue
        for k, u in all_units[d.doc_id].items():
            if k not in by:
                p.append(f"{k}: mất khỏi versions")
            elif by[k][0]["text"] != (u.get("text") or ""):
                p.append(f"{k}: phiên bản 1 khác chữ của 1.1")
    ids = set(by) | set(docs)
    for e in parse.read_jsonl(versions.output_dir() / "version_edges.jsonl"):
        if e["o"] not in ids and not e["o"].startswith("external:"):
            p.append(f"cạnh {e['p']} trỏ mã không tồn tại {e['o']}")
        if e["s"] not in ids and not e["s"].startswith("external:"):
            p.append(f"cạnh {e['p']} xuất phát từ mã không tồn tại {e['s']}")
    out.append(("2.3-2.4 phiên bản liên tiếp, khoảng hiệu lực không chồng, không mất nút, phiên bản 1 = chữ 1.1, cạnh hai đầu tồn tại", p))
    return out


def main():
    docs = corpus.load_manifest()
    results = checks(docs)
    lines, bad = ["checks báo cáo"], 0
    for name, problems in results:
        lines.append(f"[{'OK' if not problems else 'LỖI'}] {name}")
        lines += [f"    {x}" for x in problems[:15]]
        if len(problems) > 15:
            lines.append(f"    ... còn {len(problems) - 15} vấn đề")
        bad += bool(problems)
    lines.append(f"tổng kiểm lỗi: {bad}")
    path = corpus.report_dir("checks") / "checks_report.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()
