# Review phản biện A1→A7 so với yêu cầu "Liên kết Tri thức" và "Kiểm tra Đồ thị"

Ngày review: 2026-10-24. Phạm vi: toàn bộ `src/a1…a7`, dữ liệu `data/raw/blds2015_p4.md`, các file trong `data/processed` và `docs`.

Đối chiếu lại 2026-10-25 (chạy lại mọi ca tái hiện và đếm lại số liệu trên commit `b82c925`): mọi finding giữ nguyên mức; sửa hai con số (F-05: số câu "Trường hợp"; F-13: số `refers_to` giữa các Điều), chép đúng regex ở F-14, ghi yêu cầu phiên bản Python ở Phụ lục.

## 0. Cách review và giới hạn

**Thiên lệch cần nói thẳng.** Người viết review (Claude) cũng là người dựng A6, A7 trong cùng dự án và đã chấm "✔" gần hết ở lượt báo cáo trước. Review này cố ý làm khác: (1) đếm lại độc lập từ file md thay vì dùng số của pipeline; (2) thử đầu vào mà pipeline chưa từng gặp; (3) phân biệt lỗi **fail-closed** (dừng và báo lỗi, chấp nhận được) với **fail-open** (chạy xong, thoát 0, nhưng kết quả sai hoặc thiếu mà không báo, nguy hiểm hơn).

**Nhãn mức bằng chứng** dùng trong file này:

| Nhãn | Nghĩa |
|---|---|
| `[REPO]` | Đã chạy trên file thật của repo, tái hiện được |
| `[DỰNG]` | Đã chạy code của repo trên câu do mình dựng tay (không phải văn bản thật) |
| `[WEB]` | Câu trích từ luật thật qua WebFetch (mô hình nhỏ tóm tắt trang caselaw.vn, **chưa đối chiếu với bản chính thức**) |
| `[KIẾN THỨC]` | Hiểu biết chung về cách soạn văn bản pháp luật Việt Nam, **chưa kiểm chứng trong repo** |

**Chưa làm được:** chưa có luật sư hay người rà soát pháp lý; chưa có cặp (văn bản gốc, văn bản sửa đổi) thật nào để chạy A4 từ đầu đến cuối; chưa kiểm PDF/Word; chưa có tập đáp án (gold set) các liên kết do con người gán, nên **recall thật của mọi loại cạnh chưa đo được**, chỉ đo được độ phủ so với từ khoá.

## 1. Kết luận ngắn

Điểm yêu cầu tách thành 8 mục (chữ in nghiêng là cách tách của mình từ đoạn spec bạn dán).

| # | Yêu cầu | Mức | Một dòng lý do |
|---|---|---|---|
| 1 | Phân cấp cấu trúc chứa_khoản / thuộc_điều | **Đạt (tối thiểu)** | Đúng và đã kiểm chéo, nhưng phân cấp dừng ở Điều: Chương, Phần, văn bản bị bỏ (F-09) |
| 2 | `dẫn_chiếu_đến` | **Một phần** | Trên `data/raw`: đủ (41/41 mention nằm trong cụm). Với văn bản pháp luật nói chung: có lỗi fail-open (F-01, F-02) |
| 3 | `là_ngoại_lệ_của` | **Một phần** | Chỉ nhận dấu hiệu tường minh; A6 có lỗi fail-open (F-04); ngoại lệ không nối tới đơn vị mang ngoại lệ (F-10) |
| 4 | Cập nhật sửa_đổi_bổ_sung / thay_thế / bãi_bỏ | **Một phần** | Cơ chế phiên bản tốt, nhưng văn phạm chỉ thị lý tưởng hoá; dạng bị động bị bỏ qua êm (F-03); cạnh cập nhật không có trong đồ thị gộp (F-07) |
| 5 | Mở rộng không phá cấu trúc | **Đạt (cơ chế)** | Chỉ thêm phiên bản, không xoá nút; chỉ mới thử trên dữ liệu tự soạn (F-16) |
| 6 | Khử trùng lặp thực thể / bộ ba | **Một phần, đang sai tầng** | Gộp bộ ba trùng chạy được nhưng dữ liệu thật có 0 ca; `same_text_as` là trùng chữ, không phải trùng thực thể (F-06) |
| 7 | Xung đột chế tài | **Ngoài phạm vi** (bạn đã quyết) | Nhưng "mâu thuẫn hình thức" không cần chế tài vẫn chưa kiểm (F-12) |
| 8 | Tự chuẩn hoá / gắn nhãn cô lập | **Một phần** | Có `duplicate`, `dangling`; chưa có gì cho mâu thuẫn; nhãn `dangling` không bao giờ xuất hiện ở đồ thị gốc |

