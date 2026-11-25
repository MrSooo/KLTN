# Tổng hợp kết quả gần đây: pipeline luật Lao động (lld2019), benchmark ngoại lệ lồng nhau và đợt chẩn đoán s(CASP)

Cập nhật: 25/11/2026. Nhánh: `feature/neuro-symbolic-legal-cot`, commit đầu nhánh `4bf83c1`.
Phạm vi: kết quả phát sinh từ 22/11 đến 24/11/2026, gồm (1) pipeline A1–A7/A9 trên
`lld2019_labor`, (2) benchmark 14 ca ngoại lệ lồng nhau, (3) thí nghiệm 80 ca trong lịch sử git,
và (4) đợt chẩn đoán hiệu năng s(CASP) tối 24/11.

---

## 0. Đọc nhanh trong 1 phút

- **Pipeline chạy được trên luật Lao động**: 45 đơn vị, 226 cặp `(s, p)`, 78 cạnh cấu trúc,
  10 cạnh `exception_of`; đồ thị gộp 53 nút / 102 cạnh; A5 báo **ĐẠT** cả 12 mục kiểm;
  S_scan **0 lỗi** trên cả 5 họ lỗi đồ thị.
- **Benchmark 14 ca ngoại lệ lồng nhau**: **14/14 = 100%** (d=1: 8/8, d=2: 3/3, d=3: 2/2),
  cặp phản chứng 1/1 nhất quán. Lưu ý: đây là **mức trần ký hiệu** do hàm quyết định viết tay
  `predict_verdict()` chấm, **không phải** kết quả của một arm LLM.
- **Thí nghiệm 80 ca** (commit `24b7613`): chỉ ghi 66/80 dòng kết quả, **không lưu cột gold**
  nên không tính được accuracy; file `results/labor_ablation_80_v3.json` đã bị xoá khỏi HEAD
  khi tái cấu trúc repo, chỉ còn trong lịch sử git.
- **Phát hiện lỗi quan trọng (24/11)**: `src/inference.py` phân giải sai đường dẫn A3/A6/A8,
  nên chương trình `.pl` sinh ra có **0 fact `exception_of`**. Dòng "s(CASP) exception
  blocking ... -> satisfiable" trong báo cáo cũ vì vậy là **kết luận rỗng**.
- **Đã sửa và kiểm chứng lại (25/11)**: đọc đúng `a3/a3_exceptions_*`, `a6/a6_exceptions_*`,
  `a8/a8_implicit_exceptions_*` và khử trùng lặp; thêm fact đơn trị `has_exception/1` để luật
  chặn không phải mở rộng `forall` trên `exception_of/2`. Chương trình mới có **10** fact
  `exception_of`, **8** fact `has_exception`, và `holds('LLD2019.D35.K2.e')` trả **`ANSWER: no`**
  trong vài giây, `blocked(...)` trả `yes` — hết timeout.
- **Dọn tiền tố sai**: `edges.triples_path()` tìm `a1/a1_<stem>.jsonl` trong khi A1 ghi
  `a1/a1_triples_<stem>.jsonl`, nên **không nguồn nào** đọc được A1; đã sửa thứ tự phân giải và
  xoá bản sao cũ mang tiền tố `BLDS2015.`.
- **`refers_to` của mẫu lao động**: A2b phát hiện **19 cụm** dẫn chiếu nhưng dừng ở danh sách
  điểm liệt kê (`LLD2019.D36.K2`), nên **0 cạnh** `refers_to` được ghi và
  `a2_unresolved_lld2019_labor.txt` rỗng — con số "19 `refers_to` edges" trong paper cũ là
  số cụm, không phải số cạnh (đã sửa lại trong `paper/proposal.tex`).

---

## 1. Nguồn số liệu

