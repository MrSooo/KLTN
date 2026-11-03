# Tổng hợp công việc đã làm: xây dựng đồ thị tri thức cho phần Thừa kế, Bộ luật Dân sự 2015

Cập nhật: 26/10/2026. Nhánh code: `sua-theo-review`, chưa gộp vào `main`.

**Muốn xem phần kỹ thuật:** mục 4 (từng bước A1 đến A8: vào/ra, thuật toán, tự kiểm, ví dụ thật), mục 6.3 (từng Pha sửa lỗi: sửa ở hàm nào, cơ chế gì, test nào), mục 7 (tầng LLM), mục 8 (kiểm thử và `run_all.py`).

---

## 0. Đọc nhanh trong 1 phút

- **Đề tài** (theo `DRAFT_Proposal_v5.docx`): hệ hỏi đáp pháp luật tiếng Việt kết hợp LLM với suy luận ký hiệu. LLM chỉ lo phần hiểu ngôn ngữ, còn việc suy ra kết luận do bộ giải logic s(CASP) làm. Hệ cần trả lời đúng cả khi luật có **ngoại lệ lồng nhau**.
- **Phần đã làm**: bước nền móng, tức **tự động xây đồ thị tri thức (KG)** từ văn bản luật. Đồ thị lưu từng Điều, Khoản, Điểm và các liên kết giữa chúng: chứa nhau, dẫn chiếu nhau, là ngoại lệ của nhau, bị văn bản nào sửa. Đồ thị cập nhật được khi có văn bản sửa đổi, và tự kiểm tra lỗi.
- **Dữ liệu thử**: Bộ luật Dân sự 2015, phần Thừa kế, Điều 609 đến Điều 662.
- **Kết quả**: đồ thị có **225 nút và 481 cạnh**, qua đủ 7 nhóm kiểm tra tự động. Có **281 test**, tất cả đều đạt.
- **Ngoài phần xây đồ thị**, project đã có thêm:
  - một đợt **tự rà soát** (review), tìm ra 22 vấn đề và sửa phần lớn;
  - một **tầng dùng LLM** để đọc các câu sửa đổi phức tạp, đã code và test xong nhưng **chưa chạy với API thật**;
  - một **trang xem đồ thị** (bước A8): file HTML mở offline, các nút tròn nối bằng cạnh thẳng, kéo thả, tìm kiếm, bật tắt từng loại cạnh. Các file của A8 mới làm, **chưa commit**.
- **Chưa làm** (các bước sau KG trong đề cương): LLM phân loại quan hệ, sổ khái niệm, trích quy tắc, suy luận s(CASP), bộ tình huống đánh giá.

---

## 1. Bức tranh tổng thể: project nằm ở đâu trong đề cương

Đề cương có 5 nội dung. Project hiện làm phần **xây đồ thị** của Nội dung 1 và phần **kiểm tra ở mức đồ thị** của Nội dung 2.

| Nội dung trong đề cương | Đã làm gì |
|---|---|
| 1. Xây cơ sở tri thức dạng đồ thị, quản lý liên kết | **Phần lớn phần đồ thị**: tách văn bản, mã định danh, liên kết cấu trúc, dẫn chiếu, ngoại lệ tường minh, phiên bản khi sửa đổi. Chưa có: LLM phân loại quan hệ, sổ khái niệm, trích quy tắc |
| 2. Kiểm tra đồ thị, kiểm soát chồng chéo | **Phần kiểm ở mức đồ thị**: trùng lặp, liên kết bị đứt, vòng ngoại lệ, cấu trúc cha con. Chưa có: kiểm ở mức quy tắc, LLM tự sửa |
| 3. Suy luận s(CASP), hỏi đáp có giải thích | Chưa làm |
| 4. Bộ dữ liệu đánh giá | Mới có khung để chấm điểm, cộng một bộ câu sửa đổi thật để thử phần cập nhật. Chưa có bộ tình huống |
| 5. Thực nghiệm | Chưa làm |

Có thể hình dung thế này: đồ thị là "bộ nhớ có cấu trúc" của hệ thống. Các bước sau (trích quy tắc, suy luận, hỏi đáp) đều đọc từ bộ nhớ này, nên nó phải đúng và kiểm được.

---

## 2. Vài khái niệm cần nắm trước

**Điều, Khoản, Điểm.** Văn bản luật chia theo cấp: Điều chứa các Khoản (1, 2, 3...), Khoản chứa các Điểm (a, b, c...). Phía trên Điều còn có Chương.

**Mã định danh.** Mỗi đơn vị có một mã cố định, ghép từ số hiệu:
- `BLDS2015.D621` là Điều 621;
- `BLDS2015.D621.K1` là khoản 1 Điều 621;
- `BLDS2015.D621.K1.a` là điểm a khoản 1 Điều 621;
- `BLDS2015.CXXII` là Chương XXII.

Chữ "đ" trong mã viết thành "dd", ví dụ `...K1.dd`.

**Đồ thị tri thức.** Gồm **nút** (các đơn vị luật) và **cạnh** (quan hệ giữa hai nút). Mỗi cạnh lưu dưới dạng **bộ ba** *(nguồn, quan hệ, đích)*. Ví dụ `(D621.K1, part_of, D621)` nghĩa là "khoản 1 thuộc Điều 621".

**Các loại cạnh trong project:**

| Cạnh | Nghĩa | Sinh ở bước |
|---|---|---|
| `contains` / `part_of` | A chứa B / B thuộc A (cấu trúc) | A2, A7 |
| `refers_to` | A dẫn chiếu tới B ("theo quy định tại Điều 652") | A2 |
| `exception_of` | A là ngoại lệ của B (A đúng thì B không được áp dụng) | A3, A6 |
| `same_text_as` | Hai đơn vị có chữ giống hệt nhau | A7 |
| `amends` / `replaces` / `repeals` | Văn bản X sửa đổi / thay thế / bãi bỏ đơn vị Y | A4, A7 |

**Nút điều kiện.** Câu "..., trừ trường hợp có thỏa thuận khác" có phần ngoại lệ là một *điều kiện*, chứ không phải một Khoản. Project tạo một nút riêng cho điều kiện đó (gọi là nút điều kiện), rồi nối nó vào quy tắc bị ngoại trừ.

**Phiên bản.** Khi một Khoản bị sửa, bản cũ không bị xoá. Bản cũ được ghi ngày hết hiệu lực, và một bản mới (phiên bản 2) được tạo. Nhờ vậy xem được luật **tại bất kỳ ngày nào**.

**Fail-closed và fail-open.** Đây là khái niệm quan trọng nhất trong đợt rà soát.
- *Fail-closed* (dừng và báo): gặp chỗ không hiểu thì dừng lại, báo lỗi rõ ràng. Chấp nhận được.
- *Fail-open* (im lặng làm sai): chạy xong, không báo gì, nhưng kết quả sai hoặc thiếu. **Nguy hiểm**, vì người dùng tin kết quả.

Nguyên tắc của project: **thà dừng còn hơn làm sai mà không biết.**

**Regex.** Mẫu tìm chữ, ví dụ mẫu "trừ trường hợp + phần còn lại của câu". Các bước A1 đến A7 chủ yếu dùng regex. Ưu điểm là chạy đúng y hệt nhau mỗi lần và kiểm được; nhược điểm là chỉ hiểu những mẫu đã viết sẵn.

**LLM.** Mô hình ngôn ngữ lớn, ở đây là Claude. Dùng cho chỗ cần hiểu câu chữ linh hoạt. Trong project, LLM chỉ được **đề xuất**; mọi đề xuất đều bị máy kiểm lại trước khi dùng.

---

## 3. Dữ liệu đầu vào

| File | Nội dung |
|---|---|
| `data/raw/blds2015_p4.md` | Phần Thừa kế BLDS 2015, Điều 609 đến 662, dạng Markdown. Gồm 4 Chương (XXI đến XXIV), 54 Điều, 115 Khoản, 46 Điểm |
| `data/sample/blds2015_5dieu.md` | Bản thu nhỏ 5 Điều (621, 626, 644, 650, 651), dùng để thử nhanh |
| `data/dev_amend/dev01…dev08.md` | 8 văn bản sửa đổi **tự soạn** để thử phần cập nhật (vì BLDS 2015 chưa có văn bản sửa đổi thật) |
| `data/ext_amend/` | 19 câu sửa đổi **thật**, lấy nguyên văn từ Luật 85/2025/QH15 (Công báo), đổi số hiệu sang BLDS. Dùng để thử phần cập nhật trên câu chữ thật |

8 văn bản dev thử 8 kiểu sửa đổi khác nhau:

| File | Kiểu sửa |
|---|---|
| dev01 | Bãi bỏ khoản 2 Điều 621 |
| dev02 | Sửa khoản 1 Điều 621 (hiệu lực 01/7/2027) |
| dev03 | Thay toàn bộ Điều 626 (có khoản bị bỏ, có khoản mới 2a) |
| dev04 | Bổ sung Điều 621a, khoản 3 Điều 621, điểm đ khoản 1 Điều 650 |
| dev05 | Bãi bỏ cùng lúc nhiều đơn vị (khoản 2 Điều 621, điểm a khoản 1 Điều 650, Điều 626, Điều 651) |
| dev06 | Sửa, bỏ, thêm **cụm từ** bên trong câu |
| dev07 | Đổi tên Điều 621 và Điều 626 |
| dev08 | Thay thế cả Bộ luật |

Trừ dev02, các văn bản đều có hiệu lực từ 01/01/2027.

---

## 4. Quy trình 7 bước (A1 đến A7) và trang xem đồ thị (A8)

Mục này là phần **kỹ thuật**: mỗi bước đọc gì, làm thế nào, tự kiểm gì, dừng khi nào. Số liệu lấy từ lần chạy trên `blds2015_p4` (Điều 609 đến 662) và đã đối chiếu với file trong `data/processed/`. Mỗi bước theo cùng một khuôn: **Vào/ra**, **Cách làm**, **Ví dụ thật**, **Tự kiểm**, **Kết quả**, **Giới hạn**.

```
văn bản luật (.md)
   │
   A1  tách thành Chương / Điều / Khoản / Điểm, gán mã ───► a1_triples
   │
   A2  cạnh cấu trúc (chứa / thuộc) + cạnh dẫn chiếu ──────► a2_edges, a2_refs
   │
   A3  ngoại lệ tường minh (2 mẫu câu) ────────────────────► a3_exceptions
   │
   A6  ngoại lệ chung "trừ trường hợp ..." ─────────────────► a6_conditions, a6_exceptions
   │
   A5  kiểm tra độc lập các file trên (trùng, cha con, phiên bản)
   │
   A7  gộp tất cả thành MỘT đồ thị + 7 nhóm kiểm ──────────► a7_..._nodes, a7_..._edges
   │
   A8  vẽ đồ thị thành một trang HTML tương tác ────────────► a8_....html

   A4  (khi có văn bản sửa đổi) tạo phiên bản mới, cập nhật cạnh ─► a4_..._versions, edge_changes
       rồi A7 dựng lại đồ thị TẠI MỘT NGÀY bất kỳ (A7 đọc kết quả của A4)
```

Tên bước không trùng thứ tự chạy. Thứ tự thật trong `src/run_all.py` (mỗi bước chạy cho cả hai nguồn) là A1, A2 (cấu trúc), A2 (`--refers-to`), A3, A6, A5, A7, A8; sau đó A4 chạy riêng cho từng văn bản sửa đổi.

### 4.0 Nguyên tắc chung của mọi bước

1. **Chỉ dùng thư viện chuẩn của Python** (regex, json, hashlib...). Ngoại lệ duy nhất là chế độ `--llm live` của A4, cần gói `anthropic`.
2. **Chạy bằng `python -I src/<file>.py <đường dẫn md>`.** Cờ `-I` (isolated) để Python không nhặt module lạ trong thư mục hiện tại. Tên file kết quả suy từ tên file md (ví dụ `blds2015_p4`), nên hai nguồn không ghi đè nhau.
3. **Chỉ ghi khi sạch.** Mỗi bước chạy hàm kiểm trước. Có lỗi thì in ra stderr, thoát mã 1 và **không ghi file dữ liệu**. A4 và A7 vẫn ghi file báo cáo lỗi để đọc.
4. **Mỗi cạnh mang bằng chứng.** Cạnh có `evidence` (đoạn nguyên văn của luật) và `method` (quy tắc đã sinh ra nó). Bước kiểm xác nhận `evidence` nằm đúng trong text của đơn vị nguồn, nên có thể truy từ cạnh về câu gốc.
5. **Chưa có quy tắc thì dừng, không đoán** (`ValueError`, hoặc `A4Error` kèm mã lỗi). Chỗ spec chưa nói được ghi vào `docs/a4_quyet_dinh.txt`, `docs/a6_a7_quyet_dinh.txt`, `utils/a8/a8_quyet_dinh.txt`.
6. **Dữ liệu trung gian là JSON Lines**: mỗi dòng một JSON, UTF-8, xuống dòng LF, không BOM. Nhờ vậy `git diff` đọc được và so hai lần chạy được.

### 4.1 Các file dữ liệu và định dạng

