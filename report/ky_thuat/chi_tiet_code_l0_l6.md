# Chi tiết từng bước L0 → L6, checks, graph, viewer: làm gì, code gì, từ vào ra bằng cách nào

Tài liệu đọc nội bộ để nắm nhanh code (không phải báo cáo gửi thầy: cái đó ở `report/tong_hop/`). Mỗi bước theo một khuôn: **Việc làm · Vào → Ra · Cách làm · Code chính · Ví dụ thật · Tự kiểm · Giới hạn · Chạy lại.**

Số liệu lấy từ file trên đĩa ngày 10/11/2026 (pipeline chạy lần cuối 09/11/2026; riêng `data/processed/l6/` và `docs/bao_cao_chay/l6/l6_report.txt` được ghi lại ngày 10/11 vì test `test_chain_is_deterministic_on_disk` chạy lại `l6_versions.py`, số liệu sau đó giống hệt trước). 120 test chạy lại ngày 10/11: 7 bộ, `tổng test lỗi: 0` ở cả 7. Code ghi dạng `file:dòng`, theo `src/` ngày 09/11; sửa file thì số dòng lệch.

---

## 0. Đọc trước: bức tranh chung

Pipeline đọc Bộ luật Lao động 45/2019 và 17 văn bản dưới luật (file `.txt`) rồi dựng **một đồ thị tri thức**: mỗi Điều, Khoản, Điểm, dòng phụ lục là một nút; mỗi quan hệ giữa chúng là một cạnh; mỗi nút mang **danh sách khoảng hiệu lực** (các phiên bản). Mỗi văn bản là một *sự kiện nạp* theo ngày hiệu lực: nạp vào thì tạo phiên bản mới cho đơn vị bị sửa và đóng phiên bản cũ. Chọn một ngày thì thấy đúng bản có hiệu lực ngày đó.

```
data/raw/labor/{base,dev}/*.txt + manifest.csv                  (18 văn bản: 1 gốc + 17 dev)
  L0      corpus.py đọc manifest · llm_client.py (LLM, cache, hạn mức) · run_all.py chạy chuỗi
  L1      tách Chương/Mục/Điều/Khoản/Điểm/phụ lục ........ → 10.202 đơn vị · 61.271 bộ ba · 30 khối trích dẫn
  L2      cạnh cha-con + dẫn chiếu ........................ → 20.070 cạnh cấu trúc · 2.348 refers_to · 129 chờ đích · 127 unresolved
  L4      nhãn từng Điều .................................. → 921 nhãn
  L5 tường minh  ngoại lệ nói thẳng trong chữ (2 quy tắc) ... → 23 cạnh exception_of
  L5 chung       ngoại lệ chung "trừ trường hợp X" ......... → 128 nút điều kiện · 336 cạnh
  L3      điều khoản giao chi tiết, based_on, details ..... → 51 điều khoản · 10 based_on · 48 details
  L6      kho phiên bản theo ngày hiệu lực ................ → 9.217 đơn vị · 9.343 phiên bản · 260 cạnh cập nhật
  checks  kiểm tra (không sinh dữ liệu) ................... → 6 nhóm, 0 lỗi
  graph   gộp thành MỘT đồ thị ............................ → 9.364 nút · 2.721 cạnh ngữ nghĩa
  viewer  trang HTML xem đồ thị theo ngày ................. → do_thi.html (4,7 MB, mở offline)
```

**Thứ tự chạy thật** (`src/run_all.py:36-45`): L1 → L2 → L4 → L5 tường minh → L5 chung → L3 → L6 → checks → graph (→ viewer nếu có `--viewer`). Thứ tự theo phụ thuộc dữ liệu, không theo số L: L4 trước L6 (L6 chỉ đọc câu chỉ thị hiệu lực từ Điều nhãn `effect_transition`), L5 tường minh trước L5 chung (L5 chung nhận các trigger mà L5 tường minh để lại), L3 trước L6 (L6 đọc cạnh `details`/`based_on` cho loại 25). Tên cũ trong plan: A1 = L1, A2 = L2, A3 = L5 tường minh, A6 = L5 chung, A4 = L6, A5 = checks, A7 = graph, A8 = viewer.

**Năm nguyên tắc chung của mọi bước:**
1. **Mỗi bước đọc file của bước trước** và ghi file riêng vào `data/processed/<bước>/`, kèm báo cáo chữ ở `docs/bao_cao_chay/<bước>/`. `data/processed/` bị `.gitignore`: máy khác phải chạy `run_all.py` (vài giây) để có lại.
2. **Mẫu câu (regex), không LLM ở lõi.** LLM chỉ có ở hai nhánh tuỳ chọn là L4 và L3 (cờ `--llm off|replay|live`, mặc định `off`). Cùng đầu vào thì cùng kết quả.
3. **Fail-closed:** dạng câu chưa có quy tắc thì không đoán. Tuỳ bước mà báo lỗi dừng (L1 thoát mã 1, không ghi file dữ liệu), ghi vào `unresolved` / `unhandled` kèm lý do (L2, L5), hoặc ghi `unknown_directive` và không áp (L6).
4. **Mỗi cạnh có `evidence`:** câu nguyên văn làm bằng chứng, và code kiểm nó nằm trong chữ của đơn vị nguồn.
5. **Có số đối chiếu cứng:** số Điều khớp `manifest.csv`, `EXPECTED` của `checks.py`, 4 mốc ở L3, 15 mốc cổng dev ở L6.

Hai quy ước nữa chạy xuyên suốt: **đích ở văn bản chưa có trong kho** thì không tạo cạnh mà ghi *quan hệ chờ đích* (L2 129, L3 18, L6 36); **hiệu lực là nửa khoảng** `[effective_from, effective_to)`, đang hiệu lực tại T nếu `from ≤ T < to`, `null` là không giới hạn.

**Quy ước mã:**

| Loại | Dạng mã | Ví dụ |
|---|---|---|
| Đơn vị thân văn bản | `<doc_id>.C<La Mã>.M<n>`, `.D<n>`, `.K<n>`, `.<điểm>` | `BLLD_45-2019.D35.K2.a` |
| Chữ `đ` | viết `dd` trong mã (`number` vẫn lưu `đ`) | `BLLD_45-2019.D35.K2.dd` |
| Hậu tố chữ | bình thường | `VBHN_125-2025.D154.K8a` |
| Phụ lục | `.PL<nhãn>.M<n>.L<chữ>.S<La Mã>.R<k>` (`I.7` viết `I_7`) | `NQ_66-16-2026.PLI_7.M1.LB.SI` |
| Nút điều kiện (L5 chung) | `<doc_id>.X<8 ký tự đầu sha1>` | `BLLD_45-2019.X1162b718` |
| Văn bản ngoài kho | `external:<số hiệu>` | `external:157/2018/NĐ-CP` |

**Số liệu chính (toàn kho):**

| | Số |
|---|---|
| Văn bản | 18: 1 gốc (BLLĐ) + 17 dev (10 nghị định, 5 thông tư, 1 nghị quyết, 1 bản hợp nhất) |
| Đơn vị L1 | 10.202 = 893 Điều + 3.014 Khoản + 3.006 Điểm + 76 Chương + 90 Mục + 28 phụ lục + 74 mục phụ lục + 3.021 dòng phụ lục |
| Cạnh cấu trúc L2 | 20.070 (10.035 cặp `contains` / `part_of`) |
| `refers_to` L2 | 2.348 (gồm 245 của bản hợp nhất; graph không vẽ cạnh của bản hợp nhất nên báo 2.103) |
| Điều khoản giao chi tiết L3 | 51 cụm ở 51 đơn vị (A 35, B 10, D 5, E 1) |
| Cạnh L3 | 10 `based_on`, 48 `details` (44 regex + 4 LLM; 1 giữ, 3 cô lập) |
| Nhãn L4 | 921: substantive 649, authority 95, procedural 57, definition 53, effect_transition 39, appendix 28 |
| L5 tường minh | 23 cạnh (xem mục Giới hạn của L5 tường minh) |
| L5 chung | 128 nút điều kiện (cu_the 116, tuy_nghi 8, dan_chieu_mo 4); 336 cạnh (156 `general_except` + 180 `general_except_ref`) |
| L6 | 9.217 đơn vị, 9.343 phiên bản (118 đơn vị có từ 2 phiên bản), 260 cạnh cập nhật, 36 chờ đích |
| Trạng thái cuối L6 (as_of 2026-09-10) | in_force 7.263 · expired 1.845 · suspended 91 · pending_event 18 (tính theo phiên bản cuối của mỗi đơn vị) |
| Đồ thị | 9.364 nút, 2.721 cạnh ngữ nghĩa, 232 thành phần liên thông (mức Điều) |
| LLM | 23 lượt API thật ngày 09/11 (17 chính + 6 kiểm); cache: 15 phản hồi L4, 8 phản hồi L3 |
| Test | 120 test / 7 file |

---

## L0. Nền: manifest, lớp gọi LLM, chạy cả chuỗi

### corpus.py: danh mục văn bản

**Việc làm.** Đọc `data/raw/labor/manifest.csv` thành bảng 18 văn bản và cung cấp đường dẫn, hằng cho mọi bước. Không chép cứng thông tin văn bản vào code.

**Vào → Ra.** Vào: `manifest.csv` (UTF-8 có BOM, đọc bằng `utf-8-sig`). Ra: dict `{doc_id: Doc}` theo thứ tự dòng.

**Cách làm.**
- `Doc` (`corpus.py:40`) giữ: `doc_id`, `path`, `so_hieu`, `loai`, `ten_ngan`, `ngay_ban_hanh`, `issued_uncertain`, `ngay_hieu_luc`, `nhom` (`base` / `dev`), `so_dieu`. Ngày ban hành có thể là `None` nếu manifest ghi `?` (cờ `issued_uncertain`: TT_09, TT_10).
- **Các cột `quan_he`, `nguon`, `ghi_chu` của manifest không vào `Doc`.** Đó là mốc kiểm của học viên, không phải đầu vào pipeline, để không bước nào dùng nhầm.
- `so_dieu` là cột `so_dieu_dem_duoc`, đếm độc lập bằng regex `^Điều N.`; L1 phải khớp con số này.
- Hằng có chủ đích: `BASE_DOC_ID = "BLLD_45-2019"` (`:19`); cấp văn bản `LEVEL_BY_TYPE` (`:23`: luật/bộ luật/hợp nhất = 1, nghị định/nghị quyết CP = 2, thông tư = 3); `PL_IN_SCOPE` (`:33`: chỉ Phụ lục I.7 của NQ 66.16 được bóc chi tiết); `DUP_CHUONG_OK` (`:37`: ND_145 có hai "Chương XI").
- `load_manifest` (`:79`) báo `ValueError` khi `doc_id` lặp, loại văn bản lạ, thiếu ngày hiệu lực, hoặc file không có.

**Code chính.** `load_manifest :79` · `get_doc :101` · `out_dir :113` (thư mục `data/processed/<bước>/`) · `report_dir :118` · `find_vn_date :129` (ngày dạng "ngày 20 tháng 11 năm 2019" đầu tiên trong chữ).

### llm_client.py: nơi duy nhất gọi LLM

**Việc làm.** Một lớp bao quanh Gemini: đọc cấu hình, lưu mọi phản hồi vào cache, đếm lượt theo ngày và theo vai, giãn nhịp, chạm hạn mức thì dừng gọn. Đề xuất của LLM **không bao giờ được áp thẳng**: bước gọi (L3, L4) phải kiểm bằng máy.

**Vào → Ra.** Vào: `docs/llm_config.md` (các dòng `khoá = giá trị`), biến môi trường `GEMINI_API_KEY` (chỉ ở chế độ live). Ra: `data/llm_cache/<tác vụ>/<khoá>.json`, `data/llm_cache/_usage.json`.

**Cách làm.**
1. **Cấu hình** (`load_config :89`): vai `chinh` = `gemini-3.5-flash-lite` (15 RPM, 500 lượt/ngày), vai `kiem` = `gemini-3.8-flash` (5 RPM, 20 lượt/ngày), `max_output_tokens = 32000`; temperature và thinking để mặc định. Thiếu khoá cấu hình thì `LLMError`.
2. **Ba chế độ** (`Client :110`): `off` không gọi gì (báo `LLMUnavailable`); `replay` chỉ đọc cache, thiếu thì `CacheMiss`; `live` thiếu cache thì gọi API rồi lưu.
3. **Khoá cache** (`cache_key :103`) = sha256 của `(model, tác vụ, phiên bản prompt, đầu vào, chữ system, lược đồ)`. Sửa prompt hay lược đồ mà quên đổi phiên bản vẫn không dùng nhầm phản hồi cũ. Tính tái lập đến từ cache, không từ temperature.
4. **Gọi** (`ask :161`): có cache và qua `validate` thì trả; không thì (live) kiểm hạn mức, giãn nhịp (`_throttle :204`: chờ đủ 60/RPM giây giữa hai lần gọi cùng vai), gọi `_call :226` (thử lại 3 lần với mã 429/500/503, chờ 20 s × lần thử), rồi lưu.
5. **Phản hồi không hợp lệ** (`validate` ném `ValueError`): không vào cache chính mà sang `<tác vụ>/_rejected/` kèm lý do, **vẫn tính lượt** (API đã tốn), ném `InvalidOutput`; chạy lại sẽ gọi lại (`_quarantine :153`). Phản hồi đã lưu mà nay không qua kiểm chặt hơn cũng bị chuyển sang `_rejected/`.
6. **Hạn mức:** chạm giới hạn của một vai thì `QuotaReached`; bước gọi dừng gọn, phần đã gọi nằm trong cache, hôm sau chạy tiếp.
7. **Log tiến độ** (chỉ lượt API thật, ra stderr): một dòng trước, một dòng sau (kèm giây và token), nhịp "vẫn đang chờ" mỗi 30 giây (`_Heartbeat :46`), dòng riêng khi phải thử lại.

