"""A5: bốn phép kiểm (1-3 trên A1-A3, 4 trên A4 khi có --versions) trên file đã sinh, để chắc lớp văn bản không có chỗ trùng hay hở trước khi xây bước B. Không sinh dữ liệu mới.

Đầu vào: a1_triples_<stem>.jsonl, a2_edges_<stem>.jsonl, a2_refs_<stem>.jsonl, a3_exceptions_<stem>.jsonl.
Đọc thẳng từng dòng JSON, không qua a2.load_units / a2.parent_of, để phép kiểm độc lập với code đã sinh các file đó.
Đầu ra: docs/a5_report_<stem>.txt (ghi cả khi mọi thứ đạt), cùng nội dung in ra màn hình.

  Bước 1, mã trùng (a1_triples). 1a: số s có dòng type bằng số đơn vị kỳ vọng. 1b: số Điều bằng số kỳ vọng.
    1c: mỗi s có đúng một dòng type. 1d: mỗi cặp (s, p) xuất hiện đúng một lần.
  Bước 2, mỗi đơn vị đúng một cha (a2_edges). 2a: Điều không có part_of. 2b: Khoản và Điểm có đúng một part_of.
    2c: cha = mã con bỏ đoạn cuối. 2d: contains đối xứng với part_of. 2e: số part_of = số đơn vị - số Điều.
    2f: cha là đơn vị có trong triples và đúng bậc ngay trên của con (Khoản → dieu, Điểm → khoan).
  Bước 3, cạnh trùng: gom (s, p, o) của a2_edges, a2_refs, a3_exceptions; bộ ba nào xuất hiện nhiều hơn một lần là vi phạm,
    ghi nơi xuất hiện và evidence. Evidence khác nhau vẫn là trùng, khoá chỉ là (s, p, o). Không sửa A2.

  Bước 4, lớp phiên bản của A4 (chỉ khi truyền --versions; mỗi dòng a4_<name>_versions.jsonl là một phiên bản của một đơn vị).
    4a: cặp (id, version) duy nhất, các version của một id là 1, 2, 3 liên tiếp. 4b: previous_version của version k là k-1,
    version 1 thì null. 4c: khoảng hiệu lực [from, to) không chồng: có version k+1 thì version k phải có to và to <= from của
    k+1 (version k+1 không có from cũng là sai); from < to khi cả hai có giá trị. 4d: mọi mã của A1 còn trong versions
    (cam kết "không xoá nút", Q19). Đơn vị chỉ có trong versions (thêm bởi văn bản sửa đổi) không bị báo.
    4e: dòng version 1 của mỗi mã A1 giữ nguyên type, number, heading, text của A1: so bằng ==, không chuẩn hoá khoảng trắng,
    chỉ so trường mà A1 có dòng tương ứng; mã chỉ có ở một bên thì bỏ qua (4d lo phần thiếu).
    4f: mọi dòng version 1 của mã A1 có cùng một effective_from và source_doc khác null (ngày hiệu lực và mã văn bản gốc), mọi
    dòng khác có effective_from sau ngày đó (review F-08).

Số kỳ vọng nằm ở bảng EXPECTED theo stem (đã đối chiếu độc lập bằng grep trên md); stem không có trong bảng thì báo lỗi.
Thoát 1 nếu bước nào có vi phạm, hoặc đầu vào lỗi (thiếu file, JSON hỏng, thiếu khoá, stem lạ); các bước luôn chạy hết
trước khi thoát. Cạnh trùng làm thoát 1 vì bàn giao ghi "không có cạnh trùng" là yêu cầu.

Chạy: python -I src/a5_checks.py <file md nguồn> [--versions PATH]   (bắt buộc truyền path md, chỉ dùng để suy stem)
Báo cáo: docs/a5_report_<stem>.txt; có --versions thì docs/a5_report_<stem>_<name>.txt, <name> lấy từ a4_<name>_versions.jsonl
(tên file không đúng dạng đó thì dùng tên file bỏ đuôi), để các lần chạy khác nhau không đè nhau và không đè báo cáo bước 1-3.
"""
import argparse
import collections
import datetime
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import a2_edges as a2
import a3_exceptions as a3

TYPES = ("dieu", "khoan", "diem")
PARENT_TYPE = {"khoan": "dieu", "diem": "khoan"}  # bậc ngay trên của mỗi bậc con
EDGE_SOURCES = ("a2_edges", "a2_refs", "a3_exceptions")  # thứ tự gom ở bước 3
TRIPLE_KEYS = ("s", "p", "o")
VERSION_KEYS = ("id", "version", "previous_version", "effective_from", "effective_to")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
CONTENT_FIELDS = ("type", "number", "heading", "text")  # trường nội dung A1 có thể có; không nằm trong VERSION_KEYS (không bắt buộc)
SHOW_CHARS = 60  # số ký tự đầu của giá trị in trong dòng vi phạm 4e


