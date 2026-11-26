r"""Dựng kho con từ data/subsets/<tên>.json (A41): cắt file nguồn và viết manifest riêng vào data/processed_subset/<tên>/raw/.

Chạy: python -I utils/subset/build_subset.py lldnn
Sau đó chạy pipeline trên kho con: python -I src/run_all.py --tap-con lldnn   (run_all tự gọi script này trước)

Cách cắt: chia file thành đoạn tại dòng Chương / Mục / Điều (dùng đúng regex của bước 1.1 để không lệch cách đọc).
Giữ phần đầu văn bản (trước Chương đầu tiên: số hiệu, ngày, "Căn cứ ..." mà bước 2.2 cần), các Điều được khai,
và dòng Chương / Mục chứa chúng. Đoạn của Điều cuối cùng kéo tới hết file nên phần ký tên, nơi nhận đi theo Điều cuối.
Văn bản khai "ca_van_ban" thì chép nguyên. Cột so_dieu_dem_duoc của manifest con = số Điều giữ lại (cổng của 1.1).
Điều đã khai mà không thấy, hoặc thấy hai lần, thì dừng: không dựng kho con thiếu mà không báo.
"""
import csv
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
import parse  # noqa: E402  (chỉ dùng regex của 1.1)

FULL_RAW = ROOT / "data" / "raw" / "labor"  # luôn đọc kho đầy đủ, không theo KLTN_TAP_CON
SPEC_DIR = ROOT / "data" / "subsets"
OUT_BASE = ROOT / "data" / "processed_subset"


def expand(ranges):
    """["52-58", "220"] -> {52, ..., 58, 220} (số Điều dạng chuỗi)."""
    out = set()
    for r in ranges:
        a, _, b = r.partition("-")
        out |= {str(n) for n in range(int(a), int(b or a) + 1)}
    return out


def cut(lines, keep):
    """Giữ phần đầu, các Điều trong keep, và dòng Chương/Mục bao chúng. Trả (dòng giữ lại, số Điều đã thấy theo số)."""
    segs, cur = [], ("head", None, [])
    for line in lines:
        s = line.strip()
        kind = "chuong" if parse.RE_CHUONG.match(s) else "muc" if parse.RE_MUC.match(s) else "dieu" if parse.RE_DIEU.match(s) else None
        if kind:
            segs.append(cur)
            cur = (kind, parse.RE_DIEU.match(s)[1] if kind == "dieu" else None, [line])
        else:
            cur[2].append(line)
    segs.append(cur)

    out, seen = [], {}
    pending = {}  # Chương/Mục chưa in: chỉ in khi có Điều được giữ nằm dưới nó
    for kind, num, body in segs:
        if kind == "head":
            out += body
        elif kind == "chuong":
            pending = {"chuong": body}
        elif kind == "muc":
            pending["muc"] = body
        else:
            seen[num] = seen.get(num, 0) + 1
            if num in keep:
                for k in ("chuong", "muc"):
                    out += pending.pop(k, [])
                out += body
    return out, seen


def build(name):
    spec = json.loads((SPEC_DIR / f"{name}.json").read_text(encoding="utf-8"))
    dest = OUT_BASE / name / "raw"
    if dest.exists():
        shutil.rmtree(dest)  # kho con là đầu ra dựng lại được; dựng lại từ đầu để không sót file cũ
    with open(FULL_RAW / "manifest.csv", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields, rows = reader.fieldnames, {r["doc_id"]: r for r in reader}
    missing = [d for d in spec["van_ban"] if d not in rows]
    if missing:
        raise SystemExit(f"LỖI: spec có văn bản không có trong manifest: {missing}")

    out_rows, report = [], []
    for doc_id, how in spec["van_ban"].items():
        row = dict(rows[doc_id])
        src = FULL_RAW / row["nhom"] / row["file"]
        target = dest / row["nhom"] / row["file"]
        target.parent.mkdir(parents=True, exist_ok=True)
        if how == "ca_van_ban":
            shutil.copyfile(src, target)
            report.append(f"{doc_id:<16} cả văn bản, {row['so_dieu_dem_duoc']} Điều")
        else:
            keep = expand(how["dieu"])
            lines = src.read_text(encoding="utf-8").splitlines(keepends=True)
            kept, seen = cut(lines, keep)
            lost = sorted(keep - set(seen), key=int)
            dup = sorted((n for n in keep if seen.get(n, 0) > 1), key=int)
            if lost or dup:
                raise SystemExit(f"LỖI {doc_id}: Điều khai mà không thấy {lost}, thấy hai lần {dup}")
            target.write_text("".join(kept), encoding="utf-8")
            row["so_dieu_dem_duoc"] = str(len(keep))
            report.append(f"{doc_id:<16} {len(keep)} Điều ({', '.join(how['dieu'])}), {len(kept)}/{len(lines)} dòng")
        out_rows.append(row)

    with open(dest / "manifest.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out_rows)
    print(f"kho con {name}: {dest}")
    print("\n".join(report))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 2:
        raise SystemExit("cách dùng: python -I utils/subset/build_subset.py <tên tập con>")
    build(sys.argv[1])