**Code chính.**

| Hàm / lớp | Việc |
|---|---|
| `load_config :89`, `cache_key :103` | Đọc cấu hình; khoá cache |
| `Client.ask :161` | Cache → hạn mức → giãn nhịp → gọi → kiểm → lưu |
| `Client._call :226` | Gọi `google-genai` (import trễ, chỉ khi live), JSON schema, thử lại |
| `_quarantine :153` | Chuyển phản hồi sai sang `_rejected/` |
| `LLMError :68`, `InvalidOutput :72`, `LLMUnavailable :77`, `CacheMiss :81`, `QuotaReached :85` | Các lỗi để bước gọi bắt riêng |
| `key_is_set :265`, `check_models :270` | Kiểm khoá có hay không (không in khoá); hỏi `models.list` (không tốn lượt) |

**Ví dụ thật.** Ngày 09/11/2026 đã gọi API thật 23 lượt (`_usage.json`: chính 17, kiểm 6): L4 dùng 13 chính + 2 kiểm, L3 dùng 4 chính + 4 kiểm. `data/llm_cache/l4_classify/` có 15 file, `l3_details/` có 8 file, không có `_rejected/`.

**Tự kiểm.** 5 test trong `tests/test_checks_graph_viewer_llm.py` (off và replay không chạm mạng; live lưu cache rồi replay trả đúng bản ghi; khoá cache phụ thuộc model, tác vụ, prompt, đầu vào; dừng gọn ở hạn mức theo vai; cấu hình đọc từ `llm_config.md`) và 10 test trong `tests/test_llm_steps.py` (giãn nhịp RPM nhưng không chờ khi đọc cache; đầu ra không phải JSON là lỗi và không tính lượt; live thiếu khoá thì dừng ngay ở mọi bước; phản hồi sai bị cách ly, vẫn tính lượt và lần sau gọi lại; phản hồi cũ không qua kiểm chặt hơn bị cách ly; log lượt thật kèm nhãn nhưng không log lượt đọc cache; im lặng mặc định; log khi thử lại; nhịp chờ dừng ngay khi xong; khoá cache gồm cả system và lược đồ). Toàn bộ dùng API giả.

**Giới hạn.** `llm_config.md` ghi model của hai vai nhưng L6 không gọi LLM (`llm_calls: 0` cố định ở `l6_directives.py:150`). Chất lượng đầu ra thật của hai model mới được đo gián tiếp qua L3 và L4 (xem hai mục đó). Gói miễn phí có thể bị Google dùng nội dung để cải thiện sản phẩm: chỉ gửi văn bản luật công khai.

**Chạy lại.** `python -I src/llm_client.py` (in cấu hình, lượt đã dùng) · thêm `--check-models` (cần khoá).

### run_all.py: chạy cả chuỗi

**Việc làm.** Chạy lần lượt từng bước như một lệnh con, in một dòng mỗi bước (OK kèm số giây, hoặc LỖI kèm đầu ra), dừng ở bước lỗi.

**Cách làm.** `STEPS :36` là danh sách 9 bước; `VIEWER_STEPS :47` thêm trang xem; `run :54` chạy `python -X utf8 -I <script>` với `cwd = ROOT` (cờ `-I` để không nạp nhầm file cạnh script); `step_tests :64` chạy từng `tests/test_*.py` và yêu cầu dòng cuối đúng `tổng test lỗi: 0`. Cờ `--llm` chỉ truyền cho hai script `l4_classify.py`, `l3_links.py` (`LLM_SCRIPTS :34`); `--llm live` mà không thấy `GEMINI_API_KEY` thì dừng ngay, trước khi chạy bước nào. Khi LLM bật, stderr của hai bước đó đi thẳng ra console để thấy log tiến độ.

**Chạy lại.** `python -I src/run_all.py` · `--viewer` (thêm trang xem) · `--tests` (thêm 7 bộ test) · `--llm replay` (đọc cache, không tốn lượt).

---

## L1. Tách văn bản thành đơn vị

**Việc làm.** Đọc mỗi file `.txt` thành cây đơn vị (Chương > Mục > Điều > Khoản > Điểm, và phụ lục) với mã ổn định. Tách ra riêng, **không phải đơn vị của văn bản chứa chúng**: khối trích dẫn “…” của văn bản sửa đổi, chú thích `[n]` của bản hợp nhất, bảng lương vùng. Đọc đầu văn bản (số hiệu, ngày, các dòng "Căn cứ").

**Vào → Ra.**
- Vào: `data/raw/labor/<nhóm>/<doc_id>.txt` và dòng manifest của nó.
- Ra (`data/processed/l1/`, mỗi văn bản một bộ): `l1_triples_<doc>.jsonl` (bộ ba `{s, p, o}` với `p` ∈ type, number, heading, parent, scope, footnote, text, version, source_line), `l1_payloads_<doc>.jsonl` (khối trích dẫn), `l1_tables_<doc>.jsonl` (bảng lương), `l1_footnotes_<doc>.jsonl` (chú thích). Thêm `data/processed/documents.jsonl` (thông tin 18 văn bản, ghi khi chạy `--all`) và `docs/bao_cao_chay/l1/l1_report_<doc>.txt`.

**Cách làm.**
1. **Chuẩn hoá dòng** (`read_lines :124`, `normalize_line :110`): bỏ BOM, đổi CRLF thành LF, NFC, `\xa0` thành dấu cách, gộp khoảng trắng. `scan_source :116` chỉ ghi nhận (BOM, CRLF, dòng chưa NFC, ký tự điều khiển) để báo cáo.
2. **Máy trạng thái** (`Parser.run :248`) duyệt từng dòng, theo thứ tự ưu tiên: (a) đang trong khối trích dẫn thì nuốt đến khi nháy “ ” cân bằng; (b) dòng `[1] ...` thì dừng thân, sang vùng chú thích; (c) tiêu đề phụ lục thì dừng thân, sang phụ lục; (d) dòng "Nơi nhận" thì bỏ (đếm vào `skipped`, chỉ ở thân văn bản); (e) còn lại do `_token :339` phân loại bằng regex: Chương, Mục, Điều, (đầu văn bản thì vào `header_lines`), Khoản, Điểm, hoặc đoạn chữ không nhãn.
3. **Cây và mã:** Điều có cha là Mục (nếu có) hoặc Chương; Khoản có cha là Điều; Điểm có cha là Khoản, hoặc Điều nếu Điều không có Khoản (ND_283 Điều 1, mã `D1.a`). Đoạn chữ không nhãn nối vào Khoản (chưa có thì Điều); gạch đầu dòng nối vào đơn vị sâu nhất; đoạn chữ ngay sau một Điểm gắn vào Khoản và ghi `notes`.
4. **Đánh số phải liền** (`next_number_ok :151`: n+1, hoặc cùng n với hậu tố chữ kế tiếp `'' → a → b`; `next_letter_ok :166`: theo bảng chữ `DIEM_LETTERS` có `đ`, không có f j w z; `a → a1 → a2`). Nhảy số là lỗi parse.
5. **Khối trích dẫn** (`start_payload :310`): dòng bắt đầu bằng “ mà mở nhiều hơn đóng, hoặc dòng liền trước kết thúc bằng `:`. Khối mang câu dẫn (`lead_text`) và đơn vị đang mở (`lead_unit`) để L6 biết khối là nội dung cho chỉ thị nào. Nháy mở không đóng đến hết văn bản là lỗi.
6. **Phụ lục** (`parse_appendices :423`): chia theo dòng tiêu đề (`Phụ lục I.7`, `PHỤ LỤC` đứng một mình, hoặc dòng viết hoa đứng trước `(Kèm theo ...)` khi không có nhãn như TT_11, TT_19); bỏ khối mục lục (khối ≤ 3 dòng mà nhãn còn xuất hiện lại sau). Mỗi phụ lục là nút `pl`; `Mục n` / `A.` / `I.` thành `pl_muc`; mỗi dòng còn lại là một `pl_row`. Phụ lục ngoài `PL_IN_SCOPE` chỉ giữ nút, gắn `scope = out_of_scope`.
7. **Chú thích `[n]`** (bản hợp nhất): gỡ dấu `[n]` khỏi chữ, ghi bộ ba `footnote` lên đơn vị; vùng chú thích bắt đầu ở dòng `[1] ...`, mọi dòng sau `[n]` (kể cả dòng trông như khoản) là chữ của chú thích.
8. **Bảng lương** (`rebuild_wage_tables :512`): bảng vùng bị trải mỗi ô một dòng được ghép lại khi gặp đúng dạng `Vùng / Mức ... tháng / Mức ... giờ` rồi từng bộ ba. Đơn vị giữ nguyên chữ gốc.
9. **Đầu văn bản** (`extract_header :535`): số hiệu, ngày ký, các dòng "Căn cứ" đọc bằng regex rồi đối chiếu manifest; lệch thì gắn cờ. TT_09, TT_10, TT_11 mất phần đầu nên lấy từ manifest (cờ `header_from_manifest`).
10. **Cổng** (`parse_document :561`, `run_doc :663`): số Điều khác manifest, mã lặp, hoặc còn lỗi parse thì chỉ ghi báo cáo, không ghi file dữ liệu của văn bản đó; `main` thoát mã 1.

**Code chính** (`src/l1_parse.py`):

| Hàm / lớp | Việc |
|---|---|
| `RE_DIEU … RE_PLS :42-58` | Nhận loại dòng. `RE_KHOAN` cho phép `8a.[2] ...` (bản hợp nhất) nhưng không nhận `4.960.000` |
| `Parser.run :248`, `_token :339` | Máy trạng thái thân văn bản; dựng cây, kiểm đánh số |
| `parse_appendices :423`, `parse_one_appendix :457` | Phụ lục, mục lục, cấp `M` / `L` / `S`, dòng `R` |
| `parse_footnotes :405` | Vùng chú thích; kiểm số liên tục |
| `rebuild_wage_tables :512` | Ghép bảng lương |
| `extract_header :535` | Đầu văn bản, cờ lệch manifest |
| `to_triples :576` | Mỗi đơn vị thành bộ ba, thứ tự `type, number, heading, parent, scope, footnote, text, version, source_line` |
| `load_units :618`, `load_payloads :630` | Đọc lại cho các bước sau (`{id: {type, number, heading, parent, text, ...}}`) |

**Ví dụ thật.**
- `BLLD_45-2019.D35.K2.dd` (dòng 476): `type = diem`, `number = đ`, `parent = BLLD_45-2019.D35.K2`, `text = "Lao động nữ mang thai phải nghỉ việc theo quy định tại khoản 1 Điều 138 của Bộ luật này;"`, `version = 1`, `source_line = 476`. Mã dùng `dd`, `number` vẫn là `đ`.
- Khối trích dẫn `ND_70-2023.Q1` (dòng 36): `lead_text = "a) Sửa đổi, bổ sung điểm a khoản 3 Điều 3 như sau:"`, `lead_unit = ND_70-2023.D1.K1.a`, nội dung “a) Tốt nghiệp đại học trở lên hoặc tương đương và có ít nhất 3 năm kinh nghiệm...”. ND_70 có 22 khối như vậy.
- Bảng lương `ND_74-2024.D3.K1.T1`: vùng I 4.960.000 đồng/tháng, 23.800 đồng/giờ; II 4.410.000 / 21.200; III 3.860.000 / 18.600; IV 3.450.000 / 16.600.
- `VBHN_125-2025.D154.K8a` có `footnote = 2`; chú thích 2 ghi "...có hiệu lực kể từ ngày 01 tháng 01 năm 2026" (L6 lấy ngày này).
- ND_145 có hai "Chương XI" do nguồn lặp nhãn; lần sau mang mã `ND_145-2020.CXI_2` (ghi `notes`, nhận bằng `DUP_CHUONG_OK`).

Số đếm theo văn bản (đơn vị; `PL` là phụ lục / dòng phụ lục):

| Văn bản | Điều | Khoản | Điểm | Phụ lục | Khối trích dẫn |
|---|---|---|---|---|---|
| BLLD_45-2019 | 220 | 638 | 267 | | 4 |
| VBHN_125-2025 | 220 | 639 | 265 | | 4 (và 3 chú thích) |
| ND_12-2022 | 64 | 334 | 565 | | |
| ND_28-2020 | 58 | 268 | 405 | | |
| ND_145-2020 | 115 | 367 | 416 | | |
| ND_283-2026 | 68 | 333 | 760 | | |
| ND_152-2020 | 30 | 125 | 100 | | |
| ND_219-2025 | 36 | 123 | 84 | | |
| ND_70-2023 | 3 | 18 | 34 | | 22 |
| ND_74-2024 | 5 | 12 | 10 | | (1 bảng lương) |
| ND_90-2019 | 6 | 15 | 14 | 1 / 87 dòng | |
| ND_135-2020 | 9 | 16 | 9 | 3 / 68 dòng | |
| NQ_66-16-2026 | 19 | 7 | 3 | 16 / 189 dòng (28 mục) | |
| TT_09-2020 | 13 | 41 | 9 | 5 / 334 dòng | |
| TT_10-2020 | 12 | 47 | 48 | 1 / 188 dòng | |
| TT_11-2020 | 3 | 4 | 8 | 1 / 1.985 dòng (41 mục) | |
| TT_18-2021 | 10 | 25 | 9 | | |
| TT_19-2023 | 2 | 2 | 0 | 1 / 170 dòng | |
| **Tổng** | **893** | **3.014** | **3.006** | | **30** |