| File trong `data/processed/<bước>/` | Do bước | Mỗi dòng là | Ví dụ thật |
|---|---|---|---|
| `a1_triples_<stem>.jsonl` | A1 | một bộ ba `{s, p, o}`. `p` là type, number, heading, chuong, text, version, source_line | `{"s":"BLDS2015.CXXI","p":"type","o":"chuong"}` |
| `a2_edges_<stem>.jsonl` | A2 | cạnh cấu trúc `{s, p, o, evidence}`, `evidence` luôn rỗng | `{"s":"BLDS2015.D609","p":"part_of","o":"BLDS2015.CXXI","evidence":""}` |
| `a2_refs_<stem>.jsonl` | A2 | cạnh dẫn chiếu `{s, p, o, evidence}` | `D616.K3` `refers_to` `D616.K1`, evidence `khoản 1 và khoản 2 Điều này` |
| `a3_exceptions_<stem>.jsonl` | A3 | cạnh ngoại lệ `{s, p, o, evidence, method}` | `D632.K1` `exception_of` `D632`, method `except_list_pattern` |
| `a6_conditions_<stem>.jsonl` | A6 | bộ ba của nút điều kiện (type, text, kind), 3 dòng mỗi nút | `{"s":"BLDS2015.C_426b8c79","p":"text","o":"có thỏa thuận khác"}` |
| `a6_exceptions_<stem>.jsonl` | A6 | như A3, `method` là `general_except_pattern` hoặc `general_except_ref` | `C_426b8c79` `exception_of` `D615.K1` |
| `a4_<name>_versions.jsonl` | A4 | một phiên bản của một đơn vị: id, version, type, number, heading, text, effective_from, effective_to, previous_version, source_doc, directive_seq | `D621.K1`, version 2, từ `2027-07-01`, source_doc `dev02_sua_khoan` |
| `a4_<name>_edge_changes.jsonl` | A4 | thay đổi cạnh `{op, s, p, o, at}` (+ evidence, method), `op` là add hoặc close | |
| `a4_<name>_amend_edges.jsonl` | A4 | cạnh từ văn bản sửa đổi tới đơn vị | `{"s":"dev05_bai_bo_ds","p":"repeals","o":"BLDS2015.D626","directive_seq":3,"effective_from":"2027-01-01","new_version":null}` |
| `a4_<name>_changed.json`, `a4_<name>_impact.json` | A4 | tập đơn vị đổi (changed, new, closed, named_unchanged); tập đơn vị cần xem lại | `{"BLDS2015.D653": ["refers_to BLDS2015.D651"]}` |
| `a7_<stem>_nodes.jsonl` | A7 | nút `{id, type, number, heading, text, source_line, status}`, nút điều kiện thêm `kind`, theo ngày thêm `version`, `effective_from` | |
| `a7_<stem>_edges.jsonl` | A7 | cạnh `{s, p, o, evidence, method, status, sources}` | `D617.K2.c` `same_text_as` `D617.K1.d`, method `exact_text` |
| `a8_<stem>.html` | A8 | một trang HTML tự chứa (không phải JSON Lines) | |

Các báo cáo đọc được bằng mắt nằm ở `docs/`: `a1_notes_*`, `a2_unresolved_*`, `a3_unhandled_*`, `a6_unhandled_*`, `a4_report_*`, `a5_report_*`, `a7_report_*`.

### A1: Tách văn bản (`src/a1_parse.py`)

- **Vào/ra.** Vào: `data/raw/blds2015_p4.md`. Ra: `a1_triples_blds2015_p4.jsonl` (1.173 bộ ba) và `docs/a1_notes_blds2015_p4.txt`.
- **Cách làm.** Chạy được từng bước riêng bằng `-s 1` đến `-s 4`.
  1. *Nhìn dữ liệu thô.* In từng dòng bằng `repr()`, quét ký tự lạ (control, format, khoảng trắng đặc biệt), BOM, `\r`, tab và khoảng trắng cuối dòng. Mục đích là thấy chữ ẩn trước khi viết regex.
  2. *Phân loại từng dòng (`tokenize`).* Mỗi dòng khớp đúng một mẫu, thử theo thứ tự Chương, Điều, Khoản, Điểm:
     - Chương: `^## Chương ([IVXLCDM]+) [–-] (.+)$`
     - Điều: `^### Điều (\d+)\\?\.\s*(.*)$` (có `\\?` vì file Markdown viết `\.` để thoát dấu chấm)
     - Khoản: `^\*\*(\d+)\\?\.\*\*\s*(.*)$`
     - Điểm: `^- \*\*([abcdđeghiklmnopq])\)\*\*\s*(.*)$`. Bảng chữ này là bảng chữ của Điểm trong văn bản luật: có `đ`, không có `f j w z`.
     - Dòng không khớp mẫu nào: dòng trống, `---` và tiêu đề `#`/`##` được bỏ qua **kèm lý do**; còn lại là đoạn chữ.
     - Làm sạch chữ: chuẩn hoá Unicode NFC, đổi `\xa0` thành dấu cách, bỏ `**`, bỏ `\` đứng trước dấu câu, gộp khoảng trắng.
     - Dòng **đáng ngờ** (`###` không khớp mẫu Điều, hoặc đoạn chữ bắt đầu bằng `- `, `**`, `#`) phải bằng 0, nếu không thoát mã 1.
  3. *Dựng cây (`parse`).* Máy trạng thái giữ Chương, Điều, Khoản hiện tại cùng các bộ đếm. Số Điều được so với dãy mong đợi `EXPECTED_DIEU` (609 đến 662). Khoản phải liên tiếp 1, 2, 3 và Điểm phải liên tiếp theo bảng chữ. Đoạn chữ được thêm vào Khoản hiện tại, chưa có Khoản thì vào Điều. Sau mỗi lỗi, bộ đếm được đồng bộ lại theo số thực tế, để một lỗi không kéo theo hàng loạt lỗi giả.
  4. *Ghi bộ ba.* Mã là chuỗi số hiệu nối bằng dấu chấm, ví dụ `BLDS2015.D621.K1.dd` (`đ` thành `dd`). Mỗi đơn vị sinh các bộ ba theo thứ tự type, number, heading, chuong, text, version (luôn là 1), source_line.
- **Ví dụ thật.** Dòng `- **a)** ...` đứng dưới `**1.**` đứng dưới `### Điều 617\.` thành đơn vị `BLDS2015.D617.K1.a`, với `type = diem`, `number = a`, `source_line` là số dòng trong file md.
- **Quyết định đáng nhớ.**
  - Đoạn chữ đứng **sau** một danh sách Điểm (Điều 643, Khoản 2, dòng 303) bị nối vào text của Khoản, mất vị trí gốc. Chỗ này được ghi vào `a1_notes`.
  - File gốc thiếu dòng tiêu đề Chương XXI nên đã **thêm** `## Chương XXI – QUY ĐỊNH CHUNG` ngay trên Điều 609. Mọi `source_line` phía sau lệch +2.
- **Tự kiểm.** Số Điều đúng dãy mong đợi; Khoản và Điểm liên tiếp; mọi Điều thuộc một Chương; không có Chương lặp; danh sách dòng đáng ngờ rỗng. Sai thì in lỗi kèm số dòng, thoát mã 1, không ghi file.
- **Kết quả p4.** 4 Chương, 54 Điều, 115 Khoản, 46 Điểm, tức 215 đơn vị cộng 4 Chương, **1.173 bộ ba**. Có 33 đoạn chữ; dòng bỏ qua gồm 224 dòng trống, 3 dòng `---`, 1 tiêu đề `#`; 0 dòng đáng ngờ.
- **Giới hạn.** `EXPECTED_DIEU` khai báo theo tên file (chỉ có hai file); chưa nhận Điều có hậu tố như `5a`; nguồn phải đúng định dạng Markdown này.

### A2: Cạnh cấu trúc và dẫn chiếu (`src/a2_edges.py`)

- **Vào/ra.** Vào: `a1_triples`. Ra: `a2_edges_*.jsonl` (430 cạnh), `a2_refs_*.jsonl` (25 cạnh), `docs/a2_unresolved_*.txt` (2 dòng).
- **Độc lập với A1.** A2 không import `a1_parse`, chỉ đọc file bộ ba. Cha của Khoản/Điểm được suy từ chuỗi mã (bỏ đoạn cuối), còn kiểm tra dùng thuộc tính `type` do A1 ghi. Nếu A1 đánh mã sai thì hai nguồn này mâu thuẫn và lỗi hiện ra ở đây.
- **A2a, cạnh cấu trúc.**
  - Cha của Khoản/Điểm là mã bỏ đoạn cuối. Cha của Điều là thuộc tính `chuong`. Chương không có cha.
  - Mỗi quan hệ cha con sinh 2 cạnh liền nhau: `(cha, contains, con)` và `(con, part_of, cha)`. 215 đơn vị có cha nên ra 430 cạnh.
  - `check_edges` kiểm: không cạnh trùng; cha đúng bậc (Khoản thuộc Điều, Điểm thuộc Khoản, Điều thuộc Chương); `contains` đối xứng `part_of`; Khoản/Điểm có đúng một cha; số `contains` khớp số đơn vị có cha.
- **A2b, cạnh dẫn chiếu.**
  1. *Tìm cụm.* Một cụm là chuỗi các mục "từ khoá + đối số", từ khoá là `điều`, `khoản` hoặc `điểm`, đối số là một số, một chữ điểm, hoặc "này". Các mục nối bằng dấu cách, dấu phẩy, "và" hoặc "hoặc", có thể có đuôi "của Bộ luật này". Không phân biệt hoa thường. Chỉ nối bằng dấu cách (không phải mọi khoảng trắng), nên cụm không vắt qua dòng mới giữa hai đoạn.
  2. *Giải đích (`group_targets`).* Cụm là chuỗi mục có cấp **giảm liên tiếp** (điểm, khoản, Điều); mục cấp cao đứng cuối dùng chung cho các mục trước nó.
     - `khoản 1 và khoản 3 Điều 616 của Bộ luật này` ra 2 đích: `D616.K1`, `D616.K3`.
     - `Điều 631 và Điều 632 của Bộ luật này` ra 2 đích.
     - `điểm a khoản 1 Điều 630 của Bộ luật này` ra **một** đích sâu nhất: `D630.K1.a`.
     - `khoản 1 Điều này`: "Điều này" là tổ tiên đúng loại của đơn vị chứa cụm (hàm `enclosing_unit` đi ngược theo mã).
  3. *Xét đuôi (`tail_of`).* "của Bộ luật này" là chính văn bản đang xử lý. Tên văn bản khác ("Luật Đất đai", "Nghị định"...) thì **không tạo cạnh**, ghi vào unresolved với đích `external:<tên>`. Các đuôi chưa có quy tắc (khoảng "từ ... đến ...", danh sách số trần như "Điều 5, 6", "Luật này", "của <thứ không nhận ra>") thì dừng bằng `ValueError`.
  4. *Đích không tồn tại.* Điều của đích **chưa được nạp** (khoản 2 Điều 71, Điều 236) thì ghi unresolved, không nối bừa. Đích mà Điều của nó có trong tập nhưng khoản/điểm thì không (ví dụ khoản 9 Điều 616 khi Điều 616 chỉ có 3 khoản) thì `ValueError`.
- **Ví dụ thật.** Điều 644 khoản 2 có ba cụm: `khoản 1 Điều này`, `Điều 620`, `khoản 1 Điều 621 của Bộ luật này`. Cụm đầu giải theo tổ tiên thành `D644.K1`, hai cụm sau thành `D620` và `D621.K1`.
- **Tự kiểm.**
  - *Đếm độc lập:* trong p4 có 101 lần xuất hiện từ khoá điều/khoản/điểm. Đúng **41** lần nằm trong **21** cụm; 60 lần còn lại bị loại có chủ đích vì không có đối số (ví dụ "thời điểm mở thừa kế": 23 lần "điểm mở"; "điều kiện": 4 lần). Con số 41/41 cho biết không sót cụm nào.
  - Từ khoá kèm số mà không thuộc cụm nào (ví dụ `Điều 5a`) làm cả lần chạy dừng.
  - Mỗi cạnh: không tự trỏ, không trùng, hai đầu tồn tại, `evidence` là đoạn của text nguồn.
- **Kết quả p4.** 21 cụm thuộc 9 hình dạng, giải ra 27 đích: **25 cạnh** `refers_to` và 2 unresolved.

  | Hình dạng cụm | Số cụm |
  |---|---|
  | khoản N Điều N của Bộ luật này | 4 |
  | khoản N Điều này | 4 |
  | Điều N của Bộ luật này | 4 |
  | Điều N và Điều N của Bộ luật này | 3 |
  | khoản N và khoản N Điều N của Bộ luật này | 2 |
  | khoản N và khoản N Điều này; Điều N; điểm X khoản N Điều N của Bộ luật này; điểm X khoản này | 1 mỗi loại |

- **Giới hạn.** Chỉ dẫn chiếu viết tường minh; khoảng, danh sách số trần và hậu tố chữ dừng thay vì đoán (F-01, F-02).

### A3: Ngoại lệ tường minh (`src/a3_exceptions.py`)

- **Vào/ra.** Vào: bộ ba của A1 và cạnh `contains` của A2a (tính lại trong bộ nhớ). Ra: `a3_exceptions_*.jsonl` (4 cạnh) và `docs/a3_unhandled_*.txt` (9 dòng).
- **Từ kích hoạt (trigger).** Một regex duy nhất bắt `ngoại trừ`, `trừ` hoặc `không áp dụng`, có ranh giới từ nên "trừng", "trừu" không khớp. Chữ "ngoại trừ" tính một cụm. Trong p4 có **11** trigger: 10 chữ "trừ" và 1 "không áp dụng".
- **Chỉ có hai quy tắc, không có bộ khớp tổng quát.** Chiều cạnh: `s` là phần ngoại lệ, `o` là quy tắc bị ngoại trừ.
  1. **`not_apply_pattern`.** Đơn vị U chứa "không áp dụng" và có một cụm dẫn chiếu đứng **ngay trước** nó (chỉ cách dấu cách). Khi đó `s = U`, và `o` là từng đích của cụm. Evidence là từ đầu cụm đến hết "không áp dụng".
     - Ví dụ: D644.K2 "Quy định tại khoản 1 Điều này **không áp dụng** đối với người từ chối nhận di sản..." ra `D644.K2 exception_of D644.K1`. Hai cụm khác trong cùng câu (`Điều 620`, `khoản 1 Điều 621`) không đứng ngay trước nên không bị lẫn vào.
  2. **`except_list_pattern`.** Text của U có "trừ" hoặc "ngoại trừ" **và** kết thúc bằng "sau đây:". Khi đó mỗi đơn vị con trực tiếp C của U cho một cạnh `C exception_of U`; evidence là text của U.
     - Ví dụ: Điều 632 "Mọi người đều có thể làm chứng cho việc lập di chúc, trừ những người sau đây:" có 3 khoản, ra 3 cạnh.