**Đếm: 2 đạt, 5 một phần, 1 ngoài phạm vi.** Lượt trước mình báo "mọi mục trong phạm vi đã ✔". Báo cáo đó **quá lạc quan** (mục 4 của file này liệt kê chỗ nào lạc quan).

## 2. Những điều kiểm lại và đúng (để cân bằng)

- **Cấu trúc:** 215 đơn vị, 54 Điều, 161 Khoản/Điểm, 161 contains + 161 part_of. Đếm độc lập bằng grep khớp. `[REPO]`
- **Dẫn chiếu trên `data/raw`:** đếm độc lập `(điều|khoản|điểm) + số/chữ/"này"` trong text đơn vị được 41, **cả 41 nằm trong 21 cụm** A2 nhận; 25 cạnh + 2 dẫn chiếu tới Điều chưa nạp (Điều 71, Điều 236). Tiêu đề Điều không có mention. Mình đọc cả 25 cạnh, đích đều hợp lý với câu gốc (nhưng đây là mắt người đọc, không phải đáp án chuẩn). `[REPO]`
- **p4 không chứa** khoảng ("từ Điều … đến Điều …"), danh sách số trần ("khoản 1, 2"), tham chiếu tới luật khác có tên (chỉ có "pháp luật về công chứng" và "pháp luật có quy định khác", không phải dẫn chiếu tới Điều). Nên các lỗi F-01, F-02 **không làm sai số liệu hiện tại**, chỉ là rủi ro khi sang văn bản khác. `[REPO]`
- **Đồ thị không có vòng** trong `refers_to ∪ exception_of`. `[REPO]`
- **A7 theo ngày khớp A4:** với từng văn bản trong 8 văn bản dev, tập cạnh treo của A7 bằng đúng cờ cạnh đứt của A4; 7 bộ test đều 0 lỗi. `[REPO]`
- **Cơ chế phiên bản:** nút không bị xoá, khoảng hiệu lực không chồng (A5 bước 4). `[REPO]`

## 3. Findings

Mức: **Cao** = làm sai kết quả mà không báo, hoặc thiếu hẳn một ý của yêu cầu; **Trung** = lệch yêu cầu hoặc hạn chế rõ; **Thấp** = nhỏ hoặc đã ghi nhận.

### Nhóm A. Lỗi fail-open (chạy xong, kết quả sai hoặc thiếu, không báo)

#### F-01 (Cao) A2 gán dẫn chiếu sang luật khác thành dẫn chiếu nội bộ
- **Bằng chứng** `[DỰNG]`: các câu "…theo quy định tại Điều 5 **của Luật Đất đai**", "Điều 5 **Nghị định này**", "Điều 5 **của Luật này**" đều cho cạnh `refers_to → D5` của văn bản đang xử lý. `CHAIN_RE` chỉ biết đuôi "của Bộ luật này".
- **Ảnh hưởng:** với bộ luật đầy đủ (Điều 1–689) dẫn chiếu ra ngoài sẽ thành cạnh sai tới đúng số Điều đó. Với p4 thì Điều 5 không có trong tập nên rơi vào danh sách "unresolved" với nhãn sai ("Điều chưa nạp", thực ra là văn bản khác).
- **Hiện tại không xảy ra trên p4** (test quét "Điều/khoản/điểm x của" chỉ thấy 3 chỗ "điểm chỉ của"), nhưng test đó chỉ chạy lúc kiểm thử, **không nằm trong luồng chạy của A2**.
- **Đề xuất:** thêm nhận dạng đuôi "của <Luật|Bộ luật|Nghị định|Thông tư|Pháp lệnh> …" hoặc "<văn bản> này" khác văn bản đang xử lý; cho vào danh sách `external` (không tạo cạnh); mọi "Điều N của <tên lạ>" mà không nhận dạng được thì dừng (fail-closed).

#### F-02 (Cao) A2 bỏ êm một phần các cụm danh sách và khoảng
- **Bằng chứng** `[DỰNG]`: "từ Điều 5 đến Điều 8" ra `D5, D8` (thiếu D6, D7); "các điều 5, 6 và 7" ra `D5` (thiếu D6, D7); "khoản 2a Điều 5" ra `D5` (thô hơn ý văn bản); "Điều 5a" không ra cạnh nào.
- Cùng loại nhưng **fail-closed** (đúng hướng): "khoản 1, 2 Điều 5" và "điểm a, b khoản 1 Điều 5" làm cả lần chạy dừng bằng ValueError.
- **Ảnh hưởng:** thiếu cạnh mà không biết (recall giảm im lặng). Với p4: không có ca nào.
- **Đề xuất:** thêm vào `group_targets` quy tắc cho danh sách số trần, khoảng "từ … đến …", hậu tố chữ ("5a"); nếu chưa làm thì phát hiện (từ khoá + số mà không thuộc cụm đã nhận) và dừng thay vì cho ra cạnh thiếu.

