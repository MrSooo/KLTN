# Bước 2.5 (tập ảnh hưởng), 2.6 (trích lại tri thức theo tập ảnh hưởng), 2.7 (đối chứng)

Viết ngày 19/11/2026. Quyết định và lý do: `docs/decisions.md`, A42. Phương pháp: `docs/reference/method.md` mục 3.4 (Thuật toán 1, dòng 6 đến 8). Mã: `src/knowledge_units.py` (thư viện), `src/predicate_registry.py`, `src/affected.py`, `src/update.py`; test `tests/test_update.py`.

## 1. Nhận vào
- Kho phiên bản của 2.3-2.4: `data/processed[_subset]/versions/versions.jsonl` (mọi phiên bản, khoảng `[effective_from, effective_to)`, `state`) và `version_edges.jsonl` (cạnh `overrides` có `valid_from`, `valid_to`).
- Nhãn Điều của 1.4, dẫn chiếu 1.2 (`refs_mentions_<doc>`), cạnh 1.5 của mọi văn bản, cạnh `details` của 2.2.
- 1.6A: cache KB gốc `data/llm_cache/propositions/<BLLĐ>[.<tập con>].json` (khoá `uid`) và cache KU `data/llm_cache/propositions/ku/<doc>[.<tập con>].json`.
- 1.6B: kết quả gốc `names-2.1` (replay từ `data/llm_cache/predicates/`).
- 1.7: cache KB gốc theo số thứ tự cặp và cache cặp KU `data/llm_cache/implicit_exceptions/ku_pairs[.<tập con>].json`.

Ví dụ thật (tập con `lldnn`): ND 70/2023 sửa ND 152/2020 Điều 7 khoản 14 từ 18/09/2023. Kho phiên bản có `ND_152-2020.D7.K14` phiên bản 1 `[2021-02-15, 2023-09-18)` và phiên bản 2 `[2023-09-18, 2025-08-07)`; KU của phiên bản 2 là `ND_152-2020.D7.K14@h76e091bf`.

## 2. Ra
- `data/processed[_subset]/predicate_registry/`: `predicate_registry_names.json` ({khoá gộp: tên}, tham số, chữ Việt của tên), `predicate_registry_words.jsonl` (mỗi chữ: tên, mốc được thêm, quyết định LLM hoặc bị loại).
- `data/processed[_subset]/update/`: `update_rules.jsonl` (R của chế độ tăng dần; mỗi dòng là một quy tắc kèm `valid_from`, `valid_to`, `unit`, `ku`, `source_units`, `source_kus`, `isolated`), `update_epochs.jsonl` (mỗi mốc: văn bản gây ra, T theo lý do, N theo quan hệ, A, cặp 1.7 mới hỏi), `update_check.jsonl` (sai khác của 2.7; rỗng là đạt).
- Báo cáo: `docs/run_reports[_subset]/predicate_registry/predicate_registry_report.txt`, `docs/run_reports[_subset]/update/update_report.txt` (số liệu theo mốc, kết quả 2.7, kết quả bỏ từng quan hệ của N, căn cứ chuẩn của bộ câu hỏi dev trong Π_τ).
- Dòng "không thành công": 2.7 trượt in từng sai khác `thieu_o_tang_dan` | `thua_o_tang_dan` (quy tắc có ở một chế độ mà không có ở chế độ kia, kèm ngày và đơn vị) | `cap_1_7_chua_hoi` (cặp dựng lại toàn bộ cần mà tăng dần chưa hỏi); `update.py` thoát mã 1.

## 3. Bảng field
| Field | Nghĩa | Giá trị | Ai đọc |
|---|---|---|---|
| `ku` | mã đơn vị tri thức | `uid` (đầu vào trùng bản parse) hoặc `uid@h<8 hex>` | 1.6A, 1.6B, 1.7, 2.7 |
| `unit` | mã đơn vị trần | mã của 1.1 | mọi phép theo cây, 1.9 (căn cứ) |
| `valid_from`, `valid_to` | khoảng hiệu lực của quy tắc trong R | ngày ISO; `valid_to` null là đang mở | 1.9, checks |
| `isolated` | lý do cô lập tại khoảng đó | chuỗi hoặc null | 1.9 |
| `T` (update_epochs) | đơn vị bị chạm và lý do | `ku_mo`, `ku_dong`, `overrides` | báo cáo |
| `N` (update_epochs) | đơn vị láng giềng theo quan hệ | `refers_to`, `exception_of`, `details`, `overrides`, `concept`, `cay` | báo cáo |
| `loai` (update_check) | kiểu sai khác của 2.7 | `thieu_o_tang_dan`, `thua_o_tang_dan`, `cap_1_7_chua_hoi` | báo cáo |