**Tự kiểm.** 17 test (`tests/test_l1.py`), đáng chú ý: mã có hậu tố và `dd`; đoạn chữ sau Điểm vào Khoản kèm ghi chú; nhảy số bị báo; tiêu đề Chương ở dòng kế và bị xuống dòng; `4.960.000` không phải Khoản; khối trích dẫn không thành đơn vị; nháy không đóng là lỗi; "Nơi nhận" bị bỏ; chú thích; mục lục phụ lục; phụ lục không nhãn; bảng lương; đọc CRLF, BOM, NFC; **cả 18 văn bản qua cổng**; cờ đầu văn bản. Ngoài ra `checks.py` đếm lại Điều, Khoản, Điểm của BLLĐ bằng bộ đếm riêng (xem mục checks).

**Giới hạn.**
- Dòng bảng trong phụ lục (TT_11: 1.985 dòng) là một `pl_row` mỗi dòng, **chưa tách cột**.
- "Mẫu số ..." chưa thành nút form; chỉ thị sửa mẫu biểu được L6 ghi cờ `form_directive_target_not_in_kb`.
- Không có cấp Phần / Tiểu mục trong kho; gặp thì báo lỗi, không đoán.
- Bảng lương chỉ có ở ND_74; bảng của văn bản chưa có trong kho chưa kiểm được.
- TT_09, TT_10: ngày ban hành chưa chốt (manifest ghi dấu `?`).
- Số đối chiếu độc lập cho Khoản, Điểm chỉ có cho BLLĐ.

**Chạy lại.** `python -I src/l1_parse.py <doc_id>` (một văn bản) · `--all` (cả kho, ghi `documents.jsonl`) · `python -I tests/test_l1.py`.

---

## L2. Cạnh cấu trúc và cạnh dẫn chiếu

**Việc làm.** (a) Nối cha-con: `contains` và `part_of`. (b) Tìm các câu dẫn chiếu ("khoản 3, 4, 5, 6, 7 và 8 Điều 154 của Bộ luật Lao động") và nối nguồn tới đích, **trong và giữa các văn bản**. (c) Cụm không nối được thì phải có chỗ đi: *chờ đích* hoặc *unresolved* kèm lý do.

**Vào → Ra.**
- Vào: `l1_triples_*` của cả kho (đọc lại bằng `l1.load_units`), `documents.jsonl` (dòng "Căn cứ").
- Ra (`data/processed/l2/`, mỗi văn bản): `l2_edges_<doc>.jsonl` (cạnh cấu trúc), `l2_refs_<doc>.jsonl` (`refers_to` kèm `evidence`), `l2_pending_<doc>.jsonl` (chờ đích), `l2_unresolved_<doc>.jsonl` (cụm đọc được nhưng không giải được, kèm lý do). Thêm `data/processed/pending_links.jsonl` (gộp chờ đích, khi `--all`) và `docs/bao_cao_chay/l2/l2_report_<doc>.txt`.

**Cách làm.**

*Cấu trúc.* Cha lấy từ thuộc tính `parent` của L1 (không suy từ mã). Mỗi cặp cha-con thành hai cạnh `(cha, contains, con)` và `(con, part_of, cha)` (`build_structure_edges :104`). `check_structure :115` kiểm: cha tồn tại và **đúng loại** (`PARENT_TYPES :98`), mỗi đơn vị đúng một cha (hoặc là gốc), cạnh đối xứng, không trùng.

*Dẫn chiếu.*
1. **Bỏ dòng chỉ thị sửa đổi** (`is_directive :226`, `DIRECTIVE_RE :68`: động từ chỉ thị đi liền danh từ đích, ví dụ "Sửa đổi, bổ sung khoản 6 Điều 7 như sau:"). Dẫn chiếu trong đó trỏ vào văn bản bị sửa, việc của L6. Mẫu cố ý chặt: không nhận "Sửa chữa, làm sai lệch ..." hay "Thay đổi cơ cấu ..." (điều quy tắc bình thường).
2. **Tìm cụm** (`find_refs :202`): `CHAIN_RE :42` nhận chuỗi mục "điều / khoản / điểm + số, chữ hoặc *này*", nối bằng dấu phẩy, chấm phẩy, "và", "hoặc", "của". Một mục có thể là danh sách cùng loại ("khoản 3, 4, 5, 6, 7 và 8"). Phụ lục nhận bằng `PL_REF_RE :49`.
3. **Tách chuỗi thành dẫn chiếu riêng** (`split_chain :154`): một dẫn chiếu mới bắt đầu khi cấp đi từ thô xuống mịn ("Điều 18, điểm a khoản 1 Điều 145"), hoặc ngay sau mục "này", hoặc mục Điều thứ hai sau chuỗi đã có mục thấp. Viết lược "điểm h khoản 1 và điểm đ khoản 2 Điều này": Điều nêu ở dẫn chiếu cuối dùng chung cho các dẫn chiếu trước.
4. **Đuôi văn bản** (`parse_tail :180`): "của Bộ luật này" (chính văn bản), "Nghị định số 145/2020/NĐ-CP" (theo số hiệu), "Bộ luật Lao động" / "Luật Việc làm" (theo tên).
5. **Đổi cụm thành mã đích** (`chain_targets :248`): cấp phải giảm liên tiếp và kết thúc ở Điều hoặc "này"; "này" là tổ tiên đúng loại của đơn vị chứa câu (`enclosing :238`); chỉ mục thấp nhất được là danh sách. Dạng chưa có quy tắc ("điểm này", mục cấp trên nhiều đối số, cụm kết thúc ở khoản/điểm không có Điều) trả lý do, không đoán.
6. **Giải văn bản đích** (`Resolver :278`, `resolve :296`): tự nói về mình thì là chính văn bản; có số hiệu thì tra manifest, không thấy thì chờ đích; tên "Bộ luật Lao động" thì chọn **bản 2019 hay 2012 theo dòng "Căn cứ Bộ luật Lao động ngày ..." của văn bản nguồn** (`blld_year :286`), **không theo ngày ký**; mất đầu văn bản thì theo ngày hiệu lực của văn bản nguồn (từ 01/01/2021 là bản 2019). Bản 2012 ngoài kho nên thành chờ đích với số hiệu `10/2012/QH13`.
7. **Ghép** (`resolve_ref :332`, `extract :373`): mỗi cụm thuộc đúng **một** trong ba trạng thái: nối cạnh, chờ đích, hoặc unresolved. Nhiều cụm cùng trỏ một đích thì giữ một cạnh, `evidence` là cụm đầu. `resolve_ref` được L3, L5 tường minh, L5 chung, L6 dùng lại.
8. **Kiểm** (`check_refs :410`): không trùng, không tự trỏ, hai đầu tồn tại, `evidence` nằm trong chữ của đơn vị nguồn. Có lỗi thì không ghi file của văn bản đó.

**Code chính** (`src/l2_edges.py`):

| Hàm / lớp | Việc |
|---|---|
| `build_structure_edges :104`, `check_structure :115` | Cạnh cấu trúc và kiểm |
| `CHAIN_RE :42`, `find_refs :202`, `split_chain :154` | Tìm và tách cụm dẫn chiếu |
| `parse_tail :180`, `Resolver :278` | Đuôi văn bản, giải văn bản đích, chọn BLLĐ 2012/2019 |
| `chain_targets :248`, `enclosing :238` | Cụm thành mã đích; xử lý "này" |
| `resolve_ref :332` | Cụm → `Resolved(targets, missing, pending, error)` |
| `extract :373`, `check_refs :410` | Dựng cạnh của một văn bản; kiểm |
| `load_context :442` | `(docs, all_units, resolver, available)` cho các bước đọc L1/L2 |

**Ví dụ thật.**
- Cấu trúc: `BLLD_45-2019.D35.K2.a part_of BLLD_45-2019.D35.K2` (và chiều ngược `contains`).
- Một cụm ra nhiều đích: ND_152 Điều 7 mở bằng "Ngoài các trường hợp quy định tại các khoản 3, 4, 5, 6, 7 và 8 Điều 154 của Bộ luật Lao động, ...": `evidence = "khoản 3, 4, 5, 6, 7 và 8 Điều 154 của Bộ luật Lao động"`, ra 6 cạnh `ND_152-2020.D7 → BLLD_45-2019.D154.K3` đến `.K8`. Đây là mốc kiểm của `checks.py`.
- "Này": `BLLD_45-2019.D21.K5` có "khoản 1, 2 và 3 Điều này" → `D21.K1`, `D21.K2`, `D21.K3`.
- Chờ đích: `ND_28-2020.D10.K2.a` "Điều 31 của Bộ luật Lao động"; ND_28 "Căn cứ Bộ luật Lao động ngày 18 tháng 6 năm 2012" nên là bản 2012, ghi `{target_number: "10/2012/QH13", target_units: ["D31"]}`. Ngược lại ND_135 ký 18/11/2020 nhưng căn cứ bản ngày 20/11/2019 nên nối thẳng vào `BLLD_45-2019`.
- Unresolved: `ND_145-2020.D1.K1` "khoản 3 Điều 12": cụm đủ Điều/khoản nhưng không nêu văn bản đích (Điều 12 của BLLĐ, nêu ở câu dẫn); L2 giữ unresolved kèm lý do, L3 dùng chính các đơn vị này tạo cạnh `details`.

Số đếm theo văn bản (cột 1: `refers_to`; cột 2: chờ đích; cột 3: unresolved):

| Văn bản | refers_to | chờ | unres. | | Văn bản | refers_to | chờ | unres. |
|---|---|---|---|---|---|---|---|---|
| BLLD_45-2019 | 245 | 1 | 0 | | ND_70-2023 | 0 | 0 | 0 |
| VBHN_125-2025 | 245 | 1 | 0 | | ND_74-2024 | 0 | 0 | 1 |
| ND_283-2026 | 522 | 54 | 9 | | ND_90-2019 | 4 | 0 | 0 |
| ND_145-2020 | 398 | 5 | 59 | | NQ_66-16-2026 | 16 | 0 | 0 |
| ND_12-2022 | 382 | 26 | 16 | | TT_09-2020 | 35 | 0 | 4 |
| ND_28-2020 | 195 | 21 | 3 | | TT_10-2020 | 21 | 0 | 8 |
| ND_152-2020 | 142 | 1 | 23 | | TT_11-2020 | 1 | 0 | 0 |
| ND_219-2025 | 104 | 3 | 0 | | TT_18-2021 | 17 | 0 | 3 |
| ND_135-2020 | 21 | 17 | 1 | | TT_19-2023 | 0 | 0 | 0 |
| **Tổng** | **2.348** | **129** | **127** | | | | | |

Lý do unresolved phổ biến nhất: "mục cấp trên có nhiều hơn một đối số" (24), phụ lục chưa có file nguồn (ND_152 Phụ lục I 17 cụm, ND_145 Phụ lục III 16 cụm...), "cụm kết thúc bằng khoản/điểm, không có Điều" (13). Chờ đích phổ biến nhất: Luật Bảo hiểm xã hội (48), Luật Người lao động Việt Nam đi làm việc ở nước ngoài (17), BLLĐ 2012 `10/2012/QH13` (13), Luật Xử lý vi phạm hành chính (11), Luật An toàn vệ sinh lao động (10).

**Tự kiểm.** 15 test (`tests/test_l2.py`): danh sách số và "này"; tách chuỗi sau "này"; ba dẫn chiếu dùng chung một đuôi; Điều viết lược; chấm phẩy và "của"; hậu tố số và điểm có chữ; các dạng đuôi; phụ lục; `chain_targets`; bộ nhận chỉ thị chặt; **chọn BLLĐ 2012/2019 theo dòng Căn cứ chứ không theo ngày ký**; cổng cả 18 văn bản (mọi cụm thuộc đúng một trạng thái); mốc ND_152.D7 → BLLD.D154; văn bản sửa đổi không sinh `refers_to`; chờ đích khi văn bản đích chưa nạp. `checks.py` kiểm lại cấu trúc và hai đầu `refers_to`.

**Giới hạn.**
- **L2 là tĩnh:** `available = set(all_units)` (`l2_edges.py:508`), mọi văn bản đã có L1 coi là đã nạp. Nạp theo ngày hiệu lực là việc của L6. Chưa có bước nối quan hệ chờ đích khi văn bản đích được nạp.
- Số hiệu BLLĐ 2012 (`10/2012/QH13`, `l2_edges.py:61`) lấy từ hiểu biết ngoài repo, không kiểm được trong kho.
- Tên văn bản của quan hệ chờ đích bị cắt ở từ không viết hoa nên chỉ còn "Luật Bảo", "Luật Xử", "Luật Công" (`parse_tail`); chỉ dùng để hiển thị, không dùng để nối.
- `refers_to` là dẫn chiếu thuần, chưa phân loại ngữ nghĩa (căn cứ, ngoại lệ, áp dụng...).
- 127 unresolved đều có lý do nhưng chưa xử lý: dạng chưa có quy tắc thì để nguyên.

**Chạy lại.** `python -I src/l2_edges.py <doc_id>` · `--all` (ghi thêm `pending_links.jsonl`) · `python -I tests/test_l2.py`.

---

## L3. Điều khoản giao chi tiết, `based_on`, `details`

