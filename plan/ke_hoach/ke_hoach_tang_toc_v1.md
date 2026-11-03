# Kế hoạch tăng tốc: xong thực nghiệm trước 6/12 (bản chốt 3/11/2026)

Thay cho phần lịch của `ke_hoach_hoan_thanh_2026-11-03.md`. Bảng việc gốc (mã 0.x–7.x) vẫn đúng; file này gán **ngày, đầu vào, đầu ra, cổng dừng** và cách điều phối agent. Mã bước mới (B1, C1, D1…) theo kiểu đặt tên file `src/aN_*.py` của phần A.

- **Mốc cứng:** thực nghiệm xong **CN 29/11**. Tuần 30/11–6/12 là đệm, phân tích lỗi và gói kết quả. Từ 7/12: viết luận văn, chuẩn bị báo cáo.
- **Quỹ giờ:** ngày thường 2 giờ; cuối tuần tổng 10 giờ (5 giờ mỗi ngày).

---

## 1. Quyết định đã chốt (3/11)

| # | Quyết định | Lý do |
|---|---|---|
| K1 | **Phương án 3:** cắt trước 4 mục (dưới), giữ mốc 6/12 | Giờ có khoảng 96, việc sau khi cắt khoảng 85, đệm khoảng 12% |
| K2 | Bỏ phép thử tay 5 điều (việc 2.2). Đóng Q12: LLM nháp, học viên chốt | Phép thử không đổi được quyết định. Thay bằng: 5 điều chuỗi là **lô đầu**, có cổng G-B |
| K3 | LLM tạm cho phát triển: **Gemini 3.8 Flash** free (5 RPM, 20 lượt/ngày) cho B1, C1; **Gemini 3.5 Flash-Lite** free (15 RPM, 500 lượt/ngày) cho C4 và chạy thử code | Số đo trên AI Studio của học viên ngày 3/11 |
| K4 | **Model chính thức** (D1, E2, mọi đối chứng) chốt ở **cổng M, T5 12/11**. Cả hệ thống lẫn đối chứng dùng **một** model | So sánh sòng phẳng về phương pháp. Đổi càng muộn càng phải chỉnh lại prompt |
| K5 | Soạn bộ dữ liệu (danh sách phụ thuộc, nháp chữ tình huống) bằng LLM trong **chat mới, ngoài project KLTN**, chỉ nhận chữ luật, định nghĩa độ sâu, quy ước. Lưu prompt và output thành file. **Nhãn đáp án chỉ do người gán** | Chat trong project biết thiết kế hệ thống, như người dựng hệ thống tự viết đề (Q28) |
| K6 | Model soạn tình huống **khác** model chính thức: chính thức là Claude → soạn bằng Gemini (AI Studio web); chính thức là Gemini → soạn bằng Claude Opus | Tránh để cùng một họ model vừa viết đề vừa làm bài |
| K7 | Người hỗ trợ làm cuối tuần: DS5, DS6, gán nhãn DS4. Không thay bằng agent | Kappa người–LLM không phải "hai người gán nhãn độc lập" như đề cương viết |
| K8 | Agent: Claude Code, chạy được từ tuần này | Học viên xác nhận 3/11 |

**Bốn mục cắt trước (K1):**
1. Duyệt sổ: đọc kỹ lô 5 điều; 49 điều còn lại chỉ đọc mục bị cờ và 3 điều chọn ngẫu nhiên.
2. Tập kiểm tra: đủ mọi phụ thuộc độ sâu ≥ 2, lấy mẫu ở độ sâu 1.
3. Giải thích (E3) bằng mẫu câu, không có bước LLM diễn đạt lại.
4. Phân tích lỗi ở mức gán mỗi ca sai về một khối.

Mỗi mục cắt ghi vào `SoQuyetDinh` vì đề cương đã nêu (đề cương sẽ còn sửa qua các vòng của trường).

---

## 2. Phản biện còn giữ

