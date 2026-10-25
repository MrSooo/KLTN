import argparse
import collections
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "data" / "raw" / "blds2015_p4.md"
PROCESSED_DIR = ROOT / "data" / "processed"

DOC_PREFIX = "BLDS2015"  # tiền tố id: BLDS2015.D621.K1.a (Điểm đ viết thành dd: BLDS2015.D1.K1.dd)

# Văn bản gốc (review F-08). A4 lấy hieu_luc làm effective_from của phiên bản 1 và DOC_PREFIX làm source_doc; A7 dựng nút văn bản từ đây.
BASE_DOC = {"id": DOC_PREFIX, "ten": "Bộ luật Dân sự", "so_hieu": "91/2015/QH13", "co_quan": "Quốc hội",
            "ngay_ban_hanh": "2015-11-24", "hieu_luc": "2017-01-01"}

# Dãy số Điều mong đợi của từng file nguồn, theo thứ tự xuất hiện.
EXPECTED_DIEU = {
    "blds2015_5dieu.md": [621, 626, 644, 650, 651],
    "blds2015_p4.md": list(range(609, 663)),
}

# Chữ của Điểm: bảng chữ trong văn bản luật (có đ, không có f j w z). Không dùng [a-z].
DIEM_LETTERS = "abcdđeghiklmnopq"

# Trong file `\` là ký tự thật (Markdown escape dấu chấm), nên khớp bằng `\\`.
RE_DIEU = re.compile(r"^### Điều (\d+)\\?\.\s*(.*)$")
RE_KHOAN = re.compile(r"^\*\*(\d+)\\?\.\*\*\s*(.*)$")
RE_DIEM = re.compile(rf"^- \*\*([{DIEM_LETTERS}])\)\*\*\s*(.*)$")
RE_RULE = re.compile(r"^-{3,}$")
RE_HEADING = re.compile(r"^#{1,2}(\s|$)")  # chỉ # và ## mới được bỏ qua; ### phải là Điều

# Dòng gốc của para mà bắt đầu bằng các tiền tố này thì rất có thể là Khoản/Điểm/tiêu đề sai định dạng.
SUSPECT_PREFIXES = ("- ", "**", "#")

SKIP_BLANK = "trống"
SKIP_RULE = "---"
SKIP_HEADING = "tiêu đề #/##"


class Token(NamedTuple):
    kind: str     # dieu | khoan | diem | para
    label: str    # số điều / số khoản / chữ điểm; "" với para
    text: str     # phần chữ đã làm sạch
    line_no: int  # số dòng trong file nguồn (từ 1), khớp với step 1


class Skipped(NamedTuple):
    line_no: int
    reason: str


class Suspicious(NamedTuple):
    line_no: int
    reason: str
    raw: str


class Tokenized(NamedTuple):
    tokens: list      # list[Token]
    skipped: list     # list[Skipped]
    suspicious: list  # list[Suspicious]; sau khi parse xong phải rỗng


def normalize(s):
    """NFC, \\xa0 -> dấu cách, bỏ khoảng trắng cuối dòng (kể cả 2 dấu cách ngắt dòng cứng)."""
    return unicodedata.normalize("NFC", s).replace("\xa0", " ").rstrip()


def clean_text(s):
    """Làm sạch phần chữ: NFC, bỏ \\xa0, bỏ **, bỏ `\\` trước dấu câu, gộp khoảng trắng thừa."""
    s = normalize(s).replace("**", "")
    s = re.sub(r"\\([^\w\s])", r"\1", s)
    return re.sub(r"\s+", " ", s).strip()


