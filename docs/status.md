# Trạng thái dự án

Cập nhật lần cuối: 18/11/2026. Nhánh làm việc: `v3_refactor`.

## 1. Tóm tắt
Giai đoạn 1 (dựng KB gốc từ BLLĐ): các bước 1.1 đến 1.5 đã xong; 1.6B đến 1.9 đã có mã và chạy thông trên tập con `lldnn` (A41: `python -I src/run_all.py --tap-con lldnn --llm replay`); cả kho còn chờ chạy 1.6A đủ 204 lô. Giai đoạn 2 (cập nhật khi có văn bản mới): bước 2.2 đến 2.4 đã có mã cho kho hiện tại; 2.1 và 2.5 đến 2.7 chưa làm. Thiết kế từng bước: `docs/design/pipeline_design.md`. Kế hoạch tiếp theo: `docs/roadmap.md`.

Kiểm ngày 15/11/2026 (sau khi chuẩn hoá tên và xoá thư mục lưu trữ v1): `python -I src/run_all.py --llm off --viewer --tests` rồi `--llm replay --viewer --tests`, cả hai thoát mã 0, 14/14 bước, 10 bộ test OK. Chương trình không in tổng số test. Đầu ra dữ liệu giống hệt trước khi đổi tên, trừ các nhãn chữ (xem `docs/decisions.md`, A40).

## 2. Bảng trạng thái theo bước
| Bước | Module | Trạng thái | Ghi chú |
|---|---|---|---|
| 1.1 Parse | `parse.py` | xong | 18 văn bản, 10.202 đơn vị, 893 Điều; lỗi đã biết: đoạn không ký hiệu giữa hai điểm bị gắn vào khoản cha (`D36.K1`, `D174.K1`) |
| 1.2 Dẫn chiếu | `refs.py` | xong | 2.348 `refers_to`, 129 chờ đích, 127 không giải được (BLLĐ: 0); chưa nhận dạng dẫn chiếu tới Chương, Mục (BLLĐ 1 ca, `D3.K1`) |
| 1.3 Điều khoản giao | `delegation.py` | xong | BLLĐ: 51 ca chắc, 5 ca lỏng cờ `loose` |
| 1.4 Loại Điều | `article_type.py` | xong | không dùng LLM |
| 1.5 Ngoại lệ tường minh | `exceptions_explicit.py`, `exceptions_general.py` | xong | đã mở rộng sang "trừ <danh từ>" (A31); chưa đo độ chính xác |
| 1.6A Mệnh đề | `propositions.py` | **đang làm** | lời nhắc `menh-de-3` đóng băng; chưa chạy đủ 204 lô; chưa nối vào `run_all` (xem mục 3) |
| 1.6A (bản cũ) | `concepts.py` | còn trong `run_all` | kết quả không dùng được; `concepts_names.py` và `propositions.py` còn mượn hàm của nó |
| 1.6B Sổ vị từ | `predicates.py` (bản cũ `concepts_names.py` còn trong `run_all`) | xong trên tập con | `names-2.1`, có vị từ chủ thể (A41) |
| 1.7 Ngoại lệ ngầm | `implicit_exceptions.py` | xong trên tập con | `ngoai-le-ngam-2`; tập con 4 cặp, 1 cạnh (A41) |
| 1.8 Quy tắc | `rules.py` | xong trên tập con, chưa có vòng LLM sửa | máy biên dịch; s(CASP); test phản chứng D151/D154 (A41) |
| 1.9 Hỏi đáp | `answering.py` | xong trên tập con | bộ câu hỏi dev `data/eval_dev/lldnn_questions.json` (nháp, chờ xác nhận); 11/15 câu cần 2.6 (A41) |
| 2.2 Nối văn bản | `links.py` | xong cho kho hiện tại | có LLM (Gemini, hai model độc lập kiểm chéo) |
| 2.3 Đọc chỉ thị | `directives.py`, `directives_rare.py` | xong cho kho hiện tại | 26 loại, bảng ở `docs/reference/directive_types.md` |
| 2.4 Áp phiên bản | `versions.py` | xong cho kho hiện tại | 9.217 đơn vị, 9.343 phiên bản (đo 09/11) |
| checks, graph, viewer | `checks.py`, `graph.py`, `utils/viewer/` | xong | đồ thị 9.364 nút, 2.721 cạnh |