**Việc làm.** (1) Tìm trong BLLĐ các điều khoản **giao** cấp dưới quy định chi tiết (5 dạng A-E của plan). (2) Nối mỗi văn bản dưới luật tới căn cứ của nó (`based_on`). (3) Nối mỗi văn bản dưới luật tới điều khoản nó **quy định chi tiết** (`details`). (4) Văn bản không nêu số Điều thì đề xuất bằng từ khoá và hai model LLM độc lập.

**Vào → Ra.** Vào: `l1_triples_*`, `documents.jsonl` (dòng "Căn cứ"), hàm giải dẫn chiếu của L2. Ra (`data/processed/l3/`): `delegation_clauses.jsonl` (51), `l3_links.jsonl` (58 cạnh = 10 `based_on` + 48 `details`), `l3_pending.jsonl` (18), và `docs/bao_cao_chay/l3/l3_report.txt`. Tác vụ cache: `data/llm_cache/l3_details/`.

**Cách làm.**

*Điều khoản giao* (`find_delegation :61`, `DELEG_PATTERNS :46`), regex thô trên BLLĐ:

| Dạng | Mẫu | Ví dụ |
|---|---|---|
| A | "Chính phủ / Bộ trưởng ... / Thủ tướng Chính phủ" + "quy định" (không đứng trước "tại") | "Chính phủ quy định chi tiết Điều này" |
| A, phụ C | như A nhưng có "do" đứng trước | "Trường hợp khác do Chính phủ quy định" |
| B | "theo quy định của Chính phủ / Bộ trưởng / Thủ tướng Chính phủ" | |
| D | "Bộ trưởng ... ban hành" | "Bộ trưởng Bộ Lao động - Thương binh và Xã hội ban hành danh mục nghề, công việc..." |
| E | "Thủ tướng Chính phủ quyết định" | Điều 112 |

*`based_on`* (`based_on_links :122`): mỗi dòng "Căn cứ ...": cụm điều/khoản kèm văn bản thành cạnh tới đơn vị; số hiệu văn bản thành cạnh tới văn bản; "Căn cứ Bộ luật Lao động" không kèm số thì theo `blld_year` (bản 2019 nối vào `BLLD_45-2019`, bản 2012 thành chờ đích).

*`details`* (`details_links :155`): đọc **Điều 1** (Phạm vi điều chỉnh) của văn bản. Cụm điều/khoản kèm văn bản thành cạnh; cụm không nêu văn bản thì lấy đuôi từ câu dẫn (`lead_tail :85`, "... sau đây của Bộ luật Lao động:"). Chỉ giữ đích ở văn bản khác chính nó.

*Văn bản không nêu số Điều* (cấp dưới luật, có `based_on` BLLĐ 2019, mà regex không ra `details` tới BLLĐ: hiện là ND_12, ND_70, ND_74, ND_283):
1. **Từ khoá** (`propose_by_keyword :178`): `key_phrases :96` lấy cụm danh từ sau "quy định (về)" ở Điều 1; `head_phrase :104` bỏ từ cuối rồi so với **tiêu đề Điều** của BLLĐ, ưu tiên Điều có điều khoản giao.
2. **LLM** (`--llm replay|live`, `llm_propose :222`): hai lượt **độc lập** (model chính rồi model kiểm, cùng đầu vào, lượt sau không thấy lượt trước). Đầu vào (`llm_user_message :199`): chữ Điều 1, tiêu đề các Điều của văn bản, danh sách điều khoản giao (mã, tiêu đề Điều, cụm); **không có gợi ý đích nào**. `validate_targets :208`: mã trả về phải nằm trong danh sách được cho, tối đa 5; ngoài danh sách thì loại cả lượt.
3. **Quyết định** (`decide_llm :244`): cạnh được **GIỮ** khi *cả ba*: model chính đề xuất Điều đó, model kiểm đề xuất độc lập cùng Điều, và kiểm từ khoá đạt (cụm danh từ chính của phạm vi điều chỉnh nằm trong tiêu đề hoặc chữ của Điều đích). Trượt một trong ba thì vẫn ghi nhưng gắn cờ `isolated` (không dùng khi hỏi đáp). Đề xuất chỉ do từ khoá thì không bao giờ được giữ khi đã chạy LLM. Khi LLM chưa có kết quả, cạnh ở mức từ khoá với cờ `llm_check_pending`.

*`filled_by`:* mỗi điều khoản giao ghi các văn bản đã có `details` tới chính nó (hoặc tổ tiên, con cháu của nó), sắp theo ngày hiệu lực.

*Cổng* (`l3_links.py:326-338`, `:354`): 4 mốc `delegation_clauses` (D91.K4 dạng A; D154.K1/K2/K9 dạng B; D142.K1 dạng D; D112 dạng E) và 5 mốc `details` / `based_on` (xem ví dụ). Mốc ND_74 → Điều 91 không tính vào điều kiện thoát mã 1 vì phụ thuộc LLM.

**Code chính** (`src/l3_links.py`): `find_delegation :61` · `lead_tail :85` · `key_phrases :96`, `head_phrase :104`, `keyword_candidates :110` · `based_on_links :122` · `details_links :155` · `propose_by_keyword :178` · `llm_user_message :199`, `validate_targets :208`, `llm_propose :222`, `decide_llm :244` · `main :266`.

**Ví dụ thật.**
- `DC_D91_K4_1`: Điều 91 khoản 4, dạng A, "Chính phủ quy định chi tiết Điều này; quyết định và công bố mức lương tối thiểu...", `filled_by = [ND_74-2024]`.
- `DC_D142_K1_1`: dạng D "Bộ trưởng Bộ Lao động - Thương binh và Xã hội ban hành danh mục nghề...", `filled_by = [TT_10-2020-BLDTBXH]`.
- `DC_D107_K3_dd_1`: dạng A phụ C "Trường hợp khác do Chính phủ quy định.", `filled_by = [ND_145-2020]`.
- `based_on`: `TT_18-2021-BLDTBXH → ND_145-2020.D68.K2` (và `→ ND_145-2020`), `evidence` là dòng "Căn cứ khoản 2 Điều 68 Nghị định số 145/2020/NĐ-CP ..." (chuỗi hướng dẫn 3 tầng).
- `details` bằng regex: ND_152 → D154.K1, K2, K9, D157, D150.K3; TT_10 → D21.K1-3, D73.K4, D142.K1; ND_135 → D169.
- `ND_74-2024 → BLLD_45-2019.D91`: `how = llm`, `flags = [llm_proposed]`, `check = {first_llm: true, second_llm: agree, keyword: "mức lương tối thiểu"}` → **giữ** (hai model và từ khoá đồng ý).
- `ND_70-2023 → D150, D154, D157`: `flags = [llm_proposed, isolated]`: hai model đề xuất giống nhau nhưng kiểm từ khoá không đạt (điều kiện còn lại duy nhất ở `decide_llm :257`) nên cô lập.
- ND_12 và ND_283: hai model đều trả mảng rỗng (nghị định xử phạt), không có `details`.

**Số đếm.** 51 cụm ở 51 đơn vị: A 35 (34 Điều, trong đó 2 cụm phụ C), B 10 (8 Điều), D 5 Điều (61, 142, 143, 146, 160), E 1 Điều (112). 10 `based_on`; 48 `details` (44 regex + 4 LLM); 18 chờ đích; 36 điều khoản có `filled_by`. 7 văn bản không có `based_on`: ND_90 và ND_28 (căn cứ BLLĐ 2012: chờ đích), TT_09 / TT_10 / TT_11 (mất đầu văn bản), TT_19 và NQ_66-16 (không căn cứ vào văn bản trong kho). 9/9 mốc đạt.

**Tự kiểm.** 3 test (`tests/test_l3_l4_l5.py`: các dạng giao, cụm từ khoá, mốc trên dữ liệu) và 5 test L3 trong `tests/test_llm_steps.py` (`validate_targets`; hai lượt độc lập, cùng đầu vào khác model; lượt lỗi thành `None` kèm ghi chú; chỉ giữ cạnh khi hai model và từ khoá cùng đồng ý; cô lập khi model kiểm bất đồng, từ khoá trượt, hoặc chỉ có từ khoá). `checks.py` kiểm đích của mọi `based_on` / `details` có thật.

**Giới hạn.**
- Dạng A: 35 cụm / 34 Điều, plan nêu 39 / 37; **chênh 4 cụm chưa giải thích được** (regex yêu cầu "quy định" đứng ngay sau chủ thể và không đứng trước "tại"; plan có thể đếm lỏng hơn).
- **Chưa lọc ca không phải giao chi tiết**: D61.K4, D160.K2 khớp mẫu D nhưng nghĩa là điều kiện.
- Kiểm từ khoá hợp với văn bản có phạm vi riêng (ND_74), kém với văn bản sửa đổi (ND_70: các Điều đúng nhưng bị cô lập).
- Docstring đầu `l3_links.py` (dòng 16-18) còn ghi lượt LLM kiểm "chưa chạy"; thực tế đã chạy ngày 09/11 (xem `_usage.json`).
- 7 văn bản không có `based_on`, và 8 văn bản không có `details` (ND_90, ND_28, TT_11, TT_18, TT_19, NQ_66-16: Điều 1 không nêu điều, khoản đích; ND_12 và ND_283: LLM trả mảng rỗng). Văn bản nào chưa nối được thì để trống, không đoán.

**Chạy lại.** `python -I src/l3_links.py [--llm off|replay|live]` (cả kho; thoát mã 1 nếu mốc cổng trượt).

---

## L4. Phân loại Điều

**Việc làm.** Gắn mỗi Điều và mỗi phụ lục một nhãn: `substantive` (điều kiện, quyền, nghĩa vụ, mức, thời hạn, ngoại lệ, chế tài), `definition`, `effect_transition` (hiệu lực, chuyển tiếp, bãi bỏ, và các Điều "Sửa đổi, bổ sung ..." của văn bản sửa đổi), `procedural`, `authority`, `appendix`. Nhãn cho biết Điều đi tiếp tới bước nào; **mọi Điều vẫn nằm trong kho, vẫn có phiên bản và vẫn là đích sửa đổi được.** Hiện chỉ L6 dùng nhãn: nó chỉ đọc câu chỉ thị hiệu lực từ Điều nhãn `effect_transition`.

**Vào → Ra.** Vào: `l1_triples_*`. Ra: `data/processed/l4/l4_labels.jsonl` (`{id, label, how, heading, flags}`), `docs/bao_cao_chay/l4/l4_report.txt`. Tác vụ cache: `data/llm_cache/l4_classify/`.

**Cách làm.**
1. **Regex trên tiêu đề trước** (`RULES :37`, `classify_heading :62`), `how = regex`:
   - `definition`: "Giải thích từ ngữ";
   - `effect_transition`: "Hiệu lực (thi hành)", "Quy định chuyển tiếp", "Điều khoản chuyển tiếp / thi hành", "Bãi bỏ", "Sửa đổi (, bổ sung)", "Bổ sung", "Thay thế", "Hết hiệu lực", "Áp dụng pháp luật";
   - `authority`: "Trách nhiệm của <Bộ, cơ quan, Ủy ban, Sở, Chính phủ, ...>", "Trách nhiệm thi hành / quản lý nhà nước", "Thẩm quyền", "Nhiệm vụ", "Quyền hạn", "Tổ chức thực hiện", "Cơ quan". "Trách nhiệm khi chấm dứt hợp đồng lao động" **không** là `authority` (là nghĩa vụ của các bên; có test);
   - `procedural`: "Hồ sơ", "Trình tự", "Thủ tục", "Cách thức", "Tiếp nhận", "Nộp hồ sơ", "Thời hạn giải quyết", "Quy trình".
2. **Không khớp mẫu nào** thì mang nhãn **tạm** `substantive` (an toàn: không bỏ sót quy tắc), `how = default_pending_llm`, cờ `llm_pending`. **Phụ lục** thì `appendix`, `how = type` (`build_rows :181`).
3. **Nhánh LLM** (`--llm replay|live`, `llm_classify :169`), chỉ xử lý các Điều nhãn tạm:
   - `collect_items :80` gom theo (tiêu đề, đoạn đầu 160 ký tự) đã chuẩn hoá bằng `text_norm`: bản hợp nhất trùng BLLĐ chỉ hỏi một lần. 742 Điều thành 504 mục duy nhất, chia lô 40 (`BATCH :33`) thành 13 lượt model chính.
   - `validate_labels :97`: đầu ra phải đúng lược đồ, đủ và không thừa mã, nhãn thuộc `LABELS`, không trùng. Sai thì **loại cả lô** (Điều giữ nhãn tạm, phản hồi vào `_rejected/`).
   - **Nhãn đẩy một Điều ra khỏi `substantive`** (`VERIFY_LABELS :35`: `effect_transition`, `procedural`, `authority`) chỉ được nhận khi **model kiểm** (model khác, cùng đầu vào, không thấy kết quả của model chính) phân loại ra **cùng nhãn**. Khác nhau hoặc chưa kiểm được thì trả về nhãn tạm (cờ `llm_disagree` / `llm_unverified`). Lý do bất đối xứng: nhãn sai theo hướng này làm mất quy tắc của một điều có điều kiện thật; nhãn sai ngược lại chỉ thêm một lần trích thừa. (`apply_llm :148`.)
4. Hết hạn mức thì dừng gọn (`QuotaReached`); các lô đã gọi nằm trong cache.

**Code chính** (`src/l4_classify.py`): `RULES :37` · `classify_heading :62` · `collect_items :80` · `validate_labels :97` · `ask_batch :114` · `run_pass :127` (một lượt theo lô với một vai) · `apply_llm :148` · `llm_classify :169` · `build_rows :181` · `main :195`.