## 4. Cách làm
1. **KU và mốc** (`knowledge_units.Catalog`): ở mỗi mốc, chụp kho phiên bản; mỗi đơn vị trong phạm vi (như 1.6A: Khoản, Điểm, Điều có chữ dưới Điều nhãn `substantive` hoặc `definition`) cho một ngữ cảnh (tiêu đề Điều, câu dẫn của cha, chữ); ngữ cảnh mới là KU mới.
2. **1.6A cho KU mới** (`update.py xuat-1-6a`, `nhap-1-6a`): hộp cát như A36, lô theo Điều và mốc, cổng `propositions.gate_unit`; nhập chỉ thêm.
3. **Sổ vị từ chỉ thêm** (`predicate_registry.py`): giai đoạn gốc replay; mỗi mốc mở một giai đoạn với chữ mới (khoá gộp chưa có), lượt `names-2.1` nối vào cuối; một hộp cát cho cả chuỗi (`--xuat`, `--nhap`), lượt gốc không nằm trong hộp cát.
4. **2.5** (`affected.affected_at`): T(e) rồi N(T(e)) một bước theo sáu quan hệ ở bảng trên; khớp theo cây.
5. **2.6** (`update.Engine.incremental`): theo thứ tự mốc; cặp 1.7 có đầu trong A(e) đưa vào tập đã hỏi (`xuat-1-7`, `nhap-1-7` cho cặp chưa có câu trả lời); biên dịch ảnh chụp (`compile_at`); thay quy tắc có nguồn trong A(e).
6. **2.7** (`update.compare`): dựng lại toàn bộ ở mọi mốc rồi so tập quy tắc và tập cặp; chạy lại chế độ tăng dần khi bỏ từng quan hệ của N và khi bỏ cả N.

Ví dụ khớp: mốc 2026-01-01 (VBHN_125 chèn `BLLD_45-2019.D154.K8a`). T = {D154.K8a}; N có D151.K1.d (cạnh 1.5 `D154 → D151.K1.d`, khớp theo cây vì K8a thuộc D154) và D154 (cây). Quy tắc của D151.K1.d được biên dịch lại; chặn theo vị từ nên đầu của K8a (nếu trùng atom với các khoản khác của D154) không đổi dòng `blocked` của nó.

## 5. Vì sao
- Không có 2.5 thì mỗi văn bản mới phải trích lại cả KB (đắt) hoặc chỉ trích chính văn bản đó và bỏ sót quy tắc cũ phải đổi theo. Ví dụ: nghị định có ngoại lệ vào một Khoản của luật làm quy tắc của Khoản đó có thêm literal chặn dù chữ Khoản không đổi.
- Chế độ dựng lại toàn bộ là đối chứng: không có nó thì không biết A(e) có đủ không. Phép so có răng: trên test tổng hợp, bỏ `exception_of`, bỏ `cay` hay bỏ cả N đều làm 2.7 trượt.
- Biên dịch cả ảnh chụp rồi chỉ thay phần thuộc A(e) (thay vì chỉ biên dịch A(e)): 1.8 có bước toàn cục (gắn mục con vào tổ tiên, đầu chặn lấy từ cây con nguồn, bộ quét); biên dịch riêng một phần sẽ khác cách biên dịch của 1.8 và 2.7 không còn so đúng thứ.
- Cách khác đã cân nhắc: đặt tên vị từ lại từ đầu cho cả kho ở mỗi lần dựng lại (bị loại: khoá cache 1.6B phụ thuộc trạng thái sổ, mọi lượt cũ trượt cache và cùng chữ có thể đổi tên; A42 chốt (3)).

## 6. Kiểm và số đo
- Máy kiểm: 2.7 (thoát 1 khi trượt); `checks.py` kiểm R độc lập với kho phiên bản; `tests/test_update.py` (2.7 trượt khi bỏ quan hệ cần; KU theo câu dẫn; mốc hết thời hạn; hàm kiểm của `checks` bắt R hỏng).
- Số đo 19/11 trên tập con, tri thức mới có BLLĐ: xem A42, mục Kiểm chứng.
- Chưa kiểm: mọi số đo khi đã có tri thức của nghị định (chờ phiên LLM: 1.6A 390 KU, rồi 1.6B, 1.7, 1.9); hiệu ứng thật của quan hệ `concept` và `details` trên dữ liệu thật.
