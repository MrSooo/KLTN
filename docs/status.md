# Trạng thái dự án

Cập nhật lần cuối: 24/11/2026. Nhánh làm việc: `v3_refactor`.

## 1. Tóm tắt
Giai đoạn 1 (dựng KB gốc từ BLLĐ): các bước 1.1 đến 1.5 đã xong; 1.6B đến 1.9 đã có mã và chạy thông trên tập con `lldnn` (A41: `python -I src/run_all.py --tap-con lldnn --llm replay`); cả kho còn chờ chạy 1.6A đủ 204 lô. Giai đoạn 2 (cập nhật khi có văn bản mới): bước 2.2 đến 2.4 đã có mã cho kho hiện tại; 2.5 đến 2.7 có mã và chạy thông trên tập con với tri thức BLLĐ (A42), tri thức của nghị định chờ phiên LLM; 2.1 chưa làm. Thiết kế từng bước: `docs/design/pipeline_design.md`. Kế hoạch tiếp theo: `docs/roadmap.md`.

Kiểm ngày 15/11/2026 (sau khi chuẩn hoá tên và xoá thư mục lưu trữ v1): `python -I src/run_all.py --llm off --viewer --tests` rồi `--llm replay --viewer --tests`, cả hai thoát mã 0, 14/14 bước, 10 bộ test OK. Chương trình không in tổng số test. Đầu ra dữ liệu giống hệt trước khi đổi tên, trừ các nhãn chữ (xem `docs/decisions.md`, A40).