**Ví dụ thật.** Phân bố nhãn BLLĐ: substantive 168, definition 21, authority 18, effect_transition 7, procedural 6. Điều 187 "Thẩm quyền giải quyết tranh chấp lao động cá nhân" → `authority`, `how = regex`. Điều 49 "Hợp đồng lao động vô hiệu" → `substantive`, `how = llm`. Điều 77 "Gửi thỏa ước lao động tập thể" và Điều 92 "Hội đồng tiền lương quốc gia" là hai trong 28 Điều mà model chính đề xuất đẩy ra khỏi `substantive` nhưng model kiểm không đồng ý: trả về nhãn tạm (`flags = [llm_pending, llm_disagree]`).

**Số đếm (toàn kho).** 921 nhãn = 893 Điều + 28 phụ lục. Cách xếp: regex 151, LLM 714, nhãn tạm chờ (model kiểm không đồng ý) 28, phụ lục 28. Kết cục LLM theo Điều: substantive 621, definition 50, authority 34, procedural 9, trả về nhãn tạm 28. **Cả 39 Điều `effect_transition` đều do regex; LLM không đặt Điều nào** (báo cáo ghi "Điều do LLM đặt nhãn effect_transition: 0"), nên hiện nhãn LLM chưa chảy vào L6.

**Tự kiểm.** `test_l4_classify_headings` (`tests/test_l3_l4_l5.py`) và 8 test L4 trong `tests/test_llm_steps.py`: lô sai bị loại; Điều trùng chỉ hỏi một lần; luồng đầy đủ chỉ áp phần qua kiểm; không có lượt kiểm thì không áp nhãn đẩy ra; lô bị loại không đổi dòng nào; hết hạn mức dừng gọn và giữ lô đã xong; replay với cache rỗng không đổi gì và không gọi; replay đọc lại đúng phần live đã lưu mà không tốn lượt. `checks.py` kiểm mọi Điều có nhãn.

**Giới hạn.**
- Chưa có bộ nhãn do người gán nên **chưa đo được độ chính xác** của nhãn LLM. Mẫu ngẫu nhiên trong báo cáo có ca đáng xem lại: Điều 9 "Việc làm, giải quyết việc làm" → `definition`, Điều 142 "Nghề, công việc có ảnh hưởng xấu tới chức năng sinh sản..." → `authority` (cả hai `how = llm`).
- Nhãn `form` của plan chưa dùng (L1 chưa tách "Mẫu số").
- Nếu sau này LLM đặt nhãn `effect_transition` cho Điều nào thì L6 sẽ đọc chỉ thị từ đó. Có quyết định còn treo (cho L6 chỉ tin nhãn regex tới khi người duyệt), xem `docs/tien_do_L0_L6.md` mục "Việc user cần quyết".
- Đổi prompt phải đổi `PROMPT_VERSION` (`l4-1`); khoá cache đã băm cả chữ system và lược đồ nên không dùng nhầm, nhưng đổi tên model thì chạy lại từ đầu.

**Chạy lại.** `python -I src/l4_classify.py [--llm off|replay|live]` · `python -I tests/test_l3_l4_l5.py`.

---

## L5 tường minh (`l5_explicit`): ngoại lệ nói thẳng trong chữ

**Việc làm.** Tìm các câu **nói thẳng** đây là ngoại lệ và nối bằng cạnh `exception_of`. Chiều cạnh: **nguồn (`s`) là phần ngoại lệ, đích (`o`) là quy tắc bị ngoại trừ.** Chạy cho mọi văn bản.

**Vào → Ra.** Vào: `l1_triples_*` và các hàm giải đích của L2 (kể cả sang văn bản khác). Ra (`data/processed/l5_explicit/`): `l5_explicit_exceptions_<doc>.jsonl` (`{s, p, o, evidence, method}`), `l5_explicit_unhandled_<doc>.jsonl` (trigger không rơi vào hai quy tắc), `l5_explicit_pending_<doc>.jsonl` (đích ở văn bản chưa có trong kho), và `docs/bao_cao_chay/l5_explicit/l5_explicit_report_<doc>.txt`.

**Cách làm: đúng hai quy tắc, không có bộ khớp tổng quát.**

| Quy tắc | Dấu hiệu | Cạnh sinh ra |
|---|---|---|
| `not_apply_pattern` | Đơn vị U có "không áp dụng" và **ngay trước nó** (chỉ cách dấu cách) là một cụm dẫn chiếu | U `exception_of` mỗi đích của cụm |
| `except_list_pattern` | Chữ của U có "trừ" hoặc "ngoại trừ" và **kết thúc bằng "sau đây:"** | Mỗi đơn vị con trực tiếp của U `exception_of` U |

- **Trigger** (`TRIGGER_RE :36`): "ngoại trừ", "trừ", "không áp dụng" (biên từ). `find_triggers :52` bỏ dòng chỉ thị sửa đổi (ngoại lệ trong đó thuộc văn bản bị sửa).
- Quy tắc 1 giải đích bằng `l2.resolve_ref`; đích không giải được hoặc không tồn tại thì vào `unhandled`; đích ở văn bản chưa có trong kho thì vào `pending`. Quy tắc 2 bỏ qua nếu đơn vị có hơn một cụm "trừ" hoặc không có con.
- **Mỗi trigger thuộc đúng một trong hai:** đã xử lý (có cạnh) hoặc `unhandled`. `check_exceptions :106` đếm cho khớp, nên không trigger nào mất. **Không nới quy tắc để bắt thêm ca.**

**Code chính** (`src/l5_explicit_exceptions.py`): `TRIGGER_RE :36` · `find_triggers :52` · `find_exceptions :62` (hai quy tắc) · `check_exceptions :106` (không trùng, không tự trỏ, evidence đúng chỗ, đếm trigger khớp) · `run_doc :134`.

**Số đếm.** 256 trigger trên 18 văn bản: 5 được xử lý (đều quy tắc 2, ở ND_12, ND_145, ND_283 mỗi văn bản 1 câu, ND_28 2 câu) sinh 23 cạnh; 251 vào `unhandled` (lý do duy nhất: "ngoài hai quy tắc của L5 tường minh"). **Quy tắc 1 không sinh cạnh nào trên dữ liệu thật** (chỉ có ca dựng trong test).

**Ví dụ thật** (5 câu của quy tắc 2, đọc nguyên văn ngày 10/11):
- `ND_145-2020.D59.K1`: "Trừ các trường hợp quy định tại Điều 108 của Bộ luật Lao động, các trường hợp khác khi tổ chức làm thêm giờ, người sử dụng lao động phải được sự đồng ý của người lao động tham gia làm thêm về các nội dung sau đây:" → 3 cạnh `D59.K1.a`... `exception_of D59.K1` (điểm a: "Thời gian làm thêm;").
- `ND_12-2022.D17.K2`, `ND_28-2020.D11.K1`, `ND_28-2020.D16.K2`, `ND_283-2026.D23.K2`: các câu phạt tiền kết thúc bằng "theo một trong các mức sau đây:", mỗi câu có 5 con.

**Tự kiểm.** 3 test riêng của L5 tường minh trong `tests/test_l3_l4_l5.py`: quy tắc 2 (con là ngoại lệ của cha); quy tắc 1 cần cụm đứng ngay trước; bỏ dòng chỉ thị. Cộng `test_l5_every_trigger_is_accounted_for` (chung với L5 chung: mọi trigger của cả 18 văn bản thuộc đúng một trạng thái).

**Giới hạn: cần xem lại.**
- **Quy tắc 2 nhiều khả năng bắt nhầm cả 5 câu trên dữ liệu thật.** Khi đọc nguyên văn: 4 câu là "…theo một trong các mức sau đây:" với chữ "trừ" nằm trong "khấu trừ tiền lương" (ND_12 D17.K2, ND_28 D16.K2, ND_283 D23.K2) hoặc trong "trừ trường hợp kéo dài thời hạn hợp đồng lao động..." giữa câu (ND_28 D11.K1), và các con là **mức phạt**, không phải ngoại lệ; câu còn lại (ND_145 D59.K1) mở đầu bằng "Trừ các trường hợp...", các con là **nội dung phải thoả thuận**. Nghĩa là cả 23 cạnh `l5_explicit` rất có thể sai, và đang nằm trong đồ thị (300 cạnh `exception_of` của graph gồm 23 cạnh này). Test hiện có chỉ dựng ca đúng; chưa có test chặn dạng "trừ" không đứng ở vị trí mệnh đề ngoại lệ. Tài liệu này chưa sửa code: đây là phát hiện khi viết, cần người quyết định.
- **Hệ quả sang L5 chung (đã chạy `GENERAL_RE` lên cả 5 câu):** L5 chung chỉ nhận trigger mà L5 tường minh *để lại* (`l5_general_exceptions.py:80`). Trong 5 câu chỉ **ND_28 D11.K1** khớp `GENERAL_RE` (vị trí 268, "trừ trường hợp kéo dài thời hạn hợp đồng lao động với người lao động cao tuổi...") nên đây là ca ngoại lệ chung thật đang bị L5 tường minh lấy trước và L5 chung không bao giờ thấy. Bốn câu còn lại không khớp `GENERAL_RE`: ba câu chỉ có "khấu trừ", còn ND_145 D59.K1 mở đầu "Trừ **các** trường hợp quy định tại Điều 108" nên không khớp vì có chữ "các"; nghĩa là dù L5 tường minh nhả ra thì L5 chung cũng không nhận.
- Mốc kiểm `exception_of` của `checks.py` toàn thuộc L5 chung, nên L5 tường minh hiện không có mốc kiểm nào bắt được lỗi trên.

**Chạy lại.** `python -I src/l5_explicit_exceptions.py <doc_id>` hoặc `--all`.

---

## L5 chung (`l5_general`): ngoại lệ chung "…, trừ trường hợp X"

**Việc làm.** Câu "…, trừ trường hợp có thỏa thuận khác" có phần ngoại lệ **không phải một Điều/Khoản cụ thể** mà là một *điều kiện*. L5 chung tạo một **nút điều kiện** cho phần đó và nối nó vào quy tắc bị ngoại trừ.

**Vào → Ra.** Vào: `l1_triples_*`, và các trigger L5 tường minh để lại (L5 chung gọi lại `l5x.find_exceptions` trong cùng tiến trình, `l5_general_exceptions.py:146`). Ra (`data/processed/l5_general/`): `l5_general_conditions_<doc>.jsonl` (nút `{id, type = dieu_kien, kind, text, units}`), `l5_general_exceptions_<doc>.jsonl`, `l5_general_unhandled_<doc>.jsonl`, `l5_general_pending_<doc>.jsonl`, và `docs/bao_cao_chay/l5_general/`.

**Cách làm.**
1. Từ các trigger L5 tường minh để lại, nhận trigger mà tại vị trí đó khớp `GENERAL_RE :31` ("(ngoại) trừ trường hợp"). "Không được áp dụng" ghi `unhandled`. Một đơn vị có **hơn một** "trừ trường hợp" thì `unhandled`, không đoán.
2. **Mệnh đề X** (`clause_of :55`) = chữ sau "trừ trường hợp" đến hết đoạn (bỏ `. ; : ,` cuối). Nếu "trừ trường hợp" đứng **đầu đoạn** thì X dừng ở dấu phẩy đầu tiên (phần sau là quy tắc chính). Thiếu dấu phẩy hoặc mệnh đề rỗng thì `unhandled`.
3. **Nút điều kiện:** id `<doc_id>.X<8 ký tự đầu sha1 của khoá chuẩn hoá>` (`condition_id :51`; `norm_text :38`: gộp khoảng trắng, hoa/thường, bỏ `. ; : ,` hai đầu). Mệnh đề giống nhau thì **một** nút, nối nhiều đơn vị; dùng băm để mã ổn định khi tập câu đổi.
4. **Phân loại** (`condition_kind :43`): `tuy_nghi` ("(các bên) có thỏa thuận khác"), `dan_chieu_mo` ("pháp luật có quy định khác"), còn lại `cu_the`. Hai loại đầu là câu chung chung, một nút nối nhiều Điều không liên quan.
5. **Cạnh:** nút điều kiện `exception_of` đơn vị chứa câu (`method = general_except`). Nếu mệnh đề dẫn chiếu tới đơn vị T (giải bằng `l2.find_refs` + `resolve_ref`, T có thể ở văn bản khác) thì thêm cạnh `T exception_of` đơn vị (`method = general_except_ref`).
6. **Kiểm** (`check_general :117`): không trùng; evidence nằm trong chữ đơn vị; mỗi nút có cạnh; số trigger L5 tường minh để lại = đã xử lý + `unhandled`.

**Code chính** (`src/l5_general_exceptions.py`): `GENERAL_RE :31` · `TUY_NGHI_RE :33`, `DAN_CHIEU_RE :35` · `clause_of :55` · `find_general :76` · `check_general :117` · `run_doc :144`.

**Ví dụ thật** (BLLĐ).
- `D35.K2.a` "...theo thỏa thuận, trừ trường hợp quy định tại Điều 29 của Bộ luật này;" → nút `BLLD_45-2019.X1162b718` (`cu_the`, text "quy định tại Điều 29 của Bộ luật này") `exception_of D35.K2.a` (`general_except`), và `BLLD_45-2019.D29 exception_of D35.K2.a` (`general_except_ref`, vì mệnh đề nhắc Điều 29).
- Nút `tuy_nghi` `Xbdd95425` "hai bên có thỏa thuận khác" nối `D28` và `D168.K2`; `X798cfde0` "các bên có thỏa thuận khác" nối 4 đơn vị (`D35.K2.e`, `D70.K2`, `D83`, `D207.K2`).
- `D154` `exception_of` `D151.K1.d` (cùng nút điều kiện `X01f711f0`): "trừ trường hợp quy định tại Điều 154". Cạnh đi từ đơn vị được dẫn tới đơn vị chứa "trừ trường hợp", cùng chiều với "s là phần ngoại lệ".

