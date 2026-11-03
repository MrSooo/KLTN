# Chi tiết từng bước A1 → A7: làm gì, code gì, từ vào ra bằng cách nào

Tài liệu đọc nội bộ để nắm nhanh code. Mỗi bước theo một khuôn: **Việc làm · Vào → Ra · Cách làm · Code chính · Ví dụ thật · Tự kiểm · Giới hạn · Chạy lại.**

Số liệu lấy từ file trên đĩa ngày 04/11/2026 (test chạy ngày 03/11). Code ghi dạng `file:dòng`.

---

## 0. Đọc trước: bức tranh chung

Pipeline đọc văn bản luật (Markdown) và dựng thành **đồ thị tri thức**: mỗi Điều / Khoản / Điểm là một nút, mỗi quan hệ giữa chúng là một cạnh.

```
blds2015_p4.md   (Điều 609–662)
  A1  tách Chương/Điều/Khoản/Điểm, gán mã ......... → a1_triples        1173 bộ ba
  A2  cạnh cấu trúc + cạnh dẫn chiếu .............. → a2_edges 430 · a2_refs 25
  A3  ngoại lệ tường minh (2 mẫu câu) ............. → a3_exceptions     4 cạnh
  A6  ngoại lệ chung "trừ trường hợp ..." ......... → a6_conditions 5 nút · a6_exceptions 10 cạnh
  A5  kiểm tra độc lập A1–A3 (không sinh dữ liệu)  → docs/bao_cao_chay/a5/a5_report_*.txt
  A7  gộp thành MỘT đồ thị + 7 nhóm kiểm .......... → a7_nodes 225 · a7_edges 481
  A4  văn bản sửa đổi → phiên bản mới ............. → a4_*_versions … (A7 đọc lại để dựng đồ thị tại một ngày)
```

Thứ tự chạy thật trong `src/run_all.py`: A1 → A2 → A3 → A6 → A5 → A7, rồi A4 cho từng văn bản sửa đổi, A5 với `--versions`, A7 với `--date`.

**Năm nguyên tắc chung của mọi bước:**
1. **Mỗi bước đọc file của bước trước** và ghi file riêng vào `data/processed/<bước>/`, kèm báo cáo chữ ở `docs/bao_cao_chay/<bước>/`.
2. **Dùng mẫu câu (regex), không dùng LLM** ở A1–A7. Kết quả giống nhau mỗi lần chạy và kiểm được. (LLM chỉ có ở tầng tuỳ chọn của A4.)
3. **Fail-closed:** gặp dạng câu chưa có quy tắc thì **dừng, thoát mã 1, không ghi file**. Thà dừng còn hơn sai mà không biết.
4. **Mỗi cạnh có `evidence`:** câu nguyên văn làm bằng chứng, để người đọc kiểm.
5. **Có số đối chiếu cứng:** A5 và A7 có bảng `EXPECTED` (số đơn vị, nút, cạnh). Kết quả lệch số là bị báo.

**Số liệu chính trên Điều 609–662:**

| | Số |
|---|---|
| Đơn vị | 54 Điều, 115 Khoản, 46 Điểm (215), cộng 4 Chương |
| Bộ ba A1 | 1173 |
| Cạnh cấu trúc A2 | 430 (215 `contains` + 215 `part_of`) |
| Cạnh dẫn chiếu A2 | 25 `refers_to` (7 trong cùng Điều, 18 sang Điều khác), 2 chưa nối được |
| Ngoại lệ tường minh | 4 (A3) + 10 (A6) = 14 `exception_of` |
| Đồ thị A7 | 225 nút, 481 cạnh |
| Test | 287 hàm test trong 11 file, đều đạt |

---

## A1. Tách văn bản thành đơn vị và bộ ba

**Việc làm.** Đọc file Markdown, tách thành Chương, Điều, Khoản, Điểm. Gán mỗi đơn vị một mã ổn định (`BLDS2015.D621.K1.a`). Ghi thành các bộ ba `(s, p, o)` = (đơn vị, thuộc tính, giá trị).

**Vào → Ra.**
- Vào: `data/raw/blds2015_p4.md`.
- Ra: `data/processed/a1/a1_triples_blds2015_p4.jsonl` (1173 dòng `{"s","p","o"}`) và `docs/bao_cao_chay/a1/a1_notes_blds2015_p4.txt` (chỗ cần người xem, hiện có 1 dòng).