| Tệp | Thời điểm | Trạng thái git | Dùng cho |
|---|---|---|---|
| `results/labor_ablation_v3.json` | 25/11 | chưa track | metric 14 ca + 45 đơn vị in-force |
| `results/labor_ablation_v3.md` | 25/11 | chưa track | bảng 14 ca, model s(CASP) mẫu |
| `data/processed/a9_lld2019_labor.pl` | 25/11 | chưa track | chương trình s(CASP) (**10** `exception_of`, **8** `has_exception`) |
| `docs/bao_cao_chay/a{1,2,3,5,6,7}/*_lld2019_labor.txt` | 24/11 08:41–08:51 | chưa track | số liệu từng bước A1–A7 |
| `data/processed/a{1,2,3,6,7}/*_lld2019_labor*.jsonl` | 24/11 | chưa track | đầu ra pipeline |
| `results/labor_ablation_80_v3.json` | 22/11 (commit `24b7613`) | **không còn ở HEAD** | thí nghiệm 80 ca |
| `paper/proposal.tex` | 25/11 | chưa track nội dung mới | số liệu đang công bố |
| `tests/test_inference.py` | 25/11 | chưa track | test đường dẫn JSONL + chặn ngoại lệ |

`src/inference.py`, `src/eval_benchmark.py`, `src/edges.py`, `src/exceptions.py`,
`src/general_exceptions.py`, `src/law_registry.py`, `src/a1_parse.py`, `src/a7_graph.py` có
**thay đổi chưa commit** — xem mục 5 và 7.

---

## 2. Benchmark 14 ca ngoại lệ lồng nhau (`lld2019`)

Nguồn: `results/labor_ablation_v3.json` + `results/labor_ablation_v3.md`.

### 2.1 Tổng hợp

| Chỉ số | Giá trị |
|---|---|
| Tổng số ca | 14 |
| Đúng | 14 |
| Accuracy | **1.0000 (14/14)** |
| Cặp phản chứng | 1 cặp, 1 nhất quán |
| S_scan (5 họ lỗi) | dead_rule 0, duplicate 0, broken_link 0, blocking_cycle 0, contradiction 0 |
| Chương trình sinh ra | 45 đơn vị in-force, **10** fact `exception_of`, **8** fact `has_exception`, 0 rule A8 |

### 2.2 Theo verdict và theo độ sâu ngoại lệ

| verdict | tổng | đúng | accuracy |
|---|---|---|---|
| Concluded | 6 | 6 | 100.0% |
| Refuted | 3 | 3 | 100.0% |
| Insufficient Basis | 2 | 2 | 100.0% |
| Quarantined/Out-of-Scope | 3 | 3 | 100.0% |

| độ sâu | tổng | đúng | accuracy |
|---|---|---|---|
| $d=1$ | 8 | 8 | 100.0% |
| $d=2$ | 3 | 3 | 100.0% |
| $d=3$ | 2 | 2 | 100.0% |

### 2.3 Từng ca

| id | d | gold | dự đoán | `holds(anchor)` | đúng |
|---|---|---|---|---|---|
| lab_d1_001 | 1 | Concluded | Concluded | SAT | ✓ |
| lab_d1_002 | 1 | Concluded | Concluded | SAT | ✓ |
| lab_d2_001 | 2 | Concluded | Concluded | SAT | ✓ |
| lab_d2_002 | 2 | Refuted | Refuted | SAT | ✓ |
| lab_d2_003 | 2 | Refuted | Refuted | SAT | ✓ |
| lab_d3_001 | 3 | Concluded | Concluded | SAT | ✓ |
| lab_d3_002 | 3 | Concluded | Concluded | SAT | ✓ |
| lab_cf_001 | 1 | Concluded | Concluded | SAT | ✓ |
| lab_cf_002 | 1 | Refuted | Refuted | SAT | ✓ |
| lab_ins_001 | 1 | Insufficient Basis | Insufficient Basis | SAT | ✓ |
| lab_ins_002 | 1 | Insufficient Basis | Insufficient Basis | SAT | ✓ |
| lab_quar_001 | – | Quarantined/Out-of-Scope | Quarantined/Out-of-Scope | – | ✓ |
| lab_quar_002 | 1 | Quarantined/Out-of-Scope | Quarantined/Out-of-Scope | – | ✓ |
| lab_quar_003 | 1 | Quarantined/Out-of-Scope | Quarantined/Out-of-Scope | – | ✓ |

**Cách đọc kết quả này cho đúng**

1. Accuracy được tính bằng `predict_verdict()` trong `src/eval_benchmark.py` — một hàm quyết
   định viết tay theo `data/labor/concept_book.json`. Vì vậy 14/14 là **trần trên của tầng
   ký hiệu**, không nói gì về chất lượng trích xuất của LLM.
