# Tiến độ (file đọc đầu tiên mỗi phiên)

Cập nhật lần cuối: **10/11/2026**, cuối buổi thảo luận thiết kế (chưa viết code mới).

## Đọc theo thứ tự
1. `.claude/CLAUDE.md` (tự nạp). Lưu ý: tên bước L-số trong đó là tên **cũ**, đang được thay bằng "giai đoạn.bước" (xem file 3).
2. File này.
3. `docs/pipeline_moi.md`: thiết kế pipeline mới và trạng thái từng bước.
4. `docs/quyet_dinh/pipeline_moi_quyet_dinh.txt`: quyết định đã chốt và chỗ lệch plan, kèm lý do.
5. Khi cần: `docs/tien_do_L0_L6.md` (lịch sử code cũ L0-L6), `docs/quyet_dinh/l*_quyet_dinh.txt` (quyết định của code cũ), `plan/ke_hoach/` (plan tham khảo, không sửa), `plan/ke_hoach/method_vi_3_1_den_3_6_2026-11-09.md` (bản Method của luận, nguồn của mô hình K).

## Câu mở phiên và câu kết phiên (user copy-paste)
- **Trước khi mở:** `git pull` trên nhánh `v3_refactor`.
- **Mở phiên:** "Đọc `.claude/CLAUDE.md` và `docs/tien_do.md`, rồi cho mình biết bạn đã nắm gì, việc kế tiếp là gì và còn thiếu gì. Chưa sửa gì."
- **Kết phiên:** "Tạm dừng." (agent làm đúng mục "Khi user nói tạm dừng" bên dưới: cập nhật file, commit, push).

## Trạng thái hiện tại
- Nhánh `v3_refactor`. Mốc `d83a4d4` ("Finalize before refactor v2") là code cũ L0-L6, cây sạch. Ngày 10/11 chạy lại 7 bộ `tests/test_*.py` ở mốc này: mỗi bộ cuối ra `tổng test lỗi: 0`.
- **Giai đoạn công việc: thiết kế lại pipeline, chưa viết code mới.** Code cũ trong `src/` giữ nguyên làm bản đối chứng. Dựng lại xong thì archive nó (như `archive/v1_thua_ke/`).
- Hướng đã chốt: pipeline hai giai đoạn. Giai đoạn 1 dựng KB gốc từ chỉ BLLĐ, đủ các lớp và hỏi đáp được. Giai đoạn 2 là update engine nạp ND/TT. Chi tiết ở `docs/pipeline_moi.md`.

## Việc kế tiếp (theo thứ tự)
1. Bàn **lớp cấu trúc (bước 1.1 đến 1.3)**: lập bảng sở hữu field (mỗi field nghĩa gì, bước nào ghi, bước nào đọc, thiếu thì hỏng gì). Ví dụ cần làm rõ: nhãn `isolated` được ghi ở L3, L4 nhưng ghi chú nội bộ của Method nói không chỗ nào lọc nó (chưa kiểm lại trong code).
2. Chốt xong thì ghi vào `docs/pipeline_moi.md` (cột trạng thái) và `docs/quyet_dinh/pipeline_moi_quyet_dinh.txt`.
3. Bàn lần lượt các lớp sau: quan hệ pháp lý (1.3 đến 1.5), tri thức (1.6 đến 1.8), hỏi đáp (1.9), rồi giai đoạn 2.
4. Chỉ sau khi một lớp được duyệt mới viết code cho lớp đó, so với số đối chiếu của code cũ (xem `docs/pipeline_moi.md`).

## Chờ user
- Tự cài và biên dịch s(CASP) (user nói sẽ tự làm; cần cho bước 1.8-1.9). Xong thì ghi cách cài vào mục "Dựng lại trên máy mới" bên dưới.
- Duyệt dòng trỏ tới file này trong `.claude/CLAUDE.md` mục 5 (chưa sửa, đã đề xuất).
- Khi nào đủ thiết kế thì cập nhật CLAUDE.md mục 2 và quy tắc 10 cho khớp tên bước mới và việc archive `src/` cũ.