**Cách làm** (4 step trong code, chạy riêng bằng `-s 1..4`):
1. **Nhìn dữ liệu thô** (step 1): in từng dòng, quét ký tự lạ. Chỉ để kiểm, không ghi file.
2. **Tokenize** (step 2): mỗi dòng thành một token `chuong / dieu / khoan / diem / para`, nhận bằng 4 regex. Dòng bỏ qua phải có lý do (trống, `---`, tiêu đề). Dòng đáng ngờ thì dừng.
3. **Parse** (step 3): máy trạng thái dựng cây Chương > Điều > Khoản > Điểm và kiểm thứ tự: Điều 609→662 liền nhau, Khoản 1, 2, 3 liền nhau, Điểm theo bảng chữ.
4. **Ghi bộ ba** (step 4): chỉ ghi khi parse sạch.

**Code chính** (`src/a1_parse.py`):

| Hàm | Việc |
|---|---|
| `RE_DIEU / RE_KHOAN / RE_DIEM / RE_CHUONG` `:31-37` | Nhận loại dòng. `\\?` vì Markdown viết `621\.` |
| `DIEM_LETTERS` `:28` | Bảng chữ Điểm của luật: `abcdđeghiklmnopq` (có `đ`, không có f j w z) |
| `tokenize` `:84` | Thử 4 regex theo thứ tự. Không khớp thì ghi vào `skipped` hoặc `suspicious`, không bỏ qua âm thầm |
| `parse` `:151` | Máy trạng thái. Lỗi thu vào danh sách rồi **đồng bộ lại bộ đếm** để một lỗi không kéo theo lỗi giả |
| `diem_code` `:146` | Điểm `đ` thành `dd` trong mã (`BLDS2015.D617.K1.dd`), mã không chứa chữ có dấu |
| `to_triples` `:306` | Mỗi đơn vị thành dòng `type, number, heading, chuong, text, version=1, source_line` |
| `fail_if_errors` `:297` | Còn lỗi parse thì thoát 1, không ghi file |

**Ví dụ thật.** Dòng `**1\.** Những người sau đây không được quyền hưởng di sản:` (dòng 98) thành:

| s | p | o |
|---|---|---|
| `BLDS2015.D621.K1` | `type` / `number` | `khoan` / `1` |
| `BLDS2015.D621.K1` | `text` | `Những người sau đây không được quyền hưởng di sản:` |
| `BLDS2015.D621.K1` | `version` / `source_line` | `1` / `98` |

Số đếm toàn bộ: 252 token (4 Chương, 54 Điều, 115 Khoản, 46 Điểm, 33 đoạn chữ). Bộ ba theo loại: `type` 219, `number` 219, `version` 219, `source_line` 219, `heading` 58, `chuong` 54, `text` 185.

**Tự kiểm.** 11 test (`tests/test_a1.py`). Đáng chú ý:
- **Đếm độc lập:** số đơn vị (215) và bộ ba (1173) khớp số đếm bằng grep/awk, không qua parser.
- **Bảo toàn từ:** tập từ của file gốc bằng tập từ của mọi đơn vị. Bắt từ bị mất, thừa, đổi.
- Mã không trùng, `d` khác `dd`, không còn ký tự Markdown, mỗi Điều thuộc đúng Chương.

**Giới hạn.**
- Dòng `## Chương XXI – QUY ĐỊNH CHUNG` (dòng 3) **do dự án thêm vào file nguồn**, vì nguồn thiếu tiêu đề Chương cho 15 Điều đầu.
- Đoạn chữ đứng ngay sau danh sách Điểm (Điều 643 Khoản 2, dòng 303) được nối vào Khoản, không vào Điểm. Có ghi trong `a1_notes`.
- Chỉ nhận file đã khai báo dãy Điều trong `EXPECTED_DIEU`.

**Chạy lại.** `python -I src/a1_parse.py data/raw/blds2015_p4.md` (ghi đè file đầu ra) · `python -I tests/test_a1.py`.

---

## A2. Cạnh cấu trúc và cạnh dẫn chiếu

**Việc làm.** (a) Nối cha–con: Chương chứa Điều, Điều chứa Khoản, Khoản chứa Điểm. (b) Tìm các câu dẫn chiếu ("theo quy định tại khoản 1 Điều 616") và nối nguồn tới đích.

**Vào → Ra.**
- Vào: `a1_triples` (chỉ đọc file, không import code A1).
- Ra: `a2_edges_*.jsonl` (430 cạnh), `a2_refs_*.jsonl` (25 cạnh), `docs/bao_cao_chay/a2/a2_unresolved_*.txt` (2 dòng).

**Cách làm.**