#### F-03 (Cao) A4 bỏ qua êm chỉ thị viết ở dạng bị động hoặc "hết hiệu lực"
- **Bằng chứng** `[DỰNG]`, thoát mã 0, 0 chỉ thị, dòng chỉ vào mục "Dòng bị bỏ qua" với lý do "không phải chỉ thị": "Khoản 2 Điều 5 được bãi bỏ.", "Điều 5 bị bãi bỏ.", "Khoản 2 Điều 5 hết hiệu lực kể từ ngày…", "Các Điều 5 và 6 hết hiệu lực.", "Sửa cụm từ “A” thành “B” tại Điều 5.", và dạng cụm từ bị động "Cụm từ “Tòa án cấp tỉnh” tại Điều 48 được thay bằng cụm từ “…”" (dựng lại theo dạng trích `[WEB]`, chữ nguyên bản có thể khác).
- **Nguyên nhân:** `RE_WORDS` (danh sách từ để coi một dòng là "có vẻ chỉ thị") không có "được bãi bỏ", "bị bãi bỏ", "hết hiệu lực", "thay bằng". Dòng không khớp từ nào nên bị coi là chữ thường.
- **Ảnh hưởng:** một văn bản sửa đổi có thể được nạp "thành công" mà không áp thay đổi nào. Đây là lỗi nghiêm trọng nhất với yêu cầu "cập nhật liên kết khi có văn bản mới", vì đồ thị trông vẫn nhất quán.
- **Đề xuất:** (1) mọi dòng ngoài nháy có từ khoá cấu trúc (Điều/khoản/điểm kèm số) cùng từ khoá hành động mở rộng (bãi bỏ, hết hiệu lực, thay, sửa, bổ sung, bỏ) mà không khớp chỉ thị thì lỗi E_UNKNOWN_LINE; (2) văn bản sửa đổi mà 0 chỉ thị thì cảnh báo hoặc lỗi; (3) mục "bị bỏ qua" nên đếm vào mã thoát khi có dòng có từ khoá hành động.

#### F-04 (Cao) A6 nuốt cả quy tắc chính vào "điều kiện" khi mệnh đề ngoại lệ đứng đầu câu
- **Bằng chứng** `[DỰNG]`: "Trừ trường hợp pháp luật có quy định khác, người thừa kế phải thực hiện nghĩa vụ tài sản của người chết." ra nút điều kiện có text `pháp luật có quy định khác, người thừa kế phải thực hiện nghĩa vụ tài sản của người chết` (gồm cả quy tắc chính). Tương tự "Trừ trường hợp có thỏa thuận khác, di sản được chia đều."
- **Vì sao hiểm:** cả 9 ca trong p4 đều đặt "trừ trường hợp" ở **cuối** câu nên không lộ. `[KIẾN THỨC]`: câu mở đầu bằng "Trừ trường hợp luật có quy định khác, …" rất phổ biến trong văn bản quy phạm. Khi gặp, A6 vẫn sinh nút và cạnh, qua cả `check_general`, và còn **không trùng khoá** với nút "có thỏa thuận khác" thật.
- **Đề xuất:** nếu "trừ trường hợp" đứng đầu đoạn thì mệnh đề kết thúc ở dấu phẩy đầu tiên (hoặc ValueError, chưa có quy tắc); thêm test cho dạng này.

#### F-05 (Trung) Một số cách viết ngoại lệ không phải trigger, hoặc chỉ bị đẩy vào "unhandled"
- `[DỰNG]` Ba ca "trừ các trường hợp quy định tại khoản 2 Điều này", "trừ khi có thỏa thuận khác" và "ngoại trừ những trường hợp sau." rơi vào `a6_unhandled` (**thấy được**, chấp nhận được). "Không được áp dụng" không nằm trong `TRIGGER_RE` nên **không ra ở đâu cả**, kể cả danh sách unhandled (fail-open).
- p4 không có "ngoại trừ", "trừ khi", "ngoại lệ", "không được áp dụng" (đều 0 lần). `[REPO]`
- **Không đo được** bao nhiêu ngoại lệ **ngầm** (câu "Trường hợp … thì …" ghi quy tắc đặc biệt ghi đè quy tắc chung, ví dụ lex specialis) vì không có đáp án gán tay. Có 29 đơn vị có text mở đầu bằng "Trường hợp" trong p4 (6 Điều, 23 Khoản; tính theo đoạn là 35 đoạn; tổng 39 lần xuất hiện cụm này trong raw); chưa phân loại được. `[REPO]`

