<<<<<<< HEAD
# KLTN — Neuro-Symbolic Legal Reasoning

Kho lưu trữ nghiên cứu về suy luận ký hiệu kết hợp nơ-ron cho văn bản luật Việt Nam. Pipeline trích xuất conoscenza từ sách luật, dựng đồ thị kiến thức, biên dịch sang s(CASP), và xác minh tính nhất quán.

## Cấu trúc thư mục

```
data/
  raw/              Văn bản luật gốc (không chỉnh tay)
  dev_amend/        8 văn bản sửa đổi dev (đầu vào A4)
  ext_amend/        Điều chỉnh nguồn ngoài
  gold/             Ground truth (gold TSV, danh sách đơn vị)
  labor/            Benchmark Luật Lao động (nested exceptions)
  sample/           Bản prób 5 điều
  processed/        Lưu trữ đầu ra từng bước (dual-path: flat + subdir)
src/
  a1_parse.py       Tách văn bản thành đơn vị + triples
  a2_edges.py       Cạnh cấu trúc contains/part_of + dẫn chiếu refers_to
  a3_exceptions.py  Ngoại lệ tường minh
  a4_versions.py    Áp dụng văn bản sửa đổi, quản lý phiên bản
  a4_llm.py         Gọi LLM để chuẩn hoá khối sửa đổi
  a5_checks.py      Kiểm tra tính nhất quán A1–A3
  a6_general_exceptions.py Ngoại lệ chung
  a7_graph.py       Đồ thị gộp các phiên bản
  edges.py          Path resolver (ROOT, PROCESSED_DIR), đọc units/edges
  inference.py      Biên dịch chương Πτ sang s(CASP)
  knowledge_layer.py Trích xuất mệnh đề/vị từ qua LLM (S_know)
  law_registry.py   Danh mục pháp luật (identity, articles, expected counts)
  run_all.py        Chạy toàn bộ pipeline A1→A7, A8, tests
  symbolic_legal_verifier.py Xác minh ký hiệu
  scasp_feedback_loop.py Vòng phản hồi scasp
  cot_rule_extractor.py Trích xuất quy tắc CoT
  v3_kb_adapter.py  Adapter nhập KB từ origin/v3_refactor
  validation.py     Schema validation
  versioning.py     Quản lý phiên bản thời gian
tests/              Bộ kiểm thử (pytest)
paper/              Bản propuesta LaTeX (chỉ .tex/.bib được track)
docs/               Báo cáo chạy, quyết định, papers (PDF reference không track)
results/            Đầu ra thí nghiệm (archive_legacy_v2 tách riêng)
utils/              Script hỗ trợ (giữ tạm thời)
```

## Quickstart

```bash
# 1. Chạy toàn bộ pipeline A1→A7 (cần Python >= 3.10)
python -I src/run_all.py

# 2. Thêm A8 (trang xem đồ thị)
python -I src/run_all.py --a8

# 3. Chạy kiểm thử
python -I src/run_all.py --tests

# 4. Chạy pytest trực tiếp (nếu đã cài)
python3 -m pytest tests/ -q
```

Dữ liệu đầu ra ghi vào `data/processed/<bước>/` và báo cáo chạy vào `docs/bao_cao_chay/<bước>/`. Sau mỗi lần sửa, `git diff --stat data/ docs/bao_cao_chay/` cho biết những đầu ra nào thay đổi.

## Tuân thủ

- Không sử dụng ASCII dividers (`# ====`) trong mã nguồn.
- Comment và tài liệu được viết thủ bằng tiếng Việt, tránh boilerplate AI.
- `.gitignore` loại trừ `.env`, `__pycache__/`, `*.pyc`, artifacts LaTeX (`*.aux`, `*.log`, …), `docs/papers/*.pdf` (giữ file trên disk, không track).
=======
# kltn: cơ sở tri thức Bộ luật Lao động thích nghi theo ngày hiệu lực

Đồ án tốt nghiệp. Hệ thống dựng một cơ sở tri thức (KB) từ Bộ luật Lao động 45/2019 và các văn bản dưới luật (nghị định, thông tư, nghị quyết, bản hợp nhất). KB trả lời câu hỏi có/không theo ngày sự việc kèm căn cứ pháp lý, và cập nhật được khi nạp thêm văn bản: mỗi văn bản là một sự kiện nạp, tạo phiên bản mới của các đơn vị bị sửa và đóng phiên bản cũ theo ngày hiệu lực.

**Trạng thái:** giai đoạn 1 (dựng KB gốc) xong các bước 1.1 đến 1.5, đang làm lại bước 1.6; giai đoạn 2 (cập nhật) có mã cho bước 2.2 đến 2.4. Chi tiết: [docs/status.md](docs/status.md). Kế hoạch: [docs/roadmap.md](docs/roadmap.md).

## Tài liệu
Đọc theo thứ tự này nếu mới vào dự án:

