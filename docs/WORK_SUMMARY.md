# Tổng kết công việc — nhánh `feat/paper-architecture-alignment`

**Ngày:** 2026-11-16
**Nhánh:** `feat/paper-architecture-alignment` (tạo từ `docs/codebase-architecture-audit`, gốc `main`)

## Mục tiêu

Chuyển pipeline tri thức luật (rule-based) hiện có sang hệ suy diễn theo thời gian dùng LLM theo kiến trúc bài báo (**S_upd**, **S_know**, **S_infer**), wrap quanh nền tất định hiện có — không phá vỡ hành vi A1–A7.

## Cấu trúc thư mục

```
src/      parse.py, edges.py, exceptions.py, versioning.py, validation.py,
          general_exceptions.py, graph.py            (A1–A7)
          knowledge_layer.py (S_know), inference.py (S_infer)
          llm.py, law_registry.py                    (cơ sở hạ tầng)
tests/    test_parse, test_edges, test_exceptions, test_versioning,
          test_validation, test_general_exceptions, test_graph
docs/     WORK_SUMMARY.md, discovery/, papers/
data/     raw/, sample/, dev_amend/, processed/
```

## Đổi tên module (chuyên nghiệp, bỏ hậu tố `an_`)

| Stage | Cũ | Mới |
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

Test chuyển sang thư mục riêng `tests/`. Tên file dữ liệu (`a1_triples_*`, `a2_edges_*`, `a8_rules_*`, `a9_*.pl`…) giữ nguyên — là quy ước artifact, không phải tên module.

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
| `2e5284c` | refactor | rename stage modules to descriptive names |
| `53a559a` | refactor | tighten comments to engineer tone, drop redundant import aliases |
| `978d356` | refactor | move tests to tests/ directory |

## Chi tiết các thành phần mới

- **S_upd — `versioning.py`:** `normalize_unknown_line()` nhờ LLM viết lại dòng chỉ thị không parse được về ngữ pháp R1–R6, rồi parse lại bằng `match_directive`. LLM tắt/lỗi/kết quả sai → `None`, giữ đúng lỗi `E_*` cũ (model yếu chỉ fail-closed).
- **S_know — `knowledge_layer.py`:** với mỗi đơn vị đang hiệu lực, LLM trích mệnh đề + vị từ `P` (`concept|input`), cạnh `exception_of` ngầm, quy tắc `R`. Mọi payload đều kiểm định schema; mục lỗi vào **tập cách ly Q** (`a8_quarantine_*.jsonl`), không sang A9.
- **S_infer — `inference.py`:** biên dịch chương trình $\Pi_\tau$ (đơn vị `in_force` tại ngày $\tau$) sang s(CASP); chặn bằng negation-as-failure:
  ```prolog
  blocked(U) :- exception_of(_, U).
  holds(U)   :- in_force(U), not blocked(U).
  ```
- **Thu nạp luật động — `law_registry.py`:** nguồn định danh luật (prefix, dãy Điều, số đối chiếu). Đăng ký `blds2015` và `lld2019` (Luật Lao động 45/2019/QH14 = $d_0$; Nghị định 152/2020, 219/2025 làm văn bản sửa đổi). `parse`/`validation`/`graph`/`versioning` bỏ magic-string cứng.
- **Cấu hình — `llm.py` + `.env`:** client chat-completions thuần stdlib (urllib), tự nạp `.env`; chưa có key+model thì `complete()` trả `None` → các bước LLM rơi về đường tất định.

## Cách chạy

```bash
cd /mnt/e/KLTN            # (WSL) hoặc E:\KLTN (Windows)

# pipeline (mẫu 5 Điều)
python -I src/parse.py data/sample/blds2015_5dieu.md
python -I src/edges.py data/sample/blds2015_5dieu.md
python -I src/edges.py data/sample/blds2015_5dieu.md --refers-to
python -I src/exceptions.py data/sample/blds2015_5dieu.md
python -I src/knowledge_layer.py data/sample/blds2015_5dieu.md
python -I src/inference.py data/sample/blds2015_5dieu.md

# test
python -I tests/test_parse.py
# … test_edges, test_exceptions, test_versioning, test_validation,
#   test_general_exceptions, test_graph
```

## Trạng thái kiểm thử

- Python chạy qua **WSL (Ubuntu, Python 3.14.4)**; Windows chưa cài interpreter.
- Smoke test mẫu 5 Điều: A1 (35 đơn vị / 176 triples), A2 (60 cạnh), A2b (3 refers_to + 1 unresolved), A3 (1 exception_of), A9 (`a9_*.pl` hợp lệ, chặn NAF đúng) ✅.
- Sau khi chuyển `tests/`: `python -I tests/test_parse.py` xanh (exit 0). Đã kiểm import toàn bộ module graph sạch (không circular import); các suite còn lại chưa chạy hết do I/O WSL1/drvfs chậm.
- **A8/S_know chưa đánh giá được**: API key Gemini free-tier bị 503/429 (quota) — cần **key trả phí** để chạy thật.

## Ghi chú

- `docs/discovery/CODEBASE_ARCHITECTURE_AUDIT.md` là snapshot lịch sử (còn ghi tên module cũ `a1_parse.py`…) — chủ ý giữ nguyên để phản ánh trạng thái tại thời điểm audit.
- `.env` bị gitignore (chứa key); `.env.example` là bản mẫu đã commit.