- **Rủi ro lớn nhất vẫn là bộ dữ liệu**, vì nó là việc của người. Người hỗ trợ chỉ có cuối tuần; DS4 phải có nhãn trước CN 22/11, nếu không thì X1 không chạy được.
- **Đề cương vừa nộp, trường có thể đổi phương án đánh giá.** Phần dựng hệ thống (B–E) không phụ thuộc phương án đánh giá nên làm trước; thực nghiệm dồn vào 23–29/11.
- **Dùng Flash/Lite thay model mạnh nhất:** hội đồng có thể hỏi "LLM mạnh hơn thì sao". Trả lời ở phần hạn chế, không chạy thêm.
- **Free tier:** Google dùng dữ liệu gửi lên để cải thiện sản phẩm. Luật là văn bản công khai; tập kiểm tra chỉ gửi bằng model chính thức. Ghi vào phần hạn chế.
- **Ngày thường 2 giờ liên tục 5 tuần sau giờ làm** là giả định của plan. Tuần nào hụt thì lấy từ đệm, không nén việc của tuần sau.

**Ngân sách giờ** [Suy luận, ước lượng]:

| Khối | Giờ học viên |
|---|---|
| Mở khoá (1.1–1.3, `llm_config`, nhắn thầy) | 3 |
| B. Sổ khái niệm | 10 |
| C. Ngoại lệ ngầm | 3 |
| D. Quy tắc, bộ quét, tự sửa, cập nhật, đổi model | 17 |
| E. s(CASP), hỏi đáp, giải thích | 7 |
| Bộ dữ liệu | 25 |
| Đối chứng và chạy thực nghiệm | 12 |
| Phân tích lỗi, gói kết quả | 8 |
| **Tổng** | **khoảng 85** |

Giờ có 4/11–6/12: khoảng 96 (tuần 0: 6 + 10; bốn tuần sau: 4 × 20).

---

## 3. Bản đồ để học thuộc (một màn hình)

```
A (xong)  luật → đơn vị + cạnh văn bản + phiên bản
   │  a1_triples, a2_edges, a2_refs, a3/a6_exceptions, a4_versions
B  đơn vị → SỔ VỊ TỪ (input / concept + neo) → ĐỒ THỊ KHÁI NIỆM
   │  b1_r3_rows, b1_predicates, b3_concept_edges, b3_allowed_predicates
C  đồ thị khái niệm → cặp ứng viên → NGOẠI LỆ NGẦM (rebut / undercut)
   │  c1_implicit_exceptions
D  điều + vị từ được phép + cạnh ngoại lệ → QUY TẮC → QUÉT 5 LỖI → SỬA ≤2 VÒNG / CÔ LẬP
   │  d1_rules, d2_scan, d3_isolated, d4_update_diff
E  quy tắc + chặn → s(CASP) ; câu hỏi → dữ kiện (vị từ input) → 3 trạng thái + giải thích
   │  e1_program.pl, e2_facts, e3_explanations
──────────────────────────────────────────────
DỮ LIỆU  phụ thuộc giữa điều → cặp tình huống (dev / test kín) → nhãn 2 người → Kappa
         + bộ quan hệ chuẩn (Tầng 2) + văn bản sửa đổi kín (cập nhật)
ĐO       Tầng 1: (i) LLM tự viết s(CASP) | (ii) hệ thống | (iii) hệ thống + cả sổ  → tỷ lệ phụ thuộc đạt theo độ sâu
         Tầng 2: P/R/F1 quan hệ ngoại lệ, tỷ lệ cờ đúng
         Tầng 3: hệ thống vs LLM trả lời trực tiếp có cấp điều luật → accuracy 3 trạng thái, McNemar
         Cập nhật: hệ thống vs LLM sửa chương trình cũ (ii) vs LLM trả lời trên toàn văn đã sửa
```

Bốn thứ tự không được đảo:
1. **Chốt model chính thức (12/11) → mới chạy D1 cho 49 điều.**
2. **Đóng băng sổ (CN 15/11) → mới viết tập kiểm tra.**
3. **Ghi ngưỡng bác bỏ + tag code v1.0 (CN 22/11) → mới nạp tập kiểm tra vào repo và chạy.**
4. **Văn bản sửa đổi kín không vào repo trước 28/11.**

---

## 4. Lịch theo ngày

Nhịp ngày thường (2 giờ): 10 phút đọc báo cáo agent chạy hôm trước → 60–80 phút duyệt → 30 phút việc bộ dữ liệu → 10 phút viết brief bước sau → agent chạy qua đêm.