class Expect(NamedTuple):
    units: int
    dieu: int


EXPECTED = {
    "blds2015_5dieu": Expect(units=35, dieu=5),
    "blds2015_p4": Expect(units=215, dieu=54),
}


class Check(NamedTuple):
    id: str
    title: str
    summary: str
    problems: list


def versions_name(versions):
    """<name> của a4_<name>_versions.jsonl; tên file không đúng dạng đó thì tên file bỏ đuôi."""
    stem = Path(versions).stem
    m = re.fullmatch(r"a4_(.+)_versions", stem)
    return m.group(1) if m else stem


def report_path(src, versions=None):
    suffix = f"_{versions_name(versions)}" if versions is not None else ""
    return a2.ROOT / "docs" / f"a5_report_{Path(src).stem}{suffix}.txt"


def load_rows(path, keys=TRIPLE_KEYS):
    """[(số dòng, dòng JSON)] của một file jsonl. Thiếu file, JSON hỏng hoặc thiếu một trong keys thì ValueError."""
    path = Path(path)
    if not path.exists():
        raise ValueError(f"chưa có {path}; chạy bước sinh file này trước")
    rows = []
    with open(path, encoding="utf-8", newline="") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"{path}:{line_no}: JSON hỏng ({e})")
            if not isinstance(row, dict) or not set(keys) <= row.keys():
                raise ValueError(f"{path}:{line_no}: thiếu khoá {'/'.join(keys)}")
            rows.append((line_no, row))
    return rows


def check_codes(triples, expect):
    """Bước 1. Trả về (các Check 1a-1d, {đơn vị: type của dòng type đầu tiên}) để bước 2 dùng."""
    subjects = {}                                   # s theo thứ tự xuất hiện
    type_rows = collections.defaultdict(list)       # s -> [o của các dòng type]
    pair_lines = collections.defaultdict(list)      # (s, p) -> [số dòng]
    for line_no, r in triples:
        subjects[r["s"]] = True
        pair_lines[(r["s"], r["p"])].append(line_no)
        if r["p"] == "type":
            type_rows[r["s"]].append(r["o"])
    unit_types = {s: v[0] for s, v in type_rows.items()}
    n_units = len(unit_types)
    n_dieu = sum(1 for t in unit_types.values() if t == "dieu")

    one_type = []
    for s in subjects:
        n = len(type_rows.get(s, []))
        if n != 1:
            one_type.append(f"{s}: {n} dòng type" + (f" ({', '.join(type_rows[s])})" if n else ""))
    repeated = [f"({s}, {p}) lặp ở dòng {', '.join(map(str, lines))}" for (s, p), lines in pair_lines.items() if len(lines) > 1]
    checks = [
        Check("1a", "số đơn vị (s có dòng type)", f"{n_units}, kỳ vọng {expect.units}",
              [] if n_units == expect.units else [f"có {n_units} đơn vị, cần {expect.units}"]),
        Check("1b", "số Điều", f"{n_dieu}, kỳ vọng {expect.dieu}",
              [] if n_dieu == expect.dieu else [f"có {n_dieu} Điều, cần {expect.dieu}"]),
        Check("1c", "mỗi s có đúng một dòng type", f"{len(subjects)} s", one_type),
        Check("1d", "mỗi cặp (s, p) một lần", f"{len(pair_lines)} cặp", repeated),
    ]
    return checks, unit_types