**Số đếm.** Toàn kho: 128 nút (cu_the 116, tuy_nghi 8, dan_chieu_mo 4), 336 cạnh (156 `general_except` + 180 `general_except_ref`), 95 `unhandled` (90 ngoài hai quy tắc, 5 đơn vị có hơn một "trừ trường hợp"). Riêng BLLĐ: 30 nút (26 / 3 / 1; 39 đơn vị), 59 cạnh (39 + 20). Graph chỉ có 98 nút điều kiện vì không đưa nút của bản hợp nhất (VBHN_125 lặp lại 30 nút của BLLĐ).

**Tự kiểm.** 3 test riêng của L5 chung (`tests/test_l3_l4_l5.py`): tách mệnh đề; kiểu nút và khoá gộp; **4 mốc trên chữ thật của BLLĐ** (`D154 → D151.K1.d`, `D36.K1.b → D37.K1`, `D29 → D35.K2.a`, `D97.K4 → D35.K2.b`); cộng `test_l5_every_trigger_is_accounted_for` dùng chung với L5 tường minh. `checks.py` kiểm lại 4 mốc đó và hai đầu cạnh tồn tại.

**Giới hạn.**
- Phần tách điều kiện / hệ quả và phạm vi vế (ví dụ một "trừ trường hợp" chỉ áp cho một vế của câu) **chưa làm**: mệnh đề là toàn bộ chữ đến hết đoạn.
- 90 trigger "ngoài hai quy tắc" gồm cả "trừ" không phải ngoại lệ (như "khấu trừ"); chưa lọc.
- Plan nêu BLLĐ có 42 cụm ngoại lệ; L5 chung ra 30 nút ở 39 đơn vị. Hai con số đếm theo đơn vị khác nhau, chưa đối chiếu cụm với cụm.
- **`GENERAL_RE` chỉ nhận "trừ trường hợp"**: dạng "Trừ **các** trường hợp ..." (ND_145 Điều 59 khoản 1) không khớp nên ở lại `unhandled`. Đếm thô bằng regex trong `l5_general_unhandled_*`: 7 trigger nằm trong câu chứa "trừ các / những trường hợp" (ND_145 3, ND_152 4); chưa xác minh từng ca.
- Ngoại lệ chung trong câu mà L5 tường minh đã nhận trước không đến được đây: hiện có 1 ca (ND_28 D11.K1, xem Giới hạn của L5 tường minh).

**Chạy lại.** `python -I src/l5_general_exceptions.py <doc_id>` hoặc `--all` (chạy sau L5 tường minh).

---

## L6. Phiên bản theo ngày hiệu lực

**Việc làm.** Dựng **kho phiên bản** của mọi đơn vị và chạy vòng *nạp từng văn bản theo ngày hiệu lực*. Mỗi văn bản là một sự kiện: thêm đơn vị của nó, **đọc câu chỉ thị từ chính chữ văn bản** (không dùng cột `quan_he` của manifest), mở phiên bản mới, đóng phiên bản cũ. **Không xoá nút.**

**Vào → Ra.**
- Vào: L1 (đơn vị, khối trích dẫn, chú thích), L4 (nhãn), L3 (`l3_links.jsonl`, cho loại 25), manifest (ngày hiệu lực).
- Ra (`data/processed/l6/`): `versions.jsonl` (mọi phiên bản), `version_edges.jsonl` (cạnh cập nhật), `pending_links.jsonl` (chờ đích của L6, tách khỏi của L2), `corrections.jsonl` (đính chính; hiện rỗng), `events/<doc_id>.json` (nhật ký mỗi sự kiện, 18 file). Báo cáo `docs/bao_cao_chay/l6/l6_report.txt` (số liệu, cờ, chỉ thị chưa hiểu, 15 mốc cổng).

**Mô hình phiên bản** (`src/l6_versions.py`).
- `Ver :50`: `id, version, type, number, heading, text, parent, effective_from, effective_to, applies_from, state, trigger, source_event, closed_by, previous_version, flags, directive, footnote`. `in_force(d) :71`: `state == normal` và `from ≤ d < to`. `to_row :85` thêm `text_norm` và `status`.
- `state ∈ normal | pending_event | suspended`. `pending_event` (hiệu lực có điều kiện, chưa kích hoạt) và `suspended` (tạm ngưng hoặc chưa chắc) **không bao giờ** `in_force`. `status` tính tại `as_of` (ngày hiệu lực của sự kiện cuối, 2026-09-10): `in_force | expired | pending_event | suspended | not_yet`.
- `Store :94`: `new_version :134` đóng bản hiện hành tại ngày hiệu lực rồi mở bản kế (hai chỉ thị cùng sự kiện sửa cùng đơn vị thì sửa tại chỗ, không tạo phiên bản rỗng `[d, d)`); `close :154` và `close_tree :164` đóng mà không thay chữ; `add_edge :170`; `snapshot :175` (mỗi đơn vị một phiên bản hiệu lực tại một ngày).
- `text_norm :35`: khoá so khớp chữ giữa hai bản: NFC, hoa/thường, kiểu đặt dấu thanh (hòa/hoà, ủy/uỷ), bỏ `[n]`, thống nhất gạch, **bỏ mọi khoảng trắng**, bỏ dấu câu cuối. Hai chữ chỉ khác chuẩn hoá thì không tạo phiên bản; khác ở số ("điều 189" và "điều 89") vẫn khác.

**Vòng nạp** (`l6_versions.main :221`): nạp BLLĐ gốc (phiên bản 1, hiệu lực từ 2021-01-01, không là sự kiện) rồi `order_docs :194` (theo ngày hiệu lực, cùng ngày theo ngày ban hành rồi `doc_id`), mỗi văn bản gọi `apply_event` (`l6_directives.py:263`). Với văn bản không phải bản hợp nhất, `apply_event` làm lần lượt:

| # | Bước | Hàm | Loại |
|---|---|---|---|
| 1 | Đọc câu "<loại> này có hiệu lực ... [đến hết ngày ...]", đối chiếu manifest; có "đến hết ngày X" thì `term_end = X + 1` | `own_effective :293` | 13 |
| 2 | Nạp mọi đơn vị làm phiên bản 1 từ ngày hiệu lực (đến `term_end` nếu có) | `add_doc_units :185` | |
| 3 | Căn cứ BLLĐ 2012 thì gắn cờ `law_2012_era_document`, không nối vào BLLĐ 2019 | | 18 |
| 4 | Dòng chỉ thị có đích (xem dưới) | `amending :312` | 1, 2, 3, 4, 16, 20 |
| 5 | Câu hiệu lực / hết hiệu lực, **chỉ ở Điều nhãn `effect_transition`** | `effect_statements :475` | 5, 10, 11, 13, 24 |
| 6 | Bổ sung danh mục | `supplements :661` | 8 |
| 7 | Cạnh `overrides` trong `[hiệu lực, term_end)` | `overrides :700` | 14 |
| 8 | Quét mẫu câu loại hiếm | `l6_rare.apply_rare` | 19, 21, 22, 26 |
| 9 | Văn bản vừa nạp có kích hoạt đơn vị `pending_event` không | `check_triggers :647` | 12 |
| 10 | Văn bản được hướng dẫn bị sửa thì đánh cờ văn bản hướng dẫn | `mark_parent_changed` | 25 |

*Bước 4, dòng chỉ thị* (`amending :312`): văn bản bị sửa lấy từ đuôi gần nhất đi ngược từ đơn vị lên tổ tiên (`directive_doc :171`), giải bằng `Resolver`; chưa có trong kho thì ghi chờ đích (`pending_target_doc`). Sau đó phân theo dạng:
- **Có khối trích dẫn** → `payload_directive :365` (loại 1, 2: sửa / bổ sung "như sau"): `parse_payload :64` dựng khối thành cây Điều/Khoản/Điểm; `apply_node :199` đặt chữ (con cũ không còn trong khối thì **bị đóng**, cờ `removed_by_replace`; mã đã đóng thì mở lại, cờ `reopened`); bổ sung vào mã đã có hoặc cha không tồn tại là lỗi. "Sửa đổi tên khoản..." chỉ đổi chữ, không đóng con (`rename_only`). Cạnh `amends` / `replaces`.
- **Có cụm trong nháy “…”** → `phrase_directive :429` (loại 3: thay / bỏ cụm từ): `mask_quotes :251` thay cụm bằng `§k§`; `replace_phrase :236` khớp mềm (khoảng trắng, dấu thanh, hoa/thường). Cụm không thấy trong đích thì ghi "đích / cụm không khớp", không làm lỗi cả bước.
- **"Bãi bỏ ..." không khối** → `repeal_directive :412` (loại 4): `close_tree`, cờ `repealed`.
- Chỉ thị sửa **Mẫu số / Phụ lục** của văn bản bị sửa mà kho không có mẫu → cờ `form_directive_target_not_in_kb`, không lỗi.
- Không thuộc dạng nào → **`unknown_directive`**, không áp, không đoán.

*Bước 5, câu hiệu lực* (chỉ đọc Điều `effect_transition`): "Nội dung về X quy định tại <văn bản> hết hiệu lực" → `topic_expire :558` (loại 10); "<đích> ... có hiệu lực kể từ ngày <sự kiện> có hiệu lực" → `conditional :599` (loại 11); "quy định tương ứng trong Nghị quyết này hết hiệu lực" → cạnh `ends_when_replaced` (loại 13); "X hết hiệu lực" → `repeal_docs :510` / `repeal_one :524` (loại 5, 24): cả văn bản thì đóng cả cây tại ngày nêu trong câu và cạnh `replaces`; đơn vị của văn bản khác thì chờ đích (`pending_unit_repeal`); văn bản ngoài kho thì chờ đích và cạnh tới `external:<số hiệu>`; câu "bị hủy bỏ / bãi bỏ vì trái ..." đóng như loại 5 và gắn cờ `annulled`.

*Loại 10, hết hiệu lực theo chủ đề* (`topic_expire`): không theo số điều mà theo **tiêu đề Chương** (regex, không LLM): Chương có tiêu đề chứa chủ đề thì đóng; Chương chung ("quy định chung", "điều khoản thi hành", "điều khoản chuyển tiếp") thì `suspended` + cờ `topic_uncertain` (không tự quyết); Chương khác giữ nguyên.

*Loại 11 và 12, hiệu lực có điều kiện* (`conditional`, `check_triggers`): đơn vị đích thành `pending_event`, `effective_from = null`, `trigger` = nguyên văn mô tả sự kiện, cạnh `pending_on`. Văn bản nạp sau kích hoạt đơn vị chỉ khi **đủ ba điều kiện** (`trigger_matches :627`): (1) cùng loại với câu mô tả ("Nghị định ..."), (2) mọi số hiệu mô tả nêu đều có trong chữ của nó, (3) cụm mô tả chính nó (dài ≥ 12 ký tự sau chuẩn hoá) nằm trong Điều 1 của nó. Chỉ nhắc đúng số hiệu là chưa đủ: ND_219 Điều 35 trích đúng hai số hiệu mà ND_283 Điều 66 khoản 3 trích, nhưng không phải văn bản đó. Thất bại là an toàn (đơn vị vẫn chờ).

*Bản hợp nhất, loại 15* (`consolidation_compare :742`): VBHN_125 **không tạo nút riêng**; so từng đơn vị với BLLĐ bằng `text_norm`. Giống thì không đổi; khác thật **và** chú thích có "có hiệu lực kể từ ngày ..." thì mở phiên bản / đơn vị mới từ ngày đó (không lấy ngày ký bản hợp nhất); chỉ khác chỗ ngắt dòng (`line_only_dieu :721`: cùng tập đơn vị, cùng bộ ký tự) thì bỏ qua; khác mà không có chú thích thì cờ `consolidation_discrepancy`, **không tạo phiên bản**.

*Loại hiếm* (`src/l6_rare.py`): kho không có ca thật; mỗi loại là một hàm nhỏ trên `Store` cộng một mẫu câu, câu không khớp thì không làm gì. 16 bãi bỏ một phần phụ lục (`repeal_appendix :100`); 19 hồi tố (`retroactive :43`: đặt `applies_from` sớm hơn `effective_from`; hồi tố đặt trách nhiệm mới / nặng hơn thì chặn, cờ `retroactive_blocked`); 20 đính chính (`correct :63`: giữ cả hai chữ, cạnh `corrects`, **không** tạo phiên bản pháp lý); 21 tạm ngưng (`suspend :74`); 22 đánh số lại (`renumber :87`: mã cũ đóng, mã mới mở với chữ cũ, cạnh `renumbered_to`); 25 văn bản được hướng dẫn bị sửa (`mark_parent_changed :111`: cờ và cạnh, **không** đóng văn bản hướng dẫn); 26 thay cả văn bản cùng tên (`possible_replacement :121`: cờ, không tự đóng; so tên bằng cột `ten_ngan` của manifest).

**Các loại thay đổi:**

