# Kế hoạch sửa A1→A7 theo `review_a1_a7_findings.md`

Ngày lập: 2026-10-25. Gốc: commit `b82c925`. Mỗi bước ghi: finding, file/hàm phải đổi, test thêm, đầu ra nào được phép thay đổi.

## 0. Chuẩn bị (làm trước mọi bước)

| # | Việc | Ghi chú |
|---|---|---|
| 0.1 | Thống nhất interpreter **Python ≥ 3.10** (repo từng chạy 3.14; máy hiện chỉ có `python3` 3.9.6) | Ví dụ `brew install python@3.13`. Không hạ code xuống 3.9. |
| 0.2 | `.gitignore` cho `__pycache__/`, `git rm --cached src/__pycache__/*.pyc` | |
| 0.3 | Commit `review_a1_a7_findings.md` + file này | |
| 0.4 | Script `src/run_all.py`: chạy A1→A7 cho `blds2015_5dieu`, `blds2015_p4`, 8 văn bản dev (+ bộ ghép dev01+dev02), rồi 7 bộ test | Dùng làm **hồi quy**: sau mỗi bước, `git diff --stat data/ docs/` chỉ được đổi đúng các file liệt kê ở bước đó. |

## 1. Các câu hỏi cần bạn quyết (chặn Pha 2 và 3)

Đây là §6 của review. **Đã chốt 2026-10-25: Q1–Q4 theo đề xuất mặc định; A4 theo hướng C (LLM có kiểm), mô hình Claude Sonnet 5.5, ngân sách khoảng 500k đ/tháng.** Q5: BLDS 2015 chưa có văn bản sửa đổi nào nên không có cặp thật; bộ kiểm thử ngoài của A4 là văn bản **giả lập**, cách làm ở 3.2.

| Câu | Đề xuất mặc định | Ảnh hưởng nếu chọn khác |
|---|---|---|
| Q1 (F-06) "khử trùng lặp thực thể" | **(a)** đổi nhãn `duplicate` → `same_text`, coi `same_text_as` là bằng chứng trùng chữ | (b) tầng khái niệm: thêm hẳn một bước trích chủ thể/đối tượng, lớn hơn mọi bước còn lại cộng lại |
| Q2 phạm vi tổng quát hoá | **Chỉ BLDS 2015**; F-01, F-02, F-14, F-15, F-18 làm fail-closed + ghi giới hạn | "Văn bản nói chung" kéo theo Pha 3.3, 3.4 (đăng ký văn bản, văn phạm A4 mở rộng) |
| Q3 (F-07) cạnh cập nhật vào đồ thị gộp | **Có**: đưa vào A7 ở chế độ `--versions` | Giữ ở file A4: chỉ cần ghi giới hạn |
| Q4 (F-12) mâu thuẫn hình thức | **Thêm kiểm vòng tự động** (rẻ) và ghi rõ phạm vi | Chỉ ghi phạm vi |
| Q5 bộ kiểm thử ngoài | Bạn cung cấp một cặp (gốc, sửa đổi) thật, nguyên văn từ nguồn chính thức | Không có thì F-16, F-17 chỉ ghi là giới hạn |

## 2. Pha 1: đổi fail-open thành fail-closed (không phụ thuộc câu hỏi nào)

Kỳ vọng chung: p4 và 5dieu **không có** ca nào trong pha này (review §2), nên toàn bộ `data/processed` và `docs` phải **giữ nguyên byte**. Chỉ có test mới.

### 1.1 A4: chỉ thị bị động / "hết hiệu lực" bị bỏ qua êm (F-03), ưu tiên cao nhất
- `a4_versions.py`:
  - Thêm `RE_ACTION` (không phân biệt hoa thường): `bãi bỏ|hết hiệu lực|thay bằng|thay thế|sửa|bổ sung|(?<!\w)bỏ(?!\w)`, và `RE_STRUCT_REF`: `(?:Điều|khoản|điểm) \d+` (không phân biệt hoa thường).
  - `skip_reason`: sau hai nhánh tiêu đề, nếu dòng khớp **cả** `RE_ACTION` và `RE_STRUCT_REF` thì trả `None` (đẩy sang `E_UNKNOWN_LINE`). Nhánh `RE_WORDS` hiện tại giữ nguyên cho phần còn lại.
  - Kiểm cấp văn bản: `parse_amendment` ra 0 chỉ thị thì `A4Error("E_NO_DIRECTIVE", …)`.
  - Dòng ngày hiệu lực ("Luật này có hiệu lực thi hành từ ngày…") không có `Điều N` nên không bị bắt nhầm; vẫn phải xác nhận trên 8 văn bản dev.