### Tuần 0 (T3 3/11 – CN 8/11): mở khoá + sổ khái niệm

| Ngày | Học viên | Agent | Ra khỏi ngày phải có |
|---|---|---|---|
| T3 3/11 | Đã xong: setup AI Studio, đo rate limit. Còn: nhắn thầy G1, G11 (0.3) nếu chưa | | |
| T4 4/11 | Viết `docs/llm_config.md` (K3, K4); viết brief B1 | 1.1 `run_all.py`, gộp nhánh; 1.2 đếm cạnh xuyên điều; wrapper gọi LLM (cache, gom lô, kiểm nguyên văn); B1 lô 5 điều | con số sàn N; `b1_*` lô 1 |
| T5 5/11 | Duyệt lô 5 điều (khoảng 20 phút/điều) → **cổng G-B** | | qua/trượt G-B |
| T6 6/11 | Trượt: sửa R1–R2/prompt. Qua: bắt đầu duyệt | B1 cho 49 điều (4–5 lượt, khoảng 12 điều/lượt); C4 bằng 3.5 Flash-Lite | `b1_*` đủ 54 điều |
| T7 7/11 | Duyệt mục cờ 49 điều + 3 điều ngẫu nhiên; xử lý mục lệch C4 | B2 kiểm C1–C4 | báo cáo C1–C4 sạch |
| CN 8/11 | Duyệt B3; DS1 bắt đầu (2 giờ, chat mới); DS2 quy ước (1 giờ) | B3 đồ thị khái niệm | `b3_*`; `ds_convention.md` bản đầu |

Người hỗ trợ, cuối tuần 7–8/11: bắt đầu DS5 nếu sắp xếp được (khung chấm 11 Điều đã có).

### Tuần 1 (9/11 – 15/11): ngoại lệ ngầm + quy tắc + chốt model

| Ngày | Học viên | Agent | Ra khỏi ngày phải có |
|---|---|---|---|
| T2 9/11 | Vẽ đồ thị con 621/626; viết brief C1; DS1 (30 phút) | C1 bằng 3.8 Flash | `c1_*` |
| T3 10/11 | Duyệt mục C1 bị cờ; viết brief D1; DS1 | D1 lô 5 điều (model tạm) + biên dịch + 4 ca | `d1_*` lô 1 |
| T4 11/11 | **Cổng G-D**; DS1 | | qua/trượt G-D |
| T5 12/11 | **Cổng M: chốt model chính thức**, ghi vào `llm_config.md`; so lô 5 điều chạy lại với lô của G-D | D1 lô 5 với model chính thức, rồi 49 điều | `d1_rules` đủ, bằng model chính thức |
| T6 13/11 | Đọc báo cáo quét; DS1 xong | D2 bộ quét 5 loại lỗi | `d2_scan_report` |
| T7 14/11 | Duyệt mọi mục cô lập (3 giờ); DS3 tập dev (2 giờ, model soạn theo K6) | D3 tự sửa ≤2 vòng, cô lập | `d3_*`; DS3 bản đầu |
| CN 15/11 | DS3 xong; chạy dev qua hệ thống, sửa lỗi; **đóng băng sổ (B4)** | E1 biên dịch toàn bộ + bộ quét vòng chặn; E2 bản đầu | tag `so-v1-2026-11-15` |

Người hỗ trợ, cuối tuần 14–15/11: DS5 xong; DS6 bắt đầu.

### Tuần 2 (16/11 – 22/11): tập kiểm tra + hỏi đáp + cập nhật + đối chứng

| Ngày | Học viên | Agent | Người hỗ trợ |
|---|---|---|---|
| T2–T6 16–20/11 | Viết tập kiểm tra DS4, **ngoài repo**, 1,5 giờ/ngày; 30 phút/ngày duyệt agent | E2 câu hỏi → dữ kiện; E3 giải thích bằng mẫu; D4 cập nhật mức quy tắc (2 văn bản dev) | |
| T7 21/11 | DS4 xong (2,5 giờ); tự gán nhãn (2,5 giờ) | Dựng đối chứng (i), (iii), Tầng 3, hai đối chứng cập nhật, **chỉ chạy trên dev** | gán nhãn DS4 độc lập; DS6 xong |
| CN 22/11 | Duyệt đối chứng trên dev (1,5 giờ); Kappa, hợp nhất nhãn (2 giờ); **X0 ghi ngưỡng** (30 phút); tag `v1.0` | | |