### Nhóm B. Thiếu so với yêu cầu hoặc lệch nghĩa

#### F-06 (Cao) "Khử trùng lặp thực thể" đang làm ở tầng chữ, không phải tầng thực thể
- Mã đơn vị sinh từ vị trí (`BLDS2015.D621.K1.a`) nên **trùng nút là không thể xảy ra từ đầu**. Hai lớp kiểm của A5/A7 chỉ xác nhận điều đó.
- Việc A7 thực sự làm là gắn `same_text_as` cho đơn vị có text giống hệt: 4 cặp. Đọc văn bản gốc `[REPO]`:
  - `D617.K1.d` ≡ `D617.K2.c` ("Bồi thường thiệt hại nếu vi phạm nghĩa vụ…"): cùng nghĩa vụ nhưng cho **hai chủ thể khác nhau** (K1: người quản lý di sản; K2: người đang chiếm hữu, sử dụng).
  - `D618.K1.b/c` ≡ `D618.K2.b/c`: cùng quyền, hai chủ thể khác nhau.
  - `D632.K1` ≡ `D637.K1` ("Người thừa kế theo di chúc hoặc theo pháp luật của người lập di chúc"): cùng **khái niệm chủ thể** dùng ở hai quy tắc khác mục đích (không được làm chứng; không được công chứng).
- Nhận xét: đây là **trùng chữ có chủ đích pháp lý**, không phải dư thừa. Cái "thực thể" thật ở cặp cuối là khái niệm "người thừa kế của người lập di chúc", đáng là một nút khái niệm được hai quy tắc cùng nối tới. Hiện không có tầng khái niệm nào ngoài 5 nút điều kiện nên bước khử trùng lặp **chưa chạm tới tầng spec muốn**.
- Gộp bộ ba trùng (EdgeSet) đúng kỹ thuật nhưng chỉ được thử bằng dữ liệu dựng tay, thật có 0 ca.
- **Đề xuất:** hoặc (a) đổi tên khái niệm thành "trùng chữ (textual coincidence)" và bỏ nhãn `duplicate` (dễ gây hiểu nhầm là dư thừa), hoặc (b) làm tầng khái niệm (chủ thể, đối tượng) rồi khử trùng ở đó. Cần bạn quyết (xem mục 6).

#### F-07 (Cao) Cạnh cập nhật không nằm trong đồ thị gộp; văn bản sửa đổi không phải nút
- A7 chỉ có 5 loại cạnh: contains, part_of, refers_to, exception_of, same_text_as. **Không có `amends`, `replaces`, `repeals`.** `[REPO]`
- Trong `a4_<name>_amend_edges.jsonl`, `s` là **chuỗi** (ví dụ `"dev05_bai_bo_ds"`), không có nút văn bản, không có thuộc tính nào của văn bản (số hiệu, ngày ban hành, cơ quan, loại). `replace_doc` trỏ tới `"BLDS2015"` cũng không phải nút nào. `[REPO]`
- **Ảnh hưởng:** yêu cầu "thiết lập mạng lưới liên kết … sửa_đổi_bổ_sung, thay_thế, bãi_bỏ" mới đạt ở file A4 riêng, chưa thành một đồ thị truy vấn được ("văn bản nào sửa Điều 621?" cần đọc file A4, không đi qua đồ thị A7).
- **Đề xuất:** thêm nút văn bản (kể cả văn bản gốc) vào A7, đưa amend_edges vào cạnh với `status`, giữ `directive_seq` và `new_version`.

#### F-08 (Trung) Văn bản gốc không có ngày hiệu lực và không có metadata
- 215/215 dòng phiên bản 1 có `effective_from = null`, `source_doc = null`. `[REPO]` BLDS 2015 có hiệu lực từ 01/01/2017 `[KIẾN THỨC]`, nhưng snapshot tại 2016-06-01 vẫn trả về cả bộ luật như đang có hiệu lực.
- Không có gì chặn một văn bản sửa đổi có ngày hiệu lực **trước** ngày hiệu lực của luật gốc.
- **Đề xuất:** metadata văn bản gốc (số hiệu 91/2015/QH13, ngày ban hành, ngày hiệu lực) và kiểm `effective_from` của sửa đổi ≥ ngày hiệu lực gốc.

