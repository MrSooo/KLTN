"""Đo precision / recall của cạnh refers_to và exception_of so với đáp án do người gán (review F-17, plan bước 3.2a).

Chạy: python -I src/eval_gold.py <file md nguồn> --template   (sinh bảng đơn vị và file đáp án trống; không ghi đè file đã có)
      python -I src/eval_gold.py <file md nguồn>              (chấm; cần đã chạy A7 và đã gán xong file đáp án)

Mẫu: các Điều có số chia 5 dư (609 mod 5), tức 609, 614, ..., 659 (SAMPLE_STEP). Chọn theo quy tắc cố định, không theo kết quả
của pipeline, để mẫu không thiên về chỗ pipeline làm tốt.
Đáp án: data/gold/gold_<stem>.tsv, cột p, s, o, ngam, ghi_chu (tab). Dòng bắt đầu bằng # là chú thích; phải có dòng
"# trang_thai: da_gan" thì mới chấm (file mới sinh ghi "chua_gan").
  p: refers_to | exception_of | refers_to_external (dẫn chiếu tới văn bản khác; o là tên văn bản, chỉ để đếm, không chấm).
  s, o: mã đơn vị, viết đủ (BLDS2015.D615.K1) hoặc bỏ tiền tố (D615.K1); với exception_of, s có thể là mệnh đề ngoại lệ trong
    nháy kép ("có thỏa thuận khác"), so với nút điều kiện của A7 bằng a6.norm_text.
  ngam: 1 nếu là ngoại lệ ngầm (không có từ "trừ", "không áp dụng": ví dụ "Trường hợp … thì …" ghi đè quy tắc chung), để
    tách recall phần tường minh. Trống = 0.
Phạm vi chấm: refers_to có s thuộc mẫu; exception_of có o thuộc mẫu. Dòng đáp án ngoài phạm vi bị bỏ và liệt kê.
Báo cáo: docs/gold_report_<stem>.txt. Thoát 1 nếu chưa gán xong hoặc đáp án lỗi định dạng.
"""
import argparse
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import a1_parse as a1
import a2_edges as a2
import a6_general_exceptions as a6
import a7_graph as a7

GOLD_DIR = a2.ROOT / "data" / "gold"
SAMPLE_FIRST, SAMPLE_STEP = 609, 5
SCORED = ("refers_to", "exception_of")
PREDICATES = SCORED + ("refers_to_external",)
COLUMNS = ["p", "s", "o", "ngam", "ghi_chu"]
DONE = "# trang_thai: da_gan"
TODO = "# trang_thai: chua_gan"


def gold_path(src):
    return GOLD_DIR / f"gold_{Path(src).stem}.tsv"


def units_path(src):
    return GOLD_DIR / f"units_{Path(src).stem}.md"


def report_path(src):
    return a7.DOCS_DIR / f"gold_report_{Path(src).stem}.txt"


def sample_dieu(nodes):
    """Mã các Điều thuộc mẫu, theo thứ tự nút."""
    return [n["id"] for n in nodes if n["type"] == "dieu" and (int(n["number"]) - SAMPLE_FIRST) % SAMPLE_STEP == 0]


def in_sample(code, dieu):
    return a2.dieu_of(code) in dieu


def full_code(code):
    """'D615.K1' -> 'BLDS2015.D615.K1'; mã đã có tiền tố giữ nguyên."""
    code = code.strip()
    return code if code.startswith(a1.DOC_PREFIX + ".") else f"{a1.DOC_PREFIX}.{code}"


class GoldError(ValueError):
    pass