| Loại (theo plan) | Việc | Nơi cài | Ca thật |
|---|---|---|---|
| 1, 2 | Sửa / bổ sung đơn vị "như sau" | `payload_directive` | có |
| 3 | Thay / bỏ cụm từ | `phrase_directive` | có |
| 4 | Bãi bỏ đơn vị | `repeal_directive` | có |
| 5 | Hết hiệu lực cả văn bản | `repeal_docs`, `repeal_one` | có |
| 6, 7 | Văn bản hướng dẫn lấp điều khoản giao; chuỗi 3 tầng | L3 (`details`, `based_on`) | có |
| 8 | Bổ sung danh mục, không sửa dòng cũ | `supplements` | có |
| 9 | Điều khoản chuyển tiếp | giữ thành đơn vị | có |
| 10 | Hết hiệu lực theo chủ đề | `topic_expire` | có |
| 11 | Hiệu lực có điều kiện (chờ sự kiện) | `conditional` | có |
| 13, 14 | Hiệu lực có thời hạn; áp dụng thay trong thời hạn | `own_effective`, `overrides` | có |
| 15 | Bản hợp nhất | `consolidation_compare` | có |
| 17 | Chưa có hiệu lực tại ngày hỏi | `status = not_yet` | có |
| 18 | Ban hành theo luật cũ | cờ `law_2012_era_document` | có |
| 23 | Danh sách số trần "Điều 5, 6 và 8" | L2 (`find_refs`, `chain_targets`) | có |
| 12 | Kích hoạt hiệu lực có điều kiện | `check_triggers`, `trigger_matches` | không (fixture) |
| 16, 19, 20, 21, 22, 24, 25, 26 | Xem đoạn "Loại hiếm" | `l6_rare.py`, `repeal_one` | không (fixture) |

**Code chính** (`src/l6_directives.py` trừ khi ghi khác): `Context.build :118` (nạp mọi đầu vào) · `apply_event :263` · `own_effective :293` · `amending :312` · `payload_directive :365`, `repeal_directive :412`, `phrase_directive :429` · `effect_statements :475`, `repeal_docs :510`, `repeal_one :524`, `topic_expire :558`, `conditional :599` · `trigger_matches :627`, `check_triggers :647` · `supplements :661`, `overrides :700` · `consolidation_compare :742` · `dev_gates :817` (15 mốc cổng). `l6_versions.py`: `Ver :50`, `Store :94`, `text_norm :35`, `order_docs :194`, `main :221`. `l6_rare.py`: xem trên.

**Ví dụ thật.**

Chuỗi nạp thật (`events/<doc>.json`; cột "mới" là đơn vị thêm, "đóng" là số đơn vị sự kiện đã xử lý đóng theo nhật ký sự kiện, có thể lệch 1 so với đếm trạng thái cuối, ví dụ ND_219 ghi 130 còn trạng thái cuối có 129):

| Ngày hiệu lực | Văn bản | mới | đóng | Cờ / việc chính |
|---|---|---|---|---|
| 2021-01-01 | BLLD_45-2019 | 1.166 | 0 | văn bản gốc |
| 2020-01-01 | ND_90-2019 | 123 | 0 | `law_2012_era_document`; thay ND 157/2018 (ngoài kho) |
| 2020-04-15 | ND_28-2020 | 739 | 0 | `law_2012_era_document` |
| 2021-01-01 | TT_10-2020 | 296 | 0 | |
| 2021-01-01 | ND_135-2020 | 105 | 0 | `pending_unit_repeal` 3 |
| 2021-02-01 | ND_145-2020 | 929 | 0 | thay 13 văn bản, đều ngoài kho (chờ đích) |
| 2021-02-15 | ND_152-2020 | 265 | 0 | |
| 2021-03-01 | TT_11-2020 | 2.042 | 0 | |
| 2021-03-15 | TT_09-2020 | 404 | 0 | |
| 2022-01-17 | ND_12-2022 | 972 | 739 | thay ND_28 |
| 2022-02-01 | TT_18-2021 | 44 | 0 | |
| 2023-09-18 | ND_70-2023 | 64 | 5 | sửa ND_152: chạm 35 đơn vị; 9 chỉ thị Mẫu số |
| 2024-02-15 | TT_19-2023 | 348 | 0 | bổ sung 170 dòng danh mục vào TT_11 |
| 2024-07-01 | ND_74-2024 | 27 | 0 | |
| 2025-08-07 | ND_219-2025 | 254 | 130 | hết hiệu lực một phần ND_152 theo chủ đề |
| 2026-01-01 | VBHN_125-2025 | 1 | 0 | bản hợp nhất: 1.115 đơn vị giống; thêm D154.K8a |
| 2026-04-15 | NQ_66-16-2026 | 265 | 0 | có thời hạn đến 28/02/2027; `overrides` |
| 2026-09-10 | ND_283-2026 | 1.173 | 972 | thay ND_12; hiệu lực có điều kiện 18 đơn vị |

- **Sửa nhiều lần:** `ND_152-2020.D7.K6` có v1 (2021-02-15 → 2023-09-18, đóng bởi ND_70) và v2 (từ 2023-09-18, `source_event = ND_70-2023`, `directive = ND_70-2023.D1.K4.a`, `previous_version = 1`); v2 bị ND_219 đóng ngày 2025-08-07.
- **Hết hiệu lực theo chủ đề (ND_219 Điều 35 khoản 2):** `ND_152-2020.D7.K8` (người lao động nước ngoài) đóng 2025-08-07, cờ `topic_by_chapter`; `ND_152-2020.CIII` (người Việt Nam làm cho tổ chức nước ngoài) vẫn `in_force`; `ND_152-2020.CI` có v2 `suspended` từ 2025-08-07 (`trigger = "chủ đề: lao động nước ngoài làm việc tại Việt Nam"`, cờ `topic_uncertain`). Trạng thái cuối của 274 đơn vị ND_152 (265 gốc + 9 do ND_70 bổ sung): 134 `expired` (129 do ND_219, 5 do ND_70 bãi bỏ trước đó), 49 `in_force`, 91 `suspended` (Chương I và IV).
- **Bản hợp nhất:** `BLLD_45-2019.D154.K8a` có v1 từ **2026-01-01** (lấy từ chú thích [2], không phải ngày ký 27/8/2025), `source_event = VBHN_125-2025`, cờ `from_consolidation`. `BLLD_45-2019.D185.K4` có cờ `consolidation_discrepancy` ("điều 189" thành "điều 89" ở bản hợp nhất).
- **Chờ sự kiện:** `ND_283-2026.D61.K2`: `state = pending_event`, `effective_from = null`, `trigger = "Nghị định sửa đổi, bổ sung một số điều của Nghị định số 189/2025/NĐ-CP ..."`, cạnh `ND_283-2026.D66.K2 pending_on ND_283-2026.D61.K2`.
- **Có thời hạn:** mọi đơn vị của NQ_66-16 có `[2026-04-15, 2027-03-01)`; cạnh `NQ_66-16-2026.PLI_7.M1.LB.SI overrides ND_145-2020.D24` với `valid_from / valid_to` cùng khoảng đó (6 cạnh `overrides`, các Điều 24-28 của ND_145).
- **Thay cả văn bản:** ND_283 đóng 972 đơn vị của ND_12 ngày 2026-09-10; ND_12 đóng 739 đơn vị của ND_28 ngày 2022-01-17.

**Số đếm.** 9.217 đơn vị, 9.343 phiên bản (118 đơn vị có từ 2 phiên bản). 260 cạnh cập nhật: `supplements_list` 171, `replaces` 45, `amends` 24, `overrides` 6, `pending_on` 6, `repeals` 5, `expires_by_topic` 1, `consolidates` 1, `ends_when_replaced` 1. 36 quan hệ chờ đích (30 `replaces`, 4 `repeals`, 2 `amends`). Trạng thái phiên bản: in_force 7.263, expired 1.971, suspended 91, pending_event 18. `unknown_directive` = 0. Một chỉ thị đọc được nhưng đích không khớp (ND_70 Điều 1 khoản 14 điểm c "Bãi bỏ điểm a khoản 6a Điều 30": ND_152 Điều 30 có khoản 6 nhưng không có khoản 6a).

**15 mốc cổng dev** (`dev_gates :817`, đều đạt): ND_28 đóng 2022-01-17; ND_12 đóng 2026-09-10; BLLĐ Điều 154 có khoản 8a từ 2026-01-01; các đơn vị khác của BLLĐ không đổi phiên bản; BLLĐ Điều 185 khoản 4 có cờ `consolidation_discrepancy`; ND_283 Điều 66 khoản 2, 3 → các đơn vị đích `pending_event`; NQ_66-16 `[2026-04-15, 2027-03-01)`; NQ_66-16 có cạnh `overrides`; ND_152 D7.K6 và D7.K14 có v2 từ 2023-09-18; ND_152 D8.K2 đổi cụm từ 2023-09-18; ND_152 D7.K8 đóng 2025-08-07; ND_152 Điều 22-28 vẫn hiệu lực; TT_11 có 170 dòng mới từ 2024-02-15, dòng cũ không đổi; không còn `unknown_directive`.

**Tự kiểm.** 20 test (`tests/test_l6.py`): chuẩn hoá chữ; kho phiên bản (nửa khoảng, hai chỉ thị cùng sự kiện, `close_tree` không xoá, `pending_event` / `suspended` không bao giờ hiệu lực); `parse_payload`; thay cụm từ; cổng dev; ND_70 sửa ND_152; hết hiệu lực theo chủ đề; thay cả văn bản và chờ đích; hiệu lực có điều kiện, **và văn bản chỉ trích cùng số hiệu không kích hoạt nhầm**; NQ_66-16; bản hợp nhất; bổ sung danh mục TT_19 → TT_11; **chạy chuỗi hai lần ra file giống hệt** (băm `versions.jsonl`, `version_edges.jsonl`, `pending_links.jsonl`; test này chạy lại `l6_versions.py` nên ghi đè các file đó bằng nội dung tất định). 22 test loại hiếm (`tests/test_l6_rare.py`) bằng ví dụ tự soạn: loại 12 (có ca dương và ca âm), 16, 19, 20, 21, 22, 24, 25, 26. `checks.py` kiểm bất biến của phiên bản trên dữ liệu thật (xem mục checks).

**Giới hạn.**
- **9 loại không có ca thật** (12, 16, 19, 20, 21, 22, 24, 25, 26): đã cài, chỉ kiểm bằng ví dụ tự soạn. Loại 12 chưa có ca dương trên dữ liệu thật (ND_283 là sự kiện cuối; các văn bản nạp muộn hơn không kích hoạt).
- Loại 10 chỉ có bản regex theo tiêu đề Chương: 91 đơn vị `suspended` (Chương I và IV của ND_152) chờ quyết định, không tự đóng.
- Loại 26 so tên bằng `ten_ngan` của manifest (tên do học viên đặt), không phải tiêu đề trong chữ văn bản (L1 chưa lưu tiêu đề văn bản). Chỉ dùng để gợi ý, không đóng gì.
- Chỉ thị sửa mẫu biểu (ND_70: 9 chỉ thị) không áp được vì kho không có mẫu của ND_152.
- NQ_66-16: plan nhắc Điều 21-28 của ND_145, I.7 chỉ nêu Điều 24-28; Điều 21-23 chưa tìm thấy nên chưa nối.
- L6 đọc câu hiệu lực chỉ từ Điều `effect_transition` (39 Điều, đều do regex); Điều hiệu lực nhận nhãn sai sẽ không được đọc.
- Chưa làm: chuỗi nạp *tăng dần* theo tập ảnh hưởng và `--rebuild` (L11).

**Chạy lại.** `python -I src/l6_versions.py [--until YYYY-MM-DD]` · `python -I tests/test_l6.py` · `python -I tests/test_l6_rare.py`.

---

## checks. Kiểm tra các bước L1-L6

**Việc làm.** Kiểm lại dữ liệu của L1-L6 trên cả kho và đối chiếu số đếm với đĩa. **Không sinh dữ liệu mới.**

**Vào → Ra.** Vào: file của L1-L6 trên đĩa. Ra: `docs/bao_cao_chay/checks/checks_report.txt` (ghi cả khi đạt); thoát mã 1 nếu có nhóm lỗi.

**Cách làm.** `checks.checks :80` trả 6 nhóm, mỗi nhóm một danh sách vấn đề:

| # | Nhóm | Kiểm gì |
|---|---|---|
| 1 | L1 | Số Điều = manifest; đếm thô Điều ≥ manifest; riêng BLLĐ: Điều, Khoản, Điểm của L1 = `EXPECTED` = **đếm độc lập** (`independent_counts :37`) |
| 2 | L2 | `check_structure` cho mọi văn bản; mọi `refers_to` có đích tồn tại và `evidence` nằm trong chữ nguồn; mốc ND_152.D7 → BLLD.D154 |
| 3 | L5 | 4 mốc `exception_of` trên BLLĐ; mọi cạnh L5 chung có đích tồn tại |
| 4 | L3 | Đích của mọi `based_on` / `details` là nút thật |
| 5 | L4 | Mọi Điều có nhãn |
| 6 | L6 | `version_problems :61`: số phiên bản liên tiếp, bản kế chỉ có khi bản trước đã đóng, khoảng nửa mở không chồng, `from ≤ to`; mọi mã L1 còn trong `versions` (không mất nút); phiên bản 1 giữ chữ của L1 (trừ bản hợp nhất); hai đầu mọi cạnh tồn tại |