### Tuần 3 (23/11 – 29/11): chạy thực nghiệm

| Ngày | Học viên | Agent |
|---|---|---|
| T2 23/11 | Đưa tập kiểm tra vào `data/heldout/` (sau tag v1.0) | X1 Tầng 1: (i), (ii), (iii) |
| T3 24/11 | Kiểm tay 10 cặp ngẫu nhiên của X1 | X2 Tầng 2 (cần DS5) |
| T4 25/11 | Kiểm tay X2 | X3 Tầng 3 + McNemar |
| T5 26/11 | Kiểm tay X3 | |
| T6 27/11 | Đệm | |
| T7 28/11 | Nạp DS6; kiểm tay X4 | X4 cập nhật |
| CN 29/11 | X5 phân tích lỗi | bảng tổng hợp |

### Tuần 4 (30/11 – 6/12): đệm + gói kết quả

X5 xong; X6 gói kết quả (bảng, hình, lệnh tái lập); README; gặp thầy trình số liệu. Không có việc trễ thì tuần này bắt đầu viết chương thực nghiệm.

---

## 5. LLM: ai dùng model nào

| Việc | Model | Số lượt (ước) | Ghi chú |
|---|---|---|---|
| B1 nháp sổ | 3.8 Flash free | 5–10 | gom khoảng 12 điều/lượt, đưa sổ hiện tại vào mỗi lượt |
| C4 lượt độc lập | 3.5 Flash-Lite free | khoảng 5 | phải khác model của B1 |
| C1 ngoại lệ ngầm | 3.8 Flash free | 5–10 | gom cặp ứng viên theo điều |
| D1 lô 5 trước cổng M | 3.8 Flash free | 2–4 | chỉ để qua G-D |
| Chạy thử code, debug | 3.5 Flash-Lite hoặc Gemma 4 | tuỳ | output vứt đi, không đưa vào báo cáo |
| D1 54 điều, D3, E2, mọi đối chứng, X1–X4 | **model chính thức (cổng M)** | vài trăm | một model cho tất cả |
| Soạn tình huống DS3, DS4 | khác model chính thức (K6) | chat | lưu prompt và output thành file |

**Cổng M, T5 12/11, ba khả năng:**
- Claude API đã thanh toán được → dùng Claude.
- Có thanh toán Google → Gemini 3.8 Flash bản trả phí, cùng model với lúc phát triển.
- Chỉ có free → 3.5 Flash-Lite (500 lượt/ngày), ghi vào phần hạn chế. 3.8 Flash free 20 lượt/ngày không đủ cho Tầng 3 (khoảng 2 lượt × số câu).

Khoá trong `llm_config.md`: model ID, mức thinking, temperature, ngày khoá. Temperature: tài liệu Gemini 3 có thể khuyên giữ mặc định 1.0 thay vì 0 [Chưa kiểm chứng, xem trang model]. Dù đặt bao nhiêu, mọi phản hồi thô đều lưu vào `data/llm_cache/`; con số trong luận văn tính từ cache.

---

## 6. Thẻ bước

Mỗi thẻ: mục đích, đầu vào, đầu ra, agent làm gì, học viên kiểm gì, cổng, giờ học viên, **sai thì thấy gì**. Đường dẫn theo kiểu repo phần A (`src/`, `data/processed/`, `docs/`); tên file là đề xuất, đổi theo repo được nhưng ghi lại một lần.

### B. Sổ khái niệm

