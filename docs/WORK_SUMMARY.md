# Tổng kết công việc — nhánh `feat/paper-architecture-alignment`

**Ngày:** 2026-11-16
**Nhánh:** `feat/paper-architecture-alignment` (tạo từ `docs/codebase-architecture-audit`, gốc `main`)

## Mục tiêu

Chuyển pipeline tri thức luật (rule-based) hiện có sang hệ suy diễn theo thời gian dùng LLM theo kiến trúc bài báo (**S_upd**, **S_know**, **S_infer**), wrap quanh nền tất định hiện có, không phá vỡ hành vi cũ.

## Định danh module (đã đổi tên cho chuyên nghiệp)

| Stage | Tên cũ | Tên mới |
|---|---|---|
| A1 | `a1_parse.py` | `parse.py` |
| A2 / A2b | `a2_edges.py` | `edges.py` |
| A3 | `a3_exceptions.py` | `exceptions.py` |
| A4 | `a4_versions.py` | `versioning.py` |
| A5 | `a5_checks.py` | `validation.py` |
| A6 | `a6_general_exceptions.py` | `general_exceptions.py` |
| A7 | `a7_graph.py` | `graph.py` |
| S_know | `a8_knowledge_layer.py` | `knowledge_layer.py` |
| S_infer | `a9_inference.py` | `inference.py` |
| LLM client | — | `llm.py` |
| Law registry | — | `law_registry.py` |

Test nằm trong thư mục `tests/`: `test_parse.py`, `test_edges.py`, `test_exceptions.py`, `test_versioning.py`, `test_validation.py`, `test_general_exceptions.py`, `test_graph.py` (chạy: `python -I tests/test_parse.py` …).
Ghi chú: tên file dữ liệu (`a1_triples_*`, `a2_edges_*`, `a8_rules_*`, `a9_*.pl`…) giữ nguyên — đó là quy ước artifact, không phải tên module.

## Danh sách commit

| Hash | Loại | Nội dung |
|---|---|---|
| `020e070` | docs | finalize codebase architecture audit and paper alignment analysis |
| `bc1520b` | feat | activate LLM update engine (S_upd) in a4 amendment parser |
| `06c2d14` | feat | add knowledge layer (S_know) for propositions, predicates, rules and quarantine Q |
| `04fe95b` | feat | add s(CASP) inference compiler with time-aware blocking (S_infer) |
| `aa55148` | refactor | generalize law ingestion via registry (Labour Code d0 support) |
| `b991ce6` | feat | load LLM config from project .env |
| `6da5551` | docs | translate comments and docstrings to English in new modules |

## Chi tiết từng mốc

- **S_upd (versioning.py):** `normalize_unknown_line()` gọi LLM chuẩn hoá chỉ thị lạ/không hỗ trợ, kết quả buộc qua `match_directive` trước khi áp; `resolve_unmatched` thử LLM trước cả khi `E_UNSUPPORTED`. LLM tắt → hành vi cũ giữ nguyên.
- **S_know (knowledge_layer.py):** trích mệnh đề + vị từ P (concept/input), cạnh `exception_of` ngầm, quy tắc R; output lỗi → **tập cách ly Q** (`a8_quarantine_*.jsonl`).
- **S_infer (inference.py):** biên dịch Π_τ sang s(CASP), chặn bằng negation-as-failure: `blocked(U) :- exception_of(_, U).` / `holds(U) :- in_force(U), not blocked(U).`
- **Thu nạp luật động:** `law_registry.py` (BLDS2015 + LLD2019 = Luật Lao động 45/2019/QH14); bỏ magic-string/`EXPECTED` cứng ở parse/validation/graph/versioning.
- **Cấu hình:** `.gitignore`, `.env.example`, `.env` (gitignored); `llm.py` tự nạp `.env`.

## Cách chạy

```bash
cd /mnt/e/KLTN            # (WSL) hoặc E:\KLTN (Windows)
python -I src/parse.py data/sample/blds2015_5dieu.md
python -I src/edges.py data/sample/blds2015_5dieu.md
python -I src/edges.py data/sample/blds2015_5dieu.md --refers-to
python -I src/exceptions.py data/sample/blds2015_5dieu.md
python -I src/knowledge_layer.py data/sample/blds2015_5dieu.md
python -I src/inference.py data/sample/blds2015_5dieu.md
```

## Trạng thái kiểm thử

- Python qua WSL (Ubuntu, 3.14.4) ✅; Windows chưa cài.
- Smoke test mẫu 5 Điều: A1 (35 đv/176 triples), A2 (60 cạnh), A2b (3 refers_to + 1 unresolved), A3 (1 exception_of), A9 (`a9_*.pl` hợp lệ) ✅.
- Sau đổi tên: `test_parse` và `test_edges` chạy xanh (exit 0); toàn bộ module graph import sạch (không circular import). Các suite còn lại chưa chạy hết do I/O WSL1/drvfs chậm.
- A8/S_know: chưa chạy xong do API key Gemini free-tier 503/429 — cần key trả phí.