2. Cột `holds(anchor)` chỉ là **tín hiệu cấu trúc**: câu truy vấn dùng anchor cấp Điều
   (`holds('LLD2019.D35')`), không phải đơn vị bị ngoại lệ, nên hầu như luôn SAT.
3. Cột này **không** phải phép kiểm cơ chế chặn ngoại lệ: nó chỉ hỏi anchor cấp Điều. Phép kiểm
   chặn ngoại lệ là dòng smoke trong `results/labor_ablation_v3.md`:
   `holds('LLD2019.D35.K2.e')` → `ANSWER: no`, `blocked('LLD2019.D35.K2.e')` → `yes`,
   `holds('LLD2019.D35.K1.a')` → `yes` kèm model, không còn cảnh báo `exception_of/2` không tồn tại.
4. Cả 11 ca in-scope đều SAT trên anchor cấp Điều; riêng `holds('LLD2019.D46')` từng trả UNSAT
   một lần do lỗi engine tạm thời, nay `scasp_query()` phân biệt `SCASP_ERROR` với "không có
   model" nên trường hợp đó sẽ hiện `ERR` chứ không bị đọc thành `UNSAT`.

---

## 3. Thí nghiệm 80 ca (commit `24b7613`)

Nguồn: `git show 24b7613:results/labor_ablation_80_v3.json` (file không còn ở HEAD).

Thiết lập: corpus `lld2019_labor.md`, concept book `LLD2019.D35,D36,D37,D39,D46,R169`,
độ sâu `d ∈ {1,2,3}`, `num_questions = 80`.

| arm | mô tả | số dòng ghi được | phân bố verdict | reward (min / trung bình / max từ các dòng) |
|---|---|---|---|---|
| 1 | LLM trực tiếp, không Concept Graph, không s(CASP) | 25 | Concluded 13, Insufficient 5, Refuted 3, Quarantined 4 | 0.00 / 0.451 / 0.85 |
| 2 | Concept Graph + CoT, một lượt, η=0, không feedback | 21 | Concluded 10, Insufficient 5, Refuted 2, Quarantined 4 | 0.00 / 0.398 / 0.81 (kiểu dữ liệu lẫn chuỗi và số) |
| 3 | Lặp với feedback nhị phân, η=2 | 13 | Concluded 10, Insufficient 2, Refuted 1 | 0.00 / 0.692 / 0.92 (khối `summary` ghi 0.55) |
| 4 | Lặp với feedback chi tiết (V_legal + s(CASP)), η=2 | 7 | Concluded 2, Insufficient 2, Refuted 1, Quarantined 2 | 0.00 / 0.373 / 0.91 (khối `summary` ghi 0.60) |

Hai khối `summary` (arm 3, 4) không khớp với giá trị trung bình tính từ chính các dòng dữ liệu;
cần chạy lại trước khi trích dẫn. Arm 3 và 4 cũng có nhiều dòng reward 0.0, tức có ca bị tính là
thất bại hoàn toàn nhưng vẫn ghi verdict.

**Hạn chế cần ghi rõ nếu dùng số liệu này**

- Mỗi dòng chỉ có `verdict`, `steps`, `reward`; **không có gold** ⇒ không suy ra được accuracy.
- Số dòng không bằng 80 (25/21/13/7 = 66) ⇒ các arm sau chỉ chạy một phần danh sách câu hỏi.
- Nhãn `Quarantined` và `Quarantined/Out-of-Scope` bị tách làm hai giá trị trong arm 1–2 ⇒
  thống kê verdict chưa chuẩn hoá.
- File đã bị xoá trong commit tái cấu trúc (`b884e0a`) nên `results/` hiện **không còn** số
  liệu 80 ca; `paper/proposal.tex` cũng không trích bảng này.

Kết luận thẳng: thí nghiệm 80 ca **chưa phải bằng chứng định lượng**; muốn dùng phải sinh lại
gold và chạy thống nhất trên đủ 80 câu cho cả 4 arm.

---

## 4. Số liệu pipeline trên `lld2019_labor` (A1–A7, A9)