*A2a, cạnh cấu trúc.* Cha của Khoản/Điểm suy ra từ mã: bỏ đoạn cuối (`D621.K1.a` → `D621.K1`). Cha của Điều là Chương, lấy từ thuộc tính `chuong`. Mỗi cặp cha–con thành **hai cạnh**: `(cha, contains, con)` và `(con, part_of, cha)`. Phần kiểm so loại cha theo thuộc tính `type` của A1 chứ không theo mã, để A1 đánh mã sai thì lộ ra.

*A2b, dẫn chiếu.* Ba bước:
1. **Tìm cụm** bằng `CHAIN_RE`: chuỗi các mục "khoản/điểm/Điều + số, chữ hoặc *này*", nối bằng dấu phẩy, "và", "hoặc". Ví dụ: `khoản 1 và khoản 3 Điều 616 của Bộ luật này`.
2. **Đổi cụm thành mã đích** (`group_targets`). Các mục có cấp giảm dần (điểm > khoản > Điều). Mục cấp cao nhất đứng cuối **dùng chung** cho các mục trước nó: "khoản 1 và khoản 3 Điều 616" ra `D616.K1` và `D616.K3`. "Điều này / khoản này" là tổ tiên đúng loại của đơn vị chứa câu.
3. **Xem đuôi sau cụm** (`tail_of`): "của Bộ luật này" là chính văn bản. Tên luật khác thì ghi là dẫn chiếu ra ngoài. Dạng chưa có quy tắc (khoảng "từ … đến …", danh sách số trần) thì **báo lỗi dừng**.

Đích mà Điều của nó không nằm trong tập đang xử lý (Điều 71, Điều 236) thì **không tạo cạnh**, ghi vào `unresolved`.

**Code chính** (`src/a2_edges.py`):

| Hàm | Việc |
|---|---|
| `parent_of` `:62`, `build_edges` `:74` | Suy cha, dựng cặp `contains`/`part_of` |
| `check_edges` `:90` | Không trùng, đối xứng, mỗi Khoản/Điểm đúng một cha, cha đúng bậc |
| `CHAIN_RE` `:174`, `find_refs` `:204` | Tìm cụm dẫn chiếu, đếm từ khoá bị loại để không sót |
| `group_targets` `:294` | Cụm → mã đích (quy tắc cấp giảm dần, "này") |
| `tail_of` `:350` | Phân loại đuôi: văn bản này, văn bản khác, chưa hỗ trợ |
| `build_refs` `:378`, `check_refs` `:408` | Dựng cạnh, kiểm: không tự trỏ, không trùng, `evidence` nằm trong text nguồn |
| `TRIGGER_RE` `:479` | Tìm cụm "trừ", "ngoại trừ", "không áp dụng" (cho A3 dùng) |

**Ví dụ thật.**
- Cấu trúc: `BLDS2015.D621.K1.a part_of BLDS2015.D621.K1` (và chiều ngược `contains`).
- Dẫn chiếu: `D617.K1 → D616.K1` và `D617.K1 → D616.K3`, cùng `evidence = "khoản 1 và khoản 3 Điều 616 của Bộ luật này"`.
- Chưa nối được: `D611.K1` "khoản 2 Điều 71 của Bộ luật này" (Điều 71 không thuộc Phần 4).

**Tự kiểm.** 43 test. Có đếm lại độc lập số `refers_to`, test nhiều dạng cụm ("này", nhiều cấp, đuôi lạ), test "đưa dữ liệu hỏng thì bị bắt".

**Giới hạn.** Dẫn chiếu ra văn bản khác không thành cạnh. Mẫu chỉ nhận các dạng cụm đã liệt kê, dạng khác dừng báo lỗi.

**Chạy lại.** `python -I src/a2_edges.py data/raw/blds2015_p4.md` (ghi `a2_edges`) · thêm `--refers-to` (ghi `a2_refs` và `a2_unresolved`) · `--refs`, `--triggers` chỉ in, không ghi.

---

## A3. Ngoại lệ tường minh

**Việc làm.** Tìm các câu **nói thẳng** đây là ngoại lệ của quy tắc khác, và nối bằng cạnh `exception_of`. Chiều cạnh: **nguồn là phần ngoại lệ, đích là quy tắc bị ngoại trừ.**

**Vào → Ra.** Vào: `a1_triples`, cạnh `contains` của A2a. Ra: `a3_exceptions_*.jsonl` (4 cạnh, có `evidence` và `method`) và `docs/bao_cao_chay/a3/a3_unhandled_*.txt` (9 dòng).