- **Mọi trigger phải có chỗ đi.** Nó hoặc sinh cạnh, hoặc vào `unhandled` (mã đơn vị và câu). Bước kiểm đếm `đã xử lý + unhandled = số trigger`. Trong p4: 2 + 9 = 11. Chín đơn vị unhandled này chính là đầu vào của A6.
- **Không nới quy tắc để bắt thêm.** Các tình huống spec chưa nói đều `ValueError`: cụm trước "không áp dụng" có dạng `group_targets` không nhận; đích không có trong tập; quy tắc 2 khớp mà U không có con; U có hơn một "trừ" mà vẫn kết thúc "sau đây:".
- **Tự kiểm.** Không cạnh trùng; không tự trỏ; hai đầu tồn tại; evidence nằm trong text (của `o` với quy tắc 2, của `s` với quy tắc 1); evidence quy tắc 1 kết thúc bằng "không áp dụng", quy tắc 2 kết thúc bằng "sau đây:"; `s` là con trực tiếp của `o` theo `contains`; đếm trigger khớp.
- **Kết quả p4.** **4 cạnh**: 1 từ quy tắc 1 (D644.K2) và 3 từ quy tắc 2 (D632).

### A6: Ngoại lệ chung "trừ trường hợp" (`src/a6_general_exceptions.py`)

- **Vào/ra.** Vào: bộ ba của A1 (A6 không đọc kết quả A3). Ra: `a6_conditions_*.jsonl` (5 nút, 15 dòng), `a6_exceptions_*.jsonl` (10 cạnh), `docs/a6_unhandled_*.txt` (rỗng).
- **Phân việc với A3.** Trigger "trừ" thuộc A3 khi và chỉ khi text của đơn vị kết thúc bằng "sau đây:". A6 dùng đúng điều kiện này để bỏ qua các đơn vị đó, nên không cần chạy A3, và A7 tái dùng được khi dựng đồ thị theo ngày.
- **Cách làm.**
  1. Tại vị trí trigger "trừ" (hoặc "ngoại trừ"), nhận mẫu `(ngoại )trừ trường hợp`.
  2. **Mệnh đề** Y là phần text sau "trừ trường hợp" đến hết đoạn (không vượt qua dòng mới), bỏ các dấu `. ; : ,` ở cuối. Nếu cụm đứng **đầu đoạn** ("Trừ trường hợp X, quy tắc ...") thì mệnh đề dừng ở dấu phẩy đầu tiên vì phần sau là quy tắc chính (F-04). Evidence là từ "trừ" đến hết mệnh đề, nguyên văn.
  3. **Nút điều kiện.** Khoá gộp là `norm_text(Y)`: gộp khoảng trắng, hạ chữ thường, bỏ dấu cuối. Mã nút là `BLDS2015.C_<8 ký tự đầu của sha1(khoá)>`, ví dụ `C_426b8c79`. Dùng băm thay vì đánh số 1, 2, 3 để mã **không đổi** khi tập câu thay đổi giữa các phiên bản hay các ngày. Hai khoá khác nhau mà trùng mã băm thì `ValueError`.
  4. **Cạnh.** `nút điều kiện exception_of đơn vị quy tắc`, method `general_except_pattern`.
  5. **Ngoại lệ có dẫn chiếu (`clause_targets`).** Chạy lại bộ tìm cụm của A2 trên riêng mệnh đề. Đích T tìm được thì thêm cạnh `T exception_of đơn vị`, method `general_except_ref`. Ví dụ Điều 619 "..., trừ trường hợp thừa kế thế vị theo quy định tại Điều 652" ra `D652 exception_of D619`.
  6. **Phân loại `kind`**, khớp **toàn bộ** mệnh đề (nên "có thỏa thuận khác về thời hạn" là `cu_the`): `tuy_nghi` cho "(các bên) có thỏa thuận khác"; `dan_chieu_mo` cho "pháp luật / luật / luật khác / bộ luật này (có liên quan) có quy định khác"; còn lại `cu_the`. Hai loại đầu là câu chung chung, nối nhiều Điều không liên quan, nên A7 báo thêm số cụm khi bỏ chúng.
  7. **Unhandled.** Trigger "trừ" không kèm "trường hợp" (và không thuộc A3); và mỗi chữ "không được áp dụng" (A6 tự quét bằng regex riêng vì bộ trigger chung không bắt chữ này, mà A3 đang dùng chung bộ đó nên không sửa) (F-05).
- **ValueError.** Một đơn vị có hơn một "trừ trường hợp"; mệnh đề rỗng; "trừ trường hợp" đầu đoạn mà đoạn không có dấu phẩy.
- **Tự kiểm.** Mã nút khớp băm của mệnh đề và 1-1 với khoá; mỗi nút có ít nhất một cạnh; evidence bắt đầu bằng "trừ trường hợp" và nằm trong text; phép đếm `thuộc A3 + đã xử lý + unhandled = số trigger trừ/ngoại trừ + số "không được áp dụng"`. Trong p4: 1 + 9 + 0 = 10.
- **Kết quả p4.** **5 nút điều kiện**: 1 nút `tuy_nghi` ("có thỏa thuận khác", dùng chung cho 5 đơn vị thuộc 3 Điều D615, D659, D662), 1 nút `dan_chieu_mo` (D617.K1.a), 3 nút `cu_the` (D619, D620.K1, D646.K3). **10 cạnh**: 9 từ nút điều kiện và 1 cạnh dẫn chiếu `D652 exception_of D619`.
- **Giới hạn.** Chưa tách mệnh đề thành điều kiện và hệ quả (D646.K3); chưa ghi phạm vi vế của ngoại lệ (D617.K1.a, ngoại lệ chỉ áp cho vế "thu hồi tài sản" mà cạnh gắn vào cả Điểm); ngoại lệ **ngầm** ("Trường hợp ... thì ...", 29 đơn vị) chưa nhận dạng.

### A4: Cập nhật khi có văn bản sửa đổi (`src/a4_versions.py`)

Đây là bước phức tạp nhất, khoảng 1.600 dòng code.

- **Vào/ra.** Lệnh `apply --base <md gốc> --amend <văn bản> [--amend ...] [--effective-from] [--doc-id] [--name] [--llm off|replay|live]`. Vào: file md gốc (nạp bằng `a1.load_parsed`), cạnh gốc `a2_edges`, `a2_refs`, `a3_exceptions` (chỉ đọc), và một hay nhiều văn bản sửa đổi. Ra: `a4_<name>_versions.jsonl`, `_amend_edges.jsonl`, `_edge_changes.jsonl`, `_changed.json`, `_impact.json` và `docs/a4_report_<name>.txt`. Lệnh `snapshot --name --date` in luật như đang có hiệu lực tại một ngày, dạng Markdown cùng quy ước với file gốc.
- **Mô hình dữ liệu.**
  - Mỗi đơn vị có danh sách `Version`. Hiệu lực là **nửa khoảng** `[effective_from, effective_to)`: đang hiệu lực tại ngày T nếu (`from` rỗng hoặc ≤ T) và (`to` rỗng hoặc > T).
  - Phiên bản 1 của đơn vị gốc có `effective_from = 2017-01-01`, `source_doc = BLDS2015`.
  - **Không bao giờ xoá**: sửa là đóng bản cũ (đặt `effective_to`) rồi tạo bản mới với `previous_version` là số của bản trước. Nếu bản hiện tại chính là bản tạo ra trong cùng văn bản và cùng ngày thì sửa tại chỗ, để không sinh khoảng rỗng `[d, d)`.
- **Đọc văn bản sửa đổi (`parse_amendment`).**
  1. Chuẩn hoá: bỏ BOM, đổi `\r\n` thành `\n`, NFC, gộp khoảng trắng, giữ dòng trống (dòng trống phân biệt đoạn mới).
  2. **Ngày hiệu lực:** tìm "có hiệu lực (thi hành) (kể) từ ngày D tháng M năm Y" trên toàn văn bản. Không có thì `E_NO_DATE` (trừ khi có `--effective-from`); có hai ngày khác nhau thì `E_DATE_CONFLICT`; ngày không có thật (31/02) thì `E_DATE_INVALID`; ngày không sau 2017-01-01 thì `E_DATE_BEFORE_BASE`.
  3. **Nhận dạng dòng ngoài dấu nháy** theo văn phạm chuẩn:

     | Dạng | Chỉ thị tạo ra | Ví dụ (câu thật của Luật 85/2025/QH15 trong bộ thử) |
     |---|---|---|
     | R1: "Sửa đổi, bổ sung" hoặc "Sửa đổi" hoặc "Thay thế" + đơn vị + "như sau:"; hoặc đơn vị + "được sửa đổi, bổ sung" / "được sửa đổi" / "được thay thế" + "như sau:" | `replace_unit`; quan hệ `replaces` nếu có chữ "thay thế", còn lại `amends` | "Sửa đổi, bổ sung Điều 18 như sau:" |
     | R2: "Bổ sung Điều / khoản / điểm N (vào sau M) như sau:" | `insert_unit` | "Bổ sung Điều 31a vào sau Điều 31 như sau:" |
     | R3: "Bãi bỏ" + danh sách đích | `repeal_unit`, mỗi đích một chỉ thị | "Bãi bỏ các điểm a, d và đ khoản 2 Điều 7." |
     | R4: "Tên Điều N được sửa đổi như sau:" | `rename_heading` | |
     | R5: sửa / thay / bỏ / bổ sung **cụm từ** (+ "tại" danh sách đích, hoặc một dòng phạm vi "một số cụm từ tại ... như sau:") | `phrase` | "Thay thế cụm từ “xã, phường, thị trấn” bằng cụm từ “xã, phường, đặc khu” tại khoản 4 Điều 36 và Điều 43." |
     | R6: "Luật này thay thế Bộ luật dân sự ..." | `replace_doc` | |

  4. **Nội dung trong dấu nháy** (cho R1, R2, R4): đếm nháy cong “ ” có lồng; phần ngoài nháy chỉ được là khoảng trắng, `.` và `;` (`E_BODY`). Dựng cây Điều, Khoản, Điểm từ nội dung với kiểm thứ tự (`E_ORDER`): Khoản đầu là 1, Điểm đầu là a, rồi liên tiếp (2, 2a, 2b, 3 ... / a, b, c, d, đ, e ...). Cây có đúng một gốc và gốc phải khớp đích của chỉ thị (`E_ROOT`).
  5. **Dòng không khớp.** Là "dòng lạ", **báo lỗi `E_UNKNOWN_LINE`**, nếu dòng có "bãi bỏ" hoặc "hết hiệu lực", hoặc có cả một từ hành động (sửa, bổ sung, thay, bỏ) lẫn một tham chiếu cấu trúc (Điều / khoản / điểm + số). Tiêu đề Điều của chính văn bản sửa đổi và tiêu đề chung thì bỏ qua có ghi lý do. Văn bản không có chỉ thị nào thì `E_NO_DIRECTIVE`. Đây là chỗ chặn lỗi fail-open của F-03.
- **Áp dụng (`apply_doc`).**
  1. `check_overlap`: hai chỉ thị có cây đích chồng nhau (trùng mã hoặc là tổ tiên của nhau) thì `E_OVERLAP`, trừ hai chỉ thị cụm từ.
  2. Mỗi chỉ thị chạy một hàm riêng:

     | Chỉ thị | Cách áp |
     |---|---|
     | `replace_unit` | Đích phải đang hiệu lực (`E_TARGET`). Với từng nút của cây mới: có rồi mà chữ khác thì đóng bản cũ, tạo bản mới; chữ giống thì giữ nguyên (ghi vào `named_unchanged`); chưa có thì tạo (mã từng tồn tại rồi đã đóng thì mở lại, tính là `changed`; mã chưa từng có tính là `new`). Con cháu của đích mà cây mới không còn thì bị đóng |
     | `insert_unit` | Mã mới chưa từng tồn tại, kể cả đã đóng (`E_EXISTS`); cha phải đang hiệu lực (`E_PARENT`); có "vào sau M" thì M phải là đơn vị có thật và số mới phải xếp sau M (`E_AFTER`). Điều mới trong văn bản có Chương thuộc Chương của M; không có "vào sau" thì `E_PARENT` |
     | `repeal_unit` | Đóng đích và **mọi con cháu** (đặt `effective_to`), không xoá |
     | `rename_heading` | Tiêu đề cũ trong chỉ thị phải trùng tiêu đề hiện tại (`E_HEADING`), rồi tạo phiên bản mới |
     | `phrase` | Trên đích và mọi con cháu: thay, xoá hoặc chèn sau **mọi lần xuất hiện** của cụm, phân biệt hoa thường. Xoá thì gộp dấu cách thừa nhưng không sửa dấu câu còn sót. Cụm không có ở đâu trong cây đích thì `E_PHRASE_MISSING` |
     | `replace_doc` | Đóng mọi đơn vị đang hiệu lực |

  3. **Cập nhật cạnh chỉ cho đơn vị đã đổi (`recompute_edges`).** Gọi S là các đơn vị `changed` hoặc `new` còn hiệu lực. A4 chạy lại `a2.build_refs` và `a3.find_exceptions` chỉ trên text của S (các đơn vị khác có mặt nhưng không có text, làm đích và tổ tiên). Rồi so với cạnh hiện có cùng nguồn theo bộ ba `(s, p, o)`: cạnh cũ không còn thì ghi `close`, cạnh mới thì ghi `add`, và thêm `contains`/`part_of` cho mã mới. Không chạy lại trên toàn bộ đơn vị đang hiệu lực, vì khi đó một khoản bị bãi bỏ mà có người dẫn chiếu sẽ làm A2 báo lỗi, không bao giờ ra được "cờ cạnh đứt".
  4. **Cờ cạnh đứt (`find_broken`).** Cạnh `refers_to` hoặc `exception_of` mà nguồn còn hiệu lực và đích bị đóng đúng vào ngày hiệu lực của văn bản này.
  5. **Tập ảnh hưởng (`impact_set`).** Gọi U là đơn vị `changed` hoặc `closed` cả lượt. Một đơn vị còn hiệu lực vào danh sách nếu nó có `refers_to m`, hoặc là ngoại lệ của `m` (`exception_of m`), hoặc `m` là ngoại lệ của nó (`exception_of_by m`), với `m` thuộc U. Đây là danh sách "cần xem lại", và là chỗ chừa sẵn để tầng quy tắc sau này mở rộng.
  6. **Mục "Chưa phủ".** Từ khoá điều/khoản/điểm kèm số trong đơn vị đã đổi mà không nằm trong cụm A2 nhận ra thì được liệt kê trong báo cáo. Không chặn.