| Tài liệu | Nội dung |
|---|---|
| [docs/overview.md](docs/overview.md) | Toàn bộ pipeline kể bằng một ví dụ xuyên suốt (Điều 35); đọc đầu tiên |
| [docs/status.md](docs/status.md) | Trạng thái từng bước, việc đang dở, nợ kỹ thuật |
| [docs/roadmap.md](docs/roadmap.md) | Lộ trình và phụ thuộc giữa các việc |
| [docs/design/pipeline_design.md](docs/design/pipeline_design.md) | Thiết kế: mô hình dữ liệu, nguyên tắc, bảng các bước |
| [docs/design/steps_1_1_to_1_5.md](docs/design/steps_1_1_to_1_5.md) | Mô tả chi tiết bước 1.1 đến 1.5: dữ liệu vào ra, trường, số đo |
| [docs/design/step_1_6a_propositions.md](docs/design/step_1_6a_propositions.md) | Bước 1.6A (tách mệnh đề) |
| [docs/design/steps_1_6_to_1_8.md](docs/design/steps_1_6_to_1_8.md) | Phân tích lỗi bước 1.6 bản cũ; bản nháp bước 1.7, 1.8 |
| [docs/decisions.md](docs/decisions.md) | Sổ quyết định (A1 đến A40) kèm lý do và số đo |
| [docs/operations/llm_sandbox.md](docs/operations/llm_sandbox.md) | Cách chạy phần LLM bằng phiên Claude Code ngoài repo |
| [docs/llm_config.md](docs/llm_config.md) | Model, hạn mức, khoá API (file này được mã đọc) |
| [docs/reference/](docs/reference) | Tài liệu tra cứu: phương pháp (`method.md`), 26 loại chỉ thị, khảo sát văn bản |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Quy ước đặt tên, quy trình làm việc, quy tắc về LLM và dữ liệu |

## Yêu cầu
- Python 3.10 trở lên. Mã nguồn chỉ dùng thư viện chuẩn (đã chạy trên 3.13 và 3.14).
- **Claude Code** (không bắt buộc cho phần còn lại): chỉ cần để *tạo mới* đầu ra của bước 1.6 (1.6A tách mệnh đề, 1.6B đặt tên vị từ), vì phần LLM của bước này chạy bằng một phiên Claude Code ngoài repo. Không có Claude Code thì mọi việc khác vẫn làm được: chạy toàn bộ chuỗi bằng `--llm off` hoặc `--llm replay`, đọc và sửa mã, chạy test, đọc báo cáo, xem đồ thị. Đường gọi API Gemini cũng có sẵn (`propositions.py gemini`) nhưng không được chọn cho 204 lô (A39).
- Chỉ khi chạy LLM thật (`--llm live`): gói `google-genai` (Gemini) hoặc `anthropic` (Claude) trong một `.venv`, cùng biến môi trường `GEMINI_API_KEY` và `ANTHROPIC_API_KEY`. Xem [docs/llm_config.md](docs/llm_config.md).
- Chỉ từ bước 1.8: SWI-Prolog 10 trở lên và pack `scasp` (kiểm bằng `swipl --version` và nạp `library(scasp)`).

## Bắt đầu nhanh
```
git clone <địa chỉ repo> kltn
cd kltn
git switch v3_refactor

python -I src/run_all.py --viewer --tests
```
Lệnh cuối chạy toàn bộ chuỗi trên cả kho (khoảng 35 giây), dựng `data/processed/` (đầu ra, không nằm trong git), ghi báo cáo vào `docs/run_reports/`, dựng trang xem đồ thị và chạy toàn bộ test. Kết quả mong đợi: dòng cuối `XONG: 14/14 bước`.

Hai chế độ LLM, đều không gọi mạng:
```
python -I src/run_all.py --llm off    --viewer --tests   # mặc định; bước dùng LLM chỉ chạy phần máy
python -I src/run_all.py --llm replay --viewer --tests   # đọc lại phản hồi LLM đã lưu ở data/llm_cache/
```
`--llm live` gọi API thật, tốn hạn mức hoặc tiền, và chỉ chạy khi được cho phép. Trang xem đồ thị sau khi dựng: `data/processed/viewer/graph_viewer.html` (mở bằng trình duyệt, không cần máy chủ).

Chạy riêng một bước: `python -I src/<module>.py` (xem đầu mỗi file để biết tham số). Chạy riêng một bộ test: `python -I tests/test_<module>.py`; dòng cuối phải là `tổng test lỗi: 0`. Trên Windows, một số lệnh cần thêm `-X utf8` (ví dụ `python -X utf8 -I src/propositions.py ...`).

## Pipeline và cấu trúc mã

