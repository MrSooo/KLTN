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