- **Nhiều văn bản.** Sắp theo ngày hiệu lực rồi áp lần lượt; hai văn bản cùng ngày thì `E_SAME_DATE`. Kết quả nhiều văn bản là hợp của các bước.
- **Ví dụ thật 1, `dev05_bai_bo_ds` (bãi bỏ).** 4 chỉ thị `repeal_unit` đóng **15 đơn vị**: `D621.K2`; `D626` cùng 5 khoản; `D650.K1.a`; `D651` cùng 3 khoản và 3 điểm. Cờ cạnh đứt: `D653 refers_to D651` (evidence "Điều 651 và Điều 652 của Bộ luật này"). Tập ảnh hưởng: chỉ `D653`. Cạnh bị bỏ của đơn vị đã đóng không ghi vào `edge_changes` (nguồn đã đóng nên đồ thị theo ngày tự loại).
- **Ví dụ thật 2, `dev02_sua_khoan` (sửa).** Khoản `D621.K1` có dòng phiên bản 2: `effective_from = 2027-07-01`, `previous_version = 1`, `source_doc = dev02_sua_khoan`, `directive_seq = 1`; điểm con `D621.K1.b` cũng có phiên bản 2 vì chữ của nó trong cây mới khác bản cũ (nút nào giữ nguyên chữ thì không được tạo phiên bản).
- **Tự kiểm và mã lỗi.** Có hơn 25 mã, mỗi mã một tình huống:

  | Nhóm | Mã lỗi |
  |---|---|
  | Tham số, file, ngày | `E_ARGS`, `E_BASE`, `E_NO_DATE`, `E_DATE_INVALID`, `E_DATE_CONFLICT`, `E_DATE_FLAG` (cờ khác ngày trong văn bản), `E_SAME_DATE`, `E_DATE_BEFORE_BASE` |
  | Đọc văn bản | `E_NO_DIRECTIVE`, `E_UNKNOWN_LINE`, `E_UNSUPPORTED` (đánh số lại, trở thành), `E_REFLIST`, `E_SCOPE`, `E_PHRASE`, `E_BODY`, `E_ORDER`, `E_ROOT`, `E_CODE` |
  | Áp dụng | `E_OVERLAP`, `E_TARGET`, `E_EXISTS`, `E_PARENT`, `E_AFTER`, `E_HEADING`, `E_PHRASE_MISSING`, `E_A2`, `E_A3` |
  | Tầng LLM (mục 7) | `E_LLM`, `E_LLM_SHAPE`, `E_LLM_CACHE`, `E_LLM_API` |

  **Gặp lỗi thì cả lượt không được áp**, không có chuyện áp một nửa. Chỉ ghi `docs/a4_report_<name>.txt` (mã lỗi, văn bản, số dòng, mô tả) và thoát mã 1. File dữ liệu của lần chạy thành công trước không bị xoá hay ghi đè.
- **Giới hạn.** Văn phạm chưa hỗ trợ "được bổ sung như sau", "đánh số lại"/"trở thành", nháy lồng trong cụm từ, danh sách số trần ("Điều 5, 6"), điểm đứng trực tiếp dưới Điều. Một số dạng trong đó được tầng LLM của mục 7 xử lý.

### A5: Kiểm tra độc lập (`src/a5_checks.py`)

- **Vào/ra.** Vào: `a1_triples`, `a2_edges`, `a2_refs`, `a3_exceptions` và (với `--versions`) `a4_<name>_versions.jsonl`. Ra: `docs/a5_report_<stem>.txt`, ghi cả khi mọi thứ đạt.
- **Độc lập với bước trước.** A5 đọc thẳng từng dòng JSON, không dùng `a2.load_units` hay `a2.parent_of`, nên nếu hai hàm này sai thì A5 vẫn thấy. Số kỳ vọng nằm trong bảng `EXPECTED` theo stem (p4: 215 đơn vị, 54 Điều, 4 Chương), đã đối chiếu độc lập bằng `grep` trên file md.
- **Các phép kiểm.**
  - *Bước 1, mã không trùng.* 1a: số đơn vị bằng số kỳ vọng. 1b: số Điều. 1c: mỗi mã có đúng một dòng `type`. 1d: mỗi cặp (mã, thuộc tính) xuất hiện một lần. 1e: số Chương.
  - *Bước 2, mỗi đơn vị một cha.* 2a: Điều có đúng một `part_of` nếu văn bản có Chương; Chương không có `part_of`. 2b: Khoản và Điểm có đúng một `part_of`. 2c: cha là mã bỏ đoạn cuối (cha của Điều là Chương ghi ở dòng `chuong`). 2d: `contains` đối xứng `part_of`. 2e: số `part_of` bằng số đơn vị trừ số Điều (cộng số Điều nếu có Chương). 2f: cha tồn tại và đúng bậc ngay trên.
  - *Bước 3, cạnh không trùng.* Gom bộ ba `(s, p, o)` của ba file cạnh; bộ ba nào xuất hiện hơn một lần là vi phạm, kể cả khi `evidence` khác nhau.
  - *Bước 4, phiên bản (khi có A4).* 4a: cặp (mã, version) duy nhất và các version của một mã là 1, 2, 3 liên tiếp. 4b: `previous_version` của version k là k-1, version 1 thì rỗng. 4c: khoảng hiệu lực không chồng. 4d: mọi mã của A1 còn trong versions (cam kết "không xoá nút"). 4e: dòng version 1 giữ nguyên type, number, heading, text của A1 (so bằng `==`, không chuẩn hoá khoảng trắng). 4f: mọi version 1 của mã gốc có cùng `effective_from` và `source_doc` khác rỗng; các dòng khác có ngày sau đó.
- **Cách thoát.** Các bước luôn chạy hết rồi mới thoát; có vi phạm hoặc đầu vào lỗi (thiếu file, JSON hỏng, stem lạ) thì thoát mã 1.
- **Kết quả p4.** Bước 1 đến 3 đều đạt (3: 459 bộ ba, 459 khác nhau, 0 lặp, đúng bằng 430 + 25 + 4). Bước 4 chạy trong `run_all.py` cho 3 bộ: `5dieu` với dev01+dev02, `5dieu` với dev04, `p4` với dev01.
- **Giới hạn.** A5 không đọc file A6 và A7 (hai bước đó tự kiểm); bảng `EXPECTED` ghi cứng theo tên file.

### A7: Gộp thành một đồ thị (`src/a7_graph.py`)

- **Vào/ra.** Chế độ gốc: vào `a1_triples`, `a2_edges`, `a2_refs`, `a3_exceptions`, `a6_conditions`, `a6_exceptions`; ra `a7_<stem>_nodes.jsonl`, `a7_<stem>_edges.jsonl`, `docs/a7_report_<stem>.txt`. Chế độ theo ngày (`--versions <a4_..._versions.jsonl> --date YYYY-MM-DD`): thêm `edge_changes` và `amend_edges` của A4; tên file thêm `<name>_<date>`.
- **Chế độ gốc, các việc làm.**
  1. **Nút:** đơn vị từ `a1_triples` (kể cả Chương), nút điều kiện từ `a6_conditions` (có thêm cột `kind`), và nút văn bản BLDS 2015 (`type = van_ban`, số hiệu, ngày ban hành, ngày hiệu lực lấy từ `a1.BASE_DOC`).
  2. **Cạnh:** nối bốn file cạnh theo thứ tự `a2_edges`, `a2_refs`, `a3_exceptions`, `a6_exceptions`, **gộp theo bộ ba `(s, p, o)`** (lớp `EdgeSet`): giữ dòng đầu; cột `sources` ghi một nhãn cho mỗi lần xuất hiện nên `len(sources) > 1` nghĩa là đã gộp; evidence khác nhau được cất vào `evidences`. Với p4: 0 bộ ba bị gộp.
  3. **Một cây duy nhất.** `attach_to_doc` thêm `contains`/`part_of` từ nút văn bản tới từng Chương (hoặc tới từng Điều nếu văn bản không có Chương), thành cây văn bản, Chương, Điều, Khoản, Điểm.
  4. **Trùng chữ.** Nhóm đơn vị theo (loại, `a6.norm_text(text)`); Khoản không gộp với Điểm. Đơn vị đứng đầu nhóm là *canonical*; các đơn vị sau mang `status = same_text` và có cạnh `same_text_as` tới canonical (method `exact_text`). **Không gộp nút**, vì mỗi đơn vị là một vị trí pháp lý có cha riêng, gộp sẽ phá quy tắc "một cha" của A5.
- **Chế độ theo ngày (`graph_at`).**
  1. *Nút:* các dòng `versions` đang hiệu lực tại T. Chương không lập phiên bản nên có mặt từ ngày hiệu lực của văn bản gốc, cho tới khi có văn bản thay cả bộ luật.
  2. *Cạnh:* cạnh gốc, rồi áp các dòng `edge_changes` có `at ≤ T` theo thứ tự (`add` thì thêm, `close` thì bỏ; `close` một cạnh không có là `ValueError`).
  3. *Lọc theo hiệu lực:* `contains`/`part_of` có một đầu đã đóng thì bỏ; cạnh ngữ nghĩa có **nguồn** đã đóng thì bỏ; cạnh ngữ nghĩa có nguồn còn hiệu lực mà **đích** đã đóng thì **giữ** và gắn `status = dangling`.
  4. *Nút điều kiện và cạnh ngoại lệ chung* được tính lại bằng `a6.find_general` trên text đang hiệu lực (không đọc file A6).
  5. *Nút văn bản sửa đổi* (id là tên văn bản) với mỗi văn bản có hiệu lực ≤ T, kèm cạnh `amends`/`replaces`/`repeals` đọc từ `amend_edges`. Đích không còn hiệu lực thì cạnh mang `status = historical`.
  6. Nhóm trùng chữ được tính lại mỗi ngày; nếu canonical bị đóng thì đơn vị bản sao kế tiếp lên làm canonical.
- **7 nhóm kiểm.** Báo cáo luôn ghi; **file dữ liệu chỉ ghi khi mọi nhóm đạt**, nếu không thoát mã 1.

  | Nhóm | Kiểm gì |
  |---|---|
  | 7a | mã nút duy nhất, `status` nút hợp lệ |
  | 7b | cạnh `ok` có đủ hai đầu là nút; cạnh `dangling`/`historical` có nguồn là nút và đích **không** phải nút |
  | 7c | không còn bộ ba `(s, p, o)` lặp |
  | 7d | mỗi nút `same_text` có đúng một `same_text_as` tới đơn vị đầu nhóm (nhóm dựng lại từ chính các nút) |
  | 7e | mỗi Chương/Điều/Khoản/Điểm có đúng một `part_of` tới cha đúng bậc; `contains` đối xứng. (Nhóm này chặn lỗi nếu cạnh `add` của A4 bị thiếu khi nạp theo ngày) |
  | 7f | (chỉ chế độ gốc) số nút, số cạnh, số nút `same_text` khớp bảng `EXPECTED` |
  | 7g | không có vòng trong `exception_of` (A ngoại lệ của B và B ngoại lệ của A, trực tiếp hay bắc cầu). Vòng `refers_to` chỉ ghi lại, không tính lỗi |

- **Mục "Liên thông" của báo cáo.** Đếm số thành phần liên thông: toàn đồ thị, chỉ theo cạnh ngữ nghĩa, và chỉ theo cạnh ngữ nghĩa khi bỏ các nút `tuy_nghi`/`dan_chieu_mo`.
- **Kết quả.**

  | Trường hợp | Nút | Cạnh | Ghi chú |
  |---|---|---|---|
  | p4, trạng thái gốc | 225 | 481 | 7/7 đạt; 4 nút `same_text`; 1 thành phần liên thông; chỉ theo cạnh ngữ nghĩa: 187 thành phần (191 khi bỏ 2 nút chung chung) |
  | p4 + `dev05_bai_bo_ds` tại 2027-01-01 | 211 (200 đơn vị, 5 điều kiện, 4 Chương, 2 văn bản) | 454 | 1 cạnh `dangling` (`D653 refers_to D651`), 4 cạnh `historical` (`repeals`); bỏ 30 cạnh cấu trúc và 1 cạnh có nguồn đã đóng |

