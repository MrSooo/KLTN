"""Danh mục văn bản của kho lao động: đọc `data/raw/labor/manifest.csv`, không chép cứng thông tin văn bản vào code.

Các bước 1.1-2.4, checks, graph, viewer lấy từ đây: đường dẫn file, số hiệu, ngày ban hành/hiệu lực, cấp văn bản, số Điều đối chiếu.
Cột `quan_he` và `ghi_chu` của manifest chỉ là mốc kiểm, KHÔNG phải đầu vào của pipeline: module này
không đưa chúng vào Doc để không bước nào dùng nhầm.
"""
import csv
import datetime
import os
import re
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parent.parent

# Tập con (A41): biến môi trường KLTN_TAP_CON=<tên> trỏ cả pipeline sang kho con do utils/subset/build_subset.py dựng từ
# data/subsets/<tên>.json. Vì sao đổi ở đây chứ không lọc trong từng bước: mọi bước lấy đường dẫn từ module này, nên
# pipeline chạy nguyên vẹn trên kho nhỏ, không có nhánh "nếu tập con" rải trong code. llm_cache KHÔNG đổi: khoá cache
# tính theo nội dung gửi model, kho con giữ nguyên chữ của văn bản nên dùng chung được.
SUBSET = os.environ.get("KLTN_TAP_CON", "").strip() or None
if SUBSET:
    SUBSET_ROOT = ROOT / "data" / "processed_subset" / SUBSET
    RAW_DIR = SUBSET_ROOT / "raw"
    PROCESSED_DIR = SUBSET_ROOT / "processed"
    REPORT_DIR = ROOT / "docs" / "run_reports_subset" / SUBSET
else:
    RAW_DIR = ROOT / "data" / "raw" / "labor"
    PROCESSED_DIR = ROOT / "data" / "processed"
    REPORT_DIR = ROOT / "docs" / "run_reports"

# Lần chạy LLM khác (A46): KLTN_LLM_RUN=<tên> (ví dụ `ckey`) là một bộ kết quả LLM song song với bộ mặc định (Sonnet qua phiên Claude Code).
# Vì sao cần: cache theo khoá sha (có tên model trong khoá) không đụng nhau, nhưng cache đặt tên theo văn bản (`<doc>[.<tập con>].json`)
# và đầu ra, báo cáo thì có: chạy bộ mới mà không tách sẽ ghi đè bộ cũ. Chỉ đổi đầu ra và báo cáo, KHÔNG đổi RAW_DIR (cùng chữ luật).
LLM_RUN = os.environ.get("KLTN_LLM_RUN", "").strip() or None
if LLM_RUN:
    PROCESSED_DIR = PROCESSED_DIR.with_name(f"{PROCESSED_DIR.name}_{LLM_RUN}")
    REPORT_DIR = REPORT_DIR.with_name(f"{REPORT_DIR.name}_{LLM_RUN}")
MANIFEST = RAW_DIR / "manifest.csv"


def cache_tag():
    """Hậu tố tên file cache đặt theo văn bản: '' (kho đầy đủ, lần chạy mặc định), '.lldnn', '.ckey', '.lldnn.ckey'."""
    return "".join(f".{x}" for x in (SUBSET, LLM_RUN) if x)


def cache_name(stem):
    """Tên file cache của một văn bản hay một bộ câu hỏi theo kho và lần chạy đang dùng: `<stem><hậu tố>.json`."""
    return f"{stem}{cache_tag()}.json"


def _subset_spec():
    import json
    return json.loads((ROOT / "data" / "subsets" / f"{SUBSET}.json").read_text(encoding="utf-8"))


def in_subset(uid):
    """Mã đơn vị (hay doc_id) có nằm trong kho con không; kho đầy đủ thì luôn True.

    Tính từ spec chứ không từ đầu ra 1.1, để dùng được ở mọi bước kể cả khi 1.1 chưa chạy. Mã như 'BLLD_45-2019.D91.K4':
    văn bản phải có trong spec, và nếu văn bản bị cắt thì số Điều phải nằm trong danh sách giữ lại.
    """
    if not SUBSET:
        return True
    doc, _, rest = uid.partition(".")
    how = _subset_spec()["van_ban"].get(doc)
    if how is None:
        return False
    if not isinstance(how, dict) or not rest.startswith("D"):
        return True
    num = re.match(r"D(\d+)", rest)
    return bool(num) and int(num[1]) in _kept(how)