def read_gold(path):
    """(đã gán xong?, [(số dòng, {p, s, o, ngam, ghi_chu})]). Lỗi định dạng thì GoldError (nêu số dòng)."""
    done, rows = False, []
    for no, line in enumerate(Path(path).read_text(encoding="utf-8").split("\n"), 1):
        if not line.strip():
            continue
        if line.startswith("#"):
            done = done or line.strip() == DONE
            continue
        cells = line.split("\t")
        if cells[:len(COLUMNS)] == COLUMNS:
            continue  # dòng tiêu đề
        cells += [""] * (len(COLUMNS) - len(cells))
        row = dict(zip(COLUMNS, (c.strip() for c in cells)))
        if row["p"] not in PREDICATES:
            raise GoldError(f"{path}:{no}: p {row['p']!r} không thuộc {PREDICATES}")
        if not row["s"] or not row["o"]:
            raise GoldError(f"{path}:{no}: thiếu s hoặc o")
        if row["ngam"] not in ("", "0", "1"):
            raise GoldError(f"{path}:{no}: ngam phải trống, 0 hoặc 1")
        rows.append((no, row))
    return done, rows


def gold_key(row, cond_by_text):
    """(s, p, o) dạng mã đầy đủ; s là mệnh đề trong nháy thì đổi sang mã nút điều kiện (hoặc giữ chữ nếu A7 không có nút đó)."""
    s = row["s"]
    if s.startswith('"') and s.endswith('"'):
        clause = s[1:-1]
        s = cond_by_text.get(a6.norm_text(clause), f"(mệnh đề) {clause}")
    else:
        s = full_code(s)
    return s, row["p"], full_code(row["o"])


def score(gold_rows, nodes, edges):
    """Theo từng p trong SCORED: dict(tp, fp, fn, tp_explicit, fn_explicit, precision, recall, recall_explicit)."""
    dieu = set(sample_dieu(nodes))
    cond_by_text = {a6.norm_text(n["text"]): n["id"] for n in nodes if n["type"] == a6.COND_TYPE}
    in_scope = {"refers_to": lambda s, o: in_sample(s, dieu), "exception_of": lambda s, o: in_sample(o, dieu)}
    out_of_scope, external = [], 0
    gold, implicit = collections.defaultdict(set), set()
    for no, row in gold_rows:
        if row["p"] == "refers_to_external":
            external += 1
            continue
        key = gold_key(row, cond_by_text)
        if not in_scope[row["p"]](key[0], key[2]):
            out_of_scope.append((no, key))
            continue
        gold[row["p"]].add(key)
        if row["ngam"] == "1":
            implicit.add(key)
    result = {}
    for p in SCORED:
        got = {(e["s"], e["p"], e["o"]) for e in edges if e["p"] == p and in_scope[p](e["s"], e["o"])}
        tp, fp, fn = got & gold[p], got - gold[p], gold[p] - got
        explicit = gold[p] - implicit
        result[p] = {"tp": sorted(tp), "fp": sorted(fp), "fn": sorted(fn), "gold": len(gold[p]), "got": len(got),
                     "precision": len(tp) / len(got) if got else None, "recall": len(tp) / len(gold[p]) if gold[p] else None,
                     "recall_explicit": len(tp & explicit) / len(explicit) if explicit else None,
                     "implicit": len(gold[p] & implicit)}
    return result, sorted(dieu), out_of_scope, external


def pct(x):
    return "không tính được (mẫu số 0)" if x is None else f"{x:.1%}"


def format_report(stem, result, dieu, out_of_scope, external):
    L = [f"Đối chiếu đáp án gán tay: {stem}", f"mẫu {len(dieu)} Điều: {', '.join(d.split('.')[-1] for d in dieu)}", ""]
    for p, r in result.items():
        L.append(f"== {p} == đáp án {r['gold']} (ngầm {r['implicit']}) | pipeline {r['got']} | đúng {len(r['tp'])}")
        L.append(f"precision {pct(r['precision'])} | recall {pct(r['recall'])} | recall phần tường minh {pct(r['recall_explicit'])}")
        L.append(f"thừa (pipeline có, đáp án không) ({len(r['fp'])}):")
        L += [f"  {s} {p} {o}" for s, _, o in r["fp"]] or ["  (không có)"]
        L.append(f"thiếu (đáp án có, pipeline không) ({len(r['fn'])}):")
        L += [f"  {s} {p} {o}" for s, _, o in r["fn"]] or ["  (không có)"]
        L.append("")
    L.append(f"dẫn chiếu tới văn bản khác trong đáp án (không chấm): {external}")
    L.append(f"dòng đáp án ngoài phạm vi mẫu, bị bỏ ({len(out_of_scope)}):")
    L += [f"  dòng {no}: {' '.join(k)}" for no, k in out_of_scope] or ["  (không có)"]
    return "\n".join(L) + "\n"