## 3. Việc đang dở: chạy 204 lô của bước 1.6A
- Đường chạy đã chốt (A39): phiên Claude Code, Sonnet 5.5, effort `high`, khối tối đa 20 lô mỗi subagent, song song tối đa 4, lời nhắc `menh-de-3`.
- Thư mục làm việc cũ `bo_menh_de_v3` nằm trên máy của người khởi tạo, ngoài repo (9/204 lô đã làm, chưa nhập vào `data/llm_cache/propositions/`). Có thể làm lại từ đầu và dựng lại bằng `python -X utf8 -I src/propositions.py xuat <thư mục mới> claude-sonnet-5-5 high --tat-ca`. Không cần mang thư mục cũ theo.
- Luật dừng: sau 3 khối đầu (60 lô), dừng và báo nếu có câu dẫn lọt thành `menh_de` hoặc lỗi cổng còn lại vượt 5% số dòng.
- Quy trình vận hành: `docs/operations/llm_sandbox.md`.
- Người thực hiện: chưa phân công (điền vào đây khi nhận việc).

## 4. Nợ kỹ thuật
1. **Bước 1.2, tầng 2:** xác định đích duy nhất cho 13 ca khoản/điểm trơ trụi (đều ở văn bản dưới luật); BLLĐ có 0 ca.
2. **Bước 1.3:** 5 ca lỏng chưa ai xác nhận (đọc thủ công: 4 thật, `D133.K1` nghi không). Không chặn.
3. **`checks.py`:** chưa rà toàn bộ theo thiết kế mới (tầng lỏng của 1.3, 1.4 không LLM, khuôn cạnh chung).
4. **Văn bản mới (manifest):** cần khai `file`, `nhom`, `so_hieu`, `loai`, `ngay_hieu_luc` (nên có `ngay_ban_hanh`). Cột `so_dieu_dem_duoc` nên tuỳ chọn nhưng mã hiện còn đòi.
5. **Bước 1.5 chung:** nút điều kiện dài do mệnh đề chạy "đến hết đoạn" (ví dụ `ND_28-2020.D11.K1` 724 ký tự); đo độ chính xác phần mở rộng "trừ <danh từ>" trên mẫu đọc tay.
6. **Cổng phần dư của `refs.py`** hiện chỉ ghi báo cáo (đo: 0 sót); khi nạp văn bản mới nên quyết có thành lỗi dừng không.
7. **Cạnh của bước 2.3-2.4** (`version_edges.jsonl`) chưa theo khuôn cạnh chung (A12).
8. **`narrower_than`** (quan hệ hẹp hơn giữa vị từ gần nghĩa): hoãn, làm sau khi chạy một vòng KB đầy đủ (A32).
9. **Kiểm dữ kiện thô:** phần máy làm được chuyển sang bộ quét của bước 1.8 (vị từ là kết luận của một quy tắc thì không được là `input`; mỗi `input` phải được ít nhất một quy tắc dùng).
10. **Mã gọi API của vai `trich`** (`llm_client.py`, `concepts.py`) còn nhưng không dùng (A36); cần quyết giữ hay bỏ.
11. **Cache cũ:** đã xoá ngày 16/11/2026 các thư mục `data/llm_cache/concepts_names/` (hỏng theo A37 và A38) và `data/llm_cache/propositions/` (thí điểm Gemini), cùng 414 bản ghi cũ của `data/llm_cache/concepts_spans/` (Sonnet, Haiku, Gemini, `concepts-1`); giữ 204 bản ghi `concepts-2` (Opus 5.5) mà `replay` đọc. Đầu ra và báo cáo của bước 1.6A sau khi xoá giống hệt trước.
12. **Phụ lục I.7 của NQ 66.16:** Điều 21-23 của ND_145 chưa thấy trong I.7 nên chưa nối cạnh `overrides`.
13. **s(CASP) trên máy mới:** kiểm `swipl --version` và `library(scasp)` nạp được (A7), cần từ bước 1.8.
14. **Mục 3.5 của `docs/reference/method.md`** còn mô tả "model khác trích lại để kiểm" mà hệ thống không làm (A25); bài báo cáo cần đổi chữ.
15. **Model ghi trong bài báo cáo:** bước 1.6 dùng phiên Claude Code (Opus 5.5 cho bản cũ, Sonnet 5.5 cho bản mới), khác chốt ban đầu "model nhẹ, miễn phí" ở `docs/llm_config.md`; cần ghi lý do.
16. **Lời nhắc 1.6A `menh-de-3` thiếu tên khoá `bo_ngu`** (`original_text`, `scope`): đang vá bằng bí danh khoá trong `propositions.normalize` (A41); thêm vào chữ lời nhắc khi chạy cả kho bằng API.

## 5. Việc treo (không chặn)
- Văn bản ngoài kho: NĐ 38/2022, NĐ 35/2022, TT 54/2015, BLLĐ 2012, NĐ 189/2025, Luật 64/2025.
- Luật sửa đổi BLLĐ đang ở kỳ họp Quốc hội; khi được thông qua có thể thêm vào làm lần cập nhật chưa thấy.
- Ngày ký TT 09/2020 và TT 10/2020 (manifest ghi dấu "?").
- Nhóm văn bản dùng để đo nằm ngoài repo và chưa được mở; chỉ mở khi bắt đầu giai đoạn đo.