**Cách làm: đúng hai quy tắc, không có bộ khớp tổng quát.**

| Quy tắc | Dấu hiệu | Cạnh sinh ra |
|---|---|---|
| `not_apply_pattern` | Đơn vị U có "không áp dụng", và **ngay trước nó** là một cụm dẫn chiếu | U `exception_of` mỗi đích của cụm |
| `except_list_pattern` | Text của U có "trừ" và **kết thúc bằng "sau đây:"** | Mỗi đơn vị con của U `exception_of` U |

Mỗi cụm "trừ / ngoại trừ / không áp dụng" (từ A2) phải rơi vào **đúng một** trong hai: đã xử lý (có cạnh) hoặc `unhandled`. Phần kiểm đếm cho khớp, nên không có cụm nào mất. **Không nới quy tắc để bắt thêm ca:** ca ngoài hai quy tắc là ngoại lệ chung (việc của A6).

**Code chính** (`src/a3_exceptions.py`): `phrase_before` `:51` (cụm dẫn chiếu đứng ngay trước), `find_exceptions` `:68` (hai quy tắc), `check_exceptions` `:111` (không trùng, không tự trỏ, `evidence` đúng chỗ, đếm khớp).

**Ví dụ thật.**
- `D632.K1, K2, K3 → D632` (quy tắc 2): Điều 632 "Mọi người đều có thể làm chứng …, trừ những người sau đây:", ba Khoản là ba nhóm bị loại.
- `D644.K2 → D644.K1` (quy tắc 1): khoản 2 "Quy định tại khoản 1 Điều này **không áp dụng** đối với …".

**Tự kiểm.** 19 test (ví dụ dựng tay cho từng quy tắc, dạng khớp nhưng spec không nói thì phải báo lỗi, file trên đĩa).

**Giới hạn.** Chỉ 4 cạnh. 9 câu ngoại lệ chung "trừ trường hợp …" nằm ở `a3_unhandled` và do A6 nhận (đúng 9 đơn vị).

**Chạy lại.** `python -I src/a3_exceptions.py data/raw/blds2015_p4.md`.

---

## A4. Cập nhật theo văn bản sửa đổi (phiên bản)

**Việc làm.** Khi có văn bản sửa đổi, **không xoá nút cũ**. Đơn vị bị sửa nhận phiên bản mới, phiên bản cũ ghi ngày hết hiệu lực. Cạnh được tính lại cho đơn vị đổi chữ. Lập danh sách đơn vị bị ảnh hưởng để kiểm lại.

**Vào → Ra.**
- Vào: văn bản gốc, cạnh gốc của A2/A3 (chỉ đọc), và các văn bản sửa đổi (Markdown, ví dụ `data/dev_amend/dev02_sua_khoan.md`).
- Ra (mỗi văn bản một thư mục `data/processed/a4/<name>/`): `versions.jsonl` (mọi phiên bản), `amend_edges.jsonl` (văn bản nào sửa đơn vị nào), `edge_changes.jsonl` (cạnh thêm/đóng), `changed.json`, `impact.json`, cộng `docs/bao_cao_chay/a4/a4_report_<name>.txt`. Lệnh `snapshot` xuất văn bản luật tại một ngày.

**Cách làm.**
1. **Ngày hiệu lực:** phải có đúng một ngày "có hiệu lực từ ngày …", sau ngày hiệu lực của văn bản gốc (2017-01-01).
2. **Nhận chỉ thị** từng dòng bằng regex. Có 6 loại (bảng dưới).
3. **Đọc nội dung mới** trong dấu nháy “…” và dựng cây Khoản/Điểm, kiểm thứ tự (Khoản 1, 2, 2a, 3 … / Điểm a, b, c, d, đ …).
4. **Áp lên kho phiên bản** (`Store`). Sửa: đóng bản cũ (`effective_to` = ngày hiệu lực), tạo bản `version + 1`. Bãi bỏ: đóng cả cây con. Bổ sung: tạo mới, kiểm "vào sau". Chỉ đơn vị **thật sự đổi chữ** mới nhận phiên bản mới.
5. **Tính lại cạnh:** chạy lại A2b và A3 trên text mới của đơn vị đổi, so với cạnh cũ, ghi `add` / `close` vào `edge_changes`. Cạnh gốc không bị xoá khỏi file gốc.
6. **Cờ cạnh đứt:** cạnh `refers_to` / `exception_of` mà nguồn còn hiệu lực nhưng đích vừa bị đóng.
7. **Tập ảnh hưởng:** đơn vị khác dẫn chiếu tới, hoặc có quan hệ ngoại lệ với, đơn vị đã đổi hay bị đóng.
8. **Chỉ ghi file khi không có lỗi nào.** Có lỗi thì chỉ ghi báo cáo, thoát 1.