- **Giới hạn.** Gộp chỉ theo chữ giống hệt, không theo nghĩa. Ngoại lệ chung chỉ nhận dạng "trừ trường hợp". Quan hệ cấp văn bản khác (văn bản sửa một phần, hết hiệu lực một phần) chưa có vì A4 không sinh ra.

### A8: Trang xem đồ thị (`utils/a8/a8_viz.py`, `utils/a8/a8_template.html`)

A8 **không tạo tri thức mới và không đổi dữ liệu**; nó chỉ đọc đồ thị A7 và vẽ ra để duyệt và demo. Không thuộc yêu cầu của hai spec.

- **Vào/ra.** `python -I utils/a8/a8_viz.py <md> [--versions V --date D]`. Vào: `a7_<stem>_nodes.jsonl` và `_edges.jsonl`. Ra: một file `data/processed/a8/a8_<stem>[_<tag>].html` (khoảng 0,5 MB), mở được **offline** bằng trình duyệt.
- **Cách làm.**
  1. **Dựng dữ liệu cho trang (`build_view`).** Thêm cho mỗi nút khoá `parent` (lấy từ `part_of`); chỉ giữ cạnh ngữ nghĩa (`refers_to`, `exception_of`, `same_text_as`, `amends`, `replaces`, `repeals`) vì cạnh cấu trúc được vẽ lại từ `parent`. Với đầu cạnh `dangling`/`historical` mà A7 không còn coi là nút, A8 dựng nút kiểu `da_dong` (vẽ vòng đứt nét đỏ, nhãn kèm ✕); cha của nó suy từ mã nếu mã có từ ba đoạn trở lên và cha còn trong đồ thị.
  2. **Nhúng một file (`render_html`).** Dữ liệu JSON và thư viện Cytoscape.js 3.30.2 (giấy phép MIT, để ở `utils/a8/vendor/cytoscape.min.js`) được chèn thẳng vào mẫu HTML. JSON thoát ký tự `<` thành `<` để dữ liệu không thể đóng thẻ `script` sớm. Không gọi tài nguyên nào bên ngoài.
  3. **Bố cục force-directed tự viết** (không thêm thư viện): vị trí đầu là cây tròn đồng tâm (không dùng số ngẫu nhiên); lực gồm lò xo theo cạnh (cạnh cha con ngắn hơn cạnh ngữ nghĩa), lực đẩy giữa mọi cặp nút, tách các vòng tròn chạm nhau, hút nhẹ về tâm; chạy 320 bước đồng bộ rồi tiếp tục khi người xem kéo nút. Cùng dữ liệu thì cùng hình (đã kiểm hai lần chạy cùng một hash vị trí; p4 có 0 cặp vòng tròn chồng nhau).
  4. **Hiển thị.** Kích thước nút theo bậc (văn bản 40, Chương 30, Điều 20, Khoản 12, Điểm 9, nút điều kiện 24). Cạnh cấu trúc (219 cặp) vẽ mờ, có công tắc tắt; 43 cạnh ngữ nghĩa nổi bằng màu: xanh là dẫn chiếu, cam là ngoại lệ, xanh lá nét đứt là trùng chữ. Màu đã chạy bộ kiểm bảng màu của skill `dataviz` cho nền sáng và tối; mỗi loại cạnh còn khác kiểu nét và đầu mũi tên nên không chỉ dựa vào màu. Nhãn dài dần theo mức phóng to. Kéo một nút thì ghim, bấm đúp để thả, nút "Xếp lại" về hình ban đầu. Có ô tìm kiếm không dấu, bảng cạnh, và trạng thái mở sẵn qua phần `#` của URL.
- **Tự kiểm.** `build_view` báo `ValueError` khi gặp loại cạnh trang chưa biết vẽ, khi một nút có hai `part_of`, hoặc khi cạnh `ok` có đầu không phải nút. `tests/test_a8.py` có 15 test Python (kể cả đọc dữ liệu A7 thật: 225 nút, 43 cạnh ngữ nghĩa, và 4 nút đã đóng của bản dev05). Đã thử phá có chủ đích 5 chỗ trong `a8_viz.py` và cả 5 lần đều bị test bắt.
- **Kết quả.** Ba trang trong `data/processed/a8/`: `a8_blds2015_p4.html` (225 nút), bản mẫu 5 Điều `a8_blds2015_5dieu.html`, và bản theo ngày `a8_blds2015_p4_p4_dev05_bai_bo_ds_2027-01-01.html`.
- **Giới hạn.** Phần JavaScript của trang chưa có test tự động (đã thử tay bằng trình duyệt Edge không giao diện: bấm, kéo, ghim, bật tắt cạnh, tìm kiếm, phóng to, xếp lại). Chưa có thanh trượt thời gian (mỗi ngày là một file). `run_all.py` gọi A8 sau A7 và ghi ba trang vào `data/processed/a8/`. Chi tiết quyết định: `utils/a8/a8_quyet_dinh.txt`.

---

## 5. Kết quả: đồ thị hiện tại

### Đồ thị gốc (luật như ban hành)

| Loại nút | Số lượng |
|---|---|
| Văn bản (BLDS 2015) | 1 |
| Chương | 4 |
| Điều | 54 |
| Khoản | 115 |
| Điểm | 46 |
| Nút điều kiện (từ "trừ trường hợp") | 5 |
| **Tổng** | **225** |

| Loại cạnh | Số lượng | Ghi chú |
|---|---|---|
| `contains` + `part_of` | 219 + 219 | Cây văn bản > Chương > Điều > Khoản > Điểm |
| `refers_to` | 25 | Dẫn chiếu tường minh |
| `exception_of` | 14 | 4 từ A3, 10 từ A6 |
| `same_text_as` | 4 | 4 cặp đơn vị trùng chữ |
| **Tổng** | **481** | 7/7 nhóm kiểm đạt |

### Ví dụ đồ thị theo ngày (nạp dev05, xem tại 01/01/2027)

- 15 đơn vị bị bãi bỏ biến mất khỏi đồ thị; còn 200 đơn vị đang hiệu lực.
- Có 1 cạnh dẫn chiếu bị đứt được gắn cờ: Điều 653 vẫn dẫn chiếu tới Điều 651, mà Điều 651 đã bị bãi bỏ.
- Có 4 cạnh `repeals` từ văn bản dev05, mang nhãn `historical` vì đích đã hết hiệu lực.
- Nhờ vậy, câu hỏi "văn bản nào đã sửa Điều X?" trả lời được ngay trên đồ thị.

### Nhận xét trung thực về độ giàu của đồ thị

Phần lớn cạnh là cạnh cấu trúc. Cạnh mang nghĩa (dẫn chiếu, ngoại lệ, trùng chữ) chỉ có 43. Nếu chỉ nhìn các cạnh mang nghĩa thì đồ thị rời thành 187 cụm. Lý do là hiện chỉ bắt được quan hệ **viết tường minh** bằng từ khoá. Theo đề cương, quan hệ **ngầm** sẽ do LLM đề xuất ở bước sau.

---

## 6. Đợt tự rà soát và sửa lỗi

### 6.1. Vì sao rà soát

Sau khi xong A1 đến A7, mọi test đều đạt, và lượt báo cáo trước ghi "mọi mục đã đạt". Đợt rà soát được làm theo hướng **cố tìm chỗ sai**:
- đếm lại số liệu bằng cách khác, không dùng số của chính chương trình;
- thử đầu vào chương trình chưa từng gặp;
- tách riêng lỗi "dừng và báo" với lỗi "im lặng làm sai".

Kết quả là **22 vấn đề** (F-01 đến F-22). Đánh giá lại 8 yêu cầu: lúc đầu chỉ 2 đạt và 5 đạt một phần. Lượt báo cáo trước đã **lạc quan quá mức**. Chi tiết nằm trong `review_a1_a7_findings.md`.

### 6.2. Đã sửa gì, giải thích dễ hiểu

Phần này giải thích bằng ví dụ. Cách sửa cụ thể (hàm nào, regex nào, test nào, đầu ra nào đổi) nằm ở mục 6.3.

**Pha 1: chặn các lỗi "im lặng làm sai".** Đây là ưu tiên số một.

| Vấn đề | Trước khi sửa | Sau khi sửa |
|---|---|---|
| F-03: câu bị động "Khoản 2 Điều 5 **được bãi bỏ**." | A4 coi là chữ thường, bỏ qua; văn bản "nạp thành công" mà không sửa gì | Báo lỗi "câu lạ". Văn bản không có chỉ thị nào cũng báo lỗi |
| F-01: "Điều 5 **của Luật Đất đai**" | Nối nhầm tới Điều 5 của chính BLDS | Ghi là dẫn chiếu ra văn bản khác, không nối |
| F-02: "từ Điều 5 đến Điều 8", "các điều 5, 6 và 7", "Điều 5a" | Thiếu cạnh mà không báo (chỉ ra Điều 5 và 8) | Dừng và báo "chưa có quy tắc" |
| F-04: câu bắt đầu "Trừ trường hợp X, quy tắc Y" | Gộp cả quy tắc Y vào nút điều kiện | Cắt điều kiện ở dấu phẩy đầu tiên |
| F-05: "không **được** áp dụng" | Không hiện ở đâu cả | Được liệt kê vào danh sách "chưa xử lý" |

Với dữ liệu BLDS hiện có, pha này **không làm thay đổi kết quả nào**, vì phần Thừa kế không có các câu kiểu đó. Pha này phòng lỗi khi gặp văn bản khác.

**Pha 2: bổ sung phần còn thiếu so với yêu cầu.**

| Vấn đề | Đã làm |
|---|---|
| F-12: chưa kiểm vòng ngoại lệ | Thêm kiểm 7g. Vòng dẫn chiếu qua lại thì hợp lệ, chỉ ghi lại |
| F-10, F-11: ngoại lệ không nối tới đơn vị mang ngoại lệ; nút "có thỏa thuận khác" tạo đường nối giả giữa các Điều không liên quan | Thêm cạnh Điều 652 là ngoại lệ của Điều 619; phân loại nút điều kiện; báo cáo số cụm khi bỏ các nút chung chung |
| F-08: văn bản gốc không có ngày hiệu lực | Ghi ngày 01/01/2017 và số hiệu; chặn văn bản sửa đổi có ngày sai |
| F-07: cạnh sửa đổi không nằm trong đồ thị | Đồ thị theo ngày có nút văn bản sửa đổi và cạnh `amends` / `replaces` / `repeals` |
| F-09: không có Chương; 54 Điều là 54 cây rời | Thêm 4 Chương (bổ sung dòng tiêu đề Chương XXI còn thiếu trong file gốc), thành một cây duy nhất; Điều mới chèn vào tự thuộc Chương của Điều đứng trước |

**Pha 3: định hướng và độ tin cậy.**

| Vấn đề | Đã làm |
|---|---|
| F-06: nhãn `duplicate` dễ hiểu nhầm là dư thừa | Đổi thành `same_text` (trùng chữ). 4 cặp trùng là cố ý về mặt pháp lý. Khử trùng lặp đúng nghĩa sẽ làm ở sổ khái niệm |
| F-17: chưa đo được độ chính xác thật | Có khung chấm điểm: mẫu 11 Điều chọn theo quy tắc cố định, script tính precision/recall. **Chờ người gán đáp án** |
| F-15, F-16: A4 chỉ được thử trên văn bản tự soạn | Bộ thử 19 câu thật (Luật 85/2025/QH15); thêm tầng LLM (xem mục 7) |

### 6.3. Chi tiết kỹ thuật từng Pha

**Cách làm chung cho mọi bước sửa.** Mỗi bước là một commit riêng. Trước khi commit chạy `src/run_all.py` (chạy lại cả pipeline rồi các bộ test: 7 bộ lúc bắt đầu, 10 bộ hiện nay vì có thêm test của tầng LLM và hai bộ chấm điểm), sau đó `git diff --stat data/ docs/` cho biết bước đó đã đổi những file kết quả nào. Mỗi bước ghi trước "đầu ra nào được phép đổi"; file nào đổi ngoài dự kiến là dấu hiệu lỗi. Mỗi bước còn cập nhật file `quyet_dinh` tương ứng và bảng theo dõi trong `review_a1_a7_findings.md`.

#### Pha 0: Chuẩn bị (commit `ed9314f`)

| Việc | Cách làm |
|---|---|
| Thống nhất Python | Từ **3.10 trở lên** (code dùng kiểu `str \| None` trong `dataclass` và `NamedTuple`). `run_all.py` kiểm phiên bản và dừng nếu thấp hơn. Với Python 3.9, `test_a1`, `test_a4`, `test_a7` dừng ngay khi nạp module |
| Dọn git | Thêm `.gitignore` cho `__pycache__/`, bỏ các file `.pyc` đã lỡ commit |
| Lưu bằng chứng | Commit `review_a1_a7_findings.md` và `plan_sua_a1_a7.md` trước khi sửa code |
| `src/run_all.py` | Một script chạy lại **toàn bộ** pipeline trên 2 nguồn và 8 văn bản dev (xem mục 8.2), rồi chạy test. Dùng làm bộ **hồi quy** cho mọi bước sau |

#### Pha 1: Đổi "im lặng làm sai" thành "dừng và báo"

Quy ước của cả pha: p4 và 5dieu **không có** ca nào thuộc các lỗi này, nên toàn bộ `data/processed` và `docs` phải **giữ nguyên từng byte**; chỉ có test mới.