def _kept(how):
    """Số Điều giữ lại của một văn bản bị cắt: {"dieu": ["52-58", "220"]} -> [52, ..., 58, 220] (đã sắp)."""
    nums = []
    for r in how["dieu"]:
        a, _, b = r.partition("-")
        nums += range(int(a), int(b or a) + 1)
    return sorted(nums)


def landmark(name, needs, ok):
    """Một mốc cổng (tên, kết quả). Kết quả: True đạt, False trượt, None bỏ qua (kho con, mốc cần đơn vị ngoài kho con; A41).

    Vì sao không lặng lẽ bỏ: báo cáo vẫn liệt kê mốc để người đọc thấy mốc nào chưa được kiểm trên kho con.
    Nơi gọi coi None là không trượt (`ok is not False`) và in bằng mark_word. Kho đầy đủ: kết quả luôn là bool như cũ.
    """
    if SUBSET and not all(in_subset(u) for u in needs):
        return name, None
    return name, bool(ok)


def mark_word(ok):
    """Chữ in trong báo cáo cho kết quả của landmark()."""
    return "bỏ qua (ngoài kho con)" if ok is None else "đạt" if ok else "KHÔNG đạt"


def subset_jumps(doc_id):
    """Các bước nhảy số Điều mà kho con cố ý tạo khi cắt (A41), dạng {("58", "150"), ...}; kho đầy đủ hoặc văn bản giữ nguyên thì rỗng.

    Vì sao: cổng 1.1 đòi Điều liên tục để bắt lỗi parse; kho con cắt bớt Điều nên có bước nhảy thật. Chỉ nhận đúng các
    bước nhảy ở chỗ cắt đã khai trong data/subsets/<tên>.json, mọi bước nhảy khác vẫn là lỗi.
    """
    if not SUBSET:
        return set()
    how = _subset_spec()["van_ban"].get(doc_id)
    if not isinstance(how, dict):
        return set()
    nums = _kept(how)
    return {(str(x), str(y)) for x, y in zip(nums, nums[1:]) if y != x + 1}

BASE_DOC_ID = "BLLD_45-2019"  # văn bản gốc: KB ban đầu chỉ dựng từ văn bản này

# Cấp văn bản: luật/bộ luật = 1; nghị định, nghị quyết Chính phủ = 2; thông tư = 3.
# Văn bản hợp nhất mang cấp của luật mà nó hợp nhất.
LEVEL_BY_TYPE = {"Bộ luật": 1, "Văn bản hợp nhất": 1, "Nghị định": 2, "Nghị quyết CP": 2, "Thông tư": 3}
SLUG_BY_TYPE = {"Bộ luật": "bo_luat", "Văn bản hợp nhất": "van_ban_hop_nhat", "Nghị định": "nghi_dinh",
                "Nghị quyết CP": "nghi_quyet_cp", "Thông tư": "thong_tu"}
ISSUER_BY_TYPE = {"Bộ luật": "Quốc hội", "Văn bản hợp nhất": "Văn phòng Quốc hội", "Nghị định": "Chính phủ",
                  "Nghị quyết CP": "Chính phủ", "Thông tư": "Bộ"}

# Phụ lục của một văn bản mà pipeline bóc chi tiết (mục, dòng). Phụ lục không nằm trong danh sách này vẫn là một nút
# (để dẫn chiếu giải được) nhưng chỉ giữ tiêu đề, gắn scope `out_of_scope`. Chỉ NQ 66.16 cần: văn bản này kèm 14
# phụ lục của các bộ, và chỉ Phụ lục I.7 (Bộ Nội vụ: cho thuê lại lao động, sửa quy định NĐ 145) thuộc phạm vi lao động.
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
