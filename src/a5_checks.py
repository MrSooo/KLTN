"""A5: kiểm tra độc lập các bước A1-A4, A6, L3, L4 trên cả kho; đối chiếu số đếm với đĩa và các mốc cổng của plan.

Chạy: python -I src/a5_checks.py          (cần các bước trước đã chạy; thoát mã 1 nếu có vi phạm)
Báo cáo: docs/bao_cao_chay/a5/a5_report.txt.

Số đối chiếu cứng (EXPECTED) chỉ cho BLLĐ; nguồn độc lập với A1:
  Điều: grep -c -E '^Điều [0-9]+\\.' data/raw/labor/base/BLLD_45-2019.txt            = 220 (khớp cột so_dieu_dem_duoc của manifest)
  Khoản: grep -c -E '^[0-9]+[a-z]?\\. ' ...                                         = 645; trừ 7 dòng nằm trong 4 khối trích dẫn của Điều 219 = 638
  Điểm:  grep -c -E '^[a-zđ][0-9]?\\) ' ...                                         = 287; trừ 20 dòng trong các khối đó             = 267
Phép đếm thứ hai (independent_counts) quét file thô bằng bộ đếm nháy riêng, không dùng A1.
"""
import collections
import datetime
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import a1_parse as a1
import a2_edges as a2
import a4_versions as a4
import corpus


class Expect(NamedTuple):
    dieu: int
    khoan: int
    diem: int


EXPECTED = {"BLLD_45-2019": Expect(dieu=220, khoan=638, diem=267)}
D = datetime.date


def independent_counts(path):
    """Đếm Điều / Khoản / Điểm trên file thô: bỏ dòng trong khối “...” (bắt đầu ở dòng mở nháy, kết thúc khi nháy cân bằng) và dừng
    ở phụ lục đầu tiên. Cài đặt riêng, không dùng A1."""
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


