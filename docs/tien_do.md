# Tiến độ (đọc sau README.md)

Cập nhật lần cuối: **12/11/2026**, cuối ngày (người dùng nói "tạm dừng" để về nhà làm tiếp; commit và push cùng lượt).

## Đọc theo thứ tự
1. `README.md` (điểm vào, có mục "Việc của phiên này").
2. `.claude/CLAUDE.md` (tự nạp). Tên bước L-số trong bảng mục 2 là tên **cũ**; quy tắc 11 là cách làm việc với người dùng.
3. File này.
4. `docs/pipeline_moi.md`: thiết kế pipeline, cách làm từng bước, ví dụ dữ liệu thật, giải thích field, mẫu "thẻ bước" và thẻ mẫu 1.3.
5. `docs/quyet_dinh/pipeline_moi_quyet_dinh.txt`: quyết định đã chốt (mục A, A1 đến A20) và số đo, quan sát (mục B, B1 đến B10).
6. `docs/kiem_hieu.md` và `docs/kiem_hieu_dap_an.md`: bộ kiểm hiểu 1.1 đến 1.6 (10 câu mỗi bước, tổng 60 câu; đáp án ý chính chỉ dành cho agent chấm). **Đang TẠM DỪNG** theo yêu cầu người dùng đến khi chốt xong 1.6.
6b. `docs/the_buoc_1_1_den_1_5.md`: thẻ bước 1.1 đến 1.5 với số đo và bảng phát hiện (viết 12/11).
7. Khi cần: `docs/tien_do_L0_L6.md` (lịch sử code cũ), `docs/quyet_dinh/l*_quyet_dinh.txt` (quyết định của code cũ), `plan/ke_hoach/` (plan tham khảo, không sửa), `plan/ke_hoach/method_vi_3_1_den_3_6_2026-11-09.md` (bản Method của luận, nguồn của mô hình K).

## Câu mở phiên và câu kết phiên (người dùng copy-paste)
- **Trước khi mở:** `git pull` trên nhánh `v3_refactor`.
- **Mở phiên:** "Đọc README.md và làm theo mục 'Việc của phiên này'."
- **Kết phiên:** "Tạm dừng." (agent làm đúng mục "Khi người dùng nói tạm dừng" bên dưới).

## Trạng thái hiện tại
- Nhánh `v3_refactor`. Mốc cũ `d83a4d4` là code L0-L6 trước refactor.
- **Bước 1.1 đến 1.5 đã code xong** và chạy xanh (kiểm lại 12/11 cuối ngày): `python -I src/run_all.py --viewer --tests` ra 12/12 bước, 7 bộ test (119 test, `tổng test lỗi: 0`), cả `--llm off` lẫn `--llm replay`, đủ 18 file triples. Trong ngày 12/11 sửa 3 chỗ (A21 nhãn 1.4, A22 ngoại lệ tường minh 1.5, A23 tên chờ đích 1.2); `CLAUDE.md` mục 3 vẫn ghi 113 test (chưa sửa). Tên file mới: `parse`, `refs`, `delegation` (1.3), `links` (2.2), `article_type` (1.4, đã bỏ LLM), `exceptions_explicit`, `exceptions_general`, `textutil`. Bản đồ tên cũ sang mới ở `docs/pipeline_moi.md`.
- Khuôn cạnh chung `{s, p, o, evidence, how, flags}` (riêng 1.5 thêm `rule`). Đã bỏ field không ai đọc: `version` (1.1) và `heading` (1.4).
- Đếm lại trên đĩa 11/11, khớp số cũ: 10.202 đơn vị, 893 Điều, 2.348 `refers_to`, 129 chờ đích, 51 điều khoản giao chắc (cộng 5 ca lỏng cờ `loose`).
- Chưa làm: 1.6 (đang bàn, chưa code; còn chờ đúng một điểm: cách gộp tên đồng nghĩa) đến 1.9 và toàn bộ giai đoạn 2 (đã có code cũ cho 2.3, 2.4 ở `l6_*.py`; 2.5 đến 2.7 chưa có).
- Mục tiêu người dùng đặt (A11): hết T7 (14/11/2026) có KB đủ lớp, có cơ chế cập nhật và một demo hỏi đáp nhỏ. Lịch đề xuất (người dùng chưa duyệt từng ngày): T5 12/11 làm 1.6 và 1.7; T6 13/11 làm 1.8, 1.9 và demo; T7 14/11 làm giai đoạn 2.