## 2. Bảng trạng thái theo bước
| Bước | Module | Trạng thái | Ghi chú |
|---|---|---|---|
| 1.1 Parse | `parse.py` | xong | 18 văn bản, 10.202 đơn vị, 893 Điều; lỗi đã biết: đoạn không ký hiệu giữa hai điểm bị gắn vào khoản cha (`D36.K1`, `D174.K1`) |
| 1.2 Dẫn chiếu | `refs.py` | xong | 2.348 `refers_to`, 129 chờ đích, 127 không giải được (BLLĐ: 0); chưa nhận dạng dẫn chiếu tới Chương, Mục (BLLĐ 1 ca, `D3.K1`) |
| 1.3 Điều khoản giao | `delegation.py` | xong | BLLĐ: 51 ca chắc, 5 ca lỏng cờ `loose` |
| 1.4 Loại Điều | `article_type.py` | xong | không dùng LLM |
| 1.5 Ngoại lệ tường minh | `exceptions_explicit.py`, `exceptions_general.py` | xong | đã mở rộng sang "trừ <danh từ>" (A31); chưa đo độ chính xác |
| 1.6A Mệnh đề | `propositions.py` | **đang làm** | lời nhắc `menh-de-3` đóng băng; đường A39 chưa chạy đủ 204 lô; chưa nối vào `run_all` (xem mục 3). Lần chạy riêng ckey (DeepSeek, `menh-de-4`, A46) đã chạy đủ 204 lô. A54 (21/11): luật sửa lỗi không xoay vòng (bộ khó 19 lô `data/eval_dev/proposition_panel.json`, chấm mọi loại lỗi A1-A4 cùng lúc); phủ định kép do máy sửa (`effective_cuc`); đã đo nhiễu (ba lần) |
| 1.6A (bản cũ) | `concepts.py` | còn trong `run_all` | kết quả không dùng được; `concepts_names.py` và `propositions.py` còn mượn hàm của nó |
| 1.6B Sổ vị từ | `predicates.py` (bản cũ `concepts_names.py` còn trong `run_all`) | xong trên tập con | `names-2.1`, có vị từ chủ thể (A41) |
| 1.7 Ngoại lệ ngầm | `implicit_exceptions.py` | xong trên tập con | `ngoai-le-ngam-2`; tập con 4 cặp, 1 cạnh (A41) |
| 1.8 Quy tắc | `rules.py` | xong trên tập con, chưa có vòng LLM sửa | máy biên dịch; s(CASP); test phản chứng D151/D154 (A41) |
| 1.9 Hỏi đáp | `answering.py` | xong trên tập con | bộ câu hỏi dev `data/eval_dev/lldnn_questions.json` (nháp, chờ xác nhận); 11/15 câu cần 2.6 (A41) |
| Web demo hỏi đáp | `utils/demo/qa_server.py` | chạy trên tập con | A45: câu kết luận do máy viết, diễn giải LLM `tra-loi-1` qua cổng; LLM tạm là `claude -p`; chạy thật 2 câu (tổng 6 đến 18 giây); A48: giao diện chat, cây chứng minh và dữ kiện chỉ ghi `demo_log.jsonl` |
| Bộ chạy hộp cát qua API | `sandbox_api.py`, nhà cung cấp `ckey` của `llm_client.py` | đã chạy thật (20/11) | A46: `deepseek-v4.1-flash`, lần chạy riêng `--llm-run ckey`: KB cả BLLĐ (1.6A `menh-de-4`, 1.6B, 1.7, 1.8; 1.142 quy tắc, replay 18/18) và cả chuỗi tập con `lldnn`; ba lần sửa lời nhắc chỉ trên tập con: ckey2 `menh-de-5` (A50), ckey3 `-6` (A51), ckey4 `-7` (A52); hỏi đáp dev 3/15, 3/15, 6/15, ckey4 không có (2.7 trượt). Báo cáo `docs/run_reports_ckey/ckey_kb_report.md`, log ở `run_logs/` của từng thư mục báo cáo, script đo ở `utils/llm_runs/`, thư mục làm việc hộp cát ở `data/sandbox_runs/` (A53) |
| 2.2 Nối văn bản | `links.py` | xong cho kho hiện tại | có LLM (Gemini, hai model độc lập kiểm chéo) |
| 2.3 Đọc chỉ thị | `directives.py`, `directives_rare.py` | xong cho kho hiện tại | 26 loại, bảng ở `docs/reference/directive_types.md` |
| 2.4 Áp phiên bản | `versions.py` | xong cho kho hiện tại | 9.217 đơn vị, 9.343 phiên bản (đo 09/11) |
| 2.5 Tập ảnh hưởng | `affected.py` | có mã | N một bước qua 6 quan hệ (A42) |
| 2.6 Trích lại theo A(e) | `update.py`, `predicate_registry.py`, `knowledge_units.py` | chạy trên phần lõi của tập con | 44 KU lõi đã có 1.6A, 1.6B; 346 KU khác chưa (chủ đề tài: không chạy cả nghị định; lần chạy riêng ckey, ckey2 đến ckey4 đã chạy đủ 390 KU, A46-A52); 1.9: 11/15, 11/11 trong phạm vi, trên bộ dev đã dùng để sửa lời nhắc (A42-A44) |
| 2.7 Đối chứng | `update.py` | đạt trên tập con (mặc định, ckey, ckey2, ckey3); **trượt ở ckey4** | gồm tri thức nghị định lõi và mốc ND 70 sửa ND 152; bỏ quan hệ concept thì trượt. ckey4: lỗ hổng A42 × A43 (đầu chặn dạng tương đương xuất hiện ở mốc sau, D151.K1.d không vào A(e)), chờ quyết (A52) |
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
17. **Tập ảnh hưởng A42 không thấy phụ thuộc toàn cục của `BLOCK_ALIAS` (A43)** (A52): khi một mốc sau có quy tắc kết luận dạng tương đương của một đầu chặn cũ, quy tắc bị chặn ở văn bản khác không vào A(e); 2.7 trượt ở ckey4. Chưa sửa.
18. **`update.py xuat-1-6a` cần sổ vị từ của 1.6B gốc** (A51): không chạy riêng 1.6A cập nhật được.
19. **Sửa lỗi 1.6A (A54-A57), việc kế tiếp:** A56 (`menh-de-10` cắt chữ, `-11` thêm luật "mỗi dòng một việc") không giảm gộp ý; A57 refactor khuôn đầu ra (`menh-de-12`: LLM ghi khoảng 10 trường, máy dựng phần còn lại qua `propositions.check_unit`; lô tối đa 8 đơn vị). Kết quả Gemini (`gflash`) trên bộ khó, hai lần mỗi bản: hết lỗi do LLM tự ghi `trich`/`nguon`, bắt được 4-9 dòng mỗi lần bỏ mất "không" hay một vế "hoặc" (nay là lỗi cổng), nhưng mệnh đề dài và gộp liên từ KHÔNG giảm rõ. Chưa quyết bước tiếp (lượt hỏi lại dòng có liên từ; máy cắt chữ dẫn chiếu khỏi `doan`); chưa chạy tập con. Model: Gemini flash qua ckey rẻ hơn DeepSeek khoảng 10 lần, ngang chất lượng trên `-9`. Thư mục làm việc và log ở `data/sandbox_runs/bo_kho/`. A58 (lượt rút gọn dòng dài) chỉ tách được một phần danh sách. **A59 (22/11): đổi cách tiếp cận**, 1.6A-v2: máy cắt câu, lượt 1 LLM chỉ gạch ranh giới mệnh đề (có đoạn dùng chung), lượt 2 gán vai/cây AND/OR, máy dựng lại khuôn cũ. Thử khả thi lượt 1 trên 6 câu khó: máy kiểm qua 6/6, gộp ý giảm rõ, nhưng 2/5 câu mới sai ranh giới (mệnh đề "để"; động từ trong danh sách căn cứ), chưa đạt ngưỡng đặt trước. Chạy dò lượt 1 một lần trên cả BLLĐ (23/11, `data/sandbox_runs/seg_thu_3/gom_loi.md`): 993/993 câu (9 câu lúc đầu thiếu do tuyến model ckey báo không có, gọi lại ngày 23/11 thì được), máy kiểm qua 985, khoảng 6.450 VND; danh sách động từ tách đều; lỗi còn lại là chữ nối/chữ đánh dấu và thiếu tách điều kiện, ngoại lệ trong câu dài. E4 (bổ ngữ "đối với") user chốt 24/11: lượt 1 không tách, lượt 2 đánh span (A59). Đặc tả lượt 1 chốt 24/11 (A60, `docs/design/step_1_6a_propositions.md` mục 9). Bước 0 và máy kiểm đã có mã và test (`src/segments.py`, `tests/test_segments.py`), chưa nối vào `run_all`. Gold 60 câu (`data/eval_dev/segment_gold_{dev,test}.json`) user duyệt 24/11, quy ước ở đặc tả mục 9.3; việc kế: lời nhắc lượt 1, chạy 40 câu phát triển.

## 5. Việc treo (không chặn)
- Văn bản ngoài kho: NĐ 38/2022, NĐ 35/2022, TT 54/2015, BLLĐ 2012, NĐ 189/2025, Luật 64/2025.
- Luật sửa đổi BLLĐ đang ở kỳ họp Quốc hội; khi được thông qua có thể thêm vào làm lần cập nhật chưa thấy.
- Ngày ký TT 09/2020 và TT 10/2020 (manifest ghi dấu "?").
- Nhóm văn bản dùng để đo nằm ngoài repo và chưa được mở; chỉ mở khi bắt đầu giai đoạn đo.