Hiệu lực tính theo nửa khoảng `[effective_from, effective_to)`: đang hiệu lực tại ngày T nếu `from ≤ T` và (`to` rỗng hoặc `to > T`).

**Sáu loại chỉ thị (văn phạm chuẩn):**

| Mã | Mẫu câu | `op` |
|---|---|---|
| R1 | "Khoản 1 Điều 621 được sửa đổi, bổ sung như sau: “…”" (hoặc "Thay thế …") | `replace_unit` |
| R2 | "Bổ sung Điều 621a vào sau Điều 621 như sau: “…”" (cả khoản, điểm) | `insert_unit` |
| R3 | "Bãi bỏ khoản 2 Điều 621." (nhiều đích) | `repeal_unit` |
| R4 | "Tên Điều 626 được sửa đổi như sau: “…”" | `rename_heading` |
| R5 | "Thay thế cụm từ “a” bằng cụm từ “b” tại …", "Bỏ cụm từ …", "Bổ sung cụm từ … vào sau …" | `phrase` |
| R6 | "Luật này thay thế Bộ luật dân sự năm 2015." | `replace_doc` |

**Code chính** (`src/a4_versions.py`):

| Hàm / lớp | Việc |
|---|---|
| `match_directive` `:437` | Nhận một dòng là chỉ thị R1–R6 (các regex `RE_R1…` ở `:398-426`) |
| `_parse_lines` `:650` | Vòng đọc văn bản sửa đổi, dựng danh sách `Directive` |
| `read_block` `:501`, `extract_body` `:532` | Lấy chữ trong dấu nháy cho chỉ thị cần nội dung |
| `Store` `:952` | Kho mọi phiên bản: `modify`, `close`, `create`, `subtree` |
| `apply_replace_unit` … `apply_replace_doc` `:1101-1214` | Áp từng loại chỉ thị |
| `recompute_edges` `:1249` | Tính lại `refers_to`/`exception_of`, ghi `add`/`close` |
| `impact_set` `:1023` | Tập đơn vị bị ảnh hưởng |
| `apply_series` `:1398` | Áp lần lượt các văn bản theo ngày hiệu lực |
| `active_rows` `:1511`, `render_markdown` `:1517` | Lọc đơn vị hiệu lực tại ngày T, xuất lại Markdown |

**Ví dụ thật** (`dev02_sua_khoan.md`, hiệu lực 2027-07-01): sửa khoản 1 Điều 621 thêm cụm "theo quy định của pháp luật", và Điểm b đổi "nuôi dưỡng" thành "nuôi dưỡng, chăm sóc".
- `versions`: 217 dòng = 215 đơn vị gốc + 2 phiên bản mới. `D621.K1` có v1 (`2017-01-01` → `2027-07-01`) và v2 (từ `2027-07-01`).
- Đổi chữ: `D621.K1` và `D621.K1.b`. Điểm a, c, d giữ nguyên (`named_unchanged`).
- Tập ảnh hưởng: `D621.K2` và `D644.K2` (cả hai dẫn chiếu tới `D621.K1`).

**Tự kiểm.** 63 test trong `test_a4.py`: từng loại chỉ thị, hơn 25 mã lỗi `E_*` (ví dụ `E_UNKNOWN_LINE`, `E_TARGET`, `E_OVERLAP`, `E_DATE_BEFORE_BASE`), 8 văn bản dev, snapshot khớp bản viết tay. Có thêm bộ kiểm thử ngoài: 19 câu thật của Luật 85/2025/QH15 (đổi số hiệu sang BLDS). Khi chưa bật LLM: 9 câu qua đường ký hiệu, 10 câu dừng báo lỗi, 0 câu áp sai. Sau đó A5 bước 4 kiểm lớp phiên bản.

**Tầng LLM (tuỳ chọn, `src/a4_llm.py`).** Dòng không khớp R1–R6 mặc định là **lỗi**. Với `--llm replay|live`, cả khối đó được gửi cho LLM đề xuất. LLM **không áp thẳng**: máy dựng lại thành câu chuẩn, parse bằng chính văn phạm trên, rồi kiểm ba điều (phủ đủ số hiệu, nội dung nguyên văn, cụm từ nguyên văn). Hỏng thì gửi lỗi cho LLM sửa, tối đa 3 lần. Mặc định tắt. **Chưa chạy với API thật.**