## Nợ (ghi 11/11)
1. **1.2 tầng 2** (xác định đích duy nhất cho 13 ca khoản/điểm trơ trụi, đều ở nghị định, thông tư) hoãn; BLLĐ có 0 ca (B10).
2. **5 ca lỏng của 1.3** chưa ai xác nhận (agent đọc: 4 thật, `D133.K1` nghi không). Không bắt buộc: pipeline không có người duyệt giữa chuỗi.
3. **`src/checks.py`** (bộ kiểm độc lập) chưa rà theo thiết kế mới (1.3 tầng lỏng, 1.4 không LLM, khuôn cạnh).
4. **Đầu vào khai báo của văn bản mới (`manifest.csv`):** cần khai `file`, `nhom`, `so_hieu`, `loai`, `ngay_hieu_luc` (và nên có `ngay_ban_hanh`); `so_dieu_dem_duoc` đề xuất cho tùy chọn nhưng code hiện còn đòi. Chưa sửa code.
5. ~~Thẻ bước 1.1, 1.2, 1.4, 1.5~~ **Đã viết 12/11** cùng thẻ 1.3 ở `docs/the_buoc_1_1_den_1_5.md`; mục cuối file đó gom 4 phát hiện. Ba cái đầu **đã sửa 12/11** (A21 nhãn 1.4, A22 trigger và quy tắc 2 của 1.5, A23 tên chờ đích của 1.2; xem `docs/quyet_dinh/pipeline_moi_quyet_dinh.txt`; 119 test xanh). Còn MỞ: file triples NQ_66 biến mất một lần (không tái hiện); 64 ca "trừ <danh từ>" ở kho (BLLĐ 5) chưa có quy tắc nào (cần user quyết trước khi bàn 1.7/1.8); nút điều kiện dài 724 ký tự của `ND_28-2020.D11.K1` do quy tắc chung "đến hết đoạn".
6. **Cổng phần dư của `refs.py`** (từ khoá điều/khoản/điểm ngoài cụm) mới chỉ ghi báo cáo (đo: 0 sót); khi nạp văn bản mới ở giai đoạn 2 nên quyết có biến thành lỗi dừng không.
7. **Cạnh của L6** (`version_edges.jsonl`, bước 2.3 và 2.4) chưa theo khuôn cạnh chung: làm ở giai đoạn 2.
8. **Tài liệu lỗi thời:** bảng vai trò ở `docs/llm_config.md` còn ghi L4 dùng LLM; cache cũ `data/llm_cache/l4_classify/` không còn dùng (chưa xoá, cần người dùng bảo).
9. **Câu hỏi thiết kế còn mở** ở cuối mục "Câu hỏi thiết kế đang mở" của `docs/pipeline_moi.md` (câu 2 đến 8; câu 1 đã giải quyết bởi A14).
10. **Mở rộng ngoại lệ chung 1.5 sang "trừ <danh từ>"** (trừ hành vi, hình thức, các, những ...; 64 ca trong kho, BLLĐ 5 ca): user đã đồng ý làm, hoãn sau 1.6 (A24). Cần đo độ chính xác trên mẫu đọc tay khi làm.
11. **Nút điều kiện quá dài của ngoại lệ chung** ("đến hết đoạn", ví dụ `ND_28-2020.D11.K1` 724 ký tự): ghi nợ, hướng cắt ở dấu ";" (A24).
12. **Kiểm dữ kiện thô của 1.6** (R2 của plan): phần ngữ nghĩa không có cách kiểm bằng máy, bỏ (A26). Phần máy làm được dời sang bộ quét lỗi của 1.8: vị từ là kết luận của một quy tắc thì không được là `input`; mỗi `input` phải được ít nhất một quy tắc dùng. Chưa bàn 1.8 nên đây mới là việc mang sang. Phần còn lại chỉ đo được qua câu hỏi thử ở 1.9, không thành cổng.

## Kiểm hiểu (người dùng bảo "khá hay, lưu lại" 11/11)
**TẠM DỪNG từ 12/11 theo yêu cầu người dùng; kiểm lại (1.1 và 1.6, rồi các bước khác) sau khi chốt xong 1.6. Agent không hỏi câu kiểm hiểu nào cho tới khi người dùng bảo.**
Bộ 50 câu (10 câu mỗi bước 1.1 đến 1.5) ở `docs/kiem_hieu.md`; ý chính đáp án cho agent ở `docs/kiem_hieu_dap_an.md`. Kết quả: 1.1 đã kiểm 12/11 (1/10 đúng, chưa đạt, cần học lại rồi kiểm lại); 1.6 kiểm lượt đầu 12/11 (2/10 đúng, 3 thiếu, 3 chưa biết, 2 chưa kiểm vì user mất câu hỏi 1.6.9 và 1.6.10; chưa đạt); 1.2 đến 1.5 vẫn "chưa trả lời" (40 câu). Người dùng nói "kiểm 1.x" thì agent hỏi 10 câu của bước đó, chấm đúng/thiếu/sai, giải thích chỗ sai, rồi ghi kết quả và "mức nắm" (ngưỡng đề xuất: 8 trên 10 là đã nắm) vào bảng.