**B1. LLM nháp bảng R3 và sổ vị từ** (việc 2.3)
- Đầu vào: `a1_triples_blds2015_p4.jsonl`; `HuongDan_SoKhaiNiem_R1R4` mục 2–7 làm đặc tả prompt; bảng 19 khái niệm (`PhepThu_DoPhuDanChieu`); sổ hiện có (để R4 dùng lại tên).
- Đầu ra: `data/processed/b1_r3_rows.jsonl` (id, unit_id, span, role, predicate, args, type, anchor, note, flags); `data/processed/b1_predicates.jsonl` (predicate, roles, type, anchor, aliases, used_in, note).
- Agent: gọi LLM theo lô điều, mỗi lô đưa sổ hiện tại; script tự kiểm (a) span là chuỗi con nguyên văn của đơn vị, (b) tên theo quy ước (không `not_`, `no_`, `_or_`, `_and_`, `all_`, `any_`, không số điều), (c) tham số chỉ dùng X, Y, T, W. Vi phạm thì gắn cờ, không tự sửa.
- Học viên kiểm: hỏi câu R2 cho mọi dòng `input` ("nêu thẳng thì bỏ qua điều nào?"); neo trỏ vào điều **nêu điều kiện**, không phải điều **dùng**; vị từ mới có thật sự mới không; gom dòng "?" vào danh sách G8. Lô 5 điều đọc hết; 49 điều đọc mục cờ + 3 điều ngẫu nhiên.
- **Cổng G-B (lô 5 điều):** số dòng phải đổi loại ≤ 10% và không span nào sai nguyên văn → chạy 49 điều. Trên 10% → sửa R1–R2 hoặc prompt, chạy lại lô 5. Trượt hai lần → dừng, mang ca khó đi hỏi.
- Giờ: khoảng 7.
- Sai thì thấy gì: một khái niệm có hai tên (bắt ở B2, C3 hoặc ở D vì quy tắc không nối); `concept` bị xếp `input` (bắt ở D: điều định nghĩa không bao giờ được dùng).

**B2. Kiểm C1–C4** (việc 2.4)
- Đầu vào: `b1_*`, `a1_triples`.
- Đầu ra: `docs/b2_report.txt`; `src/b2_checks.py`; `src/test_b2.py` có test âm cho từng kiểm như A5.
- C1: đơn vị có điều kiện thì có ít nhất một dòng. C2: mỗi `input` được dùng ít nhất một lần. C3: không `input` nào trùng tên hoặc bí danh với `concept`. C4: lượt 3.5 Flash-Lite độc lập (không thấy bảng) trích cụm điều kiện; liệt kê cụm lệch.
- Học viên kiểm: chỉ mục lệch của C4, mỗi mục quyết "thêm dòng" hoặc "bỏ, vì…".
- Cổng: C1–C3 không vi phạm; mọi mục C4 có quyết định.
- Giờ: khoảng 1,5.
- Sai thì thấy gì: thiếu cụm điều kiện thì quy tắc ở D thiếu vế, tình huống phụ thuộc vế đó sai ở Tầng 1.

**B3. Đồ thị khái niệm** (việc 2.5)
- Đầu vào: `b1_predicates`, `b1_r3_rows`.
- Đầu ra: `data/processed/b3_concept_edges.jsonl` (cạnh `uses`: đơn vị → vị từ; `anchored_to`: vị từ → đơn vị định nghĩa); `data/processed/b3_allowed_predicates.jsonl` (mỗi điều: vị từ của chính điều + vị từ của điều láng giềng qua nút khái niệm).
- Học viên kiểm: vẽ đồ thị con quanh 621/626; xem tập vị từ được phép của 3 điều bất kỳ.
- Giờ: khoảng 1.
- Sai thì thấy gì: tập quá hẹp thì D gắn cờ "thiếu vị từ" nhiều; quá rộng thì (ii) giống (iii), Tầng 1 không tách được tác dụng của đồ thị khái niệm.

**B4. Đóng băng sổ** (việc 2.6), CN 15/11
- Tag `so-v1-2026-11-15`. Sau đó mọi thay đổi ghi `docs/so_changelog.md` (ngày, vị từ, lý do, phát hiện từ dev hay từ D). **Không đổi sổ vì bất cứ gì nhìn thấy trong tập kiểm tra.**
- Để đến 15/11 vì D sẽ lộ vị từ còn thiếu; đóng băng sớm thì phải mở lại.

### C. Ngoại lệ ngầm