- `test_a4.py`: 6 câu của F-03 → `E_UNKNOWN_LINE`; văn bản chỉ có dòng hiệu lực → `E_NO_DIRECTIVE`; một dòng chuyển tiếp không có tham chiếu cấu trúc vẫn bị bỏ qua.
- `docs/a4_quyet_dinh.txt`: thêm quyết định cho hai mã lỗi mới.

### 1.2 A2: dẫn chiếu ra ngoài, danh sách, khoảng, hậu tố (F-01, F-02)
- `a2_edges.py`, trong `find_refs` / `build_refs`, xét đoạn chữ ngay sau mỗi cụm:
  - **Ra ngoài:** khớp ` của (Luật|Bộ luật|Nghị định|Thông tư|Pháp lệnh) …` mà không phải "Bộ luật này", hoặc ` (Luật|Nghị định|Thông tư|Pháp lệnh) này` → không tạo cạnh, ghi vào `unresolved` với cột lý do `external` (để phân biệt với "Điều chưa nạp"). Đuôi "của <tên lạ>" không nhận dạng được → `ValueError`.
  - **Dừng (fail-closed):** cụm theo sau bởi ` đến (Điều|khoản|điểm)`, bởi `(, | và | hoặc )\d+` (danh sách số trần), hoặc từ khoá + `\d+[a-zđ]` (hậu tố "5a", "2a") → `ValueError` "chưa có quy tắc".
  - **Đã làm khác đi một chút:** không thêm cột lý do; dẫn chiếu ra ngoài ghi vào `unresolved` với đích `external:<tên văn bản>`, nên định dạng `a2_unresolved_*.txt` giữ nguyên. "<Luật|Nghị định> này" thì dừng (văn bản đang xử lý là Bộ luật), không coi là ra ngoài. Mặc định `build_refs` dừng khi có từ khoá + số ngoài mọi cụm; A4 gọi với `allow_uncovered=True` vì đã có mục "Chưa phủ".
- `test_a2.py`: 3 câu F-01 → `external`; 4 câu F-02 → `ValueError`; hai ca đang fail-closed giữ nguyên.

### 1.3 A6: mệnh đề ngoại lệ đứng đầu câu, trigger thiếu (F-04, F-05)
- `a6_general_exceptions.py`, `find_general`:
  - Nếu `GENERAL_RE` khớp ở **đầu đoạn** (đầu text hoặc ngay sau `\n`): mệnh đề kết thúc ở dấu phẩy đầu tiên; không có dấu phẩy → `ValueError`.
  - Thêm một lượt quét riêng của A6 cho `không được áp dụng` → `unhandled`. **Không** sửa `a2.TRIGGER_RE`, vì nó dùng chung với A3 và bảng trigger của A2 (đổi sẽ làm A3 coi đây là quy tắc `not_apply`).
- `test_a6.py`: 2 câu F-04 cho đúng mệnh đề `pháp luật có quy định khác` / `có thỏa thuận khác` (và cùng mã nút với nút có sẵn ở p4); câu "không được áp dụng" → unhandled.

## 3. Pha 2: lấp chỗ thiếu so với yêu cầu

Thứ tự theo độ lan: các bước ít ảnh hưởng trước, A1 sau cùng.

### 2.1 Kiểm vòng (F-12), theo Q4
- `a7_graph.py` `check_graph`: thêm `[7g]` không có vòng trong `refers_to ∪ exception_of` (DFS, không thêm phụ thuộc networkx). Báo cáo A7 thêm một dòng ĐẠT.
- `test_a7.py`: đồ thị dựng tay có vòng → không đạt.

### 2.2 Nút điều kiện: `kind`, ngoại lệ nối tới đơn vị (F-10, F-11)
- A6: nút điều kiện thêm thuộc tính `kind` ∈ {`tuy_nghi` ("có thỏa thuận khác"), `dan_chieu_mo` ("pháp luật/luật có quy định khác"), `cu_the`}. Bảng mẫu nằm trong code, cụm không khớp mẫu nào thì là `cu_the`.
- A6: mệnh đề có dẫn chiếu (dùng lại `a2.find_refs` + `a2.group_targets` trên mệnh đề) thì thêm cạnh `<đích> exception_of <đơn vị>` với method `general_except_ref`. Ở p4 sinh đúng 1 cạnh mới: `D652 exception_of D619`.
- A7: báo cáo thêm số thành phần liên thông **khi bỏ** nút `tuy_nghi`/`dan_chieu_mo` (p4: 38 → 41 theo đếm của review).
- Chưa làm: tách điều kiện / hệ quả (D646.K3) và phạm vi vế (D617.K1.a). Hai việc này cần gán tay, ghi vào `a6_a7_quyet_dinh.txt` là giới hạn.
- Đầu ra đổi: `a6_conditions_*`, `a6_exceptions_*`, `a7_*`; `EXPECTED` của A7 cho p4 thành 365 cạnh.

