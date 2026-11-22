# CLAUDE.md — luật làm việc trong dự án kltn

## 1. Cách làm việc (đọc trước, quan trọng nhất)

Mục tiêu của user là **hiểu và kiểm soát được mình đang làm gì**. Claude viết code, user duyệt từng bước. Vì vậy:

1. **Từng bước nhỏ, không làm một mạch.** Mỗi lượt chỉ làm MỘT bước. Trước khi sửa: nói ngắn sẽ sửa file nào, vì sao. Sau khi sửa: dừng, tóm tắt, chờ user xem. Không tự nối sang bước kế tiếp, không chạy chuỗi lệnh dài mà chưa báo.
2. **Plan do user đưa là chuẩn.** User thường lập plan ở nơi khác rồi dán vào. Làm đúng thứ tự plan, không thêm việc ngoài plan, không "tiện tay" refactor. Thấy plan thiếu hoặc mâu thuẫn với code thì nói ra và hỏi, đừng tự sửa plan.
3. **Gặp điểm mơ hồ thì HỎI, không đoán** (định dạng output, tên cột, hướng cạnh, vị trí file, giá trị rỗng, thứ tự ghi...). Gom nhiều câu hỏi vào một lượt. Chỉ khi prompt nhiệm vụ ghi rõ "không hỏi lại" thì mới tự chọn cách đơn giản nhất, và phải ghi mọi lựa chọn vào file `docs/quyet_dinh/*_quyet_dinh.txt`, chỗ lệch spec đặt lên đầu.
4. **Không làm việc khó đảo ngược khi chưa được bảo:** commit, push, xoá hoặc ghi đè file, chạy `--llm live` (tốn hạn mức hoặc tiền), cài gói vào repo. Trước khi ghi đè thì xem file đích.
5. **Báo cáo trung thực, giải thích để user hiểu.** Tiếng Việt, ngắn. Nói rõ cái gì đã chạy và kết quả, cái gì CHƯA kiểm. Không nói "xong" khi chưa chạy test. Test lỗi thì dán đầu ra lỗi. Khi đổi hành vi, nói đổi gì và ảnh hưởng chỗ nào, không chỉ liệt kê tên file.
6. **Code phải đọc được để user duyệt:** thay đổi nhỏ, tách theo việc, docstring và comment tiếng Việt giải thích *vì sao* (không chép lại code). Không để lại code chết hay cờ thừa.
7. **Bí mật:** API key chỉ nằm trong biến môi trường (`GEMINI_API_KEY`, `ANTHROPIC_API_KEY`). Không bao giờ dán vào chat, file trong repo, test hay báo cáo.
8. **Phản biện (critical review) là bắt buộc, trước khi làm và trước khi báo xong.** Với mỗi bước tự hỏi: plan/spec có mâu thuẫn với code hoặc dữ liệu thật không; giả định nào mình chưa kiểm; cách làm này có thể sai ở đâu và sai sẽ lan xuống bước nào; con số nào chưa đối chiếu với đĩa. Kết quả phản biện (kể cả "không thấy vấn đề, đã kiểm X và Y") phải có một mục ngắn **"Phản biện"** trong báo cáo cuối lượt, không để chỉ nằm trong đầu. Không đồng tình với plan hoặc với chính cách làm của mình thì nói ra, không im lặng làm theo.
9. **Gặp khó khăn thì DỪNG và HỎI, không tự quyết.** Khó khăn gồm: test lỗi chưa rõ nguyên nhân; lệnh hoặc công cụ không chạy được; plan mâu thuẫn với code hoặc dữ liệu; hai cách làm đều hợp lý; phải nới quy tắc, bỏ một kiểm tra, đổi plan/model/tham số mới đi tiếp được. Không tự chọn "cách tạm", không tự đi vòng. Báo lại: đã thử gì, lỗi nguyên văn, các hướng có thể và đề xuất của mình, rồi chờ user. Chế độ "không hỏi lại" ở mục 3 chỉ áp cho chỗ spec im lặng, **không** áp cho khó khăn: gặp khó khăn vẫn dừng và hỏi.

## 2. Dự án là gì

Pipeline biến Bộ luật Dân sự 2015 (phần 4, Điều 609-662) thành đồ thị tri thức, có cập nhật theo phiên bản khi có văn bản sửa đổi. Đồ án tốt nghiệp; báo cáo cho thầy ở `report/tong_hop/tong_hop_cong_viec.md`.

| Bước | File | Việc |
|---|---|---|
| A1 | `src/a1_parse.py` | md → bộ ba (s,p,o) |
| A2 | `src/a2_edges.py` | cạnh cấu trúc `contains`/`part_of` và `refers_to` |
| A3 | `src/a3_exceptions.py` | cạnh `exception_of` (quy tắc "không áp dụng", "trừ ... sau đây:") |
| A4 | `src/a4_versions.py`, `src/a4_llm.py` | áp văn bản sửa đổi, lưu phiên bản; tầng LLM chuẩn hoá khối chỉ thị |
| A5 | `src/a5_checks.py` | kiểm tra A1-A4 |
| A6 | `src/a6_general_exceptions.py` | ngoại lệ chung ("trừ trường hợp ...") |
| A7 | `src/a7_graph.py` | đồ thị gộp |
| A8 | `utils/a8/` | trang HTML xem đồ thị (tùy chọn, không thuộc báo cáo A1-A7) |