#### F-09 (Trung) Phân cấp trên Điều bị bỏ
- Raw có 1 tiêu đề `#` và 3 tiêu đề `##` (Chương XXII, XXIII, XXIV, dòng 122, 356, 411). A1 gắn nhãn "tiêu đề #/##" và **bỏ qua**. `[REPO]`
- Spec chỉ nêu chứa_khoản/thuộc_điều nên đây chưa vi phạm chữ, nhưng cấu trúc thực của văn bản quy phạm là Phần > Chương > Mục > Điều > Khoản > Điểm; Điều hiện không có `part_of`, nên 54 Điều là 54 cây rời.
- **Đề xuất:** thêm nút Chương, Mục, văn bản và `part_of` cho Điều; thêm vào A5 kiểm tra tương ứng.

#### F-10 (Trung) Cạnh ngoại lệ không nối tới đơn vị mang ngoại lệ; mệnh đề lẫn điều kiện và hệ quả
Đọc 9 câu của A6 `[REPO]`:
- **D619** "…trừ trường hợp thừa kế thế vị theo quy định tại Điều 652": ngoại lệ thật là **Điều 652**. Đồ thị có `D619 refers_to D652` và `cond → D619` (text) nhưng không có quan hệ "D652 là ngoại lệ của D619". Hai thông tin nằm riêng, không nối.
- **D646.K3** "…trừ trường hợp toàn bộ di sản không đủ… thì phần di tặng cũng được dùng…": nút điều kiện chứa cả **hệ quả**, thực chất là một quy tắc ngoại lệ, không chỉ một điều kiện.
- **D617.K1.a** "Lập danh mục di sản; thu hồi tài sản…, trừ trường hợp pháp luật có quy định khác;": ngoại lệ chỉ áp cho vế "thu hồi tài sản", còn cạnh gắn vào cả Điểm (phạm vi quá rộng).
- **Đề xuất:** khi mệnh đề chứa dẫn chiếu tới một đơn vị thì thêm cạnh `exception_of` từ đơn vị đó; cân nhắc tách mệnh đề điều kiện / hệ quả; ghi phạm vi (vế) áp dụng.

#### F-11 (Trung) Nút dùng chung "có thỏa thuận khác" tạo kết nối giả; mất phân loại quy phạm
- Một nút nối **5 đơn vị thuộc 3 Điều** (D615, D659, D662). Đồ thị (38 thành phần liên thông) vì thế có một thành phần chỉ nhờ nút này. Một truy vấn "đường đi giữa các Điều" sẽ coi ba Điều không liên quan là có quan hệ. `[REPO]`
- "Có thỏa thuận khác" (quy phạm **tuỳ nghi**, tôn trọng tự do ý chí) và "pháp luật có quy định khác" (**dẫn chiếu mở** sang văn bản chưa xác định) khác bản chất pháp lý nhưng cùng loại nút `dieu_kien`. `[KIẾN THỨC]`
- **Đề xuất:** thuộc tính `kind` (tuỳ nghi / dẫn chiếu mở / điều kiện cụ thể); đừng cho nút "chung chung" làm cầu nối khi duyệt đồ thị (hoặc ghi nhãn `boilerplate`).

#### F-12 (Trung) "Mâu thuẫn hình thức" không cần chế tài vẫn chưa được kiểm
Bạn đã quyết bỏ xung đột chế tài. Nhưng đoạn spec nói "điểm mâu thuẫn hình thức (ví dụ: …)": chế tài chỉ là ví dụ. Đã có (không cần làm lại): sửa hoặc bãi bỏ một đơn vị đã đóng bị chặn bằng `E_TARGET`; hai chỉ thị chồng đích trong một văn bản bị chặn bằng `E_OVERLAP`; cạnh trỏ tới đơn vị đã đóng được gắn cờ (cờ cạnh đứt của A4, `dangling` của A7). Chưa có: **vòng** trong `exception_of` hoặc `refers_to` (mình đã kiểm tay bằng networkx, hiện 0 vòng, nhưng không có kiểm tự động trong A5/A7). Chưa làm không có nghĩa là sai, chỉ cần ghi rõ phạm vi để không đọc nhầm là "đã kiểm mâu thuẫn".

#### F-13 (Thấp, nhưng cho thấy độ giàu của đồ thị) Mạng liên kết thưa
`[REPO]`: 220 nút, 364 cạnh, **38 thành phần liên thông**; chỉ **49/215 đơn vị** và **25/54 Điều** có ít nhất một cạnh ngữ nghĩa; 18/25 `refers_to` nối **giữa các Điều khác nhau** nhưng chỉ thuộc **14 cặp Điều** (7 cạnh còn lại nằm trong cùng một Điều); tổng 42 cạnh ngữ nghĩa (25 + 13 + 4) trên 322 cạnh cấu trúc. Phần lớn "tri thức" hiện là cây cấu trúc. Đây là giới hạn của việc chỉ dùng từ khoá, không phải lỗi, nhưng nên ghi rõ trong mô tả đồ án để khỏi hiểu là đồ thị giàu liên kết.