**Bước 1.1, F-03 (commit `8986981`), A4 không còn bỏ qua im lặng chỉ thị dạng bị động.**
- *Chỗ sửa:* `a4_versions.py`, hàm `skip_reason` cùng ba regex mới `RE_ACTION` (sửa, bổ sung, thay, bỏ), `RE_ACTION_ALONE` (bãi bỏ, hết hiệu lực), `RE_STRUCT_REF` (Điều/khoản/điểm kèm số hoặc chữ); `parse_amendment` thêm mã `E_NO_DIRECTIVE`.
- *Cơ chế:* một dòng ngoài dấu nháy mà không khớp chỉ thị nào thì trở thành **dòng lạ (`E_UNKNOWN_LINE`)** nếu nó có "bãi bỏ" hoặc "hết hiệu lực", hoặc có cả từ hành động lẫn tham chiếu cấu trúc. Trước đó các dòng này bị ghi "không phải chỉ thị" rồi bỏ qua. Văn bản sửa đổi không có chỉ thị nào cũng là lỗi.
- *Cái giá chấp nhận:* điều khoản chuyển tiếp có các từ đó cũng thành dòng lạ (fail-closed). Dòng có tham chiếu cấu trúc nhưng không có từ hành động vẫn bị bỏ qua như cũ.
- *Test:* `test_lines_that_look_like_directives_are_unknown_not_skipped`, `test_error_no_directive`.

**Bước 1.2, F-01 và F-02 (commit `dba1ff1`), A2 không còn nối nhầm hay bỏ sót im lặng.**
- *Chỗ sửa:* `a2_edges.py`: hàm `tail_of` với các regex `TAIL_THIS_RE`, `TAIL_DOC_RE`, `TAIL_OF_RE`, `TAIL_RANGE_RE`, `TAIL_BARE_RE`; hàm `uncovered`; tham số `allow_uncovered` của `build_refs`.
- *Cơ chế:* sau mỗi cụm dẫn chiếu, xét đoạn chữ ngay sau nó. Tên một văn bản khác ("của Luật Đất đai") thì **không tạo cạnh**, ghi vào unresolved với đích `external:<tên>`. Các dạng chưa có quy tắc thì `ValueError`: "Luật này" (văn bản đang xử lý là Bộ luật), "của <thứ không nhận ra>", khoảng "từ Điều 5 đến Điều 8", danh sách số trần "các điều 5, 6 và 7", hậu tố "Điều 5a", "khoản 2a". Từ khoá kèm số mà không thuộc cụm nào cũng dừng.
- *Lưu ý:* A4 gọi `build_refs(..., allow_uncovered=True)` vì A4 đã có mục "Chưa phủ" liệt kê chính các trường hợp này.
- *Test:* `test_external_refs_are_unresolved_not_edges`, `test_unsupported_tails_and_uncovered_numbers_stop`, `test_no_reference_to_another_law`.

**Bước 1.3, F-04 và F-05 (commit `e7fd737`), A6 không còn nuốt quy tắc chính vào điều kiện.**
- *Chỗ sửa:* `a6_general_exceptions.py`, hàm `find_general` và regex mới `NOT_ALLOWED_RE`.
- *Cơ chế:* "Trừ trường hợp X, quy tắc ..." đứng đầu đoạn thì mệnh đề dừng ở **dấu phẩy đầu tiên** (không có dấu phẩy thì `ValueError`). Mỗi "không được áp dụng" đi vào danh sách `unhandled`. **Không sửa** bộ trigger chung `TRIGGER_RE`, vì A3 dùng chung với nó; thêm vào đó sẽ làm A3 coi "không được áp dụng" là quy tắc 1.
- *Test:* `test_leading_clause_stops_at_first_comma`, `test_khong_duoc_ap_dung_is_unhandled_not_lost`.

#### Pha 2: Bổ sung phần còn thiếu so với yêu cầu

Thứ tự theo độ lan: bước ít ảnh hưởng làm trước, bước đổi A1 làm sau cùng. Khác với Pha 1, các bước này **cố ý** làm đổi đầu ra.

**Bước 2.1, F-12 (commit `d8941a9`), kiểm vòng ngoại lệ.**
- *Chỗ sửa:* `a7_graph.py`: hàm `find_cycle` (duyệt sâu bằng vòng lặp, không đệ quy và không dùng thư viện đồ thị; đánh dấu nút đang nằm trên đường đi, gặp lại nút đó là có vòng) và nhóm kiểm 7g trong `check_graph`.
- *Cơ chế và điểm lệch kế hoạch:* kế hoạch ban đầu kiểm vòng trên hợp `refers_to` và `exception_of`. Khi làm thì chỉ kiểm vòng trong **`exception_of`**; vòng `refers_to` chỉ ghi lại. Lý do: `D619 refers_to D652` cùng `D652 exception_of D619` (quy tắc dẫn chiếu tới chính ngoại lệ của nó) là một vòng **hợp lệ** trong luật, kiểm trên hợp sẽ báo sai.
- *Test:* `test_find_cycle`, `test_check_7g_exception_cycle_fails_refers_to_cycle_is_only_noted`. Đầu ra: báo cáo A7 thêm một dòng 7g.

**Bước 2.2, F-10 và F-11 (commit `66a29b0`), ngoại lệ nối tới đơn vị mang ngoại lệ và phân loại nút điều kiện.**
- *Chỗ sửa:* `a6`: `condition_kind`, `clause_targets`, trường `ref_edges` của `General`; `a7`: hàm `boilerplate` và mục "Liên thông" của báo cáo.
- *Cơ chế:* chi tiết ở A6 (mục 4). Hai kết quả đo được: thêm đúng 1 cạnh `D652 exception_of D619`, và nút điều kiện có cột `kind`. A7 báo số thành phần liên thông khi bỏ các nút `tuy_nghi`/`dan_chieu_mo`, để thấy chúng đang tạo đường nối giả giữa các Điều không liên quan.
- *Test:* `test_reference_inside_clause_gives_exception_edge_from_the_target`, `test_condition_kinds`. Đầu ra đổi: `a6_conditions_*` (thêm dòng `kind`), `a6_exceptions_*` (+1 cạnh), `a7_*`.

**Bước 2.3, F-08 (commit `874af35`), metadata và ngày hiệu lực của văn bản gốc.**
- *Chỗ sửa:* `a1_parse.py` thêm `BASE_DOC` (91/2015/QH13, ban hành 2015-11-24, hiệu lực 2017-01-01); `a4_versions.py`: phiên bản 1 lấy `effective_from = hieu_luc` và `source_doc = BLDS2015`; `a5_checks.py` thêm kiểm 4f.
- *Cơ chế:* văn bản sửa đổi có ngày hiệu lực **không sau** 2017-01-01 thì `E_DATE_BEFORE_BASE` (trùng ngày cũng lỗi vì phiên bản 1 sẽ có khoảng `[d, d)` rỗng); `doc-id` trùng mã văn bản gốc thì `E_ARGS`. Snapshot trước ngày hiệu lực của luật gốc là rỗng, không phải cả bộ luật.
- *Test:* `test_error_effective_date_not_after_base_and_base_doc_id`, `test_step4f_base_dates`, `test_before_the_base_takes_effect_there_are_no_units`. Đầu ra đổi: mọi `a4_*_versions.jsonl`, snapshot, báo cáo A5.

**Bước 2.4, F-07 và F-18 (commit `c8ba817`), cạnh cập nhật và nút văn bản trong đồ thị gộp.**
- *Chỗ sửa:* `a7_graph.py`: `add_amend_edges`, nút `van_ban`, trạng thái cạnh mới `historical`.
- *Cơ chế:* ở chế độ theo ngày, A7 đọc `amend_edges` của A4 và sinh nút cho từng văn bản sửa đổi có hiệu lực ≤ T cùng cạnh `amends`/`replaces`/`repeals` (giữ `directive_seq`, `new_version`). Đích đã bị đóng không còn là nút nên cạnh mang `historical`, và nhóm kiểm 7b chấp nhận trạng thái này **chỉ khi** nguồn là nút `van_ban` và đích không phải nút. Chỉ thị thay cả bộ luật thành cạnh `replaces` từ văn bản đó tới nút `BLDS2015`.
- *Test:* `test_amend_edges_and_document_nodes`, `test_check_7b_amend_edges`, `test_dev05_closes_units_and_flags_the_broken_reference`, `test_dev08_replace_whole_document_gives_an_empty_graph`.

**Bước 2.5, F-09 (commit `209cd9d`), Chương và cây phân cấp. Bước lan rộng nhất, làm cuối.**
- *Chỗ sửa:* `a1_parse.py` (`RE_CHUONG`, đơn vị `chuong`, thuộc tính `chuong` của Điều); `a2_edges.py` (cạnh Chương, Điều); `a5_checks.py` (kiểm 1e, 2a, 2c, 2f); `a7_graph.py` (`attach_to_doc`, nhóm kiểm 7e); `a4_versions.py` (`Store.chuong`).
- *Cơ chế:* Chương nhận từ dòng `## Chương <số La Mã> – <tên>`, mã dạng `BLDS2015.CXXII`. File gốc thiếu tiêu đề Chương XXI nên đã **thêm một dòng** vào `data/raw/blds2015_p4.md` trên Điều 609 (nếu không thì phải cho phép "Điều không có Chương", làm yếu các phép kiểm cha con); mọi số dòng phía sau lệch +2 và các test ghi cứng số dòng được cập nhật. Chương không lập phiên bản vì cú pháp sửa đổi không chạm tới Chương. Điều mới chèn bằng "vào sau Điều M" thuộc Chương của M; không có "vào sau" thì `E_PARENT`.
- *Test:* `test_chapter_edges_and_checks` (A2). Đầu ra đổi: gần như mọi file; p4 thêm 4 nút và 116 cạnh (108 cạnh Điều, Chương và 8 cạnh văn bản, Chương).

#### Pha 3: Định hướng và độ tin cậy

**Bước 3.1, F-06 (commit `f2440d6`), đổi tên nhãn trùng chữ.** Nhãn trạng thái nút `duplicate` đổi thành `same_text`. Lý do: 4 cặp đơn vị của p4 có chữ giống hệt nhau nhưng là trùng có chủ đích pháp lý (ví dụ cùng một nghĩa vụ áp cho hai chủ thể khác nhau), không phải dư thừa, nên tên `duplicate` dễ đọc nhầm. Khử trùng lặp đúng nghĩa (trùng thực thể) thuộc sổ khái niệm của đề cương, chưa làm. Đầu ra đổi: chỉ đổi nhãn.

**Bước 3.2a, F-17 (commit `f4cefd8`), khung chấm precision/recall.**
- *Chỗ làm:* `tests/eval_gold.py`.
- *Mẫu:* các Điều **609, 614, 619, ..., 659** (cách nhau 5), tức 11 Điều. Chọn bằng quy tắc cố định chứ không theo kết quả của pipeline, để mẫu không thiên về chỗ pipeline làm tốt.
- *Cách chạy:* `--template` sinh `data/gold/units_<stem>.md` (để người gán đọc) và `gold_<stem>.tsv` trống, không ghi đè file đã có. Người gán điền các cột `p`, `s`, `o`, `ngam`, `ghi_chu` rồi đổi dòng đầu thành `# trang_thai: da_gan`; chưa gán xong thì lệnh chấm từ chối chạy.
- *Cách chấm:* so cạnh `refers_to` (nguồn thuộc mẫu) và `exception_of` (đích thuộc mẫu) của A7 với đáp án; tách riêng recall của ngoại lệ **ngầm** (cột `ngam = 1`). Nguồn ngoại lệ có thể viết bằng mệnh đề trong dấu nháy, so với nút điều kiện qua `a6.norm_text`. Báo cáo: `docs/gold_report_<stem>.txt`.
- *Trạng thái:* **chờ người gán đáp án**, nên chưa có số.
- *Test:* `test_sample_rule`, `test_score_precision_recall_and_implicit`, `test_read_gold_status_and_format_errors`.

**Bước 3.2b và 3.3 (commit `bd93cce`), bộ kiểm thử ngoài cho A4 và tầng LLM.**
- *Bộ kiểm thử:* `data/ext_amend/cases_blds2015_p4.json` có 19 ca. Mỗi ca ghi `cau_goc` (câu chỉ thị nguyên văn của Luật 85/2025/QH15), `van_ban_bld` (cùng khung câu, chỉ đổi số hiệu, cụm từ, nội dung sang BLDS) và `mong_doi` (danh sách `(op, đích)` đúng). `tests/eval_ext_amend.py` ghép mỗi ca thành một văn bản sửa đổi (đầu chuẩn, các dòng, câu hiệu lực), áp lên p4 bằng `apply_series` rồi so.
- *Bốn kết quả mỗi ca:* `ky_hieu` (đúng, văn phạm chuẩn nhận hết), `llm` (đúng, có dùng tầng chuẩn hoá), `dung_loi` (A4 dừng với mã lỗi, fail-closed), `SAI` (chạy xong mà kết quả khác mong đợi, là fail-open nghiêm trọng; có ca `SAI` thì thoát mã 1).
- *Tầng LLM:* mục 7.
- *Test:* `test_original_sentences_are_verbatim_from_the_source` (câu gốc phải đúng nguyên văn trong file nguồn), `test_off_mode_never_applies_a_wrong_change`, và 14 test của `test_a4_llm.py`.

### 6.4. Đánh giá lại sau khi sửa

- **Phân cấp cấu trúc:** từ "đạt tối thiểu" lên **"đạt"**.
- **Dẫn chiếu, ngoại lệ, cập nhật:** vẫn **"đạt một phần"**. Không còn lỗi im lặng, nhưng phạm vi câu chữ hiểu được vẫn hẹp, và chưa bắt được quan hệ ngầm.

---

## 7. Tầng LLM cho phần cập nhật (A4)

### 7.1 Vấn đề

