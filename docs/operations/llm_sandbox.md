# Vận hành: chạy phần LLM bằng phiên Claude Code trong thư mục làm việc ngoài repo

Áp dụng cho bước 1.6 (A36). Phần LLM không gọi API: một phiên Claude Code đóng vai LLM trong **thư mục làm việc ngoài repo** (gọi là "thư mục làm việc" ở dưới), mỗi lô giao cho một subagent mới. Máy (mã của repo) dựng đầu vào, kiểm và ghi bản ghi cache. Thư mục làm việc **không** dựng trong repo và có thể dựng lại bất cứ lúc nào. Chạy xong thì có thể chép vào `data/sandbox_runs/` để lưu (A53), không chạy phiên LLM trong đó.

## 1. Nguyên tắc
- Thư mục làm việc nằm **ngoài repo**, tên trung tính, chưa có hoặc rỗng. Phiên Claude Code mở **trong thư mục đó**, không `--resume`, không `-c`, nên không nạp tài liệu của dự án; cách ly này dựa trên hướng dẫn trong thư mục, không có gì chặn kỹ thuật nếu phiên cố tình đọc thư mục cha.
- Chữ lời nhắc của bước (`SYSTEM`) và lược đồ nằm trong khoá cache của mọi bản ghi. **Sửa một chữ sau khi đã dựng thư mục là phải dựng lại thư mục mới**; `nhap` từ chối thư mục dựng với lời nhắc khác code.
- Lời khai model và effort của subagent trong `nhat_ky.tsv` là lời tự khai, máy không kiểm được. Bản ghi không có `request_id` và `usage`.
- Mỗi subagent đặt tường minh model (tên tắt) và effort; phiên chính chỉ điều phối, không tự làm lô nào. Không chạy lại một lô trừ khi người vận hành bảo.
- Không chạy `--llm live` khi chưa được phép (tốn hạn mức hoặc tiền).

## 2. Bước 1.6A mới (`src/propositions.py`)
Đường chạy đã chốt (A39): Sonnet 5.5, effort `high`, khối tối đa 20 lô mỗi subagent, song song tối đa 4, lời nhắc `menh-de-3`.

1. **Dựng thư mục** (ở gốc repo, thư mục đích ngoài repo):
   ```
   python -X utf8 -I src/propositions.py xuat <thư mục> claude-sonnet-5-5 high --tat-ca
   ```
   Thư mục chứa `HUONG_DAN.md`, `system.txt`, `cau_hinh.json`, `lo/001.json` đến `lo/204.json` và `out/` rỗng. Bỏ `--tat-ca` thì dựng bộ thí điểm 30 đơn vị.
2. **Mở phiên Claude Code mới trong thư mục đó** (`cd <thư mục>`, rồi `claude`). Cho phép Agent tool và ghi file trong thư mục. Giao: "Đọc HUONG_DAN.md và làm theo." Phiên tự chia lô thành khối, giao từng khối cho subagent, ghi `out/NNN.json` và dòng `nhat_ky.tsv` (số lô và ID model, cách nhau bằng tab). Hết hạn mức giữa chừng: mở phiên mới và giao lại cùng câu; phiên bỏ qua lô đã có `out/NNN.json`.
3. **Luật dừng sau 3 khối đầu (60 lô):** nếu có câu dẫn lọt thành `menh_de` hoặc lỗi cổng còn lại vượt 5% số dòng thì dừng và báo; không tự sửa lời nhắc.
4. **Nhập vào repo** (ở gốc repo, nhập được nhiều lần):
   ```
   python -X utf8 -I src/propositions.py nhap <thư mục>
   ```
   Kiểm hình, cổng nguyên văn, cổng âm tiết; từ chối lô sai hình, lô thiếu dòng nhật ký, lô mà model tự khai khác `cau_hinh.json`; ghi `data/llm_cache/propositions/<doc_id>.json` (với `--tat-ca`) hoặc `data/pilot_propositions/llm_output.json` (bộ thí điểm).
5. **So với đáp án thí điểm** (chỉ với bộ 30 đơn vị): `python -X utf8 -I src/propositions.py so`.
6. Đo ba số nghiệm thu của A39 và ghi vào `docs/status.md`.

## 3. Bước 1.6B (`src/concepts_names.py`)
Đang phải viết lại để đọc mệnh đề (`names-2`, A39). Cơ chế thư mục làm việc của bản cũ vẫn là mẫu cho bản mới và được giữ trong mã: `--xuat <thư mục>` dựng thư mục; trong thư mục có `tiep.py` (mỗi lệnh dựng lại trạng thái bằng cách gấp các `out/` theo thứ tự; mỗi `lo/NNN.json` phải trùng từng byte với lượt dựng lại, khác thì dừng); `--nhap <thư mục>` ghi cache; `--de` cho ghi đè. Bước này tuần tự (lượt sau thấy tên của lượt trước), khoảng 76 lượt, subagent Sonnet 5.5, effort `high`. Vận hành chi tiết sẽ viết khi `names-2` được duyệt.