**Giới hạn.** BLDS 2015 chưa có văn bản sửa đổi thật, nên 8 văn bản dev là tự soạn. Không hỗ trợ "đánh số lại", "trở thành", ngày hiệu lực riêng cho một phần (báo lỗi). Tập ảnh hưởng hiện chỉ theo dẫn chiếu và ngoại lệ, chưa theo khái niệm hay quy tắc.

**Chạy lại.** `python -I src/a4_versions.py apply --base data/raw/blds2015_p4.md --amend data/dev_amend/dev02_sua_khoan.md --name p4_dev02_sua_khoan` · `snapshot --name p4_dev02_sua_khoan --date 2027-07-01`.

---

## A5. Kiểm tra độc lập A1–A3 và lớp phiên bản

**Việc làm.** Kiểm xem file của A1–A3 (và của A4 khi có `--versions`) có trùng hay hở chỗ nào không. **Không sinh dữ liệu mới.**

**Vào → Ra.** Vào: `a1_triples`, `a2_edges`, `a2_refs`, `a3_exceptions` (và `a4_*_versions` với `--versions`). Ra: `docs/bao_cao_chay/a5/a5_report_<tên>.txt`, ghi cả khi mọi thứ đạt.

**Cách làm.** Đọc thẳng từng dòng JSON, **không dùng lại hàm của A2** (`parent_of`, `load_units`), để phép kiểm độc lập với code đã sinh file. Mỗi kiểm có mã để tra:

| Bước | Kiểm |
|---|---|
| 1 (`1a–1e`) | Số đơn vị, số Điều, số Chương đúng `EXPECTED`; mỗi đơn vị đúng một dòng `type`; mỗi cặp `(s, p)` một lần |
| 2 (`2a–2f`) | Mỗi Khoản/Điểm đúng một cha; Điều có cha là Chương; cha = mã bỏ đoạn cuối; `contains` đối xứng `part_of`; số `part_of` khớp; cha đúng bậc |
| 3 | Không có bộ ba `(s, p, o)` lặp trong `a2_edges + a2_refs + a3_exceptions` (459 bộ ba, 0 lặp) |
| 4 (`4a–4f`) | Phiên bản liên tiếp 1, 2, 3; `previous_version` đúng; khoảng hiệu lực không chồng; **mọi mã của A1 còn trong versions** (không xoá nút); version 1 giữ nguyên nội dung A1; ngày hiệu lực gốc nhất quán |

**Code chính** (`src/a5_checks.py`): `check_codes` `:110`, `check_parents` `:144`, `check_duplicate_edges` `:205`, `check_versions` `:234`, `check_version1_content` `:290`, `check_base_dates` `:315`, bảng `EXPECTED` `:65`.

**Ví dụ thật** (báo cáo p4): `[1a] số đơn vị: 215, kỳ vọng 215 -> ĐẠT` · `[2d] contains 215, part_of 215 -> ĐẠT` · `[3] 459 bộ ba, 459 khác nhau, 0 bị lặp -> ĐẠT`. Kết luận: ĐẠT.

**Tự kiểm.** 54 test. Cách làm chính: **bơm lỗi vào dữ liệu dựng tay** (thêm cạnh trùng, bỏ một cha, nhảy phiên bản…) rồi xác nhận kiểm nào bắt.

**Giới hạn.** Số kỳ vọng ghi cứng theo tên file (`EXPECTED`), thêm văn bản mới phải sửa bảng. A5 không kiểm A6, A7 (hai bước đó tự kiểm).

**Chạy lại.** `python -I src/a5_checks.py data/raw/blds2015_p4.md [--versions <file>]`.

---

## A6. Ngoại lệ chung "…, trừ trường hợp X"

**Việc làm.** Câu "…, trừ trường hợp có thỏa thuận khác" có phần ngoại lệ **không phải một Điều/Khoản cụ thể** mà là một *điều kiện*. A6 tạo một **nút điều kiện** cho phần đó và nối nó vào quy tắc bị ngoại trừ.

**Vào → Ra.** Vào: `a1_triples`. Ra: `a6_conditions_*.jsonl` (5 nút), `a6_exceptions_*.jsonl` (10 cạnh), `docs/bao_cao_chay/a6/a6_unhandled_*.txt` (rỗng).