Nguồn: `docs/bao_cao_chay/*/…_lld2019_labor.txt` và các tệp `data/processed/**`.

| Bước | Kết quả |
|---|---|
| A1 (tách đơn vị) | 45 đơn vị (6 Điều, 17 Khoản, 22 Điểm), 226 cặp `(s, p)`; mã trong `a1_lld2019_labor.jsonl` vẫn mang tiền tố `BLDS2015.`, được chuẩn hoá khi biên dịch |
| A2 (cạnh cấu trúc) | 78 cạnh (39 `contains` + 39 `part_of`); **0** `refers_to` cho văn bản này |
| A3 (ngoại lệ tường minh) | 0 dòng |
| A5 (kiểm tra nhất quán) | **ĐẠT** cả 12 mục (1a–1e, 2a–2f, 3): mã trùng, cha duy nhất, cạnh trùng; 78 bộ ba, 0 lặp |
| A6 (ngoại lệ chung) | 10 ngoại lệ + 21 dòng điều kiện |
| A7 (đồ thị gộp) | 53 nút (`dieu` 6, `khoan` 17, `diem` 22, `dieu_kien` 7, `van_ban` 1); 102 cạnh (`contains` 45, `part_of` 45, `exception_of` 10, `same_text_as` 2); 1 thành phần liên thông; **ĐẠT** cả 7 mục kiểm |
| A7 (nút trùng chữ) | `LLD2019.D36.K2.d` → `LLD2019.D35.K1.d`, `LLD2019.D169.K5` → `LLD2019.D46.K4` |
| A9 (biên dịch s(CASP)) | 45 đơn vị in-force; 0 rule A8; số fact `exception_of` phụ thuộc bản `inference.py` (xem mục 5) |

10 cạnh `exception_of` của A6/A7 — đây là các sự kiện mà tầng suy luận **phải** nhìn thấy:

| nguồn | đích | nguồn gốc |
|---|---|---|
| `LLD2019.C_1162b718` | `LLD2019.D35.K2.a` | "trừ trường hợp Điều 29" |
| `LLD2019.C_d5c6dd73` | `LLD2019.D35.K2.b` | "trừ trường hợp khoản 4 Điều 97" |
| `LLD2019.C_798cfde0` | `LLD2019.D35.K2.e` | "trừ trường hợp các bên có thỏa thuận khác" |
| `LLD2019.C_426b8c79` | `LLD2019.D36.K1.dd` | "trừ trường hợp có thỏa thuận khác" |
| `LLD2019.C_0af8c96d` | `LLD2019.D37.K1` | "trừ trường hợp điểm b khoản 1 Điều 36" |
| `LLD2019.C_f7c35f33` | `LLD2019.D46.K1` | "trừ trường hợp đủ điều kiện hưởng lương hưu" |
| `LLD2019.C_84491d28` | `LLD2019.D169.K3` | "trừ trường hợp pháp luật có quy định khác" |
| `LLD2019.C_84491d28` | `LLD2019.D169.K4` | "trừ trường hợp pháp luật có quy định khác" |
| `LLD2019.D36.K1.b` | `LLD2019.D37.K1` | ngoại lệ lồng: điểm b khoản 1 Điều 36 |
| `LLD2019.D36.K1.e` | `LLD2019.D46.K1` | ngoại lệ lồng: điểm e khoản 1 Điều 36 |

Hai cạnh cuối có nguồn là **đơn vị luật thật** (điểm b và điểm e khoản 1 Điều 36) thay vì nút
điều kiện, tạo thành hai chuỗi ngoại lệ lồng Điều 36 → Điều 37 và Điều 36 → Điều 46 — đúng phần
mà benchmark 14 ca muốn đo.

---

## 5. Hai lỗi gốc đã tìm ra và sửa (24–25/11)

### 5.1 Lỗi 1: đọc sai tệp ngoại lệ ⇒ chương trình `.pl` không có `exception_of`

`inference._resolve_jsonl_path()` ghép tên tệp từ **một** tham số cho cả thư mục và tiền tố:

```
đang tìm : data/processed/a3/a3_lld2019_labor.jsonl
tệp thật : data/processed/a3/a3_exceptions_lld2019_labor.jsonl
tệp thật : data/processed/a8_implicit_exceptions_lld2019_labor.jsonl   (cấp phẳng)
```