| Bước | Module (`src/`) | Việc | Đầu ra (`data/processed/<thư mục>/`) | Test |
|---|---|---|---|---|
| 1.1 | `parse.py` | tách văn bản thành đơn vị (Chương, Mục, Điều, Khoản, Điểm, phụ lục) | `parse/` | `test_parse.py` |
| 1.2 | `refs.py` | cạnh cha-con, cạnh dẫn chiếu `refers_to`, quan hệ chờ đích | `refs/` | `test_refs.py` |
| 1.3 | `delegation.py` | điều khoản luật giao cho cấp dưới quy định chi tiết | `delegation/` | `test_links_article_type_exceptions.py` |
| 1.4 | `article_type.py` | nhãn loại cho từng Điều | `article_type/` | `test_links_article_type_exceptions.py` |
| 1.5 | `exceptions_explicit.py`, `exceptions_general.py` | cạnh ngoại lệ `exception_of` ("trừ trường hợp ...") | `exceptions_explicit/`, `exceptions_general/` | `test_links_article_type_exceptions.py` |
| 1.6A | `propositions.py` (mới), `concepts.py` (bản cũ) | tách chữ luật thành mệnh đề | `concepts/` | `test_propositions.py`, `test_concepts.py` |
| 1.6B | `concepts_names.py` | đặt tên và tái dùng vị từ | `concepts/` | `test_concepts_names.py` |
| 2.2 | `links.py` | nối văn bản dưới luật vào luật gốc (`based_on`, `details`) | `links/` | `test_links_article_type_exceptions.py`, `test_llm_steps.py` |
| 2.3 | `directives.py`, `directives_rare.py` | đọc chỉ thị sửa đổi, bãi bỏ, hiệu lực | `versions/` | `test_versions_directives.py`, `test_directives_rare.py` |
| 2.4 | `versions.py` | kho phiên bản theo ngày hiệu lực | `versions/` | `test_versions_directives.py` |
| — | `checks.py` | kiểm độc lập các bước trên | (chỉ báo cáo) | `test_checks_graph_viewer_llm.py` |
| — | `graph.py` | đồ thị gộp kèm khoảng hiệu lực của nút | `graph/` | `test_checks_graph_viewer_llm.py` |
| — | `utils/viewer/` | trang HTML xem đồ thị theo ngày | `viewer/` | `test_checks_graph_viewer_llm.py` |

Mã dùng chung: `corpus.py` (đọc `manifest.csv`, đường dẫn, bảng văn bản), `llm_client.py` (nơi duy nhất gọi API: cache, hạn mức, giãn nhịp), `textutil.py` (chuẩn hoá chữ), `run_all.py` (chạy cả chuỗi).

```
src/                   mã nguồn, mỗi bước một module; run_all.py chạy cả chuỗi
tests/                 mọi test_*.py và khung _harness.py
utils/                 viewer/ (trang xem), render_report.py (Markdown sang HTML), normalize_text.py
data/raw/labor/        văn bản luật đầu vào (nhóm base và dev) và manifest.csv
data/llm_cache/        phản hồi LLM đã lưu (được theo dõi trong git, dùng cho --llm replay)
data/pilot_propositions/  dữ liệu thí điểm của bước 1.6A (đáp án nháp, đầu ra các lần thử)
data/processed/        đầu ra do code sinh ra (không nằm trong git; dựng lại bằng run_all)
docs/                  tài liệu (bảng ở trên); docs/run_reports/ do code sinh ra, không sửa tay
```

## Quy ước dữ liệu
- `doc_id` là tên file trong `data/raw/labor/` (ví dụ `BLLD_45-2019`, `ND_145-2020`). Số hiệu, ngày ban hành, ngày hiệu lực, số Điều đọc từ `data/raw/labor/manifest.csv` (UTF-8 có BOM, đọc bằng `utf-8-sig`), không chép cứng vào mã.
- Mã đơn vị: `<doc_id>.D154.K8a.b` là Điều 154, khoản 8a, điểm b. Hậu tố chữ (`D2a`, `K8a`) là bình thường; điểm `đ` viết `dd`; phụ lục `<doc_id>.PL1.M2.R15`.
- Mỗi bước nhận đầu ra của bước trước và có số đối chiếu cứng, nên một giả định sai âm thầm sẽ lan xuống các bước sau. Khi đổi một bước, chạy cả `--llm off` và `--llm replay`.

## Phần LLM
Chỉ ba bước dùng LLM: 1.6A, 1.6B và 2.2. Mọi đề xuất của LLM đi qua cổng kiểm bằng máy (khớp nguyên văn, giá trị trong tập đóng, tên đúng dạng, biên dịch) trước khi dùng; không dùng một LLM để kiểm LLM khác. Phần LLM của bước 1.6 chạy bằng phiên Claude Code mở trong thư mục làm việc ngoài repo, không gọi API (cần Claude Code, xem mục Yêu cầu): xem [docs/operations/llm_sandbox.md](docs/operations/llm_sandbox.md). Phản hồi đã lưu nằm ở `data/llm_cache/` để chạy lại không tốn lượt.

## Đóng góp
Đọc [CONTRIBUTING.md](CONTRIBUTING.md) trước khi sửa mã hoặc tài liệu. Quyết định thiết kế mới ghi vào [docs/decisions.md](docs/decisions.md).
>>>>>>> origin/v3_refactor