### 2.3 Metadata và ngày hiệu lực văn bản gốc (F-08)
- Bảng đăng ký văn bản gốc (đặt ở `a1_parse.py` cạnh `DOC_PREFIX`): `BLDS2015 = {so_hieu: "91/2015/QH13", ngay_ban_hanh: "2015-11-24", hieu_luc: "2017-01-01"}` (đã chốt 2026-10-25).
- A4: phiên bản 1 có `effective_from = hieu_luc`, `source_doc = "BLDS2015"`. Văn bản sửa đổi có ngày hiệu lực trước ngày đó → `E_DATE_BEFORE_BASE`.
- A5 `check_versions`, A7 `graph_at`: ngày trước hiệu lực gốc cho đồ thị rỗng (hoặc lỗi, cần chốt) thay vì cả bộ luật.
- Đầu ra đổi: mọi `a4_*_versions.jsonl`, snapshot, báo cáo A5.

### 2.4 Nút văn bản và cạnh cập nhật trong A7 (F-07, F-18), theo Q3
- A7 chế độ `--versions`: thêm nút `type = van_ban` cho văn bản gốc và cho từng văn bản sửa đổi đã áp dụng ≤ T (id = tên văn bản, giống `s` hiện tại của amend_edges; thuộc tính lấy từ bảng 2.3 hoặc null).
- Đọc `a4_<name>_amend_edges.jsonl`, thêm cạnh `amends|replaces|repeals` với `directive_seq`, `effective_from`, `new_version`. Đích đã bị đóng tại T (ví dụ khoản bị bãi bỏ) không còn là nút, nên cạnh mang status mới `historical`, và `[7b]` chấp nhận status này. `replace_doc` thành cạnh văn bản → văn bản.
- Chế độ gốc: chỉ thêm nút văn bản `BLDS2015`, và Điều nối tới nó qua `part_of` ở bước 2.5.
- `test_a7.py`: dev05 tại 2027-01-01 có 4 cạnh `repeals`; dev08 có cạnh văn bản → văn bản.
- `docs/a6_a7_quyet_dinh.txt`: quyết định về `historical`.

### 2.5 Phân cấp trên Điều (F-09), lan rộng nhất, làm cuối
- A1: `## Chương …` thành nút `chuong` (`BLDS2015.CXXII`); Điều thuộc chương gần nhất phía trên. 15 Điều đầu (609–623) đứng trước Chương XXII mà raw thiếu tiêu đề chương: **thêm `## Chương XXI – QUY ĐỊNH CHUNG` vào raw** ngay trên `### Điều 609`, trong cùng commit với bước này. Không thêm thì A5 phải cho phép "Điều không có chương", làm yếu kiểm tra `[2]`/`[7e]`. Dòng thêm làm lệch `source_line` của mọi dòng phía sau; test nào ghi cứng số dòng (ví dụ D643 dòng 301 của F-19) phải cập nhật. Dòng `#` là tiêu đề file, không phải đơn vị pháp lý: vẫn bỏ qua. Nếu bỏ hẳn bước 2.5 thì cũng **không** thêm dòng này.
- A2 `build_edges`: thêm `contains`/`part_of` cho chương ↔ Điều và văn bản ↔ chương.
- A5 `PARENT_TYPE`: thêm `dieu: chuong`; A7 `[7e]` tương ứng.
- A4: Điều mới chèn bằng "vào sau Điều m" thì thuộc chương của Điều m; không có "vào sau" → lỗi.
- Đầu ra đổi: gần như mọi file trong `data/processed`; cập nhật toàn bộ `EXPECTED` của A5, A7.

## 4. Pha 3: hướng đi và độ tin cậy

Cập nhật 2026-10-25 sau khi đối chiếu `DRAFT_Proposal_v5.docx` (đề cương luận văn, hướng neuro-symbolic). **Phạm vi hiện tại: chỉ dựng đồ thị tri thức (KG)**; các bước sau KG ở mục 4b chưa làm.