def checks(docs):
    """-> list[(nhãn, [vấn đề])]."""
    out = []
    all_units = a2.load_all_units(docs)
    # A1
    p = []
    for d in docs.values():
        units = all_units.get(d.doc_id)
        if units is None:
            p.append(f"{d.doc_id}: chưa có a1")
            continue
        ty = collections.Counter(u["type"] for u in units.values())
        raw_dieu = sum(1 for l in open(d.path, encoding="utf-8") if re.match(r"^Điều \d+[a-z]?\.", l))
        if not (ty["dieu"] == d.so_dieu):
            p.append(f"{d.doc_id}: số Điều A1 {ty['dieu']} khác manifest {d.so_dieu}")
        if raw_dieu < d.so_dieu:
            p.append(f"{d.doc_id}: đếm thô {raw_dieu} ít hơn manifest {d.so_dieu}")
        exp = EXPECTED.get(d.doc_id)
        if exp:
            ind = independent_counts(d.path)
            for k in ("dieu", "khoan", "diem"):
                if not (ty[k] == getattr(exp, k) == ind[k]):
                    p.append(f"{d.doc_id}: {k} A1 {ty[k]}, EXPECTED {getattr(exp, k)}, đếm độc lập {ind[k]}")
    out.append(("A1 số đơn vị = manifest / EXPECTED / đếm độc lập", p))
    # A2
    p = []
    for d in docs.values():
        units = all_units[d.doc_id]
        edges = [(r["s"], r["p"], r["o"]) for r in a1.read_jsonl(a2.a2_dir() / f"a2_edges_{d.doc_id}.jsonl")]
        p += [f"{d.doc_id}: {e}" for e in a2.check_structure(units, edges)]
        refs = a1.read_jsonl(a2.a2_dir() / f"a2_refs_{d.doc_id}.jsonl")
        for r in refs:
            tdoc = r["o"].split(".")[0]
            if r["o"] not in all_units.get(tdoc, {}):
                p.append(f"{d.doc_id}: refers_to trỏ mã không tồn tại {r['o']}")
            if r["evidence"] not in (units[r["s"]].get("text") or ""):
                p.append(f"{d.doc_id}: evidence không nằm trong text của {r['s']}")
    refs152 = a1.read_jsonl(a2.a2_dir() / "a2_refs_ND_152-2020.jsonl")
    if not any(r["s"].startswith("ND_152-2020.D7") and r["o"].startswith("BLLD_45-2019.D154") for r in refs152):
        p.append("mốc: ND_152.D7 không có refers_to tới BLLD.D154")
    out.append(("A2 cấu trúc, refers_to (hai đầu tồn tại, evidence), mốc ND_152.D7→BLLD.D154", p))
    # A3 + A6
    p = []
    ex = a1.read_jsonl(corpus.out_dir("a3") / "a3_exceptions_BLLD_45-2019.jsonl") + a1.read_jsonl(corpus.out_dir("a6") / "a6_exceptions_BLLD_45-2019.jsonl")
    pairs = {(e["s"], e["o"]) for e in ex}
    B = "BLLD_45-2019."
    for s, o in [(B + "D154", B + "D151.K1.d"), (B + "D36.K1.b", B + "D37.K1"), (B + "D29", B + "D35.K2.a"), (B + "D97.K4", B + "D35.K2.b")]:
        if (s, o) not in pairs:
            p.append(f"mốc exception_of thiếu: {s} → {o}")
    for d in docs.values():
        for e in a1.read_jsonl(corpus.out_dir("a6") / f"a6_exceptions_{d.doc_id}.jsonl"):
            if e["o"] not in all_units[d.doc_id]:
                p.append(f"{d.doc_id}: exception_of trỏ mã không tồn tại {e['o']}")
    out.append(("A3/A6 exception_of (mốc D154→D151.K1.d, D36.K1.b→D37.K1, D29/D97→D35)", p))
    # L3
    p = []
    links = a1.read_jsonl(corpus.out_dir("l3") / "l3_links.jsonl")
    for l in links:
        tdoc = l["o"].split(".")[0]
        if l["o"] not in all_units.get(tdoc, {}) and l["o"] not in docs:
            p.append(f"L3: {l['p']} trỏ mã không tồn tại {l['o']}")
    out.append(("L3 based_on / details trỏ đến nút có thật", p))
    # L4
    p = []
    labels = {r["id"] for r in a1.read_jsonl(corpus.out_dir("l4") / "l4_labels.jsonl")}
    for d in docs.values():
        p += [f"L4: {k} chưa có nhãn" for k, u in all_units[d.doc_id].items() if u["type"] == "dieu" and k not in labels]
    out.append(("L4 mọi Điều có nhãn", p))
    # A4 / L6
    p = []
    rows = a4.load_versions()
    by = collections.defaultdict(list)
    for r in rows:
        by[r["id"]].append(r)
    p += version_problems(by)
    for d in docs.values():  # không mất nút: mọi mã của A1 còn trong versions; phiên bản 1 giữ chữ của A1 (trừ bản hợp nhất)
        if d.is_consolidation:
            continue
        for k, u in all_units[d.doc_id].items():
            if k not in by:
                p.append(f"{k}: mất khỏi versions")
            elif by[k][0]["text"] != (u.get("text") or ""):
                p.append(f"{k}: phiên bản 1 khác chữ của A1")
    ids = set(by) | set(docs)
    for e in a1.read_jsonl(a4.a4_dir() / "version_edges.jsonl"):
        if e["o"] not in ids and not e["o"].startswith("external:"):
            p.append(f"cạnh {e['p']} trỏ mã không tồn tại {e['o']}")
        if e["s"] not in ids and not e["s"].startswith("external:"):
            p.append(f"cạnh {e['p']} xuất phát từ mã không tồn tại {e['s']}")
    out.append(("L6 phiên bản liên tiếp, khoảng hiệu lực không chồng, không mất nút, phiên bản 1 = chữ A1, cạnh hai đầu tồn tại", p))
    return out


def main():
    docs = corpus.load_manifest()
    results = checks(docs)
    lines, bad = ["A5 báo cáo"], 0
    for name, problems in results:
        lines.append(f"[{'OK' if not problems else 'LỖI'}] {name}")
        lines += [f"    {x}" for x in problems[:15]]
        if len(problems) > 15:
            lines.append(f"    ... còn {len(problems) - 15} vấn đề")
        bad += bool(problems)
    lines.append(f"tổng kiểm lỗi: {bad}")
    path = corpus.report_dir("a5") / "a5_report.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()