**Cách làm.**
1. Tìm "(ngoại) trừ trường hợp" bằng `GENERAL_RE`. **Mệnh đề X** chạy đến hết đoạn, bỏ dấu cuối (`. ; : ,`). Nếu "trừ trường hợp" đứng **đầu đoạn** ("Trừ trường hợp X, quy tắc…") thì X dừng ở dấu phẩy đầu tiên.
2. **Nút điều kiện:** mã `BLDS2015.C_<8 ký tự đầu của sha1>` tính từ mệnh đề đã chuẩn hoá. Mệnh đề giống nhau thì cùng một nút. Dùng băm để mã ổn định giữa các phiên bản (đánh số tuần tự sẽ đổi khi tập câu đổi).
3. **Cạnh:** nút điều kiện `exception_of` đơn vị chứa câu (`general_except_pattern`).
4. **Phân loại nút** (`kind`): `tuy_nghi` ("có thỏa thuận khác"), `dan_chieu_mo` ("pháp luật có quy định khác"), còn lại `cu_the`. Hai loại đầu là câu chung chung, một nút nối nhiều Điều không liên quan, nên khi xét liên thông đồ thị không coi là cầu nối.
5. **Dẫn chiếu trong mệnh đề:** nếu X nhắc tới Điều T có trong tập, thêm cạnh `T exception_of` đơn vị (`general_except_ref`).
6. **Phân việc với A3:** bỏ qua đơn vị có text kết thúc "sau đây:" (A3 lo). Câu "không được áp dụng" (A3 không bắt) được ghi vào `unhandled`, không mất.

**Code chính** (`src/a6_general_exceptions.py`): `GENERAL_RE` `:52`, `norm_text` `:71`, `condition_kind` `:77`, `condition_id` `:82`, `find_general` `:96`, `clause_targets` `:142`, `check_general` `:156`.

**Ví dụ thật.**
- Nút `C_426b8c79` "có thỏa thuận khác" (`tuy_nghi`) nối tới **5 đơn vị**: `D615.K1`, `D615.K3`, `D659.K1`, `D662.K1`, `D662.K2`.
- Điều 619 "…, trừ trường hợp thừa kế thế vị theo quy định tại Điều 652": nút `C_7ee9e1d1 → D619`, và vì mệnh đề nhắc Điều 652 nên thêm cạnh **`D652 → D619`** (đây là cạnh ngoại lệ giữa hai Điều khác nhau).
- Tổng: 9 cạnh `general_except_pattern` + 1 cạnh `general_except_ref` = 10. Đúng 9 đơn vị mà A3 để lại.

**Tự kiểm.** 23 test (mệnh đề đầu đoạn, hết đoạn, hai "trừ trường hợp" trong một đơn vị phải báo lỗi, đếm trigger khớp, mã nút ổn định).

**Giới hạn.** Hai "trừ trường hợp" trong một đơn vị, mệnh đề rỗng, hoặc "trừ trường hợp" đầu đoạn mà không có dấu phẩy: **báo lỗi**, không đoán. Phần tách điều kiện / hệ quả và phạm vi vế (ví dụ D646.K3, D617.K1.a) cần gán tay, ghi là giới hạn trong `docs/quyet_dinh/a6_a7_quyet_dinh.txt`.

**Chạy lại.** `python -I src/a6_general_exceptions.py data/raw/blds2015_p4.md`.

---

## A7. Đồ thị gộp và kiểm tra

**Việc làm.** Gộp kết quả A1, A2, A3, A6 thành **một đồ thị** (file nút + file cạnh), khử trùng, kiểm tra. Có thể dựng đồ thị **tại một ngày bất kỳ** từ kết quả A4.

**Vào → Ra.**
- Trạng thái gốc: đọc `a1_triples`, `a2_edges`, `a2_refs`, `a3_exceptions`, `a6_conditions`, `a6_exceptions`. Ra `a7_<stem>_nodes.jsonl` (225), `a7_<stem>_edges.jsonl` (481), `docs/bao_cao_chay/a7/a7_report_*.txt`.
- Tại ngày: thêm `--versions <a4 versions> --date YYYY-MM-DD`.

**Cách làm (trạng thái gốc).**
1. **Nút:** đơn vị (Điều, Khoản, Điểm), Chương, nút điều kiện (A6), nút văn bản gốc. 225 = 54 + 115 + 46 + 4 + 5 + 1.
2. **Cạnh:** gom `(s, p, o)` từ các file. Cạnh trùng thì **gộp thành một** và ghi `sources` (`EdgeSet`). Thêm cạnh nút văn bản ↔ Chương để đồ thị là cây văn bản > Chương > Điều > Khoản > Điểm.
3. **Bản sao chữ:** đơn vị cùng loại có chữ giống hệt đơn vị đứng trước thì đánh `status = same_text` và nối cạnh `same_text_as`. **Không gộp nút**, vì mỗi đơn vị là một vị trí pháp lý riêng. Gọi là "trùng chữ", không phải "dư thừa".
4. **Kiểm tra 7a–7g**, rồi **chỉ ghi file khi mọi kiểm đạt** (báo cáo thì luôn ghi).