def check_parents(unit_types, edges, expect):
    """Bước 2, theo cạnh contains / part_of của a2_edges. unit_types từ check_codes."""
    part_of = [(ln, r["s"], r["o"]) for ln, r in edges if r["p"] == "part_of"]
    contains = [(ln, r["s"], r["o"]) for ln, r in edges if r["p"] == "contains"]
    parents = collections.defaultdict(list)         # con -> [cha] theo part_of
    for _, child, parent in part_of:
        parents[child].append(parent)

    dieu_parent = [f"{c}: là Điều nhưng có part_of tới {', '.join(ps)}" for c, ps in parents.items() if unit_types.get(c) == "dieu"]
    one_parent = []
    for c, t in unit_types.items():
        if t not in TYPES:
            one_parent.append(f"{c}: type {t!r} không phải dieu/khoan/diem")
        elif t != "dieu" and len(parents.get(c, [])) != 1:
            ps = parents.get(c, [])
            one_parent.append(f"{c}: {len(ps)} part_of" + (f" ({', '.join(ps)})" if ps else ""))
    one_parent += [f"{c}: có part_of nhưng không có dòng type (không là đơn vị)" for c in parents if c not in unit_types]

    wrong_code = []
    for line_no, child, parent in part_of:
        want = child.rsplit(".", 1)[0] if "." in child else None  # mã bỏ đoạn cuối
        if parent != want:
            wrong_code.append(f"dòng {line_no}: {child} part_of {parent}, cha theo mã là {want}")

    contains_set = {(a, b) for _, a, b in contains}
    part_set = {(p, c) for _, c, p in part_of}      # đảo về dạng (cha, con) để so với contains
    asym = [f"contains {a} → {b} không có part_of {b} → {a}" for a, b in sorted(contains_set - part_set)]
    asym += [f"part_of {b} → {a} không có contains {a} → {b}" for a, b in sorted(part_set - contains_set)]

    bad_parent = []
    for _, child, parent in part_of:
        if parent not in unit_types:
            bad_parent.append(f"{child}: cha {parent} không phải đơn vị")
        elif child in unit_types and unit_types[child] in PARENT_TYPE and unit_types[parent] != PARENT_TYPE[unit_types[child]]:
            bad_parent.append(f"{child}: cha {parent} là {unit_types[parent]}, cần {PARENT_TYPE[unit_types[child]]}")

    want_count = expect.units - expect.dieu
    return [
        Check("2a", "Điều không có cha", f"{sum(1 for t in unit_types.values() if t == 'dieu')} Điều", dieu_parent),
        Check("2b", "Khoản và Điểm có đúng một cha", f"{sum(1 for t in unit_types.values() if t in ('khoan', 'diem'))} đơn vị", one_parent),
        Check("2c", "cha = mã con bỏ đoạn cuối", f"{len(part_of)} cạnh part_of", wrong_code),
        Check("2d", "contains đối xứng với part_of", f"contains {len(contains)}, part_of {len(part_of)}", asym),
        Check("2e", "số part_of = số đơn vị - số Điều", f"{len(part_of)}, kỳ vọng {expect.units} - {expect.dieu} = {want_count}",
              [] if len(part_of) == want_count else [f"có {len(part_of)} part_of, cần {want_count}"]),
        Check("2f", "cha tồn tại và đúng bậc", f"{len(part_of)} cạnh part_of", bad_parent),
    ]


def check_duplicate_edges(sources):
    """Bước 3. sources: [(nhãn, rows)]. Gom (s, p, o) của tất cả file, báo bộ ba xuất hiện hơn một lần (kể cả giữa các file)."""
    where = collections.defaultdict(list)           # (s, p, o) -> [(nhãn, số dòng, evidence)]
    total = 0
    for label, rows in sources:
        for line_no, r in rows:
            where[(r["s"], r["p"], r["o"])].append((label, line_no, r.get("evidence", "")))
            total += 1
    problems = []
    for (s, p, o), found in where.items():
        if len(found) > 1:
            problems.append(f"{s}\t{p}\t{o}\t{len(found)} lần\t" + "; ".join(f'{lb}:{ln} "{ev}"' for lb, ln, ev in found))
    return Check("3", "bộ ba (s, p, o) lặp trong " + " + ".join(label for label, _ in sources),
                 f"{total} bộ ba, {len(where)} khác nhau, {len(problems)} bị lặp", problems)


def parse_date(value, where, problems):
    """Ngày YYYY-MM-DD hoặc None. Giá trị khác (không phải chuỗi đúng dạng, hoặc ngày không có thật) thì ghi vào problems."""
    if value is None:
        return None
    try:
        if isinstance(value, str) and DATE_RE.fullmatch(value):
            return datetime.date.fromisoformat(value)
    except ValueError:
        pass
    problems.append(f"{where}: ngày {value!r} không hợp lệ")
    return None