Tên thư mục (`a3`, `a6`, `a8`) không suy ra được tiền tố tệp (`a3_exceptions`,
`a6_exceptions`, `a8_implicit_exceptions`), nên cả ba lần đọc trả rỗng. Hệ quả: `.pl` có **0**
fact `exception_of`, `blocked/1` vô nghĩa, và báo cáo cũ tự mâu thuẫn
(`smoke.holds_blocked = true` nhưng `smoke.blocked_true = false`, kèm cảnh báo
`scasp_predicate 'user:exception_of'/2' does not exist`).

**Đã sửa**: `_resolve_jsonl_path(stage_dir, file_prefix, stem, tag)` tách thư mục khỏi tiền tố
tệp, `exception_rows()` đọc đủ ba tầng A3/A6/A8 và khử trùng lặp theo `(s, p, o)`.

### 5.2 Lỗi 2: `edges.triples_path()` tìm sai tên tệp A1

A1 ghi `data/processed/a1/a1_triples_<stem>.jsonl`, còn `edges.triples_path()` (được
`inference.active_codes` dùng) lại tìm `a1/a1_<stem>.jsonl` — nên **không nguồn nào** đọc được
A1, và bản sao cũ `a1/a1_lld2019_labor.jsonl` (mang tiền tố `BLDS2015.`) là thứ duy nhất còn
đọc được. **Đã sửa**: ưu tiên tệp chuẩn `a1/a1_triples_<stem>.jsonl`, giữ đường lùi kiểu cũ;
xoá bản sao sai tiền tố.

Cùng gốc rễ đó, nút văn bản ở A7 lấy từ `a1.BASE_DOC` — một dict cứng của Bộ luật Dân sự — nên
đồ thị luật Lao động vẫn có nút `BLDS2015` với số hiệu 91/2015/QH13. **Đã sửa**:
`law_registry.Law` có thêm `so_hieu`/`ngay_ban_hanh`/`hieu_luc`, `a1_parse.base_doc_for(stem)`
dựng văn bản gốc theo luật của nguồn, và `a7_graph.base_doc_node(src)` dùng hàm này. Nút văn bản
của mẫu lao động nay là `LLD2019` · `45/2019/QH14` · ban hành 2019-11-20 · hiệu lực 2021-01-01.
Bản blds2015 giữ nguyên từng trường (đối chứng: chạy lại A7 có phiên bản cho
`blds2015_p4` + dev05 vẫn ĐẠT 7a–7g).

### 5.3 Lỗi mã hoá: `blocked(U) :- exception_of(_, U)` làm s(CASP) nổ `forall`

Sau khi sửa 5.1, chương trình có 10 fact `exception_of`; đo trực tiếp (24/11):

| truy vấn | kết quả | thời gian |
|---|---|---|
| `holds('LLD2019.D35.K1.a')` | `yes` + model + tree | 4.2 s |
| `blocked('LLD2019.D35.K2.e')` | `yes` | 7.3 s |
| `holds('LLD2019.D35.K2.e')` | **timeout** | > 120 s |
| thử theo số fact 0 / 1 / 3 | `yes` / `yes` / `no` | 7.2 / 7.5 / 7.4 s |
| thử theo số fact 10 | **timeout** | > 120 s |

**Đã sửa**: ngoài `exception_of/2` (giữ để truy vết nguồn), `render_program()` phát thêm fact
đơn trị `has_exception/1` cho từng đích, khử trùng lặp; luật chặn đổi thành
`blocked(U) :- has_exception(U).` Nhờ đó mọi đích `not blocked(U)` đều đã ground.

### 5.4 Kết quả sau khi sửa (chạy lại 25/11)

| Kiểm tra | Kết quả |
|---|---|
| `grep -c '^exception_of(' data/processed/a9_lld2019_labor.pl` | **10** |
| `grep -c '^has_exception(' …` | **8** (10 cạnh, 8 đích phân biệt) |
| `holds('LLD2019.D35.K2.e')` | **`ANSWER: no`** — hết timeout, không cảnh báo |
| `blocked('LLD2019.D35.K2.e')` | `ANSWER: yes` |
| `holds('LLD2019.D35.K1.a')` | `ANSWER: yes` + model + tree |
| `smoke` trong JSON | `holds_no_exception: true`, `holds_blocked: false`, `blocked_true: true` |
| Bảng 14 ca | 14/14, cả 11 ca in-scope đều `SAT`, 0 `TIMEOUT`, 0 `ERR` |
| `smoke_timed_out` | mọi giá trị `false` |