## Việc kế tiếp (theo thứ tự)
1. Dựng lại và xác nhận xanh (README, mục "Dựng lại và kiểm").
2. Kiểm hiểu: **tạm dừng** đến khi chốt xong 1.6. Khi người dùng nói "kiểm 1.x" thì agent hỏi 10 câu của bước đó, chấm và ghi lại (1.1 được 1/10 và 1.6 được 2/10 ngày 12/11, cần kiểm lại).
3. **Bàn bước 1.6 (sổ khái niệm)**, chưa code. Đọc mục 3.5 của Method trước. Làm đúng quy tắc 11: kể lại bước bằng thẻ, hỏi kiểm hiểu, rồi mới nhờ quyết. **Đang bàn từ 12/11** (thẻ 1.6 ở `docs/pipeline_moi.md`, 10 câu kiểm hiểu 1.6 ở `docs/kiem_hieu.md`, A25 ở quyết định). KHÔNG dùng model thứ hai để kiểm (nguyên tắc đã chốt); mọi bước LLM kiểm bằng cổng máy. Đã chốt 12/11 (A25, A26): bỏ model thứ hai, dùng cổng máy; ngữ cảnh = tiêu đề Điều + chapeau + chữ đơn vị; bỏ kiểm dữ kiện thô (nợ #12). Còn chờ DUY NHẤT điểm 4 (gộp tên đồng nghĩa): user loại phương án có người duyệt; agent tự bác phương án (d) "gộp khi cùng neo qua 1.2" vì nó chỉ là cổng G5 đổi tên và không phủ quan hệ ngầm. Agent đang đề xuất: lưu tên vị từ gốc cho từng cụm, bảng `same_as` riêng (công tắc), 1.6 chỉ gộp khi chữ trùng sau chuẩn hoá và xuất báo cáo cặp nghi gần nghĩa để đo; quan hệ ngầm để 1.7 xét từng cặp có câu bằng chứng. Hai câu cần user quyết: (1) tách danh tính khỏi liên hệ như trên, hay LLM tái dùng tên lúc tạo vị từ; (2) có thêm lượt thứ hai cùng model chỉ để ĐO độ ổn định (không lọc) không. Chi tiết và phản biện ở A26. Chưa code.
4. Kiểm s(CASP) trên máy này: `scasp --version`, `swipl --version`.
5. Khi rảnh: viết thẻ 1.1, 1.2, 1.4, 1.5; rà `checks.py`.

## Chờ người dùng
- Trả lời hai câu cuối của 1.6 (xem "Việc kế tiếp" mục 3). Kiểm hiểu tạm dừng, người dùng nói "kiểm 1.x" khi muốn tiếp.
- Đổi chữ ở Method 3.5 của luận: còn mô tả "model khác trích lại để kiểm" mà hệ thống không làm (A25).
- Restart VS Code ở máy chính rồi báo s(CASP) chạy được (người dùng nói chắc chắn đã cài; agent chưa thấy `scasp`, `swipl` trong PATH của phiên 11/11).
- `.claude/CLAUDE.md` mục 5 ("Việc đang dở", phần người dùng tự cập nhật) còn trỏ tới tài liệu cũ (`docs/tien_do_L0_L6.md`, nhánh `v2-lao-dong`): agent chưa sửa; muốn thì bảo.
- Xoá cache cũ `data/llm_cache/l4_classify/` và sửa `docs/llm_config.md`: cần người dùng bảo.

## Khi người dùng nói "tạm dừng" (quy trình cho agent)
1. Dừng việc đang làm, không bắt đầu bước mới.
2. Chạy kiểm: `python -I src/run_all.py --viewer --tests` (chế độ `off`), rồi `python -I src/run_all.py --llm replay --viewer --tests` (lần cuối bằng `replay` để báo cáo ở `docs/bao_cao_chay/` sinh lại đúng). Ghi kết quả thật (đỏ cũng ghi, kèm đầu ra lỗi).
3. Cập nhật file này (ghi đè "Trạng thái hiện tại", "Nợ", "Việc kế tiếp", "Chờ người dùng"; thêm một mục vào "Nhật ký", mới nhất ở trên), mục "Việc của phiên này" của `README.md`, và bảng kết quả ở `docs/kiem_hieu.md` nếu có câu mới được trả lời.
4. Nếu bước nào đổi thì sửa `docs/pipeline_moi.md`; quyết định mới hoặc chỗ lệch plan thì thêm vào `docs/quyet_dinh/pipeline_moi_quyet_dinh.txt`.
5. `git status`, soát file đổi: không đưa khoá API, heldout, file lớn ngoài ý muốn; `data/processed/` đã bị `.gitignore`; không đưa thay đổi cục bộ của người dùng (ví dụ `.vscode/settings.json`) nếu họ chưa bảo. `git add` cả file mới. Thông điệp commit tiếng Việt, **ngắn**. Rồi **commit và push luôn** lên nhánh đang làm, không `--force`. Nếu kiểm ở bước 2 đỏ thì ghi "đỏ" vào "Trạng thái hiện tại", vẫn commit và push, và báo người dùng. Nếu công cụ từ chối commit hoặc push thì đưa lệnh cho người dùng tự chạy.
6. Sau commit: kiểm cây đã commit chạy được độc lập (giải nén `git archive HEAD` vào thư mục trống, chạy `run_all.py --viewer --tests` ở đó).
7. Không ghi vào repo: khoá API, nội dung hay đường dẫn của heldout, thông tin cá nhân của người dùng.

## Cách làm việc với người dùng (tóm từ CLAUDE.md)
- Mục tiêu: người dùng **làm chủ** luận, trả lời được "vì sao bước này làm vậy mà không phải kiểu kia". Agent đề xuất, người dùng quyết. Không "làm dùm".
- Thảo luận thiết kế trước, code sau, một lớp mỗi lượt. Trước khi nhờ quyết, kể lại bước bằng "thẻ bước" (dữ liệu vào, dữ liệu ra, bảng field đủ giá trị, cách làm, vì sao, kiểm), rồi hỏi kiểm hiểu. Nói bằng tên bước mới, không dùng L-số.
- Mơ hồ thì hỏi (gom một lượt). Báo cáo ngắn, tiếng Việt, có mục "Phản biện", nói rõ cái gì đã chạy và cái gì chưa kiểm. Khi đổi một field, chạy cả `--llm off` lẫn `replay` (S3 từng hỏng nhánh `off` mà không ai thấy).
- Không commit, push, xoá, ghi đè, chạy `--llm live` khi chưa được bảo (trừ lệnh "tạm dừng").

## Dựng lại trên máy mới
- `git clone https://github.com/MrSooo/KLTN.git kltn`, rồi `git switch v3_refactor`. Trên máy cũ remote tên `KLTN`, clone mới gọi nó là `origin`.
- Python 3.14.x, chỉ dùng thư viện chuẩn. `python -I src/run_all.py --viewer --tests` (khoảng 12 giây) dựng lại `data/processed/` và kiểm; phải ra `XONG: 12/12 bước`.
- Chỉ khi chạy LLM thật (`--llm live`): `.venv` có `google-genai`, biến môi trường `GEMINI_API_KEY` đặt riêng trên từng máy. Chi tiết ở `docs/ban_giao_2026-11-07.md` mục 1 và 2.
- s(CASP): người dùng nói đã cài ở máy chính; kiểm trên từng máy bằng `scasp --version`. Cần cho bước 1.8 và 1.9.
- Mốc đối chiếu cũ (đầu ra của code `d83a4d4` ở chế độ `replay`) không nằm trong git; dựng lại bằng `git worktree add <thư mục> d83a4d4` rồi `python -I src/run_all.py --llm replay --viewer` ở đó.
- Heldout giữ ngoài repo, không mở khi chưa tới lúc đo.
- Memory của Claude nằm trên từng máy và không đi theo git; mọi thứ cần nhớ phải nằm trong README, file này, `docs/pipeline_moi.md` và `docs/quyet_dinh/`.

## Nhật ký (mới nhất ở trên)

### 12/11/2026: sửa 3 lỗi 1.2, 1.4, 1.5; bàn 1.6 (chưa code); kiểm hiểu 1.1 và 1.6
- Viết thẻ 1.1 đến 1.5 (`docs/the_buoc_1_1_den_1_5.md`). Sửa 3 lỗi tìm ra khi đo: A21 (nhãn 1.4: 6 Điều BLLĐ bị xếp nhầm `effect_transition`/`authority`), A22 (1.5: 23 cạnh tường minh giả từ "khấu trừ", "loại trừ"), A23 (1.2: tên luật chờ đích bị cắt, ví dụ "Luật Bảo" thành "Luật Bảo hiểm xã hội"). Mỗi lỗi có test, có so đầu ra trước/sau; 113 thành 119 test.
- Chốt nguyên tắc: LLM không được LLM khác kiểm, phải có kiểm bằng máy (A25); bỏ cổng model thứ hai khỏi 1.6 (lệch plan L7 và Method 3.5). Ghi nợ mở rộng ngoại lệ chung sang "trừ <danh từ>" (A24, nợ #10, #11).
- Bàn 1.6: viết thẻ (bản bàn) ở `docs/pipeline_moi.md`. Đã chốt (A26): ngữ cảnh = tiêu đề Điều + chapeau + chữ đơn vị; bỏ kiểm dữ kiện thô (nợ #12, phần máy làm được dời sang bộ quét lỗi của 1.8). Đang mở: cách gộp tên đồng nghĩa.
- Kiểm hiểu: 1.1 được 1/10, 1.6 được 2/10 (cả hai chưa đạt); người dùng tạm dừng kiểm hiểu đến khi chốt xong 1.6.
- Thêm quy tắc 12 vào `CLAUDE.md`: không chiều ý người dùng (phản biện cả ý kiến của họ). Người dùng đòi sau khi thấy agent gật quá nhanh; hai lỗi suy luận của agent đã được nhận và ghi ở A26 (lập luận bất đối xứng "tách nhầm thì lộ" sai một nửa; phương án (d) chỉ là G5 đổi tên).
- Lỗi mở: một lần chạy đầu ngày thiếu `l1_triples_NQ_66-16-2026.jsonl` (17/18) nhưng báo 12/12; không tái hiện; cổng xanh chưa kiểm đủ 18 file triples (nợ #5).
- Đã kiểm trước commit: `--llm off` và `--llm replay` đều 12/12, 119 test, `tổng test lỗi: 0`, đủ 18 file triples. Chưa kiểm: s(CASP) (máy này có `swipl` 10.0.2 nhưng không có `scasp`); Python máy này là 3.13.5 (tài liệu ghi 3.14.x), vẫn xanh. Chưa chạy `--llm live` (không có khoá trong môi trường agent).

### 11/11/2026: code xong 1.1 đến 1.5, chốt cách báo cáo
- Người dùng đặt mục tiêu hết T7 và đổi nhịp làm việc: mỗi lượt một lớp; mỗi bước phải được kể lại (dữ liệu vào, ra, field, vì sao) trước khi nhờ quyết.
- Code: S1 đổi tên 5 file và dời `text_norm` sang `textutil.py` (đầu ra giống hệt mốc, 301 file); S2 bỏ LLM khỏi 1.4 (A14; 93 trên 921 nhãn đổi, 39 `effect_transition` không đổi); S3 khuôn cạnh chung (A12); S4 tách `l3_links.py` thành `delegation.py` (1.3, có tầng lỏng `loose`) và `links.py` (2.2); bỏ `version` và `heading` (A16).
- Lỗi tự gây, đã sửa: S3 để nhánh `--llm off` đọc field `check` đã bỏ (KeyError, lệnh dựng lại mặc định hỏng) mà chỉ kiểm bằng `replay`. Từ đó chạy cả hai chế độ mỗi lần.
- Phát hiện: cổng phần dư của 1.2 đã có sẵn trong code cũ (0 sót); tầng 2 hoãn (B10); 4 ca điều khoản giao bị regex chặt bỏ sót vì dấu gạch ngang trong "Bộ Lao động - Thương binh và Xã hội".
- Cách báo cáo: mẫu "thẻ bước" v2 (người dùng duyệt), bộ 50 câu kiểm hiểu (10 mỗi bước), `README.md` làm điểm vào cho máy khác.
- Đã kiểm trước commit: bản sao sạch các file `git add` sẽ lấy chạy xanh 12/12 ở `--llm off` và `replay`; đầu ra `replay` giống hệt cây làm việc.
- Chưa kiểm: `checks.py` theo thiết kế mới; s(CASP) (agent chưa thấy trong PATH).

### 10/11/2026: chốt hướng refactor, chưa code
- Chốt pipeline hai giai đoạn, đánh số giai đoạn.bước, bỏ L-số. Tạo `docs/tien_do.md`, `docs/pipeline_moi.md`, `docs/quyet_dinh/pipeline_moi_quyet_dinh.txt`. Chi tiết ở A1 đến A10.