def tokenize(text):
    """Phân loại từng dòng của `text` thành dieu/khoan/diem/para.

    Trả về Tokenized(tokens, skipped, suspicious):
      - tokens: mỗi dòng nội dung một Token (kèm line_no).
      - skipped: dòng bỏ qua có chủ đích, kèm lý do (trống, ---, tiêu đề #/##).
      - suspicious: dòng nghi sai định dạng — `###` không khớp RE_DIEU (không thành token),
        hoặc para có dòng gốc bắt đầu bằng "- ", "**", "#" (vẫn thành token para).
    Không có gì bị bỏ qua mà không để lại dấu vết trong skipped hoặc suspicious.
    """
    tokens, skipped, suspicious = [], [], []
    lines = text.split("\n")
    if lines[-1] == "":  # mẩu rỗng sau \n cuối file, không phải một dòng
        lines.pop()

    for line_no, raw in enumerate(lines, 1):
        line = normalize(raw)
        for kind, regex in (("dieu", RE_DIEU), ("khoan", RE_KHOAN), ("diem", RE_DIEM)):
            m = regex.match(line)  # khớp mẫu đầu tiên thì dừng
            if m:
                tokens.append(Token(kind, m.group(1), clean_text(m.group(2)), line_no))
                break
        else:
            if not line:
                skipped.append(Skipped(line_no, SKIP_BLANK))
            elif RE_RULE.match(line):
                skipped.append(Skipped(line_no, SKIP_RULE))
            elif RE_HEADING.match(line):
                skipped.append(Skipped(line_no, SKIP_HEADING))
            elif line.startswith("#"):
                suspicious.append(Suspicious(line_no, "tiêu đề # không phải #/## và không khớp RE_DIEU", raw))
            else:
                tokens.append(Token("para", "", clean_text(line), line_no))
                prefix = next((p for p in SUSPECT_PREFIXES if line.lstrip().startswith(p)), None)
                if prefix:
                    suspicious.append(Suspicious(line_no, f"para bắt đầu bằng {prefix!r}", raw))
    return Tokenized(tokens, skipped, suspicious)


@dataclass
class Unit:
    id: str
    type: str            # dieu | khoan | diem
    number: str          # nhãn gốc: "621", "1", "a" / "đ"
    heading: str | None  # chỉ Điều có
    parts: list          # list[str] các đoạn chữ; ghép bằng "\n" khi ghi ra
    source_line: int     # dòng của nhãn trong file nguồn


class ParseError(NamedTuple):
    line_no: int
    reason: str


class Parsed(NamedTuple):
    units: list   # list[Unit], theo thứ tự xuất hiện trong file
    errors: list  # list[ParseError]; sau khi parse xong phải rỗng
    notes: list   # list[str]: para đứng ngay sau một Điểm, ghi vào a1_notes.txt


def diem_code(label):
    """Chữ Điểm khi ghép mã: đ -> dd (number vẫn lưu đ). Không đụng d vì d đứng một mình."""
    return label.replace("đ", "dd")


def parse(tokens, expected_dieu):
    """Máy trạng thái duyệt list token, dựng các đơn vị Điều > Khoản > Điểm.

    expected_dieu: dãy số Điều mong đợi theo thứ tự. Mọi lỗi được thu vào `errors`, parser vẫn đi
    tiếp; sau lỗi, bộ đếm được đồng bộ lại theo số thực tế để lỗi không lan sang các dòng sau.
    """
    units, errors, notes = [], [], []
    expected_dieu = list(expected_dieu)
    dieu = khoan = None  # Điều / Khoản hiện tại
    n_dieu = 0           # số phần tử expected_dieu đã dùng
    khoan_no = 0         # số Khoản gần nhất trong Điều hiện tại
    diem_idx = -1        # chỉ số trong DIEM_LETTERS của chữ Điểm gần nhất trong Khoản hiện tại

    def err(t, reason):
        errors.append(ParseError(t.line_no, reason))

    for i, t in enumerate(tokens):
        prev = tokens[i - 1] if i else None

        if t.kind == "dieu":
            number = int(t.label)
            want = expected_dieu[n_dieu] if n_dieu < len(expected_dieu) else None
            if number == want:
                n_dieu += 1
            else:
                err(t, f"Điều {number} thừa, ngoài danh sách mong đợi" if want is None
                    else f"Điều {number}, mong đợi Điều {want}")
                rest = expected_dieu[n_dieu:]
                n_dieu += rest.index(number) + 1 if number in rest else 1
            dieu = Unit(f"{DOC_PREFIX}.D{t.label}", "dieu", t.label, t.text, [], t.line_no)
            units.append(dieu)
            khoan, khoan_no, diem_idx = None, 0, -1

        elif t.kind == "khoan":
            if dieu is None:
                err(t, f"Khoản {t.label} khi chưa có Điều")
                continue
            number = int(t.label)
            if number != khoan_no + 1:
                err(t, f"Khoản {number}, mong đợi Khoản {khoan_no + 1} (Điều {dieu.number})")
            khoan = Unit(f"{dieu.id}.K{t.label}", "khoan", t.label, None, [t.text] if t.text else [], t.line_no)
            units.append(khoan)
            khoan_no, diem_idx = number, -1

        elif t.kind == "diem":
            if khoan is None:
                err(t, f"Điểm {t.label} khi chưa có Khoản" + (f" (Điều {dieu.number})" if dieu else ""))
                continue
            idx = DIEM_LETTERS.index(t.label)
            if idx != diem_idx + 1:
                want = DIEM_LETTERS[diem_idx + 1] if diem_idx + 1 < len(DIEM_LETTERS) else "(hết bảng chữ)"
                err(t, f"Điểm {t.label}, mong đợi điểm {want} (Điều {dieu.number}, Khoản {khoan.number})")
            units.append(Unit(f"{khoan.id}.{diem_code(t.label)}", "diem", t.label, None,
                              [t.text] if t.text else [], t.line_no))
            diem_idx = idx

        else:  # para: vào Khoản hiện tại, chưa có Khoản thì vào Điều hiện tại
            target = khoan if khoan is not None else dieu
            if target is None:
                err(t, "đoạn chữ khi chưa có Điều")
                continue
            if not t.text:
                err(t, "đoạn chữ rỗng sau khi làm sạch")
                continue
            target.parts.append(t.text)
            if prev is not None and prev.kind == "diem" and khoan is not None:
                notes.append(f"Điều {dieu.number}, Khoản {khoan.number}, dòng {t.line_no}")

    if n_dieu < len(expected_dieu):
        last = tokens[-1].line_no if tokens else 0
        errors.append(ParseError(last, f"hết file nhưng còn thiếu Điều: {expected_dieu[n_dieu:]}"))
    return Parsed(units, errors, notes)