def read_graph(stem):
    load = lambda path: [json.loads(line) for line in Path(path).read_text(encoding="utf-8").split("\n") if line]
    paths = (a7.nodes_path(stem), a7.edges_path(stem))
    for p in paths:
        if not p.exists():
            raise SystemExit(f"LỖI: chưa có {p}; chạy python -I src/a7_graph.py <md> trước")
    return load(paths[0]), load(paths[1])


def write_template(src):
    """Bảng đơn vị của mẫu (để đọc khi gán) và file đáp án trống. Không ghi đè file đã có."""
    nodes, _ = read_graph(Path(src).stem)
    dieu = sample_dieu(nodes)
    written = []
    if not units_path(src).exists():
        L = [f"# Đơn vị của mẫu gán tay ({Path(src).stem})", "",
             "Đọc từng đơn vị và ghi vào file gold_*.tsv cùng thư mục MỌI dẫn chiếu và MỌI ngoại lệ mà bạn thấy, kể cả ngoại lệ",
             "ngầm. Đừng mở file kết quả của pipeline (data/processed/a2_refs_*, a6_*, a7_*) trước khi gán xong.", ""]
        for n in nodes:
            if n["type"] in ("dieu", "khoan", "diem") and a2.dieu_of(n["id"]) in dieu:
                head = f"Điều {n['number']}. {n['heading']}" if n["type"] == "dieu" else ""
                L.append(f"- `{n['id'].split('.', 1)[1]}` {head}".rstrip())
                for para in (n["text"] or "").split("\n"):
                    if para:
                        L.append(f"  > {para}")
        units_path(src).parent.mkdir(parents=True, exist_ok=True)
        units_path(src).write_text("\n".join(L) + "\n", encoding="utf-8")
        written.append(units_path(src))
    if not gold_path(src).exists():
        L = [TODO, "# Đổi dòng trên thành '# trang_thai: da_gan' khi gán xong. Cách ghi: xem docstring src/eval_gold.py.",
             "# Ví dụ (xoá đi):  refers_to<TAB>D617.K1<TAB>D616.K1<TAB><TAB>",
             '#                  exception_of<TAB>"có thỏa thuận khác"<TAB>D615.K1<TAB><TAB>',
             "\t".join(COLUMNS)]
        gold_path(src).write_text("\n".join(L) + "\n", encoding="utf-8")
        written.append(gold_path(src))
    return written


def run(src):
    stem = Path(src).stem
    if not gold_path(src).exists():
        raise SystemExit(f"LỖI: chưa có {gold_path(src)}; chạy với --template rồi gán tay")
    try:
        done, rows = read_gold(gold_path(src))
    except GoldError as e:
        raise SystemExit(f"LỖI: {e}")
    if not done:
        raise SystemExit(f"LỖI: {gold_path(src)} chưa đánh dấu '{DONE}'; chưa chấm")
    nodes, edges = read_graph(stem)
    result, dieu, out_of_scope, external = score(rows, nodes, edges)
    text = format_report(stem, result, dieu, out_of_scope, external)
    print(text, end="")
    report_path(src).write_text(text, encoding="utf-8")
    print("đã ghi", report_path(src))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="file md nguồn, dùng để suy stem")
    ap.add_argument("--template", action="store_true", help="sinh bảng đơn vị và file đáp án trống (không ghi đè)")
    args = ap.parse_args(argv)
    if args.template:
        for p in write_template(args.path):
            print("đã ghi", p)
        return 0
    return run(args.path)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
