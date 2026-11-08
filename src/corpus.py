"""Danh mục văn bản của kho lao động: đọc `data/raw/labor/manifest.csv`, không chép cứng thông tin văn bản vào code.

Các bước A1-A8 lấy từ đây: đường dẫn file, số hiệu, ngày ban hành/hiệu lực, cấp văn bản, số Điều đối chiếu.
Cột `quan_he` và `ghi_chu` của manifest chỉ là mốc kiểm của học viên, KHÔNG phải đầu vào của pipeline: module này
không đưa chúng vào Doc để không bước nào dùng nhầm.
"""
import csv
import datetime
import re
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw" / "labor"
MANIFEST = RAW_DIR / "manifest.csv"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORT_DIR = ROOT / "docs" / "bao_cao_chay"

BASE_DOC_ID = "BLLD_45-2019"  # văn bản gốc: KB ban đầu chỉ dựng từ văn bản này (plan L2)

# Cấp văn bản (plan mục 3): luật/bộ luật = 1; nghị định, nghị quyết Chính phủ = 2; thông tư = 3.
# Văn bản hợp nhất mang cấp của luật mà nó hợp nhất.
LEVEL_BY_TYPE = {"Bộ luật": 1, "Văn bản hợp nhất": 1, "Nghị định": 2, "Nghị quyết CP": 2, "Thông tư": 3}
SLUG_BY_TYPE = {"Bộ luật": "bo_luat", "Văn bản hợp nhất": "van_ban_hop_nhat", "Nghị định": "nghi_dinh",
                "Nghị quyết CP": "nghi_quyet_cp", "Thông tư": "thong_tu"}
ISSUER_BY_TYPE = {"Bộ luật": "Quốc hội", "Văn bản hợp nhất": "Văn phòng Quốc hội", "Nghị định": "Chính phủ",
                  "Nghị quyết CP": "Chính phủ", "Thông tư": "Bộ"}

# Phụ lục của một văn bản mà pipeline bóc chi tiết (mục, dòng). Phụ lục không nằm trong danh sách này vẫn là một nút
# (để dẫn chiếu giải được) nhưng chỉ giữ tiêu đề, gắn scope `out_of_scope`. Chỉ NQ 66.16 cần: văn bản này kèm 14
# phụ lục của các bộ, và chỉ Phụ lục I.7 (Bộ Nội vụ: cho thuê lại lao động, sửa quy định NĐ 145) thuộc phạm vi lao động (plan L4, L5).
# Văn bản không có tên ở đây: mọi phụ lục đều được bóc chi tiết.
PL_IN_SCOPE = {"NQ_66-16-2026": {"I_7"}}

# Lỗi đánh số của chính nguồn đã biết, được nhận có chủ đích (mọi lỗi khác vẫn là lỗi parse): ND_145 có hai "Chương XI"
# (dòng 1680 và 2142, lần sau là Chương "Điều khoản thi hành"); mã của lần sau thêm hậu tố _2.
DUP_CHUONG_OK = {"ND_145-2020"}


class Doc(NamedTuple):
    doc_id: str
    path: Path
    so_hieu: str
    loai: str
    ten_ngan: str
    ngay_ban_hanh: datetime.date | None  # None khi manifest ghi "?" (xem issued_uncertain)
    issued_uncertain: bool               # manifest ghi ngày kèm dấu "?" (TT_09, TT_10)
    ngay_hieu_luc: datetime.date
    nhom: str                            # base | dev
    so_dieu: int                         # số Điều đếm độc lập bằng regex `^Điều N.` (cột so_dieu_dem_duoc)

    @property
    def level(self):
        return LEVEL_BY_TYPE[self.loai]

    @property
    def doc_type(self):
        return SLUG_BY_TYPE[self.loai]

    @property
    def issuer(self):
        return ISSUER_BY_TYPE[self.loai]

    @property
    def is_consolidation(self):
        return self.loai == "Văn bản hợp nhất"


def parse_date(s):
    """'2020-11-12?' -> (date(2020,11,12), True); '?' -> (None, True)."""
    s = (s or "").strip()
    uncertain = s.endswith("?")
    s = s.rstrip("?").strip()
    if not s:
        return None, True
    return datetime.date.fromisoformat(s), uncertain


def load_manifest(path=MANIFEST):
    """{doc_id: Doc} theo thứ tự dòng trong manifest. Lỗi dữ liệu (thiếu cột, ngày sai, file không có) thì ValueError."""
    docs = {}
    with open(path, encoding="utf-8-sig", newline="") as f:  # manifest có BOM
        for row in csv.DictReader(f):
            doc_id = row["doc_id"]
            if doc_id in docs:
                raise ValueError(f"manifest: doc_id lặp: {doc_id}")
            if row["loai"] not in LEVEL_BY_TYPE:
                raise ValueError(f"manifest: loại văn bản lạ {row['loai']!r} ({doc_id})")
            issued, uncertain = parse_date(row["ngay_ban_hanh"])
            effective, _ = parse_date(row["ngay_hieu_luc"])
            if effective is None:
                raise ValueError(f"manifest: {doc_id} thiếu ngày hiệu lực")
            file = RAW_DIR / row["nhom"] / row["file"]
            if not file.exists():
                raise ValueError(f"manifest: không thấy file {file}")
            docs[doc_id] = Doc(doc_id, file, row["so_hieu"], row["loai"], row["ten_ngan"], issued, uncertain,
                               effective, row["nhom"], int(row["so_dieu_dem_duoc"]))
    return docs


def get_doc(doc_id, docs=None):
    docs = docs or load_manifest()
    if doc_id not in docs:
        raise ValueError(f"doc_id lạ: {doc_id!r} (manifest có: {', '.join(docs)})")
    return docs[doc_id]


def doc_id_from_path(path, docs=None):
    """doc_id của một file nguồn = tên file bỏ đuôi (quy ước kho)."""
    return get_doc(Path(path).stem, docs).doc_id


def out_dir(step):
    """data/processed/<bước>/ ; test đổi PROCESSED_DIR ở module gọi nếu cần thư mục tạm."""
    return PROCESSED_DIR / step


def report_dir(step):
    return REPORT_DIR / step


def fmt_vn_date(d):
    return f"{d.day:02d}/{d.month:02d}/{d.year}"


_RE_VN_DATE = re.compile(r"ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})", re.I)


def find_vn_date(text):
    """Ngày đầu tiên dạng 'ngày 20 tháng 11 năm 2019' trong text, hoặc None."""
    m = _RE_VN_DATE.search(text)
    if not m:
        return None
    try:
        return datetime.date(int(m[3]), int(m[2]), int(m[1]))
    except ValueError:
        return None