**C1.** (việc 4.1)
- Đầu vào: `b3_concept_edges`, `a3`/`a6` (ngoại lệ tường minh), chữ đơn vị.
- Đầu ra: `data/processed/c1_candidates.jsonl` (cặp đơn vị cùng nút khái niệm); `data/processed/c1_implicit_exceptions.jsonl` (cạnh `exception_of`, loại rebut/undercut, câu bằng chứng nguyên văn, cờ).
- Agent: sinh cặp từ đồ thị; LLM đề xuất cạnh và loại; bộ quét kiểm hai đầu tồn tại, không trùng cạnh tường minh, không tạo vòng.
- Học viên kiểm: chỉ mục bị cờ (Q13). Mốc biết trước: cạnh khoản 1 Điều 621 → Điều 626 (`BanGiao` mục 2) phải có. Không có thì xem lại cách sinh cặp trước khi xem gì khác.
- Giờ: khoảng 3.
- Sai thì thấy gì: thiếu cạnh thì tình huống ngoại lệ xuyên điều ra "kết luận được" thay vì "bị bác"; thừa cạnh thì quy tắc đúng bị chặn oan.

### D. Quy tắc và bộ quét

**D1. Trích quy tắc** (việc 4.2)
- Đầu vào: chữ điều; `b3_allowed_predicates` của điều; cạnh ngoại lệ tường minh và ngầm của điều.
- Đầu ra: `data/processed/d1_rules.jsonl` (rule_id, head, body, polarity, source_unit, blocks, exception_type); `data/processed/d1_flags.jsonl` (cần vị từ ngoài tập được phép: gắn cờ, **không tự đặt tên**).
- **Cổng G-D (lô 5 điều chuỗi, T4 11/11):** biên dịch được trong s(CASP); 4 ca trong `GiaiThich_KhaiNiem` mục 8.3, viết lại bằng vị từ `input` của sổ, ra đúng trạng thái. Trượt → sửa prompt, chạy lại lô. Trượt hai lần → dừng, xem lại cách biểu diễn chặn.
- **Sau cổng M (T5 12/11):** chạy lại lô 5 bằng model chính thức. Lô 5 vẫn qua G-D → chạy 49 điều. Không qua → chỉnh prompt trên model chính thức trước (lấy từ đệm).
- Học viên kiểm: lô 5 điều đọc hết; 49 điều chỉ đọc mục bị cờ và 5 điều ngẫu nhiên.
- Giờ: khoảng 8 (gồm đổi model).
- Sai thì thấy gì: vị từ thân quy tắc không ai suy ra được (D2 loại 1 bắt); hai quy tắc kết luận ngược nhau không có chặn (D2 loại 5 bắt).

**D2. Bộ quét năm loại lỗi** (việc 4.3)
- Đầu vào: `d1_rules`, sổ, cạnh chặn.
- Đầu ra: `docs/d2_scan_report.txt`; `src/d2_scan.py`; test âm cho từng loại.
- Năm loại: (1) quy tắc không bao giờ kích hoạt (vị từ thân không phải `input` và không là đầu của quy tắc nào); (2) quy tắc trùng; (3) quan hệ đứt sau cập nhật; (4) vòng chặn, **bắt buộc**, vì vòng lẻ làm mọi câu hỏi "không có mô hình" (phép thử 20/10); (5) cặp kết luận ngược nhau không có quan hệ chặn.
- Giờ: khoảng 2.

**D3. Tự sửa và cô lập** (Q18)
- Đầu ra: `data/processed/d3_repair_log.jsonl`; `data/processed/d3_isolated.jsonl`.
- Nhận bản sửa khi: biên dịch được, không sinh cờ mới, số ca dev đúng không giảm. Tối đa hai vòng.
- Học viên kiểm: đọc **mọi** mục cô lập; mục nào là lỗi của sổ thì sửa sổ (trước 15/11) và ghi changelog.
- Giờ: khoảng 3.

**D4. Cập nhật mức quy tắc** (việc 4.4)
- Đầu vào: phiên bản A4 sau khi nạp hai văn bản dev (`dev01`, `dev02`).
- Đầu ra: `docs/d4_update_diff.txt` (đơn vị đổi, quy tắc trích lại, quy tắc và cạnh kiểm lại); số ca dev trước và sau.
- Kiểm: chỉ đơn vị đổi chữ được trích lại; phiên bản cũ còn; bộ quét chạy lại sạch.
- Giờ: khoảng 4.