A4 hiểu văn bản sửa đổi bằng các mẫu câu viết sẵn. Văn bản thật có nhiều cách viết, ví dụ:
- "Sửa đổi, bổ sung **khoản 3 và khoản 4** Điều 53 như sau:";
- "Sửa đổi, bổ sung **một số khoản của Điều 194** như sau:", kèm các ý con a), b).

Nếu cứ thêm mẫu thì không bao giờ đủ, vì cách viết là tổ hợp của nhiều thành phần. Bạn đã chốt **hướng C**: dùng LLM, nhưng có kiểm. Nguyên tắc: **LLM chỉ đề xuất, máy kiểm bằng luật quyết định**. LLM không bao giờ ghi trực tiếp vào đồ thị.

### 7.2 Luồng xử lý

```
văn bản sửa đổi
   │  mỗi dòng ──► văn phạm chuẩn R1-R6 nhận được? ──có──► chỉ thị (via = "ky_hieu"), KHÔNG gọi LLM
   │                                  │ không: lỗi E_UNKNOWN_LINE hoặc E_REFLIST
   │                                  ▼
   │                 gom thành KHỐI (dòng lạ + các dòng sau nó)
   │                                  ▼
   │              Claude đề xuất danh sách chỉ thị dạng JSON
   │                                  ▼
   │            dựng lại thành CÂU CHUẨN R1-R5 + nội dung trong nháy
   │                                  ▼
   │       parse lại bằng chính văn phạm chuẩn ──► kiểm V1, V2, V3
   │                                  │                  │
   │                         đạt ─────┘                  └── không đạt: gửi lỗi cho Claude sửa
   │                          ▼                              (tối đa 3 lần đề xuất, 2 vòng sửa)
   │              chỉ thị (via = "llm") ──► bước áp dụng như thường
   ▼                                          (E_TARGET, E_OVERLAP, E_PHRASE_MISSING ...)
```

Hết 3 lần đề xuất mà vẫn không đạt thì `E_LLM` và **cả văn bản không được áp**.

### 7.3 Từng thành phần

- **Khi nào gọi LLM.** Chỉ khi chạy với `--llm replay` hoặc `--llm live` **và** lỗi thuộc `LLM_TRIGGERS`: `E_UNKNOWN_LINE` (dòng lạ) hoặc `E_REFLIST` (khung câu nhận được nhưng danh sách đích nằm ngoài văn phạm). Mặc định là `--llm off`, hành vi y như trước, nên mọi đầu ra của 8 văn bản dev không đổi.
- **Khối (`block_end`).** Khối gồm dòng gây lỗi và các dòng sau nó, dừng trước dòng ngoài dấu nháy mà mở một mục đánh số ("N. "), một tiêu đề Điều của văn bản sửa đổi, hoặc câu hiệu lực. Nhờ vậy dòng phạm vi "một số khoản của Điều 194 như sau:" đi cùng các chỉ thị con a), b) và nội dung trong nháy.
- **Cấu hình mô hình.** `claude-sonnet-5-5`, mức suy luận `medium`, `max_tokens` 16.000. System prompt đặt `cache_control: ephemeral`. Có `fallbacks="default"` cùng beta `server-side-fallback-2026-07-01`: nếu yêu cầu bị bộ phân loại an toàn từ chối thì chạy lại trên mô hình dự phòng.
- **Khuôn đầu ra cố định (JSON Schema).** Mô hình buộc phải trả về JSON theo `SCHEMA`:
  - `chi_thi`: danh sách chỉ thị. Mỗi chỉ thị có `op` (một trong `replace_unit`, `insert_unit`, `repeal_unit`, `rename_heading`, `phrase`), `quan_he` (`amends` hoặc `replaces`), `dich` (danh sách `{dieu, khoan, diem}`), `vao_sau`, `noi_dung`, `kieu_cum` (`replace`, `delete` hoặc `insert`), `cum_cu`, `cum_moi`.
  - `khong_xu_ly_duoc`: lý do, khi khối có điều mô hình không biểu diễn được.
  - Không có `replace_doc`: thay cả bộ luật chỉ đi qua đường nhanh.
- **Prompt (`PROMPT_VERSION = a4c-1`).** Gồm định nghĩa từng `op` và sáu quy tắc: (1) `replace_unit`, `insert_unit`, `rename_heading` mỗi chỉ thị đúng **một** đích ("khoản 3 và khoản 4" là hai chỉ thị); (2) đích luôn ghi đủ Điều, khoản/điểm viết tương đối thuộc Điều nêu ở dòng đầu khối; (3) giữ nguyên số và chữ ("4a", "đ"); (4) `noi_dung` **chép nguyên văn** chữ trong cặp nháy, nếu một cặp nháy chứa nhiều khoản thì chỉ được tách tại nhãn mở đầu của từng khoản; (5) **không đoán**: gặp điều không biểu diễn được (đánh số lại, chuyển vị trí, ngày hiệu lực riêng, quy định chuyển tiếp) thì trả `chi_thi = []` kèm lý do; (6) nếu có phần "LẦN TRƯỚC BỊ TỪ CHỐI" thì sửa đúng các lỗi nêu. Có kèm một ví dụ khối và kết quả.
- **Dựng lại câu chuẩn (`render_canonical`).** Mỗi chỉ thị JSON thành các dòng R1 đến R5 kèm nội dung trong nháy. Hình dạng sai (op lạ, không có đích, sai số đích) thì `E_LLM_SHAPE`. Các dòng này được parse bằng đúng `_parse_lines` của văn phạm chuẩn, **không cho gọi LLM lồng nhau**. Đây là chỗ bảo đảm LLM không áp được điều gì mà văn phạm chuẩn không chấp nhận.
- **Ba phép kiểm ký hiệu (`check_block`).**

  | Kiểm | Nội dung | Giới hạn đã biết |
  |---|---|---|
  | V1, phủ số hiệu | Tập (cấp, nhãn) của mọi Điều, khoản, điểm nhắc **ngoài dấu nháy** trong khối phải bằng tập (cấp, nhãn) của mọi đích và "vào sau", hai chiều | So theo tập nên hoán vị Điều giữa hai đích cùng câu ("khoản 1 Điều 16, khoản 2 Điều 46") không bị V1 bắt; với `replace_unit`/`insert_unit` thì lỗi `E_ROOT` của văn phạm chuẩn (gốc nội dung phải khớp đích) bắt phần lớn ca đó |
  | V2, đúng nguyên văn nội dung | Nối các `noi_dung` (của `replace_unit`, `insert_unit`, `rename_heading`) phải bằng nối chữ các cặp nháy mở đầu dòng của khối, sau khi gộp khoảng trắng | LLM chỉ được **tách**, không được viết lại |
  | V3, đúng nguyên văn cụm từ | `cum_cu`, `cum_moi` phải là chữ của một cặp nháy nằm giữa dòng trong khối | |

  Sau đó các kiểm của bước áp dụng (`E_TARGET`, `E_EXISTS`, `E_PHRASE_MISSING`, `E_OVERLAP`...) vẫn chạy như với chỉ thị của đường nhanh.
- **Vòng sửa (`normalize_block`).** Tối đa `LLM_ROUNDS = 3` lần đề xuất (1 lần đầu cộng 2 vòng sửa, đúng với "tự sửa tối đa 2 vòng" của Nội dung 2 trong đề cương). Mỗi vòng sửa gửi lại cho mô hình một JSON gồm đề xuất trước và danh sách lỗi. Lỗi ở **bước áp dụng** (ví dụ `E_TARGET`) hiện chưa được gửi lại cho mô hình.
- **Tái lập và chi phí.** Mỗi lần gọi API lưu một file `data/llm_cache/a4/<khoá>.json` gồm đầu vào, đầu ra, mô hình thực chạy, request id và số token. Khoá là 20 ký tự đầu của sha256 trên (mô hình, `PROMPT_VERSION`, chữ của khối, phản hồi vòng trước), nên đổi prompt thì đổi `PROMPT_VERSION`. Chế độ `replay` chỉ đọc cache (thiếu thì `E_LLM_CACHE`, không gọi mạng); chế độ `live` gọi API khi thiếu cache rồi lưu lại, cần `ANTHROPIC_API_KEY` và gói `anthropic`. Nhờ cache, chạy lại cho kết quả y hệt và không tốn tiền.
- **Mã lỗi riêng:** `E_LLM` (mô hình từ chối hoặc hết lượt sửa), `E_LLM_SHAPE` (JSON sai hình), `E_LLM_CACHE` (replay mà thiếu cache), `E_LLM_API` (lỗi API hoặc thiếu gói). Mô hình bị từ chối hay đầu ra bị cắt ở `max_tokens` đều là lỗi và **không được lưu vào cache**.
- **Dấu vết.** Chỉ thị qua LLM mang `via = "llm"`. Báo cáo A4 có mục "Khối chuẩn hoá bằng LLM" ghi khối, số lần đề xuất, mô hình, khoá cache và các dòng chuẩn.

### 7.4 Bộ kiểm thử 19 câu thật và kết quả khi chưa bật LLM

Bộ này (`data/ext_amend/cases_blds2015_p4.json`, cách làm ở mục 6.3, bước 3.2b) lấy câu chỉ thị **nguyên văn** của Luật 85/2025/QH15 (Công báo số 953 và 954 ngày 21/07/2025), chỉ đổi số hiệu, cụm từ và nội dung sang BLDS. Chạy `python -I tests/eval_ext_amend.py --llm off` cho:

| Kết quả | Số ca | Ví dụ (câu gốc của Luật 85) |
|---|---|---|
| `ky_hieu`: văn phạm chuẩn nhận đúng | 9 | "Sửa đổi, bổ sung Điều 18 như sau:"; "Bổ sung Điều 31a vào sau Điều 31 như sau:"; "Bãi bỏ các điểm a, d và đ khoản 2 Điều 7."; "Thay thế cụm từ “xã, phường, thị trấn” bằng cụm từ “xã, phường, đặc khu” tại khoản 4 Điều 36 và Điều 43." |
| `dung_loi`: A4 dừng, không áp gì | 10 | "Sửa đổi, bổ sung khoản 3 và khoản 4 Điều 53 như sau:" (`E_UNKNOWN_LINE`); "Sửa đổi, bổ sung, bãi bỏ một số khoản của Điều 194 như sau:" kèm ý a), b) (`E_UNKNOWN_LINE`); "... tại khoản 1 và khoản 3 Điều 358, các khoản 1, 2, 3 và 7 Điều 359" (`E_REFLIST`) |
| `SAI`: chạy xong nhưng kết quả sai | **0** | |

Chín ca nhận đúng là các câu đơn giản. Mười ca dừng là đúng những dạng "nhiều khoản trong một câu", "một số khoản kèm ý con", "danh sách đích phức tạp" mà tầng LLM sinh ra để xử lý. Điều quan trọng nhất là **0 ca làm sai im lặng**.

### 7.5 Trạng thái

- **Đã có:** toàn bộ code và test, dùng proposer / client **giả** (14 test của `test_a4_llm.py`: gọi nhiều đích, khối có phạm vi, đường nhanh không bao giờ gọi LLM, sửa sau khi bị từ chối, nội dung bị diễn đạt lại thì bị loại sau hết lượt, mô hình từ chối thì dừng, replay mà thiếu cache thì fail-closed...).
- **Chưa làm:** chạy với API thật. Việc này cần API key; chi phí ước tính dưới 15 nghìn đồng cho 19 câu. Thư mục `data/llm_cache/` vì vậy chưa tồn tại. Bạn đã chọn để sau.

---

## 8. Kiểm thử: làm sao biết code đúng

### 8.1 Các bộ test

Project có **281 test** trong 11 file `tests/test_*.py` (đếm các hàm `test_*`; cả 11 file đều in `tổng test lỗi: 0` khi chạy lại ngày 26/10/2026). Trong đó 266 test thuộc 10 file mà `run_all.py` chạy, và 15 test của A8 chạy riêng.

| File | Số test | Phủ cái gì |
|---|---|---|
| `test_a1.py` | 11 | mã duy nhất; `đ` thành `dd` không đụng `d`; không sót ký hiệu Markdown; **bảo toàn chữ so với file gốc** (không mất, không thừa từ); vị trí đoạn chữ; Chương và các lỗi về Chương; ghi file |
| `test_a2.py` | 43 | cạnh cấu trúc (cha, tính đối xứng, thứ tự cạnh); hình dạng cụm dẫn chiếu; đếm lại độc lập số cụm, từ khoá, trigger; dẫn chiếu ra văn bản khác, số trần, hậu tố; bắt dữ liệu hỏng; kiểm A2 không import A1 |
| `test_a3.py` | 19 | hai quy tắc ngoại lệ, đếm trigger, `unhandled`, các tình huống `ValueError` |
| `test_a4.py` | 63 | văn phạm chỉ thị R1 đến R6, nội dung trong nháy, từng hàm áp dụng, ngày hiệu lực, cạnh theo văn bản cha, snapshot, các mã lỗi, mã có hậu tố |
| `test_a4_llm.py` | 14 | tầng LLM với proposer giả (xem mục 7.5) |
| `test_a5.py` | 54 | từng phép kiểm 1a đến 4f, kể cả dữ liệu cố ý làm hỏng để xem phép kiểm có bắt không |
| `test_a6.py` | 23 | mệnh đề, nút điều kiện, mã băm, `kind`, dẫn chiếu trong mệnh đề, unhandled, A6 phủ đúng phần A3 để lại |
| `test_a7.py` | 32 | `EdgeSet`, trùng chữ, từng nhóm kiểm 7a đến 7g, đồ thị theo ngày, nút văn bản, cả 8 văn bản dev |
| `test_a8.py` | 15 | dựng dữ liệu trang, nhúng an toàn, đọc dữ liệu A7 thật, CLI |
| `test_eval_gold.py` | 5 | quy tắc chọn mẫu, tính precision/recall, từ chối khi chưa gán đáp án |
| `test_eval_ext_amend.py` | 2 | câu gốc phải đúng nguyên văn trong file nguồn; chế độ tắt LLM không bao giờ áp sai |

