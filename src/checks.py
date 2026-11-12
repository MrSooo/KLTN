"""checks: kiểm tra độc lập các bước L1-L6 trên cả kho; đối chiếu số đếm với đĩa và các mốc cổng của plan.

Chạy: python -I src/checks.py          (cần các bước trước đã chạy; thoát mã 1 nếu có vi phạm)
Báo cáo: docs/bao_cao_chay/checks/checks_report.txt.

Số đối chiếu cứng (EXPECTED) chỉ cho BLLĐ; nguồn độc lập với L1:
  Điều: grep -c -E '^Điều [0-9]+\\.' data/raw/labor/base/BLLD_45-2019.txt            = 220 (khớp cột so_dieu_dem_duoc của manifest)
  Khoản: grep -c -E '^[0-9]+[a-z]?\\. ' ...                                         = 645; trừ 7 dòng nằm trong 4 khối trích dẫn của Điều 219 = 638
  Điểm:  grep -c -E '^[a-zđ][0-9]?\\) ' ...                                         = 287; trừ 20 dòng trong các khối đó             = 267
Phép đếm thứ hai (independent_counts) quét file thô bằng bộ đếm nháy riêng, không dùng L1.
"""
import collections
import datetime
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import parse as l1
import refs as l2
import l6_versions as l6v
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
    ở phụ lục đầu tiên. Cài đặt riêng, không dùng L1."""
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


def checks(docs):
    """-> list[(nhãn, [vấn đề])]."""
    out = []
    all_units = l2.load_all_units(docs)
    # L1
    p = []
    for d in docs.values():
        units = all_units.get(d.doc_id)
        if units is None:
            p.append(f"{d.doc_id}: chưa có a1")
            continue
        ty = collections.Counter(u["type"] for u in units.values())
        raw_dieu = sum(1 for l in open(d.path, encoding="utf-8") if re.match(r"^Điều \d+[a-z]?\.", l))
        if not (ty["dieu"] == d.so_dieu):
            p.append(f"{d.doc_id}: số Điều L1 {ty['dieu']} khác manifest {d.so_dieu}")
        if raw_dieu < d.so_dieu:
            p.append(f"{d.doc_id}: đếm thô {raw_dieu} ít hơn manifest {d.so_dieu}")
        exp = EXPECTED.get(d.doc_id)
        if exp:
            ind = independent_counts(d.path)
            for k in ("dieu", "khoan", "diem"):
                if not (ty[k] == getattr(exp, k) == ind[k]):
                    p.append(f"{d.doc_id}: {k} L1 {ty[k]}, EXPECTED {getattr(exp, k)}, đếm độc lập {ind[k]}")
    out.append(("L1 số đơn vị = manifest / EXPECTED / đếm độc lập", p))
    # L2
    p = []
    for d in docs.values():
        units = all_units[d.doc_id]
        edges = [(r["s"], r["p"], r["o"]) for r in l1.read_jsonl(l2.l2_dir() / f"l2_edges_{d.doc_id}.jsonl")]
        p += [f"{d.doc_id}: {e}" for e in l2.check_structure(units, edges)]
        refs = l1.read_jsonl(l2.l2_dir() / f"l2_refs_{d.doc_id}.jsonl")
        for r in refs:
            tdoc = r["o"].split(".")[0]
            if r["o"] not in all_units.get(tdoc, {}):
                p.append(f"{d.doc_id}: refers_to trỏ mã không tồn tại {r['o']}")
            if r["evidence"] not in (units[r["s"]].get("text") or ""):
                p.append(f"{d.doc_id}: evidence không nằm trong text của {r['s']}")
    refs152 = l1.read_jsonl(l2.l2_dir() / "l2_refs_ND_152-2020.jsonl")
    if not any(r["s"].startswith("ND_152-2020.D7") and r["o"].startswith("BLLD_45-2019.D154") for r in refs152):
        p.append("mốc: ND_152.D7 không có refers_to tới BLLD.D154")
    out.append(("L2 cấu trúc, refers_to (hai đầu tồn tại, evidence), mốc ND_152.D7→BLLD.D154", p))
    # L5 tường minh + L5 chung
    p = []
    ex = l1.read_jsonl(corpus.out_dir("l5_explicit") / "l5_explicit_exceptions_BLLD_45-2019.jsonl") + l1.read_jsonl(corpus.out_dir("l5_general") / "l5_general_exceptions_BLLD_45-2019.jsonl")
    pairs = {(e["s"], e["o"]) for e in ex}
    B = "BLLD_45-2019."
    for s, o in [(B + "D154", B + "D151.K1.d"), (B + "D36.K1.b", B + "D37.K1"), (B + "D29", B + "D35.K2.a"), (B + "D97.K4", B + "D35.K2.b")]:
        if (s, o) not in pairs:
            p.append(f"mốc exception_of thiếu: {s} → {o}")
    for d in docs.values():
        for e in l1.read_jsonl(corpus.out_dir("l5_general") / f"l5_general_exceptions_{d.doc_id}.jsonl"):
            if e["o"] not in all_units[d.doc_id]:
                p.append(f"{d.doc_id}: exception_of trỏ mã không tồn tại {e['o']}")
    # Ca "trừ" chưa xử lý của BLLĐ phải đúng danh sách đã biết (12/11). Không chặn mọi ca chưa xử lý (regex không bao giờ phủ hết, kiểm sẽ đỏ vĩnh viễn);
    # chỉ chặn khi danh sách đổi mà chưa ai ghi lại: thêm ca mới hay bớt ca cũ đều đỏ.
    got = {u["unit"] for u in l1.read_jsonl(corpus.out_dir("l5_general") / "l5_general_unhandled_BLLD_45-2019.jsonl")}
    p += residue_problems(got, {B + u for u in BLLD_UNHANDLED_KNOWN})
    out.append(("L5 tường minh/L5 chung exception_of (mốc D154→D151.K1.d, D36.K1.b→D37.K1, D29/D97→D35; ca chưa xử lý của BLLĐ = D24.K3, D188.K1)", p))
    # 1.6 giai đoạn A: bảng cụm. Kiểm độc lập bằng text_norm (concepts.py so theo từ), không import concepts.py.
    p = []
    base = "BLLD_45-2019"
    units = all_units[base]
    labels = {r["id"]: r["label"] for r in l1.read_jsonl(corpus.out_dir("l4") / "l4_labels.jsonl")}
    rows = l1.read_jsonl(corpus.out_dir("concepts") / f"concepts_spans_{base}.jsonl")
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
        parent = units.get(u.get("parent")) if u["type"] == "diem" else None
        src = {"own": u.get("text"), "chapeau": (parent or {}).get("text"), "heading": units.get(dieu, {}).get("heading")}[r["source"]] or ""
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
    nodes = l1.read_jsonl(corpus.out_dir("l5_general") / f"l5_general_conditions_{base}.jsonl")
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
    # L3
    p = []
    links = l1.read_jsonl(corpus.out_dir("l3") / "l3_links.jsonl")
    for l in links:
        tdoc = l["o"].split(".")[0]
        if l["o"] not in all_units.get(tdoc, {}) and l["o"] not in docs:
            p.append(f"L3: {l['p']} trỏ mã không tồn tại {l['o']}")
    out.append(("L3 based_on / details trỏ đến nút có thật", p))
    # L4
    p = []
    labels = {r["id"] for r in l1.read_jsonl(corpus.out_dir("l4") / "l4_labels.jsonl")}
    for d in docs.values():
        p += [f"L4: {k} chưa có nhãn" for k, u in all_units[d.doc_id].items() if u["type"] == "dieu" and k not in labels]
    out.append(("L4 mọi Điều có nhãn", p))
    # L6
    p = []
    rows = l6v.load_versions()
    by = collections.defaultdict(list)
    for r in rows:
        by[r["id"]].append(r)
    p += version_problems(by)
    for d in docs.values():  # không mất nút: mọi mã của L1 còn trong versions; phiên bản 1 giữ chữ của L1 (trừ bản hợp nhất)
        if d.is_consolidation:
            continue
        for k, u in all_units[d.doc_id].items():
            if k not in by:
                p.append(f"{k}: mất khỏi versions")
            elif by[k][0]["text"] != (u.get("text") or ""):
                p.append(f"{k}: phiên bản 1 khác chữ của L1")
    ids = set(by) | set(docs)
    for e in l1.read_jsonl(l6v.l6_dir() / "version_edges.jsonl"):
        if e["o"] not in ids and not e["o"].startswith("external:"):
            p.append(f"cạnh {e['p']} trỏ mã không tồn tại {e['o']}")
        if e["s"] not in ids and not e["s"].startswith("external:"):
            p.append(f"cạnh {e['p']} xuất phát từ mã không tồn tại {e['s']}")
    out.append(("L6 phiên bản liên tiếp, khoảng hiệu lực không chồng, không mất nút, phiên bản 1 = chữ L1, cạnh hai đầu tồn tại", p))
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
