# archive/v1_thua_ke: bản v1 (Bộ luật Dân sự 2015, phần 4 thừa kế)

Dọn ngày 07/11/2026 để chuyển sang Bộ luật Lao động (nhánh `v2-lao-dong`). Mọi thứ ở đây giữ **nguyên đường dẫn gốc** (ví dụ `data/raw/blds2015_p4.md` nằm ở `archive/v1_thua_ke/data/raw/blds2015_p4.md`), nên khôi phục chỉ cần `git mv` ngược lại.

## Đã archive (209 file, không tính README này)
| Mục | Số file | Vì sao |
|---|---|---|
| `data/raw/blds2015_p4.md`, `data/sample/`, `data/dev_amend/`, `data/ext_amend/`, `data/gold/` | 14 | dữ liệu đầu vào của lĩnh vực cũ |
| `data/processed/` | 136 | đầu ra A1-A8 sinh từ dữ liệu trên |
| `data/llm_cache/` | 10 | phản hồi thô Gemini cho A4 (ngày 04/11/2026) |
| `docs/bao_cao_chay/` | 37 | báo cáo chữ do code sinh khi chạy trên dữ liệu cũ |
| `docs/quyet_dinh/pham_vi_mo_rong.txt` | 1 | lập luận "BLDS không có chế tài", không còn đúng với luật lao động |
| `report/tong_hop/` | 3 | báo cáo tổng hợp cho thầy về v1 (md, html, bảng tổng quan) |
| `plan/de_cuong/`, `plan/ke_hoach/` | 3 | đề cương nộp trường, kế hoạch hoàn thành, kế hoạch tăng tốc: đã hết hiệu lực theo `KeHoach_KB_LaoDong_Agent_2026-11-06` mục 0 |
| `plan/kien_thuc/` | 2 | `phep_thu_do_phu_dan_chieu` (phép đo độ phủ dẫn chiếu Điều 609-662), `giai_thich_khai_niem` (giải thích phương pháp, ví dụ thừa kế) |
| `plan/thiet_ke/` | 3 | `huong_dan_so_khai_niem_r1r4`, `ban_giao_bat_dau_lam` (định nghĩa bước B-D, C1-C4, bộ quét), `so_quyet_dinh` |

Tổng 209 file đã chuyển bằng `git mv` (205 ngày 07/11 đợt 1, 4 file đợt 2). **Đọc khi tới bước cần:** plan mới (L7-L9) nhắc R1-R4, C1-C4, "bộ quét 5 loại lỗi", "kế hoạch cũ"; các định nghĩa đó nằm ở `plan/thiet_ke/` và `plan/de_cuong/` trong thư mục này. Chỉ đọc, rồi viết bản cho lao động ở ngoài archive.

**Cố ý KHÔNG archive** (mô tả code còn ở `src/`, sẽ dọn ví dụ v1 dần theo từng bước L): `src/`, `tests/`, `utils/`, `docs/quyet_dinh/a4_*` và `a6_a7_*`, `docs/ref/KetQua_*`, `report/review/`, `report/ky_thuat/`.

## Khôi phục
- Một mục: `git mv archive/v1_thua_ke/<đường dẫn> <đường dẫn>`.
- Cả v1 chạy được nguyên trạng: `git switch --detach 25c65e6` (commit "Chốt v1") hoặc nhánh `refactor`.

## Baseline test của v1 (chạy ngày 07/11/2026 trên bản sạch `git archive 25c65e6`, Python của `.venv`)
11 file `tests/test_*.py`, **287 dòng `OK`**, mọi file kết thúc bằng `tổng test lỗi: 0`:
`test_a1` 11, `test_a2` 43, `test_a3` 19, `test_a4` 63, `test_a4_llm` 20, `test_a5` 54, `test_a6` 23, `test_a7` 32, `test_a8` 15, `test_eval_ext_amend` 2, `test_eval_gold` 5.

## Có chủ đích: một số thứ đang đỏ
Sau khi dọn, các thứ sau trỏ vào đường dẫn đã archive nên **sẽ lỗi cho đến khi refactor** (L0):
- gần như mọi `tests/test_*.py` và `tests/eval_*.py` (đọc `data/sample/blds2015_5dieu.md`, `data/raw/blds2015_p4.md`, số đếm cứng);
- `src/run_all.py` (hằng `BASES`, `data/dev_amend/...`), bảng `EXPECTED` của `src/a5_checks.py` và `src/a7_graph.py`;
- `utils/render_report.py` (mặc định `report/tong_hop/`), `utils/a8/a8_viz.py`.

Đây không phải lỗi mới: xem baseline ở trên là mốc "đã xanh trước khi dọn".