def step1_check_data(path=SAMPLE):
    """Step 1: nhìn dữ liệu thô — in từng dòng bằng repr() và quét ký tự lạ."""
    with open(path, encoding="utf-8", newline="") as f:  # newline="" để giữ nguyên \r nếu có
        text = f.read()
    lines = text.split("\n")

    # 1a. từng dòng kèm số dòng, repr() để thấy \, **, \xa0, khoảng trắng cuối dòng
    for n, line in enumerate(lines, 1):
        if n == len(lines) and line == "":  # mẩu rỗng sau \n cuối file
            break
        end = "\n" if n < len(lines) else ""
        print(f"{n:3d}: {line + end!r}")

    # 1b. ký tự lạ / khoảng trắng thừa
    odd = collections.Counter(
        c for c in text
        if unicodedata.category(c) in ("Cc", "Cf", "Zs", "Zl", "Zp") and c not in " \n"
    )
    print()
    print("ký tự lạ (control/format/space khác):", {hex(ord(k)): v for k, v in odd.items()} or "không có")
    print("BOM:", text.startswith(chr(0xFEFF)), "| có \\r:", "\r" in text, "| có tab:", "\t" in text)
    print("dòng kết thúc bằng 2 dấu cách:", [n for n, l in enumerate(lines, 1) if l.endswith("  ") and not l.endswith("   ")])
    print("dòng kết thúc bằng 1 dấu cách:", [n for n, l in enumerate(lines, 1) if l.endswith(" ") and not l.endswith("  ")])
    print("dòng kết thúc bằng >=3 dấu cách:", [n for n, l in enumerate(lines, 1) if l.endswith("   ")])
    print("dấu cách đôi giữa dòng:", [n for n, l in enumerate(lines, 1) if "  " in l.rstrip(" ")])
    print("file kết thúc bằng \\n:", text.endswith("\n"), "| bằng \\n\\n:", text.endswith("\n\n"))


def step2_classify(path=SAMPLE):
    """Step 2: tokenize, in token + thống kê dòng bỏ qua. Thoát với mã 1 nếu còn dòng đáng ngờ."""
    with open(path, encoding="utf-8", newline="") as f:
        result = tokenize(f.read())

    for t in result.tokens:
        print(f"{t.line_no:3d}  {t.kind:<5} {t.label:>3}  {t.text[:80]!r}")
    print()
    print("số token theo loại:", dict(collections.Counter(t.kind for t in result.tokens)))
    print("dòng bỏ qua theo lý do:", dict(collections.Counter(s.reason for s in result.skipped)))
    print("dòng đáng ngờ:", len(result.suspicious))
    fail_if_suspicious(result)