Các dòng `DỪNG ...` mà `tiep.py` in là điều kiện dừng: model hoặc effort khai sai, đầu ra sai hình hai lần ở cùng lượt, `lo/` bị sửa, `system.txt` hay `schema.json` khác bản trong repo, hoặc lỗi dựng lượt (traceback ở `loi_tiep.txt`). Người vận hành xử lý, không để phiên tự sửa.

## 3b. Bước 2.6 (A42): tri thức của văn bản nạp sau, theo thứ tự này
Chạy ở gốc repo, kho con thì đặt `KLTN_TAP_CON=<tên>`; mọi lệnh trước đó cần `run_all --tap-con <tên> --llm replay` đã chạy (kho phiên bản, sổ gốc). Mỗi hộp cát mở bằng một phiên `claude -p "Đọc HUONG_DAN.md và làm theo." --model sonnet --effort high` trong chính thư mục đó (cho phép Read, Write, Edit, Agent, Glob; hộp cát 1.6B cần thêm Bash cho `tiep.py`).
1. **1.6A cho KU chưa có:** `python -X utf8 -I src/update.py xuat-1-6a <thư mục> [N lô đầu]`, chạy phiên, rồi `... update.py nhap-1-6a <thư mục>`. Luật dừng A39: làm 60 lô đầu trước, nhập, soát (câu dẫn lọt thành `menh_de`, lỗi cổng quá 5% số dòng thì dừng và báo), rồi dựng hộp cát cho phần còn lại.
2. **Sổ vị từ (một hộp cát cho cả chuỗi mốc, tuần tự):** chỉ dựng khi mọi KU đã có 1.6A (`xuat` từ chối nếu còn thiếu, vì lượt đổi khi có thêm dòng). `python -X utf8 -I src/predicate_registry.py --xuat <thư mục>`, phiên theo vòng `tiep.py` như 1.6B, rồi `--nhap <thư mục>`.
3. **1.7 cho cặp chế độ tăng dần cần:** `... update.py xuat-1-7 <thư mục>`, phiên, `... update.py nhap-1-7 <thư mục>`.
4. **1.9:** từ vựng đổi khi có quy tắc mới nên cả bộ câu hỏi phải hỏi lại: `... answering.py xuat <thư mục>`, phiên, `... answering.py nhap <thư mục>`.
5. `run_all --tap-con <tên> --llm replay`: báo cáo `update_report.txt` in kết quả 2.7 và căn cứ chuẩn của bộ câu hỏi trong Π_τ.

## 3c. Web demo hỏi đáp (A45)
Cần R của 2.6 (`run_all --tap-con <tên> --llm replay` đã chạy). Ở gốc repo:
```
KLTN_TAP_CON=lldnn python -X utf8 -I utils/demo/qa_server.py            mở http://127.0.0.1:8765/
KLTN_TAP_CON=lldnn python -X utf8 -I utils/demo/qa_server.py --llm off  không gọi LLM: chỉ câu của bộ dev, diễn giải dựng sẵn
KLTN_TAP_CON=lldnn python -X utf8 -I utils/demo/qa_server.py hoi "<câu hỏi>" 2025-06-01   một câu, in JSON
```
Mỗi câu hỏi mới gọi `claude -p` hai lượt (dữ kiện, diễn giải); khoảng 10 đến 20 giây mỗi lượt, tốn hạn mức của tài khoản Claude Code. Kết quả lưu ở `data/processed[_subset]/demo/demo_cache.json`, hỏi lại cùng câu và ngày thì không gọi lại. Trang chat không hiện cây chứng minh và dữ kiện (A48): mỗi câu hỏi ghi đủ một dòng vào `data/processed[_subset]/demo/demo_log.jsonl`.

## 3d. Chạy bằng API thay phiên Claude Code (A46, máy chủ ckey)
Cùng các thư mục làm việc như trên, nhưng `src/sandbox_api.py` làm thay phiên Claude Code: gửi nguyên văn `system.txt` và `lo/NNN.json` tới vai `api` của `docs/llm_config.md` (hiện là `deepseek-v4.1-flash` qua `https://api.xah.io`), ghi `out/` và `nhat_ky.tsv`. Kiểm tra vẫn do `nhap` của từng bước làm. Kết quả là một **lần chạy riêng** `ckey`: cache theo văn bản có hậu tố `.ckey`, đầu ra ở `data/processed_ckey/`, báo cáo ở `docs/run_reports_ckey/`; kết quả Sonnet không bị đụng.