### 5.5 Thay đổi kèm theo trong `src/eval_benchmark.py`

- `scasp_query()` bắt `subprocess.TimeoutExpired` → trả `satisfiable: None`, `timed_out: True`.
- Lỗi engine (`SCASP_ERROR`) cũng trả `satisfiable: None` kèm `error`, để một lần lỗi tạm thời
  không bị đọc thành "không có model".
- `write_markdown()` chỉ ghi **"no model (blocked)"** khi `satisfiable is False`; timeout hiện
  "timeout (undecided)", lỗi engine hiện `ERR`.
- JSON có thêm khoá `smoke_timed_out`.

### 5.6 Đường dẫn A2/A3/A6 và drift Chương (25/11)

Cùng một lỗi đặt tên như 5.2 còn ở ba mô-đun legacy (`src/edges.py`, `src/exceptions.py`,
`src/general_exceptions.py`). Đã sửa:

| Mô-đun | Trước | Sau |
|---|---|---|
| `edges.triples_path` | `a1/a1_<stem>.jsonl` (đã sửa 25/11) | `a1/a1_triples_<stem>.jsonl` |
| `edges.edges_path` | `a2/a2_<stem>.jsonl` | `a2/a2_edges_<stem>.jsonl` |
| `edges.refs_path` | `data/processed/a2_refs_<stem>.jsonl` (phẳng) | `a2/a2_refs_<stem>.jsonl` |
| `edges.unresolved_path` | `docs/a2_unresolved_<stem>.txt` | `docs/bao_cao_chay/a2/a2_unresolved_<stem>.txt` |
| `exceptions.exceptions_path` / `unhandled_path` | phẳng `data/processed/a3_*`, `docs/a3_*` | `a3/a3_exceptions_<stem>.jsonl`, `docs/bao_cao_chay/a3/…` |
| `general_exceptions.conditions_path` / `exceptions_path` / `unhandled_path` | phẳng `data/processed/a6_*`, `docs/a6_*` | `a6/a6_conditions_*`, `a6/a6_exceptions_*`, `docs/bao_cao_chay/a6/…` |

`edges_path(..., for_write=True)` trả đúng vị trí ghi chuẩn, nên `python -I src/edges.py <md>` không
còn ghi `a2/a2_<stem>.jsonl` (tên mà không reader nào đọc). Đường đọc vẫn có fallback
`a2/a2_<stem>.jsonl` và bản phẳng cho artifact cũ.

**Drift Chương.** `src/edges.py` (bản legacy mà `tests/test_edges.py` và `tests/test_a2.py` cùng
import) chưa biết `chuong`, trong khi `src/a2_edges.py` đã dựng cạnh Chương → Điều từ 24/11. Vì
vậy sau khi trỏ đúng file, `check_edges` báo 4 Chương "có 0 cha" và số cạnh lệch (322 so với 430).
Đã sửa bằng cách cho `edges.py` dùng chung `CHUONG`, `KEPT_ATTRS`, `build_edges`, `check_edges`
với `a2_edges` (kèm `sys.path.insert` để `python -I src/edges.py` import được), thay vì giữ bản
sao thứ hai. Hệ quả số liệu, đã đối chiếu độc lập với md và dòng `type` của A1:

- `blds2015_p4`: 4 Chương, 54 Điều, 115 Khoản, 46 Điểm (219 đơn vị trong A1). Cạnh = 2 × (54 + 115 + 46) = **430**; mỗi loại **215**.
- `blds2015_5dieu`: không có Chương, 5 Điều, 14 Khoản, 16 Điểm; cạnh = 2 × 30 = **60**.