def check_versions(a1_ids, rows):
    """Bước 4 trên các dòng của a4_<name>_versions.jsonl; a1_ids là mã đơn vị của A1."""
    by_id = collections.defaultdict(dict)           # id -> {version: (số dòng, dòng đầu tiên)}
    pair_lines = collections.defaultdict(list)      # (id, version) -> [số dòng]
    not_int = []
    for line_no, r in rows:
        if isinstance(r["version"], int) and not isinstance(r["version"], bool):
            pair_lines[(r["id"], r["version"])].append(line_no)
            by_id[r["id"]].setdefault(r["version"], (line_no, r))
        else:
            not_int.append(f"dòng {line_no}: {r['id']} có version {r['version']!r} không phải số nguyên")

    repeated = [f"({i}, version {v}) lặp ở dòng {', '.join(map(str, lines))}" for (i, v), lines in pair_lines.items() if len(lines) > 1]
    gaps = []
    for i, versions in by_id.items():
        have = sorted(versions)
        if have != list(range(1, len(have) + 1)):
            gaps.append(f"{i}: các version {have}, cần {list(range(1, len(have) + 1))}")

    broken_chain = []
    for i, versions in by_id.items():
        for v, (line_no, r) in sorted(versions.items()):
            want = None if v == 1 else v - 1
            if r["previous_version"] != want:
                broken_chain.append(f"dòng {line_no}: {i} version {v}: previous_version {r['previous_version']!r}, cần {want!r}")

    overlap, pairs = [], 0
    for i, versions in by_id.items():
        dates = {}                                  # version -> (from, to)
        for v, (_, r) in sorted(versions.items()):
            frm = parse_date(r["effective_from"], f"{i} version {v} effective_from", overlap)
            to = parse_date(r["effective_to"], f"{i} version {v} effective_to", overlap)
            if frm and to and not frm < to:
                overlap.append(f"{i} version {v}: khoảng hiệu lực rỗng [{frm}, {to})")
            dates[v] = (frm, to, r)
        order = sorted(dates)
        for k, nxt in zip(order, order[1:]):
            pairs += 1
            (_, to_k, r_k), (from_next, _, r_next) = dates[k], dates[nxt]
            if r_next["effective_from"] is None:
                overlap.append(f"{i}: version {nxt} không có effective_from")
            if r_k["effective_to"] is None:
                overlap.append(f"{i}: version {k} không có effective_to nhưng đã có version {nxt}")
            if to_k and from_next and to_k > from_next:
                overlap.append(f"{i}: version {k} hết hiệu lực {to_k} sau khi version {nxt} bắt đầu {from_next}")

    in_versions = set(by_id) | {r["id"] for _, r in rows}
    missing = [f"{i}: có trong A1 nhưng không còn trong versions" for i in sorted(a1_ids - in_versions)]
    return [
        Check("4a", "(id, version) duy nhất và version liên tiếp 1, 2, 3", f"{len(rows)} dòng, {len(by_id)} id", not_int + repeated + gaps),
        Check("4b", "previous_version = version - 1, version 1 thì null", f"{len(rows)} dòng", broken_chain),
        Check("4c", "khoảng hiệu lực [from, to) không chồng", f"{pairs} cặp version liên tiếp", overlap),
        Check("4d", "mọi mã của A1 còn trong versions", f"{len(a1_ids)} mã A1, {len(in_versions)} id trong versions", missing),
    ]


def check_version1_content(a1_rows, version_rows):
    """Bước 4e. Dòng version 1 của mỗi mã A1 phải có type, number, heading, text bằng (==) giá trị trong a1_triples.

    Chỉ so trường mà A1 có dòng tương ứng. Mã không có trong versions (4d đã báo) hoặc chỉ có trong versions thì bỏ qua.
    Trường versions thiếu khoá tính là None, nên khác giá trị A1. a1_rows: dòng a1_triples; version_rows: dòng versions.
    """
    a1 = {}                                         # s -> {trường: o}, giữ dòng đầu tiên của mỗi (s, p)
    for _, r in a1_rows:
        if r["p"] in CONTENT_FIELDS:
            a1.setdefault(r["s"], {}).setdefault(r["p"], r["o"])
    problems, rows_compared, fields_compared = [], 0, 0
    for _, r in version_rows:
        if r["version"] != 1 or r["id"] not in a1:
            continue
        rows_compared += 1
        for field in CONTENT_FIELDS:
            if field not in a1[r["id"]]:
                continue
            fields_compared += 1
            want, got = a1[r["id"]][field], r.get(field)
            if got != want:
                problems.append(f"{r['id']}: {field} A1 '{str(want)[:SHOW_CHARS]}' khác version 1 '{str(got)[:SHOW_CHARS]}'")
    return Check("4e", "version 1 giữ nguyên nội dung A1", f"{fields_compared} trường ở {rows_compared} dòng version 1", problems)