**Setup (một lần).** Ở terminal riêng, không dán khoá vào chat: `setx CKEY_API_KEY "<khoá>"`. Terminal trong VS Code chỉ thấy biến sau khi thoát hẳn VS Code rồi mở lại; muốn dùng ngay trong terminal đang mở thì nạp từ registry, lệnh này không in khoá:
```
$env:CKEY_API_KEY = [Environment]::GetEnvironmentVariable("CKEY_API_KEY", "User")
"do dai khoa: " + "$env:CKEY_API_KEY".Length
```
Không đặt `ANTHROPIC_BASE_URL` hay sửa `~/.claude/settings.json`: bộ chạy không dùng Claude Code.

**Dựng KB gốc (giai đoạn 1, kho đầy đủ), PowerShell ở gốc repo.** Mọi lệnh sau trong cùng terminal có `$env:KLTN_LLM_RUN = "ckey"`; thư mục làm việc ở ngoài repo, chưa có hoặc rỗng.
1. Dựng đầu ra của lần chạy (không gọi API): `python -I src/run_all.py --llm-run ckey --llm replay`.
2. 1.6A:
   ```
   python -X utf8 -I src/propositions.py xuat <thư mục 1.6A> deepseek-v4.1-flash khong_co --tat-ca
   python -X utf8 -I src/sandbox_api.py <thư mục 1.6A> --toi-da 60
   python -X utf8 -I src/propositions.py nhap <thư mục 1.6A>
   ```
   Soát theo luật dừng A39 (câu dẫn lọt thành `menh_de`, lỗi cổng quá 5% số dòng thì dừng và báo), rồi chạy lại `sandbox_api.py` không có `--toi-da` và `nhap` lần nữa. Bỏ `--tat-ca` là bộ thí điểm 30 đơn vị (nhập vào `data/pilot_propositions/llm_output.ckey.json`).
3. 1.6B (tuần tự, bộ chạy lái `tiep.py`): `python -X utf8 -I src/predicates.py --xuat <thư mục 1.6B>`, `python -X utf8 -I src/sandbox_api.py <thư mục 1.6B>`, `python -X utf8 -I src/predicates.py --nhap <thư mục 1.6B>`.
4. 1.7: `python -X utf8 -I src/implicit_exceptions.py xuat <thư mục 1.7>`, `sandbox_api.py <thư mục 1.7>`, `implicit_exceptions.py nhap <thư mục 1.7>`.
5. `python -I src/run_all.py --llm-run ckey --llm replay`: 1.8 biên dịch quy tắc từ kết quả trên; báo cáo ở `docs/run_reports_ckey/`.

Tập con và giai đoạn 2 (2.6, 1.9): như mục 3b, thêm `$env:KLTN_TAP_CON = "lldnn"` và `run_all --tap-con lldnn --llm-run ckey --llm replay`; mỗi hộp cát chạy bằng `sandbox_api.py` thay cho phiên `claude -p`.

**Bộ chạy.** Lô độc lập chạy song song 4 lượt (`--song-song K`); lô lỗi thì bỏ qua và báo, chạy lại lệnh là làm tiếp lô còn thiếu (lô đã xong đọc từ cache `data/llm_cache/sandbox_api/`, không tốn tiền). Ba lô lỗi liền nhau thì dừng (máy chủ có thể đang hỏng). Hộp cát tuần tự dừng ở lỗi đầu tiên và ở mọi dòng `DỪNG` của `tiep.py`. Hộp cát dựng cho model khác `api.model` bị từ chối trước khi gọi. Các dòng "đã bóc rào" là đầu ra bọc ` ```json ` đã được bóc (A46).

**Giới hạn riêng.** Không kiểm chứng được model thật phía sau máy chủ; máy chủ chập chờn (ngày 19/11 gặp 503, 524, 502 rồi `404 The model is not available`). Không có effort. Lời nhắc được chỉnh trên Claude.

## 4. Giới hạn
- Cách ly dựa vào hướng dẫn trong thư mục; thư mục cha vẫn đọc được nếu phiên cố tình.
- Model và effort do phiên tự khai; effort không nằm trong khoá cache nên hai lần chạy khác effort mà cùng chữ thì `replay` không phân biệt.
- Bản ghi không dựng lại được bằng API.
- Lược đồ đầu ra được đưa cho subagent đọc chứ không bị ép: đầu ra sai hình thì giao lại một lần.
- Phụ thuộc chuỗi: đổi đầu ra của 1.2, 1.4, 1.5, 1.6A, hay `ten.model`, hay lời nhắc thì khoá đổi từ lượt bị ảnh hưởng trở đi; phải chạy lại từ đó trong thư mục mới.