`EXPECTED` (`checks.py:33`) chỉ có BLLĐ: 220 Điều, 638 Khoản, 267 Điểm. Nguồn độc lập: `grep` trên file thô cho Điều 220 (= cột `so_dieu_dem_duoc`); Khoản 645 và Điểm 287 **trừ** 7 và 20 dòng nằm trong 4 khối trích dẫn của Điều 219 (chữ của luật khác, không phải đơn vị của BLLĐ). `independent_counts` cài riêng một bộ đếm nháy, bỏ dòng trong khối “...” và dừng ở phụ lục đầu tiên, không dùng L1.

**Ví dụ thật** (`checks_report.txt`): sáu dòng `[OK]` rồi `tổng kiểm lỗi: 0`.

**Tự kiểm.** 4 test (`tests/test_checks_graph_viewer_llm.py`): đếm độc lập khớp L1 cho BLLĐ; bộ đếm bỏ khối trích dẫn và phụ lục; mọi nhóm kiểm sạch; `version_problems` **bắt** khoảng chồng, bản kế khi bản trước chưa đóng, nhảy số phiên bản (dữ liệu hỏng cố ý).

**Giới hạn.**
- "Độc lập" chỉ đúng cho đếm L1 và bất biến phiên bản. Nhóm L2 tái dùng `l2.check_structure` (`checks.py:109`) nên cùng một định nghĩa "đúng" với L2.
- `EXPECTED` chỉ có BLLĐ; văn bản khác chỉ đối chiếu `so_dieu` của manifest.
- Không kiểm L5 tường minh (xem Giới hạn của L5 tường minh), graph, viewer; graph và viewer có test riêng.

**Chạy lại.** `python -I src/checks.py` (cần các bước trước đã chạy).

---

## graph. Đồ thị gộp

**Việc làm.** Gộp mọi cạnh và mọi nút thành **một đồ thị**, mỗi nút kèm khoảng hiệu lực.

**Vào → Ra.** Vào: `versions.jsonl`, `version_edges.jsonl` (L6); `l2_refs_*`; `l5_explicit_exceptions_*`, `l5_general_exceptions_*`, `l5_general_conditions_*`; `l3_links.jsonl`; `l4_labels.jsonl`. Ra (`data/processed/graph/`): `graph_nodes.jsonl` (9.364), `graph_edges.jsonl` (2.721), `docs/bao_cao_chay/graph/graph_report.txt`.

**Cách làm** (`graph.build :35`).
1. **Nút văn bản** (18): khoảng hiệu lực từ ngày hiệu lực; ngày kết thúc lấy từ cạnh `replaces` của L6 trỏ tới văn bản đó.
2. **Nút đơn vị:** mỗi mã trong `versions.jsonl` một nút. Loại, tiêu đề, chữ (cắt 240 ký tự), `status` lấy từ phiên bản **cuối**; `intervals` = `[từ, đến, state, version]` của **mọi** phiên bản; `label_class` từ L4; `flags` hợp cờ của mọi phiên bản.
3. Điều / Chương không có cha thì cha là nút văn bản. **Cạnh cấu trúc không ghi** (cha nằm ở khoá `parent`).
4. **Nút điều kiện** (L5 chung) cho từng văn bản (trừ bản hợp nhất).
5. **Cạnh ngữ nghĩa:** `refers_to` (L2), `exception_of` (L5 tường minh, L5 chung), `based_on` / `details` (L3), và mọi cạnh L6. Mỗi cạnh có khoá `source` (`l2`, `l5_explicit`, `l5_general`, `l3`, `l6`).
6. **Bản hợp nhất không có nút đơn vị riêng** (`graph_docs :65`), cạnh của nó không được đưa vào; nó chỉ tạo phiên bản trên BLLĐ.
7. **Nút `external`** cho đầu cạnh `external:<số hiệu>` (văn bản ngoài kho, 31 nút). Đầu cạnh khác mà không có nút thì `ValueError` (fail-closed).
8. **Thành phần liên thông** (`dieu_components :97`): gộp đầu cạnh lên Điều / văn bản / phụ lục / điều kiện / external chứa nó, union-find.

**Code chính** (`src/graph.py`): `short_label :29` · `build :35` · `dieu_components :97` · `main :118`.

**Ví dụ thật.**
- Nút `ND_152-2020.D7.K8`: `type = khoan`, `intervals = [["2021-02-15", "2025-08-07", "normal", 1]]`, `flags = [topic_by_chapter]`, `status = expired`.
- Nút `external:157/2018/NĐ-CP`: `type = external`, `heading = "văn bản ngoài kho"`, đích của cạnh `ND_90-2019.D6.K1 replaces`.
- Cạnh `ND_135-2020 details BLLD_45-2019.D169`, `source = l3`, `how = regex`.

**Số đếm.** Nút: document 18, chuong 59, muc 66, dieu 673, khoan 2.377, diem 2.749, pl 28, pl_muc 74, pl_row 3.191, dieu_kien 98, external 31. Cạnh: `refers_to` 2.103, `exception_of` 300, `details` 48, `based_on` 10, `supplements_list` 171, `replaces` 45, `amends` 24, `overrides` 6, `pending_on` 6, `repeals` 5, `expires_by_topic` 1, `consolidates` 1, `ends_when_replaced` 1. Theo nguồn: `l2` 2.103, `l5_general` 277, `l6` 260, `l3` 58, `l5_explicit` 23. 232 thành phần liên thông. 118 nút có từ 2 khoảng hiệu lực.

Vì sao số khác L2 và L5: `refers_to` 2.348 (L2) trừ 245 của bản hợp nhất = 2.103; Điều 893 trừ 220 của bản hợp nhất = 673; nút điều kiện 128 trừ 30 của bản hợp nhất = 98.

**Tự kiểm.** 2 test graph: không có đầu cạnh treo, 18 văn bản, 673 Điều, 28 phụ lục, mọi loại cạnh chính có mặt; khoảng hiệu lực phản ánh phiên bản (ND_28 `[2020-04-15, 2022-01-17)`, ND_152 D7.K6 có 2 khoảng, K8a từ 2026-01-01, D61.K2 `pending_event`, mọi cha đều có nút).

**Giới hạn.** `status` chỉ tính tại ngày cuối của chuỗi (2026-09-10); xem theo ngày khác dùng `intervals` (viewer làm việc đó). Cạnh của L5 tường minh (23) đang nằm trong đồ thị (xem Giới hạn của L5 tường minh). Chữ nút bị cắt 240 ký tự; chữ đầy đủ ở `versions.jsonl`.

**Chạy lại.** `python -I src/graph.py`.

---

## viewer. Trang xem đồ thị

**Việc làm.** Dựng **một file HTML** (mở offline) để xem đồ thị tại một ngày bất kỳ. Chỉ đọc file của graph, không đổi dữ liệu nào.

**Vào → Ra.** Vào: `graph_nodes.jsonl`, `graph_edges.jsonl`, manifest, `utils/viewer/template.html`, `utils/viewer/vendor/cytoscape.min.js` (Cytoscape.js 3.30.2, MIT). Ra: `data/processed/viewer/do_thi.html` (4,7 MB).

**Cách làm.**
- `viewer.build_data :24` gom: nút, cạnh, danh sách **17 mốc ngày** (mọi `từ` / `đến` của `intervals`, và `effective` của cạnh), `asOf` = ngày hiệu lực lớn nhất trong manifest (2026-09-10), danh sách văn bản.
- `viewer.render :38` thay hai chỗ giữ chỗ `/*CYTOSCAPE*/` và `/*DATA*/` trong `template.html` bằng thư viện và dữ liệu JSON (thoát `</script`, `</`). Mọi thứ nằm trong một file, không gọi tài nguyên ngoài.
- Trang (`template.html`) mặc định ở **mức Điều** (nút gốc: 18 văn bản, 673 Điều, 28 phụ lục, 98 nút điều kiện, 31 external = 848 nút, đây là tập trước khi lọc theo ngày; chọn ngày thì nút chưa hiệu lực hoặc hết hiệu lực bị ẩn hoặc làm mờ); Khoản, Điểm, mục phụ lục, dòng chỉ hiện khi **bấm đúp** cha để mở (`toggle :181`). **Ô chọn ngày** dùng khoảng hiệu lực nhúng sẵn nên đổi ngày không phải dựng lại file: nút `active :84` nếu có khoảng `normal` bao ngày đó; nút ◀ ▶ nhảy tới mốc đổi trước / sau (`jump :227`); ô "hiện cả đơn vị không còn hiệu lực" làm mờ thay vì ẩn. Lọc theo văn bản; bật / tắt từng loại cạnh (9 loại bật sẵn); ô tìm (Enter: khớp mã, rồi chứa trong mã, rồi chứa trong tiêu đề và chữ); chuyển sáng / tối; ô bên phải liệt kê cạnh vào và ra của nút đang chọn kèm `evidence`. Bố cục `cose` của Cytoscape.
- Phần `#` của URL mở sẵn trạng thái: `#date=2023-09-17&doc=ND_152-2020&open=ND_152-2020.D7&inactive=1&probe=1` (dùng cho kiểm tự động bằng trình duyệt không giao diện).

**Code chính.** `utils/viewer/viewer.py`: `build_data :24` · `render :38` · `main :45`. `template.html`: `active :84`, `statusAt :88`, `shown :94`, `visible :105`, `build :108`, `toggle :181`, `select :196`, `jump :227`.

**Ví dụ thật** (đã chứng minh bằng Edge không giao diện, theo `docs/quyet_dinh/l6_checks_graph_viewer_quyet_dinh.txt` mục E3): ngày 2025-06-01 trang có `ND_152` Điều 7 khoản 8 và không có khoản 13 của ND_219; ngày 2025-10-01 ngược lại; BLLĐ Điều 151 khoản 1 điểm d và Điều 154 khoản 9 có ở cả hai ngày. Số đếm lúc dựng: 9.364 nút, 2.721 cạnh, 17 mốc ngày.

**Tự kiểm.** 1 test (`test_viewer_data_is_consistent_with_graph`): `asOf = 2026-09-10`, có mốc 2025-08-07 và 2023-09-18, 18 văn bản, và HTML dựng ra không còn chỗ giữ chỗ hay thẻ `</script` lọt vào dữ liệu.

**Giới hạn.** **Chưa thử tương tác chuột** (bấm, bấm đúp mở Khoản / Điểm, tìm kiếm Enter) và **chưa kiểm độ tương phản** màu sáng / tối; mới kiểm bằng đếm nút theo ngày và theo văn bản qua tham số `#` và ảnh chụp trạng thái mặc định. Mức Điều là lựa chọn vì không giữ được "hiện đủ mọi nút" ở 9.364 nút.

**Chạy lại.** `python -X utf8 -I utils/viewer/viewer.py` (cần `graph.py` đã chạy) hoặc `python -I src/run_all.py --viewer`.

---

## Chạy cả pipeline

```
python -I src/run_all.py                    # L1 → L2 → L4 → L5 tường minh → L5 chung → L3 → L6 → checks → graph (GHI ĐÈ data/processed/ và docs/bao_cao_chay/)
python -I src/run_all.py --viewer           # thêm trang xem đồ thị
python -I src/run_all.py --viewer --tests   # thêm 7 bộ test (120 test)
python -I src/run_all.py --llm replay       # hai bước LLM đọc cache, không tốn lượt
python -I src/run_all.py --llm live         # GỌI API THẬT khi thiếu cache (cần GEMINI_API_KEY; chỉ chạy khi đã được duyệt)
```

Sau khi chạy trên Windows, `git status` có thể hiện file `M` giả do khác LF/CRLF: xem `git diff` trước khi `git restore`.

---

## Phát hiện khi viết tài liệu này (cần xem lại)

Các mục dưới đây thấy khi đối chiếu code, dữ liệu trên đĩa và các tài liệu khác. Chưa sửa gì; mỗi mục nói rõ đã kiểm cái gì.

1. **L5 tường minh, quy tắc 2 nhiều khả năng bắt nhầm cả 23 cạnh** (đã đọc nguyên văn cả 5 câu và chạy `GENERAL_RE` lên từng câu; chi tiết ở mục L5 tường minh). Ảnh hưởng: 23 / 300 cạnh `exception_of` của graph; và 1 ngoại lệ chung thật (ND_28 D11.K1) bị L5 tường minh lấy trước nên L5 chung không thấy. Chưa kiểm xem có ca nào của quy tắc 1 hoặc 2 đúng trên dữ liệu thật (hiện quy tắc 1 không có ca, quy tắc 2 không thấy ca đúng).
2. **Một số tài liệu còn lệch thực tế về LLM.** `.claude/CLAUDE.md` (mục 2 và 4: "chưa gọi live lần nào"), `docs/quyet_dinh/l6_checks_graph_viewer_quyet_dinh.txt` (E1) và docstring `l3_links.py:16-18` nói LLM chưa chạy. Trên đĩa có `data/llm_cache/_usage.json` ghi 23 lượt ngày 09/11/2026 và 23 file cache khớp (15 + 8). `docs/tien_do_L0_L6.md` ghi đúng (đã gọi API thật 09/11).
3. **Nhãn L4 do LLM chưa được đo.** 714 Điều nhận nhãn từ LLM; chưa có nhãn người gán để so. Hai ca trong mẫu ngẫu nhiên đáng xem (Điều 9 và Điều 142 của BLLĐ). Hiện không ảnh hưởng L6 vì LLM không đặt Điều `effect_transition` nào.
4. **Số liệu cùng tên, khác phạm vi** (dễ nhầm khi đối chiếu): `refers_to` 2.348 (L2, gồm bản hợp nhất) và 2.103 (graph); Điều 893 và 673; nút điều kiện 128 và 98. Bản hợp nhất VBHN_125 lặp lại BLLĐ nên graph bỏ nó.