### Nhóm C. Tổng quát hoá và độ tin cậy kiểm thử

#### F-14 (Cao nếu mục tiêu là "văn bản pháp luật nói chung") A1 gắn với đúng hai file và một dạng markdown
- `EXPECTED_DIEU` khai báo theo **tên file**; file khác bị từ chối. Regex `RE_DIEU = ^### Điều (\d+)\\?\.\s*(.*)$` không nhận "Điều 5a". `[REPO]/[DỰNG]` Khoản "2a" sinh dòng đáng ngờ (fail-closed).
- `DOC_PREFIX = "BLDS2015"` là hằng số; A4 dùng chung. Chưa có khái niệm nhiều văn bản trong cùng đồ thị.
- Định dạng nguồn (`### Điều N\.`, `**N\.**`, `- **a)**`) là kết quả chuyển đổi riêng của file p4; văn bản từ PDF/Word/trang pháp luật khác cần bộ chuyển đổi.
- **Đề xuất:** nếu đồ án chỉ hướng tới BLDS thì ghi rõ trong phạm vi; nếu muốn thêm văn bản thì cần lớp đăng ký văn bản (mã, tên, ngày) thay cho hằng số.

#### F-15 (Cao) Văn phạm chỉ thị của A4 chưa khớp cách soạn luật thật
Câu trích từ luật sửa đổi thật `[WEB]` (Luật sửa đổi, bổ sung một số điều của Luật Thi hành án dân sự, qua caselaw.vn) chạy qua `a4.parse_amendment` `[DỰNG]`:

| Chỉ thị (trích) | Kết quả A4 |
|---|---|
| "Sửa đổi, bổ sung các khoản 1, 2 và 3 Điều 28 như sau:" | **E_UNKNOWN_LINE** (fail-closed) |
| "Sửa đổi, bổ sung điểm c khoản 1, khoản 2 và điểm d khoản 3 Điều 35 như sau:" | **E_UNKNOWN_LINE** |
| "Sửa đổi, bổ sung điểm đ và điểm e; bổ sung điểm g khoản 1 như sau:" (khoản tương đối, không số Điều) | **E_UNKNOWN_LINE** |
| "Bổ sung Điều 7a và Điều 7b vào sau Điều 7 như sau:" | **E_UNKNOWN_LINE** |
| "Bổ sung Điều 44a vào sau Điều 44 như sau:" | Nhận đúng |
| "Bãi bỏ các Điều 32, 33, 34, 51, 138 và 139, điểm b khoản 1 Điều 163" | Nhận đúng (7 chỉ thị) |
| Cụm từ dạng bị động "…được thay bằng cụm từ…" | **Bỏ qua êm** (F-03) |

Thêm ca dựng tay `[DỰNG]`: hiệu lực tách theo Điều ("từ 01/01/2027, trừ khoản 3 Điều 5 từ 01/7/2027") là **E_DATE_CONFLICT**; "có hiệu lực kể từ ngày ký ban hành" là **E_NO_DATE**; "Bãi bỏ Điều 5 của Luật Đất đai" là **E_REFLIST**; phạm vi "tại tất cả các điều của Bộ luật" là **E_REFLIST**; điều khoản chuyển tiếp bị bỏ qua (có ghi trong báo cáo nhưng không có ngữ nghĩa nào được lưu).
Trong 7 dạng chỉ thị trích từ luật thật: **chỉ 2 qua parser, 4 dừng lỗi (fail-closed), 1 bị bỏ qua êm (fail-open)**. Cỡ mẫu nhỏ (một luật, 7 dạng, trích qua WebFetch) nên không suy ra tỉ lệ cho văn bản nói chung, nhưng đủ để thấy A4 vẫn là "khung" chưa đủ để nạp một luật sửa đổi thật nguyên văn. Bạn đã chọn không đụng A4 lần này; điều đó ổn, chỉ cần nhớ khi nói "nhận diện và cập nhật … khi có văn bản mới được nạp".

#### F-16 (Cao) Phần lớn bằng chứng kiểm thử của A4 và A6 là vòng tròn
- 8 văn bản dev trong `data/dev_amend` do cùng người dựng framework soạn, theo chính cú pháp parser hỗ trợ, nên chạy pass là điều hiển nhiên. Chưa có **một** cặp (gốc thật, sửa đổi thật) nào.
- Tương tự bảng `EXPECTED` của A5, A7: số được lấy từ đếm của chính dự án (có đối chiếu grep, nhưng grep là do cùng nhóm viết).
- 7 bộ test (A1…A7) đều 0 lỗi cho thấy **code làm đúng điều tác giả nghĩ**, không chứng minh **tác giả nghĩ đúng**.
- **Đề xuất:** chọn một cặp thật (ví dụ luật gốc và luật sửa đổi của nó, dán nguyên văn từ nguồn chính thức) làm bộ kiểm thử bên ngoài.