File test là script chạy thẳng (`python -I tests/test_a2.py`), gồm các hàm `test_*` và một `main()` in dòng tổng kết `tổng test lỗi: N`. Không dùng khung kiểm thử bên ngoài (pytest). Trên Windows nên chạy `python -X utf8 -I tests/test_a2.py` để in tiếng Việt đúng.

**Các kiểu test được dùng:**
- *Dữ liệu dựng tay:* đồ thị nhỏ, đơn vị nhỏ, để thử từng quy tắc riêng lẻ (ví dụ `test_mini_dangling_and_source_closed_after_unit_is_closed`).
- *Đếm lại độc lập:* đếm số cụm, số trigger, số nút, số cạnh bằng một cách khác với code chính (cộng số dòng của các file nguồn, đếm bằng bộ đếm riêng) rồi so (ví dụ `test_refs_keywords_reconcile_with_independent_count`, `test_files_match_independent_counts`). Bảng số kỳ vọng `EXPECTED` của A5 và A7 cũng được kiểm theo cách này, không chỉ chép từ kết quả chạy.
- *Cố ý làm hỏng:* đưa vào dữ liệu sai rồi xem bước kiểm có phát hiện không (`test_check_catches_corrupted_data`, `test_check_graph_catches_each_kind_of_problem`).
- *Fail-closed ở dòng lệnh:* khi có lỗi thì thoát mã 1 và không ghi file (`test_cli_stops_and_writes_nothing_on_error`).
- *Khớp chéo giữa hai bước:* với từng văn bản trong 8 văn bản dev, tập cạnh `dangling` của A7 bằng đúng cờ cạnh đứt của A4 (`test_every_dev_document_gives_a_consistent_graph_and_matches_a4_flags`).
- *Kiểm tra bằng phá thử (mutation):* với A8, cố ý phá 5 chỗ trong `a8_viz.py` (bỏ thoát ký tự `<`, bỏ chặn loại cạnh lạ...) và xác nhận cả 5 lần test đều báo lỗi.
- *Client giả cho LLM:* mọi test của tầng LLM chạy không cần mạng và không cần API key.

### 8.2 `src/run_all.py`: chạy lại toàn bộ

Mặc định lệnh chỉ chạy **9 bước chính** (A1 đến A7). Hai nhóm phụ là tùy chọn, bật bằng cờ: `--a8` thêm bước dựng trang xem đồ thị, `--tests` thêm bộ kiểm thử ngoài và các bộ test (`--a8 --tests` thì đủ 12 bước). Lệnh in **một dòng cho mỗi bước**: tên bước ghi trước, rồi `OK` kèm số giây hoặc `LỖI` khi bước xong, không in từng lệnh con. Bước lỗi thì in lệnh hoặc bộ test bị lỗi cùng đầu ra của nó rồi thoát mã 1, các bước sau không chạy (riêng bước test chạy hết các bộ rồi mới báo). Đạt hết thì dòng cuối là `XONG: 9/9 bước` (hoặc `12/12` khi bật cả hai cờ). Thứ tự:

1. **Sáu bước đầu, mỗi bước chạy lần lượt cho cả hai nguồn** (`5dieu` và `p4`): A1, A2 (cấu trúc rồi `--refers-to`), A3, A6, A5, A7.
2. **A4 cho văn bản dev:** với mỗi nguồn chạy 8 văn bản dev riêng lẻ và bộ ghép `dev01+dev02` (9 lần mỗi nguồn), cộng thêm `dev01_full` trên p4: tổng 19 lần `apply`. Với mỗi lần ghi thêm snapshot tại 2027-01-01 (riêng `dev02` tại 2027-07-01, riêng `dev01+dev02` tại cả hai ngày, `dev01_full` không có snapshot).
3. **A5 với bước 4 (phiên bản)** cho 3 bộ: `5dieu` với `dev01+dev02`, `5dieu` với `dev04_bo_sung`, `p4` với `dev01_full`.
4. **A7 theo ngày** cho p4 với `dev05_bai_bo_ds` tại 2027-01-01.
   *Từ đây là các bước tùy chọn:* `--a8` thêm A8 (dựng ba trang xem đồ thị, gồm bản tại ngày 2027-01-01), `--tests` thêm hai bước sau.
5. **Bộ kiểm thử ngoài** `eval_ext_amend.py --llm off` (không gọi LLM; chế độ `replay` chạy riêng khi đã có cache).
6. **10 bộ test**: `test_a1` đến `test_a7`, `test_a4_llm`, `test_eval_gold`, `test_eval_ext_amend`. Bộ nào có dòng cuối khác `tổng test lỗi: 0` thì lệnh báo lỗi.

`test_a8.py` **chưa nằm trong** danh sách test của `run_all.py` (chạy riêng); chính A8 chạy khi bật `--a8`.

**Cách dùng làm hồi quy.** `run_all.py` ghi đè đúng các file kết quả đang có trong `data/processed` và `docs`, với cùng tham số đã dùng để sinh chúng. Sau khi chạy, `git diff --stat data/ docs/` cho thấy bước sửa vừa rồi đổi những đầu ra nào. Đổi đúng những file dự kiến là bình thường; đổi file ngoài dự kiến là dấu hiệu lỗi. Với Pha 1, kỳ vọng là không có file nào đổi.

### 8.3 Lịch sử commit

4 commit ban đầu (A1 đến A7), cộng 15 commit sửa theo rà soát. Mỗi bước sửa là một commit riêng, dễ xem lại; mã commit của từng bước ở mục 6.3.

### 8.4 Giới hạn của test (nên nói thẳng với thầy)

Test cho thấy *code làm đúng điều người viết nghĩ*. Test không chứng minh *người viết nghĩ đúng*, vì 8 văn bản dev và các con số kỳ vọng đều do cùng người làm code soạn. Bộ 19 câu thật (mục 7.4) là bằng chứng độc lập đầu tiên cho A4, nhưng còn nhỏ và chưa chạy tầng LLM. Để có số đo khách quan, cần:
1. người khác gán đáp án cho 11 Điều mẫu (khung đã sẵn, mục 6.3, bước 3.2a);
2. bộ văn bản sửa đổi giả định do học viên hỗ trợ soạn, như đề cương đã ghi.

---

## 9. Giới hạn và việc chưa làm

**Giới hạn của phần đã làm:**
- Chỉ bắt quan hệ **viết tường minh**, như "trừ trường hợp", "không áp dụng", "theo quy định tại". Quan hệ ngầm (ví dụ khoản 1 Điều 621 chặn Điều 626 mà không có từ nối) chưa có.
- Ngoại lệ chưa phân biệt **phản bác** (kết luận ngược lại) với **vô hiệu hoá** (chỉ làm quy tắc gốc không áp dụng).
- Hai chỗ chưa tách được: phần điều kiện với phần hệ quả trong một mệnh đề ngoại lệ (Điều 646 khoản 3); và phạm vi áp dụng của ngoại lệ khi nó chỉ áp cho một vế của câu (Điều 617 khoản 1 điểm a).
- Chỉ chạy cho BLDS 2015. Một số chỗ vẫn ghi cứng theo tên file.
- A4 chỉ hiểu các mẫu câu chuẩn; tầng LLM chưa chạy thật.
- Chưa có con số precision/recall thật, vì chưa có đáp án do người gán.
- Trang xem đồ thị (A8): chưa có thanh trượt thời gian (mỗi ngày là một file riêng); phần JavaScript chưa có test tự động, chỉ thử tay bằng trình duyệt không giao diện; các file A8 chưa commit.

**Các bước tiếp theo của đề cương, chưa làm (ngoài phạm vi KG hiện tại):** LLM phân loại quan hệ; sổ khái niệm và đồ thị khái niệm; trích quy tắc; kiểm tra ở mức quy tắc kèm LLM tự sửa; biên dịch sang s(CASP) và hỏi đáp; bộ tình huống có nhãn độ sâu ngoại lệ; thực nghiệm so sánh.

---

## 10. Gợi ý khi báo cáo với thầy

**Ba ý chính nên nói:**
1. Đã xây xong **tự động** đồ thị tri thức cho phần Thừa kế: 225 nút, 481 cạnh. Đồ thị có cây cấu trúc đầy đủ, dẫn chiếu, ngoại lệ tường minh và phiên bản theo thời gian, cộng 7 nhóm kiểm tra tự động.
2. Đã tự rà soát và **chặn các lỗi "im lặng làm sai"**. Hệ thống dừng và báo khi gặp câu chưa hiểu, thay vì đoán.
3. Phần cập nhật đã chuyển sang **neuro-symbolic** đúng tinh thần đề cương: LLM chỉ đề xuất, máy kiểm bằng luật.

**Câu hỏi thầy có thể hỏi, và câu trả lời:**

| Câu hỏi | Trả lời |
|---|---|
| Độ chính xác bao nhiêu? | Chưa có số thật. Đã có khung chấm điểm (mẫu 11 Điều); cần người gán đáp án độc lập, không xem kết quả của máy |
| Sao không dùng LLM đọc luôn từ đầu? | Theo đề cương, LLM hay nối sai ngoại lệ lồng nhau và đặt tên khái niệm không nhất quán. Phần chắc chắn làm bằng luật để kiểm được; LLM chỉ dùng chỗ cần hiểu ngôn ngữ, và luôn bị kiểm lại |
| Văn bản sửa đổi lấy đâu ra? | BLDS 2015 phần Thừa kế chưa bị sửa. Đang dùng 8 văn bản tự soạn, cộng 19 câu thật mượn từ Luật 85/2025/QH15. Bộ chính thức sẽ do học viên hỗ trợ soạn |
| Quan hệ ngầm thì sao? | Chưa làm. Theo đề cương, LLM đề xuất và bộ quét kiểm lại |
| Cập nhật có phải dựng lại cả đồ thị không? | Không. Chỉ tính lại cho đơn vị có chữ thay đổi; phiên bản cũ được giữ lại |
| "Khử trùng lặp" làm thế nào? | Bộ ba trùng được gộp tự động; đơn vị trùng chữ được gắn nhãn, không gộp. Khử trùng lặp ở mức khái niệm sẽ làm qua sổ khái niệm |
| Cho xem đồ thị được không? | Được. Mở `data/processed/a8/a8_blds2015_p4.html` bằng trình duyệt (không cần mạng): 225 nút, kéo thả được, bấm vào nút để xem chữ gốc và các quan hệ. Có thêm bản tại ngày 01/01/2027 sau khi áp văn bản dev05, trong đó các đơn vị đã bị bãi bỏ hiện thành vòng đứt nét |

---

## 11. Bản đồ file

| Chỗ | Có gì |
|---|---|
| `src/a1_parse.py` … `src/a7_graph.py` | 7 bước chính |
| `src/a4_llm.py` | Gọi Claude API (tầng LLM của A4) |
| `src/run_all.py` | Chạy lại toàn bộ và chạy test |
| `tests/test_*.py` | 281 test trong 11 file (266 trong `run_all.py`, 15 của A8 chạy riêng) |
| `tests/eval_gold.py` | Chấm precision/recall so với đáp án gán tay |
| `tests/eval_ext_amend.py` | Chạy bộ thử 19 câu sửa đổi thật |
| `utils/a8/` | Phần phụ, không thuộc 7 bước chính: trang xem đồ thị (A8). `a8_viz.py` và `a8_template.html` đọc đồ thị A7 và ghi một file HTML vào `data/processed/a8/`; `vendor/cytoscape.min.js` là thư viện Cytoscape.js 3.30.2 (MIT), nhúng vào trang để mở offline |
| `utils/render_report.py` | Dựng `TONG_HOP_CONG_VIEC.html` từ file `.md` này |
| `data/processed/` | Mọi file kết quả, chia thư mục con theo bước: `a1/` đến `a8/`; riêng A4 chia thêm theo tên văn bản sửa đổi (`a4/<tên>/`). Đồ thị nằm ở `a7/a7_blds2015_p4_nodes.jsonl` và `a7/a7_blds2015_p4_edges.jsonl`; trang xem đồ thị là `a8/a8_blds2015_p4.html` |
| `data/llm_cache/a4/` | Kết quả LLM đã lưu để chạy lại tất định. **Chưa tồn tại** vì chưa chạy `--llm live` |
| `data/gold/` | Mẫu để gán đáp án (chờ người gán) |
| `docs/a*_report_*.txt` | Báo cáo của từng bước |
| `docs/a4_quyet_dinh.txt`, `docs/a6_a7_quyet_dinh.txt`, `utils/a8/a8_quyet_dinh.txt`, `docs/pham_vi_mo_rong.txt` | Mọi quyết định thiết kế và phạm vi, kèm lý do |
| `review_a1_a7_findings.md` | Báo cáo rà soát 22 vấn đề và bảng theo dõi đã sửa |
| `plan_sua_a1_a7.md` | Kế hoạch sửa và các khoảng trống so với đề cương |

**Chạy lại toàn bộ** (cần Python 3.10 trở lên):

```
/opt/homebrew/bin/python3.13 -I src/run_all.py
```

Chạy xong mà mọi dòng bước đều `OK` và dòng cuối là `XONG` nghĩa là các bước đã chạy đều đạt; muốn kiểm cả 10 bộ test thì chạy với `--tests`.

Trên Windows, từng bộ test chạy bằng `python -X utf8 -I tests/test_a1.py` (và tương tự cho các file khác). Cờ `-X utf8` để in tiếng Việt đúng. Trang xem đồ thị: `python -I utils/a8/a8_viz.py data/raw/blds2015_p4.md` (xem mục 4, A8).