| # | Việc | Trạng thái |
|---|---|---|
| 3.1 | Đổi `duplicate` → `same_text` | Đã làm. Ghi chú: "khử trùng lặp thực thể" đúng nghĩa của đề cương nằm ở sổ khái niệm (mục 4b), không ở A7 |
| 3.2a | Khung đáp án gán tay: mẫu 11 Điều theo quy tắc, `src/eval_gold.py` tính precision/recall | Đã làm phần khung; **chờ học viên hỗ trợ gán** `data/gold/gold_blds2015_p4.tsv` (đề cương Tầng 2). Còn thiếu: cột loại ngoại lệ (phản bác / vô hiệu hoá) |
| 3.2b | Bộ kiểm thử ngoài cho A4: 19 câu chỉ thị nguyên văn của Luật 85/2025/QH15 (Công báo), chỉ đổi số hiệu / cụm từ / nội dung sang BLDS; `src/eval_ext_amend.py` | Đã làm. `--llm off`: 9 đường nhanh, 10 dừng có lỗi, 0 áp sai. Không thay được bộ sửa đổi giả định của học viên hỗ trợ (đề cương Nội dung 4) |
| 3.3 | ~~Mở rộng văn phạm A4 theo từng mẫu câu~~ → **thay bằng hướng C**: tầng chuẩn hoá khối bằng LLM (Claude Sonnet 5.5) có kiểm ký hiệu, `--llm off/replay/live` | Đã làm code và test (proposer/client giả). **Chưa chạy live**: cần API key; ước tính chi phí cho 10 ca cần LLM vài nghìn đồng. Thiết kế: `docs/a4_quyet_dinh.txt` mục I |
| 3.4 | Đăng ký văn bản thay hằng số theo tên file | Bỏ (Q2: chỉ BLDS 2015) |
| 3.5 | F-19, F-20, F-21 | Chỉ ghi lại là giới hạn |

### 4b. Khoảng trống so với đề cương (chưa làm, ngoài phạm vi KG hiện tại)

| Đề cương | Hiện trạng pipeline |
|---|---|
| Nội dung 1: mẫu câu tìm ứng viên quan hệ, **LLM phân loại** dẫn chiếu / ngoại lệ, ngoại lệ **phản bác / vô hiệu hoá** | Chỉ có mẫu câu (A2, A3, A6); chưa có bước phân loại |
| Nội dung 1: quan hệ ngầm (khoản 1 Điều 621 với Điều 626) do LLM đề xuất, bộ quét kiểm | Chưa có; F-05 ghi 29 đơn vị "Trường hợp …" chưa phân loại |
| Nội dung 1: sổ khái niệm (vị từ khái niệm pháp lý, vị từ đầu vào) và đồ thị khái niệm | Chưa có; đây là tầng khử trùng lặp thực thể (F-06 phương án b) |
| Nội dung 1: quy tắc gắn với điều khoản nguồn; chỉ trích lại điều có chữ thay đổi | Chưa có quy tắc; A4 đã có tập changed/new và tập ảnh hưởng để làm việc này |
| Nội dung 2: bộ quét trên **quy tắc** (không bao giờ kích hoạt, trùng, đứt, vòng chặn, cặp mâu thuẫn), LLM tự sửa tối đa 2 vòng, cô lập | A5/A7 mới quét ở mức đồ thị (trùng, đứt, vòng `exception_of`) |
| Nội dung 3: biên dịch sang s(CASP), hỏi đáp có giải thích | Chưa có |
| Nội dung 4: bộ tình huống có nhãn độ sâu ngoại lệ, cặp đối chứng, bộ sửa đổi giả định do học viên hỗ trợ soạn | Chưa có; `data/ext_amend/` có thể đưa học viên hỗ trợ làm mẫu cách viết |

## 5. Hoàn tất mỗi bước

1. Chạy `run_all.py`: 7 test 0 lỗi; `git diff --stat data/ docs/` chỉ có các file mà bước đó cho phép.
2. Cập nhật file `quyet_dinh` tương ứng.
3. Trong `review_a1_a7_findings.md`, thêm cột/ghi chú "Đã sửa ở commit …" cho finding liên quan; cập nhật bảng §1 khi một mục đổi mức.
4. Một commit cho mỗi bước (1.1, 1.2, …) để dễ đối chiếu và hoàn tác.