Hai file test sinh đôi (`tests/test_edges.py`, `tests/test_a2.py`) được cập nhật theo: `REFERENCE`
161 → 215, `REFERENCE_TOTAL` 322 → 430, và các assert về cha/nhánh `part_of`/thứ tự cạnh nay coi
Chương là gốc, Điều là con của Chương khi văn bản có Chương. Sửa thêm một lỗi chính tả trong
`tests/test_a3.py` / `tests/test_exceptions.py`: `test_files_on_disk` so danh sách dòng với **mô-đun**
`edges` thay vì `edge_list`, nên test này không thể xanh dù artifact đúng.

Kết quả đo sau khi sửa: `tests/test_edges.py` + `tests/test_a2.py` **80 pass**;
`tests/test_a3.py` + `tests/test_exceptions.py` **38 pass**; `tests/test_inference.py` **8 pass**.
Toàn bộ `tests/`: **358 pass / 140 fail** (trước đợt sửa này: 340 pass / 158 fail). Hai test
`test_a6.py::test_files_on_disk` và `test_general_exceptions.py::test_files_on_disk` vẫn đỏ vì
`a6_general_exceptions.py` đã tiến hoá thêm `kind` (tuy_nghi | dan_chieu_mo | cu_the) và cạnh
`general_except_ref` — file chuẩn có 15 dòng điều kiện / 10 cạnh, bản legacy mới sinh 10 dòng / 9
cạnh. Đây là drift hành vi, không phải đường dẫn; muốn xanh phải port `condition_kind` và
`clause_targets` sang `general_exceptions.py` (chưa làm trong đợt này).

---

## 6. Đối chiếu `paper/proposal.tex` với số liệu thực tế

| Nội dung trong paper | Số liệu thực tế | Trạng thái |
|---|---|---|
| "parses to 45 units and 226 triples" | A1/A5: 45 đơn vị, 226 cặp `(s, p)` | khớp |
| "8 nested `exception_of` edges" | A7 + A6: **10** cạnh `exception_of` | **đã sửa thành 10** |
| "7 condition nodes" | A7: 7 nút `dieu_kien` (A6 sinh 21 dòng điều kiện) | khớp ở mức nút |
| "19 `refers_to` edges" | 19 **cụm** dẫn chiếu được phát hiện, **0 cạnh** được ghi; `a2_unresolved_…` rỗng | **đã sửa**: nêu rõ là cụm, không phải cạnh |
| "$14/14 = 100\%$, $8/8$ tại $d{=}1$, $3/3$ tại $d{=}2$, $2/2$ tại $d{=}3$" | khớp `labor_ablation_v3.json` | **đã thêm câu** nói rõ đây là trần `predict_verdict()` |
| "`holds/1` is defeated by negation-as-failure on `exception_of`" | nay có bằng chứng: `holds('LLD2019.D35.K2.e')` → `no`, `blocked(...)` → `yes` | **đã cập nhật** theo `has_exception/1` |
| "0 errors across all five families" | S_scan 5 họ lỗi đều 0 | khớp |

Ba điểm cần sửa trong `src/eval_benchmark.py` (mục 5.5) đã xong: bắt `TimeoutExpired`, tách
`SCASP_ERROR` khỏi "không có model", và chỉ ghi "blocked" khi `satisfiable is False`.

---

## 7. Việc cần làm tiếp (theo thứ tự ưu tiên)

1. **Commit các thay đổi** (`src/inference.py`, `src/eval_benchmark.py`, `src/edges.py`,
   `src/exceptions.py`, `src/general_exceptions.py`, `src/law_registry.py`, `src/a1_parse.py`,
   `src/a7_graph.py`, `tests/test_edges.py`, `tests/test_a2.py`, `tests/test_a3.py`,
   `tests/test_exceptions.py`, `tests/test_inference.py`, `paper/proposal.tex`, báo cáo này).
   Gợi ý tách ba commit: phân giải đường dẫn A1/A2/A3/A6 + tách `has_exception/1`; xử lý
   timeout/`SCASP_ERROR`; đồng bộ số liệu paper, văn bản gốc theo luật và test Chương.
2. **A6 legacy còn lệch hành vi (đã xác định, chưa sửa)**: `general_exceptions.py` chưa sinh
   `kind` và cạnh `general_except_ref`, nên `tests/test_a6.py` / `tests/test_general_exceptions.py`
   `::test_files_on_disk` vẫn đỏ dù đường dẫn đã đúng. Port `condition_kind` + `clause_targets`
   từ `a6_general_exceptions.py`, hoặc tuyên bố mô-đun legacy ngừng hỗ trợ và trỏ test sang bản mới.