**Cách làm (tại một ngày T).**
- Nút = đơn vị đang hiệu lực tại T (`a4.active_rows`).
- Cạnh = cạnh gốc, cộng `add`, trừ `close` trong `edge_changes` có `at ≤ T`, rồi lọc theo hiệu lực: nguồn đã đóng thì **bỏ cạnh**. Nguồn còn mà đích đã đóng thì giữ và đánh **`dangling`** (cạnh treo).
- Thêm nút văn bản sửa đổi và cạnh `amends / replaces / repeals`. Đích không còn hiệu lực thì cạnh đánh `historical`.
- Nút điều kiện và cạnh ngoại lệ chung tính lại bằng A6 trên text đang hiệu lực.

**Bảy nhóm kiểm:**

| Kiểm | Nội dung |
|---|---|
| 7a | Mã nút duy nhất, `status` hợp lệ |
| 7b | Cạnh `ok` có đủ hai đầu; cạnh treo / historical đúng dạng |
| 7c | Không còn bộ ba lặp |
| 7d | Mỗi bản sao có đúng một `same_text_as` tới đơn vị đầu nhóm |
| 7e | Mỗi đơn vị đúng một `part_of` tới cha đúng bậc, `contains` đối xứng |
| 7f | Số nút, cạnh, bản sao khớp `EXPECTED` (225 / 481 / 4) |
| 7g | **Không có vòng `exception_of`** (A ngoại lệ của B và B bắc cầu ngoại lệ của A là mâu thuẫn) |

**Code chính** (`src/a7_graph.py`): `EdgeSet` `:96`, `mark_same_text` `:134`, `graph_base` `:192`, `graph_at` `:241`, `check_graph` `:345`, `find_cycle` `:320` (DFS lặp, không đệ quy).

**Ví dụ thật.**
- p4 gốc: 225 nút, 481 cạnh (`contains` 219, `part_of` 219, `refers_to` 25, `exception_of` 14, `same_text_as` 4). Một thành phần liên thông. 4 bản sao chữ, ví dụ `D637.K1` → `D632.K1`. Kiểm 7a–7g đều đạt.
- Tại 2027-01-01 sau `dev05` (bãi bỏ khoản 2 Điều 621, điểm a khoản 1 Điều 650, Điều 626, Điều 651): 211 nút, 454 cạnh. Có **1 cạnh treo**: `D653 refers_to D651` (Điều 651 đã bị bãi bỏ mà Điều 653 vẫn dẫn chiếu). Có 4 cạnh `repeals` từ nút văn bản `dev05_bai_bo_ds`, đích đã đóng nên đánh `historical`.

**Tự kiểm.** 32 test: gộp bộ ba từ hai nguồn, bản sao chữ, cạnh treo, vòng `exception_of` phải bị bắt (còn vòng `refers_to` chỉ ghi), đồ thị theo ngày với dữ liệu dựng tay, cùng `EXPECTED` đối chiếu bằng cách cộng số dòng của các file nguồn.

**Giới hạn.** A7 **dùng lại hàm** của A1–A6 (khác A5), nên không độc lập hoàn toàn. Nhóm bản sao tính lại mỗi ngày nên đơn vị đứng đầu nhóm có thể đổi (finding F-20). `EXPECTED` ghi cứng theo tên file (F-22).

**Chạy lại.** `python -I src/a7_graph.py data/raw/blds2015_p4.md` · tại ngày: thêm `--versions data/processed/a4/p4_dev05_bai_bo_ds/a4_p4_dev05_bai_bo_ds_versions.jsonl --date 2027-01-01`.

---

## Chạy cả pipeline

```
python -I src/run_all.py            # A1 → A7 cho 2 nguồn và 8 văn bản dev (GHI ĐÈ nhiều file ở data/processed và docs)
python -I src/run_all.py --tests    # thêm bộ kiểm thử ngoài và 10 bộ test
```

Sau khi chạy trên Windows, `git status` hiện file M giả do khác LF/CRLF: `git restore docs/bao_cao_chay/a1/a1_notes_blds2015_p4.txt docs/bao_cao_chay/eval/ext_amend_report_off.txt`.