### E. Suy luận và hỏi đáp

**E1. Biên dịch s(CASP)** (việc 5.1): `d1_rules` + chặn → `e1_program.pl`. Mỗi câu hỏi chạy cả P và ¬P → kết luận được / bị bác / chưa đủ căn cứ (Q15, Q16).
**E2. Câu hỏi → dữ kiện** (5.2): LLM chỉ dùng vị từ `input` của sổ; không biểu diễn được thì "ngoài phạm vi".
**E3. Giải thích** (5.3): lấy từ cây chứng minh, điền vào mẫu câu (mục cắt 3).
- Học viên kiểm: 10 câu dev chạy trọn đường; trạng thái đúng; điều luật trong giải thích có thật trong cây chứng minh.
- Giờ cả E: khoảng 7.

### Bộ dữ liệu

**DS1. Danh sách phụ thuộc** (3.1)
- Đầu vào: chữ luật; con số sàn N từ 1.2 (chỉ để biết quy mô, không dùng làm danh sách).
- Cách làm: LLM trong chat mới đề xuất (K5); học viên đối chiếu từng mục với chữ luật, giữ hoặc bỏ có lý do.
- Đầu ra: `ds_dependencies.csv` (điều phụ thuộc, điều được phụ thuộc, loại cạnh: dẫn chiếu, ngoại lệ tường minh, ngoại lệ ngầm, khái niệm; độ sâu theo [2] mở rộng nhiều điều; ghi chú); `ds_prompts/` (prompt và output của chat).
- Giờ: khoảng 5.

**DS2. Quy ước diễn giải** (3.2): `ds_convention.md`; gồm Q14 (khoản 2 Điều 621) và mọi dòng "?" gom ở B1. Giờ: khoảng 1.

**DS3. Tập dev** (14–15/11): khoảng 20% số cặp, dùng tự do khi phát triển. Model soạn theo K6. Giờ: khoảng 4.

**DS4. Tập kiểm tra** (16–22/11)
- Mỗi phụ thuộc độ sâu ≥ 2 một cặp tình huống; độ sâu 1 lấy mẫu (mục cắt 2). Hai tình huống trong cặp chỉ khác dữ kiện liên quan tới điều được phụ thuộc; viết bằng vị từ `input` (Tầng 1) và câu tiếng Việt (Tầng 3).
- Học viên viết cặp (LLM soạn nháp theo K6); **hai người gán nhãn độc lập** (trạng thái đáp án, độ sâu); Cohen's Kappa; bất đồng thì hợp nhất có ghi lý do.
- Lưu ngoài repo đến 23/11.
- Giờ: khoảng 12.

**DS5. Bộ quan hệ chuẩn** (3.4, người hỗ trợ, 7–15/11): khung chấm 11 Điều mẫu đã có. Thiếu giờ thì giữ đúng 11 Điều.
**DS6. Văn bản sửa đổi kín** (3.5, người hỗ trợ, 14–22/11): 8–10 văn bản, mỗi văn bản kèm cặp tình huống đổi đáp án.

### Thực nghiệm

**X0. Ngưỡng bác bỏ** (6.0, CN 22/11, 30 phút): file `docs/x0_nguong_2026-11-22.md` trong project, gồm ngưỡng đọc Tầng 1 (ví dụ (i) đạt từ 90% phụ thuộc → kết luận chính là "với LLM mạnh, không cần quy trình"); mức ý nghĩa McNemar; **luật sửa lỗi sau khi thấy tập kiểm tra:** chỉ sửa lỗi làm chương trình chết, ghi log, chạy lại mọi phương pháp; không chỉnh prompt hay sổ.
**X1. Tầng 1** (6.1): (i), (ii), (iii); cùng bộ vị từ `input`, cùng số vòng sửa → tỷ lệ phụ thuộc đạt theo độ sâu.
**X2. Tầng 2** (6.2): P, R, F1 của quan hệ ngoại lệ so với DS5; tỷ lệ cờ đúng của bộ quét.
**X3. Tầng 3** (6.3): hệ thống so với LLM trả lời trực tiếp có cấp điều luật; ba trạng thái, từ chối tính sai; McNemar.
**X4. Cập nhật** (6.4): hệ thống so với (a) LLM sửa chương trình cũ của (ii) (G9a), (b) LLM trả lời trực tiếp trên toàn văn đã sửa.
**X5. Phân tích lỗi** (6.5): mỗi ca sai gán về một khối (B sổ, C ngầm, D quy tắc, E dữ kiện, nhãn); báo cáo cả kết quả âm.
**X6. Gói kết quả:** bảng số, hình, lệnh chạy lại từng con số.