3. **A2b với danh sách điểm liệt kê**: hiện dừng ở `LLD2019.D36.K2` nên 19 cụm chưa thành cạnh.
   Hoặc mở rộng ngữ pháp, hoặc giữ 0 cạnh và nêu rõ giới hạn (paper đã nêu).
4. **Thí nghiệm 80 ca**: bổ sung gold + chạy đủ 80 câu cho 4 arm rồi mới công bố, hoặc bỏ hẳn.
5. **Bộ kiểm thử hiện tại**: `python3 -m pytest tests/ -q` → **358 pass / 140 fail** (trước đợt
   sửa đường dẫn A2/A3: 340 pass / 158 fail). Toàn bộ 16 lỗi `test_edges`/`test_a2` và 2 lỗi
   `test_a3`/`test_exceptions` đã xanh; 2 lỗi A6 là drift hành vi ở mục 2. 44 lỗi `test_versioning`
   + 44 lỗi `test_a4` vẫn là `A4Error`/`FileNotFoundError` của các snapshot A4 không có trên đĩa;
   38 lỗi `test_a7`/`test_graph` là artifact đồ thị cũ (chapter + `kind`) so với bản legacy.
6. **Chốt việc có track `paper/proposal.pdf`** hay không (hiện đang untracked).

---

## 8. Cách tái lập

```bash
# 1. A1 → triples (đọc lại luật, cấp tiền tố theo law_registry)
python3 src/a1_parse.py data/raw/lld2019_labor.md

# 2. Biên dịch chương trình s(CASP); kỳ vọng 10 exception_of + 8 has_exception
python3 src/inference.py data/raw/lld2019_labor.md
grep -c '^exception_of('  data/processed/a9_lld2019_labor.pl   # 10
grep -c '^has_exception('  data/processed/a9_lld2019_labor.pl   # 8

# 3. Truy vấn trực tiếp — đường dẫn văn bản là tham số vị trí
python3 src/inference.py data/raw/lld2019_labor.md --query "holds('LLD2019.D35.K2.e')"   # ANSWER: no
python3 src/inference.py data/raw/lld2019_labor.md --query "blocked('LLD2019.D35.K2.e')"  # ANSWER: yes

# 4. Chạy lại benchmark 14 ca (khoảng 1 phút vì mỗi ca một tiến trình swipl)
python3 src/eval_benchmark.py \
    --src data/raw/lld2019_labor.md \
    --eval data/labor/eval_nested_exceptions.jsonl \
    --program data/processed/a9_lld2019_labor.pl \
    --out results/labor_ablation_v3.json \
    --md  results/labor_ablation_v3.md

# 5. Kiểm thử
python3 -m pytest tests/test_inference.py -q                 # 8 pass
python3 -m pytest tests/test_edges.py tests/test_a2.py -q     # 80 pass (A2, Chương-aware)
python3 -m pytest tests/test_a3.py tests/test_exceptions.py -q  # 38 pass
python3 -m pytest tests/ -q                                   # 358 pass / 140 fail (xem mục 7)
```

Lưu ý:

- `grep -c '^exception_of('` phải trả **10**. Nếu trả **0**, đó là bản `inference.py` cũ (lỗi 5.1)
  và mọi kết luận về "blocking" đều không hợp lệ.
- `src/a2_edges.py data/raw/lld2019_labor.md --refers-to` hiện **dừng có báo lỗi** ở
  `LLD2019.D36.K2` (danh sách điểm liệt kê), nên `a2_refs_lld2019_labor.jsonl` rỗng. Đó là hành
  vi fail-closed đã biết, không phải lỗi của bước 1–4.
- `python -I src/edges.py data/raw/blds2015_p4.md` phải in **219 đơn vị / 430 cạnh**
  (`contains` 215, `part_of` 215) và ghi `data/processed/a2/a2_edges_blds2015_p4.jsonl`;
  đây là đối chứng CLI cho mục 5.6.
- Bước 1–4 ghi đè `data/processed/**` và `docs/bao_cao_chay/**`.