#### F-17 (Cao về phương pháp) Chưa có đáp án chuẩn nên chưa đo được độ phủ thật
Chỉ so được với từ khoá. Muốn trả lời "bao nhiêu phần trăm liên kết đúng/đủ" cần người gán tay một mẫu (ví dụ 10 Điều) rồi tính precision/recall cho từng loại cạnh. Hiện không có số này.

#### F-18 (Trung) Quan hệ cấp văn bản không được mô hình hoá
`[KIẾN THỨC]`: các cơ sở dữ liệu pháp luật thường mô hình "văn bản A sửa đổi / thay thế / bãi bỏ văn bản B (toàn bộ hoặc một phần)" ở **cấp văn bản**. A4 chỉ làm ở cấp Điều/Khoản/Điểm trong một văn bản gốc, và cấp văn bản chỉ có `replace_doc` khi câu khớp một mẫu. Không có nút văn bản nên không có chỗ để ghi "văn bản này hết hiệu lực một phần".

### Nhóm D. Nhỏ, đã biết hoặc đã ghi

| ID | Mô tả | Mức |
|---|---|---|
| F-19 | A1: đoạn chữ đứng **sau** danh sách Điểm (D643 Khoản 2, dòng 301) bị ghép vào text của Khoản ngay sau câu dẫn, mất vị trí gốc; snapshot A4 không khôi phục được (`a4_quyet_dinh` G5). `[REPO]` | Thấp |
| F-20 | A7 theo ngày: nhóm bản sao tính lại mỗi ngày, canonical có thể đổi khi đơn vị đầu nhóm bị đóng (đã ghi `a6_a7_quyet_dinh` D5). | Thấp |
| F-21 | A5 không đọc file A6, A7; tính nhất quán của chúng do A6/A7 tự kiểm. | Thấp |
| F-22 | A5 và A7 dùng bảng số cứng theo tên file; thêm văn bản mới phải sửa bảng. | Thấp |

## 4. Tự kiểm: mình đã chấm quá tay ở đâu (lượt trước)

| Điều mình đã nói | Thực tế sau review |
|---|---|
| "✔ ngoại lệ chung" | Chỉ đúng khi "trừ trường hợp" đứng cuối câu và đúng cụm đó (F-04, F-05, F-10) |
| "✔ khử trùng lặp" | Mình tạo `same_text_as` để bước này có việc để làm; dữ liệu thật không có thực thể trùng và 4 cặp trùng chữ đều có lý do pháp lý (F-06) |
| "mọi mục trong phạm vi đã ✔" | 2 đạt, 5 một phần (mục 1) |
| "nhãn cô lập duplicate và dangling" | `dangling` không bao giờ xuất hiện ở đồ thị gốc; chỉ xuất hiện khi nạp A4, và được kiểm bằng văn bản dev tự soạn |
| Test 0 lỗi coi như kiểm chứng | Test chủ yếu chứng minh code khớp ý định tác giả (F-16) |

Điều mình **không** rút lại: các con số đếm cấu trúc (215, 161, 25, 9, 220/364) khớp với đếm độc lập, và cơ chế phiên bản cùng tập cạnh treo khớp A4 trên 8 văn bản dev.

## 5. Thứ tự đề xuất

**Ưu tiên 1, đổi fail-open thành fail-closed (rẻ, chặn kết quả sai im lặng):**
1. A4: dòng ngoài nháy có từ khoá hành động + tham chiếu cấu trúc mà không khớp thì báo lỗi; văn bản 0 chỉ thị thì cảnh báo/lỗi (F-03).
2. A2: nhận diện dẫn chiếu tới văn bản khác; danh sách số trần, khoảng, hậu tố thì dừng thay vì ra cạnh thiếu (F-01, F-02).
3. A6: mệnh đề ngoại lệ đứng đầu câu thì cắt ở dấu phẩy hoặc dừng; thêm trigger "trừ các trường hợp", "trừ khi", "không được áp dụng" vào unhandled (F-04, F-05).

**Ưu tiên 2, lấp chỗ thiếu so với yêu cầu:**
4. Nút văn bản + amend_edges vào đồ thị gộp A7 (F-07); ngày hiệu lực và metadata văn bản gốc (F-08).
5. Chương/Mục/văn bản trên Điều (F-09).
6. Cạnh ngoại lệ tới đơn vị mang ngoại lệ (D619 → D652), `kind` cho nút điều kiện, chặn nút chung làm cầu nối (F-10, F-11).