Thư mục: `src/` (a1..a7 + `run_all.py`), `tests/` (mọi `test_*.py` và `eval_*.py`), `utils/` (A8, `render_report.py`), `data/` (`raw`, `sample`, `dev_amend`, `ext_amend`, `gold`, `processed/<bước>/`), `docs/`, `report/`, `plan/` (xem dưới). Đừng dựng lại `.work/` hay `result/` (đã bỏ).

Bố cục tài liệu (tên file chữ thường, `snake_case`; bước mới B trở đi theo cùng cấu trúc):
- `docs/quyet_dinh/`: quyết định kỹ thuật và phạm vi, viết tay (`a4_quyet_dinh.txt`, `a6_a7_quyet_dinh.txt`, `pham_vi_mo_rong.txt`).
- `docs/bao_cao_chay/<bước>/` (`a1/ … a7/`, `eval/`): báo cáo chữ do code sinh ra mỗi lần chạy, không sửa tay.
- `report/`: `tong_hop/` (báo cáo tổng hợp cho thầy, md và html), `ky_thuat/` (giải thích code A1-A7), `review/` (rà soát và kế hoạch sửa A1-A7).
- `plan/`: tài liệu hoạch định chép từ project web, theo nhóm `de_cuong/`, `ke_hoach/`, `thiet_ke/`, `kien_thuc/`. Không sửa nội dung; đường dẫn dạng `claude/…` trong đó là của project web.

Quy ước dữ liệu: id dạng `BLDS2015.D621.K1.a` (Điểm `đ` viết thành `dd` trong id). Hai nguồn: mẫu `data/sample/blds2015_5dieu.md` và đầy đủ `data/raw/blds2015_p4.md`. Mỗi bước đầu ra là đầu vào của bước sau và có số đếm đối chiếu cứng (`EXPECTED` trong A5/A7), nên một giả định sai âm thầm sẽ lan xuống các bước sau.

## 3. Quy ước kỹ thuật

- **Chỉ dùng thư viện chuẩn của Python.** Ngoại lệ duy nhất: chế độ `--llm live` của A4 cần gói của nhà cung cấp (`anthropic` hoặc `google-genai`), cài trong `.venv` (đã nằm trong `.gitignore`), không cài vào Python hệ thống.
- Chạy script: `python -I src/<file>.py <md>` (cờ `-I` để không nạp nhầm file cạnh script). Windows: Python của venv là `.venv\Scripts\python.exe`.
- Test: `python -I tests/test_aN.py` (dòng cuối phải là `tổng test lỗi: 0`). Chạy cả pipeline: `python -I src/run_all.py` (mặc định 9 bước A1-A7); thêm `--a8` để dựng trang xem, `--tests` để chạy bộ kiểm thử ngoài và các bộ test.
- Sau mỗi lần `run_all` trên Windows, `git status` hiện file M giả (khác LF/CRLF): `git restore docs/bao_cao_chay/a1/a1_notes_blds2015_p4.txt docs/bao_cao_chay/eval/ext_amend_report_off.txt`.
- Không nới quy tắc để bắt thêm ca. Dạng spec không nói thì báo lỗi dừng (fail-closed, thoát mã 1, không ghi file), không đoán.
- Mỗi chỗ spec im lặng hoặc lệch spec phải có dòng trong `docs/quyet_dinh/a4_quyet_dinh.txt` hoặc `docs/quyet_dinh/a6_a7_quyet_dinh.txt`.
- Báo cáo: sửa `report/tong_hop/tong_hop_cong_viec.md` rồi chạy `python -X utf8 -I utils/render_report.py` để sinh HTML. **Không sửa HTML bằng tay.** Số liệu trong báo cáo phải đối chiếu với code và đĩa, không chép từ báo cáo cũ. Mục 8.4 và 10 của báo cáo là lời khuyên nội bộ, không gửi nguyên bản cho thầy.

## 4. Tầng LLM của A4

- Chỉ `src/a4_llm.py` gọi API. Đề xuất của LLM không được áp thẳng: máy dựng lại thành câu chuẩn, parse bằng văn phạm chuẩn và kiểm V1-V3; không qua kiểm thì bị loại. Đổi nhà cung cấp không được làm lỏng các kiểm tra này.
- Cờ: `--llm off|replay|live`, `--provider claude|gemini`, `--model`. Mặc định `off`/`claude`, hành vi cũ không đổi. `replay` không gọi mạng; `live` mới gọi và lưu vào `data/llm_cache/a4/`.
- Claude API đang vướng thanh toán nên đang thêm Gemini (khoá miễn phí từ Google AI Studio). Gói miễn phí có thể bị Google dùng nội dung để cải thiện sản phẩm: chỉ gửi văn bản luật công khai.

## 5. Việc đang dở (user cập nhật tay)

- Đã sửa, **chưa commit**: `src/a4_llm.py` (thêm `GeminiProposer`, `make_proposer`), `src/a4_versions.py` và `tests/eval_ext_amend.py` (cờ `--provider`, `--model`), `tests/test_a4_llm.py` (+6 test, 20/20 xanh bằng client giả).
- **Chưa kiểm:** chưa gọi Gemini thật lần nào (chưa có key); chưa biết server có nhận `SCHEMA` (có `anyOf` + `null`, `additionalProperties`) hay không; chưa chạy `run_all.py`; báo cáo `tong_hop_cong_viec.md` (các dòng nói "chỉ gói `anthropic`", "14 test của `test_a4_llm.py`", tổng số test) chưa cập nhật.
- Đã commit trước đó: `f90a060 Refactor`. Việc dời `TONG_HOP_*` sang `report/` đã `git add` (rename), chưa commit.