## Khi user nói "tạm dừng" (quy trình cho agent)
1. Dừng việc đang làm, không bắt đầu bước mới.
2. Nếu có đổi code: chạy kiểm liên quan, ghi kết quả thật (đỏ cũng ghi, kèm đầu ra lỗi).
3. Cập nhật file này: ghi đè "Trạng thái hiện tại", "Việc kế tiếp", "Chờ user"; thêm một mục vào "Nhật ký" (đầu danh sách).
4. Nếu bước nào đổi trạng thái thì sửa `docs/pipeline_moi.md`; nếu có quyết định mới hoặc chỗ lệch plan thì thêm vào `docs/quyet_dinh/pipeline_moi_quyet_dinh.txt`.
5. `git status`, liệt kê file đổi, rồi **commit và push luôn** (user đã bảo ngày 10/11: nói "tạm dừng" là commit + push, để khỏi quên). Trước khi `git add`: soát file đổi, không đưa vào khoá API, heldout hay file lớn ngoài ý muốn (`data/processed/` đã bị `.gitignore`). Thông điệp commit tiếng Việt, ngắn, nêu việc đã làm. Push lên nhánh đang làm, không dùng `--force`. Nếu kiểm ở bước 2 đỏ thì ghi rõ "đỏ" vào "Trạng thái hiện tại" rồi vẫn commit và push (nhánh làm việc, để không mất việc và máy khác thấy được), và báo user. Nếu công cụ từ chối lệnh commit hoặc push thì đưa lệnh cho user tự chạy.
6. Không ghi vào repo: khoá API, nội dung hay đường dẫn của heldout, thông tin cá nhân của user.

## Cách làm việc với user (tóm từ CLAUDE.md và các buổi trước)
- Mục tiêu: user **làm chủ** luận, trả lời được "vì sao bước này làm vậy mà không phải kiểu kia". Agent đề xuất, user quyết, nếu có công cụ advisor thì dùng nó kiểm lại đề xuất trước khi đưa user. Không làm "dùm".
- Một lượt một việc nhỏ. **Thảo luận thiết kế trước, code sau.** Mỗi bước thiết kế nêu: làm gì; thiếu thì hỏng gì; vì sao cách này mà không phải cách khác; chỗ nào dùng LLM và cổng kiểm symbolic nào đi kèm.
- Mơ hồ thì hỏi (gom câu hỏi một lượt). Gặp khó khăn thì dừng và hỏi. Báo cáo ngắn, tiếng Việt, có mục "Phản biện", nói rõ cái gì đã chạy và cái gì chưa kiểm.
- Không commit, push, xoá, ghi đè, chạy `--llm live` khi chưa được bảo. Plan trong `plan/ke_hoach/` chỉ tham khảo, không sửa.

## Dựng lại trên máy mới
- `git clone https://github.com/MrSooo/KLTN.git kltn`, rồi `git switch v3_refactor`. Trên máy cũ remote tên `KLTN`, clone mới gọi nó là `origin`.
- Python 3.14.x, chỉ dùng thư viện chuẩn. `data/processed/` bị `.gitignore`: chạy `python -I src/run_all.py --viewer --tests` (khoảng 12 giây) để dựng lại và kiểm. Mốc xanh: 7 bộ test, mỗi bộ `tổng test lỗi: 0`.
- Chỉ khi chạy LLM thật (`--llm live`): `.venv` có `google-genai`, và biến môi trường `GEMINI_API_KEY` đặt riêng trên từng máy. Chi tiết ở `docs/ban_giao_2026-11-07.md` mục 1 và 2 (các mục khác của file đó đã cũ).
- s(CASP): chưa cần cho tới bước 1.8. User tự cài và biên dịch; ghi cách làm vào đây khi xong.
- Heldout giữ ngoài repo, không mở khi chưa tới lúc đo.
- Memory của Claude nằm trên từng máy và không đi theo git; mọi thứ cần nhớ phải nằm trong file này, `docs/pipeline_moi.md` và `docs/quyet_dinh/`.

## Nhật ký (mới nhất ở trên)

### 10/11/2026: chốt hướng refactor, chưa code
- Bàn với user và chốt đổi hướng: pipeline hai giai đoạn, đánh số giai đoạn.bước, bỏ L-số. Chi tiết và lý do ở `docs/quyet_dinh/pipeline_moi_quyet_dinh.txt`.
- Tạo 3 file theo dõi: `docs/tien_do.md`, `docs/pipeline_moi.md`, `docs/quyet_dinh/pipeline_moi_quyet_dinh.txt`.
- User chốt: câu "tạm dừng" = cập nhật file, commit và push luôn; có câu mở phiên và câu kết phiên sẵn ở đầu file này. Dòng trỏ tới file này trong `.claude/CLAUDE.md` mục 5 vẫn chờ user duyệt (trong lúc đó câu mở phiên làm việc thay).
- Đã kiểm: 7 bộ test ở `d83a4d4` đều `tổng test lỗi: 0`; cây làm việc sạch lúc bắt đầu.
- Chưa kiểm: các số đối chiếu trong `docs/pipeline_moi.md` (10.202 đơn vị, 9.343 phiên bản...) chép từ `docs/tien_do_L0_L6.md` ngày 09/11, chưa đối chiếu lại với đĩa. Khẳng định "isolated không ai lọc" lấy từ ghi chú Method, chưa kiểm trong code.
