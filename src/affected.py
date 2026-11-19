"""Bước 2.5: tập ảnh hưởng A(e) = T(e) ∪ N(T(e)) ở từng mốc e của kho phiên bản (A42; method.md mục 3.4, Thuật toán 1 dòng 6).

T(e): đơn vị có KU mở hoặc đóng tại e (phiên bản mới, phiên bản hết hiệu lực, đơn vị chèn, đơn vị của văn bản vừa nạp, câu dẫn của cha
đổi), cộng hai đầu của cạnh `overrides` bắt đầu hoặc hết hạn tại e.
N(S): đơn vị nối với S bằng MỘT bước (số bước chốt 19/11, A42) qua các quan hệ dưới đây; mọi phép khớp theo cây (`knowledge_units.rel`:
cạnh tới Điều nối mọi Khoản, Điểm của Điều; cạnh `details` có đầu là văn bản nối mọi đơn vị của văn bản):
  refers_to (1.2) | exception_of (1.5; con trỏ ngoại lệ của 1.6A; 1.7 đã nhận) | details (2.2) | overrides (2.3-2.4) |
  concept: hai đơn vị cùng dùng một vị từ `concept` (theo loại tại e hoặc mốc trước), gồm cả đơn vị định nghĩa nó |
  cây [THÊM]: tổ tiên và con cháu cùng Điều (1.8 gắn điều kiện của mục con vào kết luận của tổ tiên, nên thêm hay bớt một mục con đổi quy
  tắc của tổ tiên; method.md không liệt kê quan hệ cấu trúc).
Bước 2.7 kiểm tập này có đủ không (chạy tăng dần với A(e) và dựng lại toàn bộ phải ra cùng Π_τ) và đo phần nào của N là cần (bỏ từng quan hệ).

Thư viện: `affected_at` dùng ở update.py; chạy riêng thì in báo cáo.
"""
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus  # noqa: E402
import knowledge_units as ku_lib  # noqa: E402

DIR_NAME = "affected"
RELATIONS = ("refers_to", "exception_of", "details", "overrides", "concept", "cay")


def touched(kn, i):
    """T(mốc i): {uid: lý do}."""
    cat, e = kn.catalog, kn.catalog.epochs[i]
    opened, closed = cat.changed_at(i)
    out = {}
    for k in opened:
        out.setdefault(cat.kus[k]["unit"], set()).add("ku_mo")
    for k in closed:
        out.setdefault(cat.kus[k]["unit"], set()).add("ku_dong")
    for ov in kn.store.overrides:
        if e in (ov["valid_from"], ov["valid_to"]):
            for x in (ov["s"], ov["o"]):
                out.setdefault(x, set()).add("overrides")
    return out


def _edge_hits(T, edges, universe):
    """Đơn vị của `universe` nối một bước với T qua danh sách cạnh (hai chiều, khớp theo cây)."""
    hit = set()
    for s, o in edges:
        for x, y in ((s, o), (o, s)):
            if any(ku_lib.rel(t, x) for t in T):
                hit |= {u for u in universe if ku_lib.rel(u, y)}
    return hit


def affected_at(kn, i, edges17, use=RELATIONS):
    """-> (T {uid: lý do}, {quan hệ: tập uid của N}, A). edges17: cạnh 1.7 (s, o) đã nhận đang dùng ở mốc này (người gọi tính).
    `use`: các quan hệ của N (2.7 bỏ bớt để đo phần nào cần)."""
    cat = kn.catalog
    e = cat.epochs[i]
    T = touched(kn, i)
    tset = set(T)
    live_now = kn.live(e)
    live_prev = kn.live(cat.epochs[i - 1]) if i else {}
    universe = set(kn.store.by_uid)
    N = {}
    if "refers_to" in use:
        N["refers_to"] = _edge_hits(tset, kn.refs, universe)
    if "exception_of" in use:
        con_tro = set()
        for live in (live_now, live_prev):
            for uid, ku in live.items():
                for r in kn.rows(ku):
                    if r["loai"] == "con_tro" and r["role"] == "ngoai_le":
                        con_tro |= {(t, uid) for t in r["targets"]}
        N["exception_of"] = _edge_hits(tset, sorted(kn.exc15_unit_edges() | con_tro | set(edges17)), universe)
    if "details" in use:
        N["details"] = _edge_hits(tset, kn.details, universe)
    if "overrides" in use:
        ov = [(x["s"], x["o"]) for x in kn.store.overrides_at(e)]
        if i:
            ov += [(x["s"], x["o"]) for x in kn.store.overrides_at(cat.epochs[i - 1])]
        N["overrides"] = _edge_hits(tset, ov, universe)
    if "concept" in use:
        concepts = set()
        for live in (live_now, live_prev):
            kinds, _eff = kn.kinds(live)
            for uid, ku in live.items():
                if uid in tset:
                    concepts |= {p for p in kn.uses(ku) if kinds.get(p) == "concept"}
        # đơn vị trong T mà KU đã đóng: lấy vị từ của KU cũ (ở mốc trước)
        hit = set()
        for live in (live_now, live_prev):
            for uid, ku in live.items():
                if kn.uses(ku) & concepts:
                    hit.add(uid)
        N["concept"] = hit
    if "cay" in use:
        hit = set()
        for u in universe:
            if any(ku_lib.dieu_of(u) == ku_lib.dieu_of(t) and ku_lib.rel(u, t) for t in tset if t.count(".") >= 1):
                hit.add(u)
        N["cay"] = hit
    A = set(tset)
    for s in N.values():
        A |= s
    return T, N, A


def report_lines(kn, rows):
    lines = [f"2.5 tập ảnh hưởng A(e) = T(e) ∪ N(T(e)), N một bước qua {', '.join(RELATIONS)}" + (f" (kho con {corpus.SUBSET})" if corpus.SUBSET else "")]
    for r in rows:
        lines.append(f"mốc {r['epoch']} ({', '.join(r['source'])}): |T| {len(r['T'])}, |A| {len(r['A'])}; N theo quan hệ: "
                     + ", ".join(f"{k} {len(v)}" for k, v in r["N"].items()))
        reasons = collections.Counter(x for v in r["T"].values() for x in v)
        lines.append(f"    T theo lý do: {dict(sorted(reasons.items()))}")
    return lines