**Ưu tiên 3, quyết hướng và độ tin cậy:**
7. Quyết cách hiểu "khử trùng lặp thực thể" (F-06) và có làm tầng khái niệm hay không.
8. Một cặp (gốc, sửa đổi) thật và một mẫu đáp án gán tay để đo precision/recall (F-16, F-17).
9. Mở rộng văn phạm A4 theo văn bản thật (F-15), nếu muốn nói được "nạp luật mới".

## 6. Câu hỏi cần bạn quyết

1. **F-06:** muốn (a) đổi tên `duplicate` thành "trùng chữ" và coi `same_text_as` chỉ là bằng chứng, hay (b) làm tầng khái niệm để khử trùng lặp đúng nghĩa?
2. **Phạm vi tổng quát hoá:** đồ án chỉ tập trung BLDS (khi đó F-01, F-02, F-14, F-18 chỉ cần ghi giới hạn) hay phải chạy được trên văn bản khác?
3. **F-07:** đưa cạnh cập nhật và nút văn bản vào đồ thị gộp (đổi A7) hay giữ ở file A4 riêng?
4. **F-12:** ghi rõ phạm vi "mâu thuẫn hình thức" (không có chế tài) hay làm thêm kiểm vòng và kiểm đơn vị-bị-bãi-bỏ?
5. Bạn có sẵn một luật sửa đổi thật (kèm luật gốc) để dùng làm bộ kiểm thử bên ngoài không?

## 7. Theo dõi sửa

Kế hoạch: `plan_sua_a1_a7.md`. Nhánh `sua-theo-review`. Mỗi bước chạy `src/run_all.py` (pipeline + 7 bộ test) trước khi commit.

| Finding | Bước | Commit | Trạng thái | Đầu ra p4/5dieu |
|---|---|---|---|---|
| F-03 | 1.1 | `8986981` | Đã sửa: dòng bị động / "hết hiệu lực" / "thay bằng" là `E_UNKNOWN_LINE`; văn bản 0 chỉ thị là `E_NO_DIRECTIVE` | Không đổi |
| F-01, F-02 | 1.2 | `dba1ff1` | Đã sửa: tên văn bản khác → `unresolved` với đích `external:<tên>`; "<Luật/Nghị định> này", khoảng, số trần, hậu tố → dừng | Không đổi |
| F-04, F-05 | 1.3 | (commit bước 1.3) | Đã sửa: "Trừ trường hợp X, …" đầu đoạn cắt ở dấu phẩy; "không được áp dụng" → `a6_unhandled`. Ngoại lệ ngầm vẫn chưa nhận dạng | Không đổi |

## Phụ lục: cách tái hiện

Mọi lệnh chạy trong thư mục dự án, dùng `python -I` với **Python ≥ 3.10** (code dùng `str | None` trong dataclass/NamedTuple và `Path.write_text(newline=...)`; `__pycache__` của repo là 3.14). Với `python3` 3.9 của macOS, `test_a1`, `test_a4`, `test_a7` dừng ngay khi import.

- **F-01, F-02:** `a2_edges.build_refs(units)` với `units` nhỏ dựng tay có `X.D1.K1` chứa câu cần thử và các `X.D5…X.D8` làm đích.
- **F-03, F-15:** `a4_versions.parse_amendment(text)` với `text` là câu cần thử cộng dòng "Luật này có hiệu lực thi hành từ ngày 01 tháng 7 năm 2015.". Xem `p.directives` và `p.skipped`.
- **F-04, F-05:** `a6_general_exceptions.find_general({"X.D1": {"type": "dieu", "number": "1", "source_line": 1, "text": "<câu>"}})`.
- **F-07, F-13:** đọc `data/processed/a7_blds2015_p4_edges.jsonl` và đếm `p`; thành phần liên thông bằng `networkx.connected_components`.
- **F-08:** `grep -c '"effective_from": null' data/processed/a4_p4_dev05_bai_bo_ds_versions.jsonl` ra 215.
- **F-09:** `grep -n -E '^#{1,2}( |$)' data/raw/blds2015_p4.md`.

Nguồn `[WEB]`: [Luật sửa đổi, bổ sung một số điều của Luật Thi hành án dân sự (caselaw.vn)](https://caselaw.vn/van-ban-phap-luat/115661-luat-thi-hanh-an-dan-su-sua-doi-2014). Các câu trích do WebFetch trích lại, cần đối chiếu với bản chính thức trước khi dùng làm bằng chứng chính thức.