def check_base_dates(a1_ids, version_rows):
    """Bước 4f. Mọi dòng version 1 của mã A1 có cùng một effective_from khác null và cùng một source_doc khác null (văn bản gốc);
    mọi dòng khác bắt đầu sau ngày đó (so chuỗi YYYY-MM-DD). Không đối chiếu với giá trị cụ thể của A1/A4, chỉ nhất quán trong file."""
    base = [r for _, r in version_rows if r["version"] == 1 and r["id"] in a1_ids]
    starts = collections.Counter(r["effective_from"] for r in base)
    docs = collections.Counter(r.get("source_doc") for r in base)
    problems = []
    if None in starts:
        problems.append(f"{starts[None]} dòng version 1 của mã A1 có effective_from null")
    if None in docs:
        problems.append(f"{docs[None]} dòng version 1 của mã A1 có source_doc null")
    if len(starts) > 1 or len(docs) > 1:
        problems.append(f"version 1 của mã A1 không cùng một ngày / văn bản: {dict(starts)} {dict(docs)}")
    start = next(iter(starts)) if len(starts) == 1 else None
    if start:
        problems += [f"{r['id']} version {r['version']}: effective_from {r['effective_from']!r} không sau ngày hiệu lực gốc {start}"
                     for _, r in version_rows if not (r["version"] == 1 and r["id"] in a1_ids)
                     and not (isinstance(r["effective_from"], str) and r["effective_from"] > start)]
    return Check("4f", "version 1 có ngày hiệu lực và văn bản gốc, sửa đổi bắt đầu sau ngày đó",
                 f"{len(base)} dòng gốc, ngày gốc {start}, văn bản gốc {next(iter(docs)) if len(docs) == 1 else None}", problems)


STEP_TITLES = {"1": "Bước 1: mã trùng", "2": "Bước 2: mỗi đơn vị đúng một cha", "3": "Bước 3: cạnh trùng",
               "4": "Bước 4: lớp phiên bản của A4"}


def verdict(c):
    return f"KHÔNG ĐẠT ({len(c.problems)})" if c.problems else "ĐẠT"


def failures(checks):
    return sum(len(c.problems) for c in checks)


def display_path(path):
    """Đường dẫn trong báo cáo: tương đối so với gốc dự án nếu nằm trong đó, để báo cáo không dính đường dẫn của máy."""
    try:
        return Path(path).resolve().relative_to(a2.ROOT).as_posix()
    except ValueError:
        return str(path)


def format_report(stem, paths, checks):
    L = [f"A5 báo cáo kiểm tra: {stem}", "file đã kiểm:"] + [f"  {display_path(p)}" for p in paths.values()]
    step = None
    for c in checks:
        if c.id[0] != step:
            step = c.id[0]
            L += ["", f"== {STEP_TITLES[step]} =="]
        L.append(f"[{c.id}] {c.title}: {c.summary} -> {verdict(c)}")
        L += [f"    {p}" for p in c.problems]
    bad = failures(checks)
    L += ["", "KẾT LUẬN: " + (f"KHÔNG ĐẠT ({bad} chỗ sai)" if bad else "ĐẠT")]
    return "\n".join(L) + "\n"


def write_text(text, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def run(src, versions=None):
    """Chạy các bước (bước 4 chỉ khi có versions), in và ghi báo cáo, trả về mã thoát (0 đạt, 1 có vi phạm ở bất kỳ bước nào)."""
    stem = Path(src).stem
    expect = EXPECTED.get(stem)
    if expect is None:
        raise SystemExit(f"LỖI: chưa có số đối chiếu cho {stem!r} (bảng EXPECTED có: {', '.join(EXPECTED)})")
    paths = {"a1_triples": a2.triples_path(src), "a2_edges": a2.edges_path(src),
             "a2_refs": a2.refs_path(src), "a3_exceptions": a3.exceptions_path(src)}
    try:
        rows = {name: load_rows(p) for name, p in paths.items()}
        if versions is not None:
            paths["a4_versions"] = Path(versions)
            rows["a4_versions"] = load_rows(versions, VERSION_KEYS)
    except ValueError as e:
        raise SystemExit(f"LỖI: {e}")
    checks, unit_types = check_codes(rows["a1_triples"], expect)
    checks += check_parents(unit_types, rows["a2_edges"], expect)
    checks.append(check_duplicate_edges([(name, rows[name]) for name in EDGE_SOURCES]))
    if versions is not None:
        checks += check_versions(set(unit_types), rows["a4_versions"])
        checks.append(check_version1_content(rows["a1_triples"], rows["a4_versions"]))
        checks.append(check_base_dates(set(unit_types), rows["a4_versions"]))
    text = format_report(stem, paths, checks)
    print(text, end="")
    write_text(text, report_path(src, versions))
    print("đã ghi", report_path(src, versions))
    return 1 if failures(checks) else 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="file md nguồn, dùng để suy stem của các file A1-A3")
    ap.add_argument("--versions", help="a4_<name>_versions.jsonl; có thì chạy thêm bước 4 và ghi báo cáo riêng cho file này")
    args = ap.parse_args(argv)
    return run(args.path, args.versions)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
