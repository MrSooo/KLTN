# Kết quả thực nghiệm — BLDS 2015 (bộ p4, Điều 609–662)

Thư mục này được điền tự động sau khi pipeline trên `blds2015_p4.md` chạy xong
(knowledge_layer → inference).

- `a8_*.jsonl` — tầng tri thức (propositions, predicates, implicit exceptions, rules, quarantine).
- `a9_blds2015_p4.pl` — chương trình s(CASP) biên dịch từ A8.
- `a8_report_*.txt`, `a9_report_*.txt` — báo cáo bước A8/A9.
- `a1_notes_*.txt`, `a2_unresolved_*.txt`, `a3_unhandled_*.txt` — ghi chú A1–A3.
- `knowledge_layer_run.log` — nhật ký chạy `knowledge_layer.py` (LLM).
- `run_metadata.txt` — thời gian chạy và exit code.

Các file là bản sao từ `data/processed/` và `docs/` (bản gốc được giữ nguyên).