Học viên kiểm mỗi X: chọn ngẫu nhiên 10 ca, tự chạy lại một ca bằng lệnh trong báo cáo, so với bảng.

---

## 7. Cổng dừng

| Cổng | Khi | Qua khi | Trượt thì |
|---|---|---|---|
| G-B | T5 5/11 | đổi loại ≤ 10%, span nguyên văn | sửa R1–R2/prompt, chạy lại lô 5 |
| G-D | T4 11/11 | biên dịch được, 4 ca đúng | sửa prompt; trượt 2 lần → xem lại cách biểu diễn chặn |
| M | T5 12/11 | model chính thức đã khoá; lô 5 chạy lại vẫn qua G-D | chỉnh prompt trên model chính thức, lấy từ đệm |
| Đóng băng sổ | CN 15/11 | tag có, changelog có | chưa viết DS4 |
| Kappa | CN 22/11 | κ ≥ 0,6 [quy ước tạm] | sửa DS2, gán lại phần bất đồng trước khi chạy X1 |
| Tag v1.0 + X0 | CN 22/11 | có cả hai | không chạy X1 |

---

## 8. Điều phối agent

**Mẫu brief, mỗi bước một brief:**

```
# Bước <mã>: <tên>
Mục tiêu (1 câu):
Đầu vào (đường dẫn, định dạng):
Đầu ra (đường dẫn, schema từng trường):
Model: <theo llm_config.md>
Làm:
Không được: đọc data/heldout/; sửa file của bước trước; tự đặt vị từ ngoài sổ;
            đổi tên trường; đổi prompt đã khoá sau tag v1.0
Tự kiểm trước khi báo xong: mỗi kiểm có một test âm; chạy run_all.py
Báo cáo docs/<mã>_report.txt: số dòng vào/ra, số cờ theo loại,
            5 mẫu ngẫu nhiên, lệnh chạy lại, số lượt LLM đã gọi
```

**Luật làm việc:**
1. Một bước = một nhánh git + một báo cáo. Gộp vào `main` khi học viên qua "ba câu" (dưới).
2. Gọi LLM qua một wrapper duy nhất: đọc `llm_config.md`, lưu phản hồi thô vào `data/llm_cache/`, đếm lượt so với giới hạn ngày. Chạy lại không gọi lại model.
3. Agent không thấy tập kiểm tra: để ngoài repo đến 23/11.
4. Con số nào vào luận văn cũng phải có lệnh chạy lại ra đúng số đó.
5. Câu hỏi luật agent hoặc học viên không chắc: ghi vào danh sách G8, không để agent tự quyết.

**"Ba câu" cho mỗi bước,** ghi vào `docs/ON_TAP.md`, đây là tài liệu học thuộc: (1) đầu vào là gì; (2) đầu ra là gì, ý nghĩa một dòng; (3) sai thì thấy ở đâu. Thẻ ở mục 6 đã có sẵn ba câu; học viên chép lại bằng lời của mình sau khi bước xong.

---

## 9. Khi trễ thêm

Bốn mục đã cắt ở K1. Trễ thêm thì cắt tiếp theo thứ tự:
1. DS5 về đúng 11 Điều mẫu.
2. DS6 còn 8 văn bản.
3. X4 chỉ giữ đối chứng (b).

**Không cắt:** chấm theo cặp, Kappa, đối chứng (i), X0 ghi trước.

---

Điều gì sẽ chứng minh kế hoạch này sai: cổng G-D trượt hai lần đến T5 12/11, hoặc DS4 chưa có nhãn của người hỗ trợ vào CN 22/11. Khi đó mốc 29/11 không đạt được bằng cách nén thêm; phải dời thực nghiệm sang giữa tháng 12 và báo thầy.