def fail_if_suspicious(result):
    if not result.suspicious:
        return
    print("\nDÒNG ĐÁNG NGỜ (phải rỗng):", file=sys.stderr)
    for s in result.suspicious:
        print(f"{s.line_no:3d}  {s.reason}: {s.raw!r}", file=sys.stderr)
    raise SystemExit(1)


def load_parsed(path):
    """Đọc file, tokenize (phải sạch) rồi parse. Trả về (Tokenized, Parsed); chưa kiểm lỗi parse."""
    path = Path(path)
    if path.name not in EXPECTED_DIEU:
        raise SystemExit(f"chưa khai báo dãy Điều mong đợi cho {path.name} trong EXPECTED_DIEU")
    with open(path, encoding="utf-8", newline="") as f:
        result = tokenize(f.read())
    fail_if_suspicious(result)
    return result, parse(result.tokens, EXPECTED_DIEU[path.name])


def fail_if_errors(parsed):
    if not parsed.errors:
        return
    print("\nLỖI PARSE (phải rỗng):", file=sys.stderr)
    for e in parsed.errors:
        print(f"{e.line_no:3d}  {e.reason}", file=sys.stderr)
    raise SystemExit(1)


def to_triples(units):
    """Mỗi đơn vị thành các bộ ba (s, p, o), p theo thứ tự: type, number, heading, text, version, source_line."""
    triples = []
    for u in units:
        triples.append((u.id, "type", u.type))
        triples.append((u.id, "number", u.number))
        if u.heading is not None:  # chỉ Điều
            triples.append((u.id, "heading", u.heading))
        if u.parts:
            triples.append((u.id, "text", "\n".join(u.parts)))
        triples.append((u.id, "version", 1))
        triples.append((u.id, "source_line", u.source_line))
    return triples


def write_triples(triples, path):
    """Ghi JSONL, mỗi dòng {"s","p","o"}. Không có effective_from."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for s, p, o in triples:
            f.write(json.dumps({"s": s, "p": p, "o": o}, ensure_ascii=False) + "\n")


def write_notes(notes, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:  # ghi đè mỗi lần chạy
        f.writelines(n + "\n" for n in notes)


def triples_path(src):
    return PROCESSED_DIR / f"a1_triples_{Path(src).stem}.jsonl"


def notes_path(src):
    """Mỗi file nguồn một file notes, để chạy file này không ghi đè notes của file kia."""
    return ROOT / "docs" / f"a1_notes_{Path(src).stem}.txt"


def step3_parse(path=SAMPLE):
    """Step 3: dựng Điều > Khoản > Điểm. Ghi a1_notes.txt; thoát mã 1 nếu còn lỗi parse."""
    _, parsed = load_parsed(path)

    indent = {"dieu": "", "khoan": "  ", "diem": "    "}
    for u in parsed.units:
        head = f" {u.heading[:40]!r}" if u.heading is not None else ""
        parts = [p[:40] for p in u.parts]
        print(f"{u.source_line:3d}  {indent[u.type]}{u.id}{head}  parts={parts}")
    print()
    print("số đơn vị theo loại:", dict(collections.Counter(u.type for u in parsed.units)))
    print("para ngay sau Điểm (ghi vào notes):", len(parsed.notes))
    print("lỗi parse:", len(parsed.errors))

    fail_if_errors(parsed)  # notes chỉ được ghi khi parse sạch
    out = notes_path(path)
    write_notes(parsed.notes, out)
    print("đã ghi", out)


def step4_write_triples(path=SAMPLE):
    """Step 4: ghi triples JSONL vào data/processed/. Từ chối ghi nếu còn lỗi parse."""
    _, parsed = load_parsed(path)
    fail_if_errors(parsed)
    triples = to_triples(parsed.units)
    out = triples_path(path)
    write_triples(triples, out)
    print("số đơn vị:", len(parsed.units), "| số triples:", len(triples))
    print("đã ghi", out)


STEPS = {"1": step1_check_data, "2": step2_classify, "3": step3_parse, "4": step4_write_triples}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default=SAMPLE)
    ap.add_argument("-s", "--step", choices=STEPS, help="chỉ chạy một step (mặc định: chạy tất cả)")
    args = ap.parse_args()
    for key in [args.step] if args.step else STEPS:
        print(f"===== step {key} =====")
        STEPS[key](args.path)
