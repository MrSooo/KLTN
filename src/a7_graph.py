"""A7: đồ thị gộp (nodes + edges jsonl) từ A1-A3, A6 hoặc từ kết quả A4 tại một ngày; khử trùng lặp, gắn nhãn cô lập, kiểm tra.

Trạng thái gốc: python -I src/a7_graph.py <file md nguồn>
  Đọc a1_triples, a2_edges, a2_refs, a3_exceptions, a6_conditions, a6_exceptions của stem. Ghi data/processed/a7_<stem>_{nodes,edges}.jsonl
  và docs/a7_report_<stem>.txt.
Tại một ngày: python -I src/a7_graph.py <file md nguồn> --versions data/processed/a4_<name>_versions.jsonl --date YYYY-MM-DD
  Nút là đơn vị đang hiệu lực tại T (a4.active_rows). Cạnh là cạnh gốc cộng add trừ close của a4_<name>_edge_changes.jsonl có at <= T,
  rồi lọc theo hiệu lực. Nút điều kiện và cạnh ngoại lệ chung tính lại bằng a6.find_general trên text đang hiệu lực. Ghi
  a7_<stem>_<name>_<date>_{nodes,edges}.jsonl và docs/a7_report_<stem>_<name>_<date>.txt. md phải là văn bản gốc của bộ A4 đó.

Việc làm:
  Gộp bộ ba: cạnh cùng (s, p, o) từ các file thành một cạnh (giữ dòng đầu, sources liệt kê nơi xuất hiện, evidences khi gộp).
  Bản sao text: đơn vị có text giống hệt (cùng type, a6.norm_text) với một đơn vị đứng trước: nút status "duplicate" và cạnh
    same_text_as (bản sau -> canonical = đơn vị đứng đầu nhóm). Không gộp nút: mỗi đơn vị là một vị trí pháp lý có cha riêng.
  Cạnh treo (chỉ có khi nạp A4): refers_to / exception_of có nguồn còn hiệu lực mà đích không còn: giữ, status "dangling".
    Cạnh có nguồn đã đóng, hoặc contains/part_of có một đầu đã đóng, không thuộc đồ thị tại T nên bị bỏ (báo cáo ghi số lượng).
Báo cáo ghi cả khi có lỗi; file dữ liệu chỉ ghi khi mọi kiểm tra đạt. Thoát 1 nếu có kiểm tra không đạt hoặc đầu vào lỗi.
Mọi quyết định chỗ spec chưa nói nằm trong docs/a6_a7_quyet_dinh.txt.
"""
import argparse
import collections
import json
import sys
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import a2_edges as a2
import a3_exceptions as a3
import a4_versions as a4
import a5_checks as a5
import a6_general_exceptions as a6

OUT_DIR = a2.PROCESSED_DIR  # test đổi sang thư mục tạm
DOCS_DIR = a2.ROOT / "docs"

OK, DUPLICATE, DANGLING = "ok", "duplicate", "dangling"
NODE_STATUS = (OK, DUPLICATE)
EDGE_STATUS = (OK, DANGLING)
SAME_TEXT = "same_text_as"
SAME_METHOD = "exact_text"
STRUCTURAL = ("contains", "part_of")  # cạnh cấu trúc: bỏ khi một đầu đã đóng; mọi p khác là cạnh ngữ nghĩa
BASE_SOURCES = ("a2_edges", "a2_refs", "a3_exceptions")        # nguồn cạnh gốc, chung cho cả hai chế độ
FULL_SOURCES = BASE_SOURCES + ("a6_exceptions",)                # trạng thái gốc thêm cạnh ngoại lệ chung của A6
CHANGE_KEYS = ("op", "s", "p", "o", "at")                       # khoá bắt buộc của a4_<name>_edge_changes.jsonl


class Expect(NamedTuple):
    nodes: int
    edges: int
    duplicates: int


# Số kỳ vọng của trạng thái gốc. p4: 215 đơn vị + 5 nút điều kiện; 322 (A2a) + 25 (A2b) + 4 (A3) + 9 + 1 (A6) + 4 same_text_as.
# Mẫu: 35 đơn vị; 60 + 3 + 1. Đã đối chiếu độc lập ở test_a7 (cộng số dòng của các file nguồn).
EXPECTED = {
    "blds2015_5dieu": Expect(nodes=35, edges=64, duplicates=0),
    "blds2015_p4": Expect(nodes=220, edges=365, duplicates=4),
}


def node(code, type_, number=None, heading=None, text=None, source_line=None, kind=None):
    """Dòng nút. kind chỉ có ở nút điều kiện (a6.condition_kind) nên chỉ thêm khoá khi có giá trị."""
    out = {"id": code, "type": type_, "number": number, "heading": heading, "text": text, "source_line": source_line, "status": OK}
    return {**out, "kind": kind} if kind else out


class EdgeSet:
    """Cạnh theo (s, p, o), giữ thứ tự xuất hiện đầu tiên; cạnh xuất hiện lại thì gộp vào cạnh đã có."""

    def __init__(self):
        self.edges = {}  # (s, p, o) -> dòng cạnh
        self.seen = {}   # (s, p, o) -> [evidence khác nhau, khác rỗng]

    def add(self, label, r):
        key = (r["s"], r["p"], r["o"])
        evidence = r.get("evidence") or ""
        if key not in self.edges:
            self.edges[key] = {"s": key[0], "p": key[1], "o": key[2], "evidence": evidence, "method": r.get("method"),
                               "status": OK, "sources": [label]}
            self.seen[key] = [evidence] if evidence else []
            return
        self.edges[key]["sources"].append(label)
        if evidence and evidence not in self.seen[key]:
            self.seen[key].append(evidence)

    def remove(self, key):
        del self.edges[key]
        del self.seen[key]

    def rows(self):
        return [{**e, "evidences": self.seen[key]} if len(e["sources"]) > 1 else e for key, e in self.edges.items()]

    def merged(self):
        """[(s, p, o, số lần xuất hiện)] của các bộ ba bị gộp."""
        return [(*key, len(e["sources"])) for key, e in self.edges.items() if len(e["sources"]) > 1]


class Graph(NamedTuple):
    nodes: list    # list[dict]
    edges: list    # list[dict], mỗi (s, p, o) một dòng
    merged: list   # [(s, p, o, số lần)] bộ ba đã gộp
    notes: dict    # thống kê thêm cho báo cáo (chế độ theo ngày)


def mark_duplicates(nodes):
    """Gán status duplicate cho đơn vị có text giống hệt (cùng type, a6.norm_text) một đơn vị đứng trước.

    Trả về [(bản sau, canonical)] theo thứ tự nút; canonical là đơn vị đầu nhóm theo thứ tự nút. Đơn vị không có text bị bỏ qua,
    nút điều kiện không tham gia (đã gộp theo khoá khi sinh ra).
    """
    first, pairs = {}, []
    for n in nodes:
        if n["type"] not in a5.TYPES or not n["text"]:
            continue
        canonical = first.setdefault((n["type"], a6.norm_text(n["text"])), n["id"])
        if canonical != n["id"]:
            n["status"] = DUPLICATE
            pairs.append((n["id"], canonical))
    return pairs


def assemble(units, conditions, edge_set, notes):
    """Nút (đơn vị rồi nút điều kiện), đánh dấu bản sao và thêm cạnh same_text_as vào edge_set, trả về Graph."""
    nodes = units + conditions
    for dup, canonical in mark_duplicates(nodes):
        edge_set.add("a7", {"s": dup, "p": SAME_TEXT, "o": canonical, "evidence": "", "method": SAME_METHOD})
    return Graph(nodes, edge_set.rows(), edge_set.merged(), notes)


# ---- nạp đầu vào ----

def unit_nodes(triple_rows):
    """Nút đơn vị từ dòng a1_triples: gom theo s, giữ dòng đầu của mỗi (s, p), theo thứ tự xuất hiện của s."""
    attrs = {}
    for _, r in triple_rows:
        attrs.setdefault(r["s"], {}).setdefault(r["p"], r["o"])
    out = []
    for code, a in attrs.items():
        if "type" not in a:
            raise ValueError(f"{code}: không có dòng type trong a1_triples")
        out.append(node(code, a["type"], a.get("number"), a.get("heading"), a.get("text"), a.get("source_line")))
    return out


def condition_nodes(triple_rows):
    """Nút điều kiện từ a6_conditions (bộ ba type, text, kind theo từng s)."""
    attrs = {}
    for _, r in triple_rows:
        attrs.setdefault(r["s"], {}).setdefault(r["p"], r["o"])
    out = []
    for code, a in attrs.items():
        if "type" not in a or "text" not in a or "kind" not in a:
            raise ValueError(f"{code}: nút điều kiện thiếu type, text hoặc kind")
        out.append(node(code, a["type"], text=a["text"], kind=a["kind"]))
    return out


def source_paths(src):
    return {"a1_triples": a2.triples_path(src), "a2_edges": a2.edges_path(src), "a2_refs": a2.refs_path(src),
            "a3_exceptions": a3.exceptions_path(src), "a6_conditions": a6.conditions_path(src), "a6_exceptions": a6.exceptions_path(src)}


def graph_base(src):
    """Trạng thái gốc: (Graph, {nhãn: đường dẫn file đã đọc})."""
    paths = source_paths(src)
    rows = {name: a5.load_rows(p) for name, p in paths.items()}
    edge_set = EdgeSet()
    for label in FULL_SOURCES:
        for _, r in rows[label]:
            edge_set.add(label, r)
    return assemble(unit_nodes(rows["a1_triples"]), condition_nodes(rows["a6_conditions"]), edge_set, {}), paths


def edge_changes_path(versions):
    """a4_<name>_versions.jsonl -> a4_<name>_edge_changes.jsonl cùng thư mục; tên file không đúng dạng thì ValueError."""
    name = a5.versions_name(versions)
    if Path(versions).stem != f"a4_{name}_versions":
        raise ValueError(f"tên file versions phải có dạng a4_<name>_versions.jsonl: {versions}")
    return Path(versions).parent / f"a4_{name}_edge_changes.jsonl"


def graph_at(src, versions, date):
    """Đồ thị tại ngày date (YYYY-MM-DD): (Graph, {nhãn: đường dẫn file đã đọc})."""
    paths = {k: v for k, v in source_paths(src).items() if k in ("a1_triples",) + BASE_SOURCES}
    paths["a4_versions"] = Path(versions)
    paths["a4_edge_changes"] = edge_changes_path(versions)
    version_rows = a4.read_jsonl(versions)
    rows = {name: a5.load_rows(p) for name, p in paths.items() if name not in ("a4_versions", "a4_edge_changes")}
    rows["a4_edge_changes"] = a5.load_rows(paths["a4_edge_changes"], CHANGE_KEYS)
    all_ids = {r["id"] for r in version_rows}
    stray = sorted({r["s"] for _, r in rows["a1_triples"]} - all_ids)
    if stray:
        raise ValueError(f"{versions} không phải của {Path(src).stem}: mã A1 không có trong versions, ví dụ {stray[:3]}")

    active = a4.active_rows(version_rows, date)
    units = []
    for r in active:
        n = node(r["id"], r["type"], r["number"], r["heading"], r["text"])
        n["version"], n["effective_from"] = r["version"], r["effective_from"]
        units.append(n)
    active_ids = {n["id"] for n in units}

    edge_set = EdgeSet()
    for label in BASE_SOURCES:
        for _, r in rows[label]:
            edge_set.add(label, r)
    applied = collections.Counter()
    for line_no, r in rows["a4_edge_changes"]:
        if r["at"] > date:
            continue
        key = (r["s"], r["p"], r["o"])
        if r["op"] == "add":
            edge_set.add("a4_edge_changes", r)
        elif r["op"] == "close":
            if key not in edge_set.edges:
                raise ValueError(f"{paths['a4_edge_changes']}:{line_no}: close một cạnh không có: {key}")
            edge_set.remove(key)
        else:
            raise ValueError(f"{paths['a4_edge_changes']}:{line_no}: op {r['op']!r} không phải add/close")
        applied[r["op"]] += 1

    dropped = collections.Counter()
    dangling = []
    for key in list(edge_set.edges):
        s, p, o = key
        if p in STRUCTURAL:
            if s not in active_ids or o not in active_ids:
                edge_set.remove(key)
                dropped["structural"] += 1
        elif s not in active_ids:
            edge_set.remove(key)
            dropped["source_closed"] += 1
        elif o not in active_ids:
            edge_set.edges[key]["status"] = DANGLING
            dangling.append(key)

    view = {n["id"]: {"type": n["type"], "number": n["number"], "source_line": 0, **({"text": n["text"]} if n["text"] else {})}
            for n in units}
    general = a6.find_general(view)  # ValueError nếu text mới có hai "trừ trường hợp": lỗi của dữ liệu, không đoán
    conditions = [node(c, a6.COND_TYPE, text=clause, kind=a6.condition_kind(clause)) for c, clause in general.nodes]
    for s, p, o, evidence, method in general.edges + general.ref_edges:
        edge_set.add("a6_exceptions", {"s": s, "p": p, "o": o, "evidence": evidence, "method": method})
    notes = {"date": date, "version_rows": len(version_rows), "active": len(units), "applied": dict(applied),
             "dropped": dict(dropped), "dangling": dangling}
    return assemble(units, conditions, edge_set, notes), paths


# ---- kiểm tra ----

def find_cycle(edges, p):
    """Một vòng [a, b, ..., a] trong các cạnh có predicate p (duyệt theo thứ tự cạnh), hoặc None. DFS lặp, không đệ quy."""
    succ = collections.defaultdict(list)
    for e in edges:
        if e["p"] == p:
            succ[e["s"]].append(e["o"])
    state = {}  # 1 đang trên đường đi, 2 đã xong
    for root in list(succ):
        if root in state:
            continue
        state[root], stack, path = 1, [iter(succ[root])], [root]
        while stack:
            v = next(stack[-1], None)
            if v is None:
                state[path.pop()] = 2
                stack.pop()
            elif state.get(v) == 1:
                return path[path.index(v):] + [v]
            elif v not in state:
                state[v] = 1
                stack.append(iter(succ.get(v, [])))
                path.append(v)
    return None


def check_graph(graph, expect=None):
    """Các Check 7a-7g trên Graph. expect (Expect) chỉ có ở trạng thái gốc; không có thì bỏ qua 7f."""
    nodes, edges = graph.nodes, graph.edges
    by_id = {n["id"]: n for n in nodes}

    ids = collections.Counter(n["id"] for n in nodes)
    p_a = [f"mã nút {i} lặp {c} lần" for i, c in ids.items() if c > 1]
    p_a += [f"{n['id']}: status {n['status']!r} không thuộc {NODE_STATUS}" for n in nodes if n["status"] not in NODE_STATUS]

    p_b = []
    for e in edges:
        s, o = e["s"], e["o"]
        if e["status"] not in EDGE_STATUS:
            p_b.append(f"{s} {e['p']} {o}: status {e['status']!r} không thuộc {EDGE_STATUS}")
        elif e["status"] == OK:
            p_b += [f"{s} {e['p']} {o}: {x} không phải nút" for x in (s, o) if x not in by_id]
        elif s not in by_id or o in by_id:
            p_b.append(f"{s} {e['p']} {o}: cạnh treo phải có nguồn là nút và đích không phải nút")

    p_c = [f"({s}, {p}, {o}) lặp {c} lần" for (s, p, o), c in collections.Counter((e["s"], e["p"], e["o"]) for e in edges).items() if c > 1]

    # 7d: dựng lại nhóm bản sao từ chính các nút, đối chiếu status và cạnh same_text_as
    p_d, first, expected = [], {}, {}
    for n in nodes:
        if n["type"] in a5.TYPES and n["text"]:
            canonical = first.setdefault((n["type"], a6.norm_text(n["text"])), n["id"])
            if canonical != n["id"]:
                expected[n["id"]] = canonical
    out_edges = collections.defaultdict(list)
    for e in edges:
        if e["p"] == SAME_TEXT:
            out_edges[e["s"]].append(e)
    for dup, canonical in expected.items():
        got = [e["o"] for e in out_edges.get(dup, [])]
        if by_id[dup]["status"] != DUPLICATE:
            p_d.append(f"{dup}: text giống {canonical} nhưng status {by_id[dup]['status']!r}")
        if got != [canonical]:
            p_d.append(f"{dup}: same_text_as tới {got}, cần [{canonical!r}]")
    for s in out_edges:
        if s not in expected:
            p_d.append(f"{s}: có same_text_as nhưng không phải bản sau của nhóm text giống hệt")
    for n in nodes:
        if n["status"] == DUPLICATE and n["id"] not in expected:
            p_d.append(f"{n['id']}: status duplicate nhưng không có đơn vị đứng trước cùng text")

    # 7e: mỗi Khoản/Điểm đúng một part_of (ok) tới cha là mã bỏ đoạn cuối và đúng bậc; contains đối xứng; Điều không có part_of
    p_e = []
    part_of = collections.defaultdict(list)
    for e in edges:
        if e["p"] == "part_of" and e["status"] == OK:
            part_of[e["s"]].append(e["o"])
    for n in nodes:
        if n["type"] not in a5.TYPES:
            continue
        parents = part_of.get(n["id"], [])
        if n["type"] == "dieu":
            if parents:
                p_e.append(f"{n['id']}: là Điều nhưng có part_of tới {parents}")
            continue
        want = n["id"].rsplit(".", 1)[0]
        if parents != [want]:
            p_e.append(f"{n['id']}: part_of tới {parents}, cần [{want!r}]")
        elif want not in by_id:
            p_e.append(f"{n['id']}: cha {want} không phải nút")
        elif by_id[want]["type"] != a5.PARENT_TYPE[n["type"]]:
            p_e.append(f"{n['id']}: cha {want} là {by_id[want]['type']}, cần {a5.PARENT_TYPE[n['type']]}")
    contains = {(e["s"], e["o"]) for e in edges if e["p"] == "contains" and e["status"] == OK}
    reverse = {(e["o"], e["s"]) for e in edges if e["p"] == "part_of" and e["status"] == OK}
    p_e += [f"contains {a} → {b} không có part_of ngược" for a, b in sorted(contains - reverse)]
    p_e += [f"part_of {b} → {a} không có contains ngược" for a, b in sorted(reverse - contains)]

    n_dup = sum(1 for n in nodes if n["status"] == DUPLICATE)
    checks = [
        a5.Check("7a", "mã nút duy nhất, status nút hợp lệ", f"{len(nodes)} nút", p_a),
        a5.Check("7b", "cạnh ok có đủ hai đầu, cạnh treo có nguồn là nút và đích không phải nút", f"{len(edges)} cạnh", p_b),
        a5.Check("7c", "không còn bộ ba (s, p, o) lặp", f"{len(edges)} cạnh, {len(graph.merged)} bộ ba đã gộp khi dựng", p_c),
        a5.Check("7d", "nút bản sao: đúng một same_text_as tới đơn vị đầu nhóm", f"{n_dup} nút duplicate", p_d),
        a5.Check("7e", "mỗi Khoản/Điểm đúng một part_of tới cha đúng bậc, contains đối xứng", f"{len(contains)} cặp contains", p_e),
    ]
    if expect is not None:
        n_edges = len(edges)
        p_f = [f"có {got} {what}, cần {want}" for what, got, want in
               (("nút", len(nodes), expect.nodes), ("cạnh", n_edges, expect.edges), ("nút duplicate", n_dup, expect.duplicates))
               if got != want]
        checks.append(a5.Check("7f", "số nút, cạnh, nút bản sao khớp bảng EXPECTED",
                               f"nút {len(nodes)}/{expect.nodes}, cạnh {n_edges}/{expect.edges}, duplicate {n_dup}/{expect.duplicates}", p_f))

    # 7g: A là ngoại lệ của B và B (bắc cầu) là ngoại lệ của A là mâu thuẫn. Vòng refers_to (hai đơn vị dẫn chiếu qua lại) và vòng
    # trộn refers_to với exception_of (quy tắc dẫn chiếu tới ngoại lệ của chính nó) là hợp lệ: chỉ ghi, không tính lỗi.
    cycle = find_cycle(edges, a3.PREDICATE)
    ref_cycle = find_cycle(edges, "refers_to")
    checks.append(a5.Check("7g", "không có vòng exception_of",
                           f"{sum(e['p'] == a3.PREDICATE for e in edges)} cạnh exception_of; vòng refers_to (chỉ ghi): "
                           + (" → ".join(ref_cycle) if ref_cycle else "không có"),
                           [f"vòng exception_of: {' → '.join(cycle)}"] if cycle else []))
    return checks


# ---- báo cáo, ghi file ----

def components(nodes, edges, skip=()):
    """Số thành phần liên thông (vô hướng) trên các nút không thuộc skip, chỉ dùng cạnh có hai đầu là nút đó."""
    parent = {n["id"]: n["id"] for n in nodes if n["id"] not in skip}

    def root(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for e in edges:
        if e["s"] in parent and e["o"] in parent:
            parent[root(e["s"])] = root(e["o"])
    return len({root(x) for x in parent})


def boilerplate(nodes):
    """Mã nút điều kiện chung chung (a6.BOILERPLATE_KINDS): không coi là cầu nối khi xét liên thông."""
    return {n["id"] for n in nodes if n.get("kind") in a6.BOILERPLATE_KINDS}

def tag_of(versions, date):
    return f"{a5.versions_name(versions)}_{date}"


def nodes_path(stem, tag=None):
    return OUT_DIR / (f"a7_{stem}_{tag}_nodes.jsonl" if tag else f"a7_{stem}_nodes.jsonl")


def edges_path(stem, tag=None):
    return OUT_DIR / (f"a7_{stem}_{tag}_edges.jsonl" if tag else f"a7_{stem}_edges.jsonl")


def report_path(stem, tag=None):
    return DOCS_DIR / (f"a7_report_{stem}_{tag}.txt" if tag else f"a7_report_{stem}.txt")


def format_report(stem, tag, paths, graph, checks):
    L = [f"A7 báo cáo đồ thị gộp: {stem}" + (f" ({tag})" if tag else ""), "file đã đọc:"]
    L += [f"  {a5.display_path(p)}" for p in paths.values()]
    L += ["", "== Nút =="]
    L.append(f"tổng {len(graph.nodes)} | theo loại {dict(collections.Counter(n['type'] for n in graph.nodes))} | "
             f"theo status {dict(collections.Counter(n['status'] for n in graph.nodes))}")
    L += ["", "== Cạnh =="]
    L.append(f"tổng {len(graph.edges)} | theo p {dict(collections.Counter(e['p'] for e in graph.edges))} | "
             f"theo status {dict(collections.Counter(e['status'] for e in graph.edges))}")
    L.append(f"bộ ba đã gộp ({len(graph.merged)}): " + ("; ".join(f"{s} {p} {o} ({n} lần)" for s, p, o, n in graph.merged) or "(không có)"))
    dups = [e for e in graph.edges if e["p"] == SAME_TEXT]
    L.append(f"nút bản sao text ({len(dups)}, bản sau -> canonical):")
    L += [f"  {e['s']} -> {e['o']}" for e in dups] or ["  (không có)"]
    skip = boilerplate(graph.nodes)
    L += ["", "== Liên thông =="]
    L.append(f"thành phần liên thông: {components(graph.nodes, graph.edges)} | bỏ {len(skip)} nút điều kiện chung chung "
             f"({'/'.join(a6.BOILERPLATE_KINDS)}): {components(graph.nodes, graph.edges, skip)} (chưa tính chính các nút đó)")
    notes = graph.notes
    if notes:
        L += ["", f"== Tại ngày {notes['date']} =="]
        L.append(f"dòng versions {notes['version_rows']} | đơn vị đang hiệu lực {notes['active']} | "
                 f"edge_changes đã áp {notes['applied'] or '(không có)'}")
        L.append(f"cạnh bị bỏ: {notes['dropped'] or '(không có)'} (structural: contains/part_of có đầu đã đóng; "
                 f"source_closed: refers_to/exception_of có nguồn đã đóng)")
        L.append(f"cạnh treo ({len(notes['dangling'])}, nguồn còn hiệu lực, đích đã đóng):")
        L += [f"  {s} {p} {o}" for s, p, o in notes["dangling"]] or ["  (không có)"]
    L += ["", "== Kiểm tra =="]
    L += [f"[{c.id}] {c.title}: {c.summary} -> {a5.verdict(c)}" for c in checks]
    for c in checks:
        L += [f"    {c.id}: {p}" for p in c.problems]
    bad = a5.failures(checks)
    L += ["", "KẾT LUẬN: " + (f"KHÔNG ĐẠT ({bad} chỗ sai)" if bad else "ĐẠT")]
    return "\n".join(L) + "\n"


def write_jsonl(rows, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def run(src, versions=None, date=None):
    """Dựng đồ thị, kiểm tra, in và ghi báo cáo; ghi file dữ liệu khi sạch. Trả về mã thoát (0 đạt, 1 có kiểm tra không đạt)."""
    stem = Path(src).stem
    expect, tag = None, None
    if versions is None:
        expect = EXPECTED.get(stem)
        if expect is None:
            raise SystemExit(f"LỖI: chưa có số đối chiếu cho {stem!r} (bảng EXPECTED có: {', '.join(EXPECTED)})")
    else:
        try:
            date = a4.parse_iso(date).isoformat()
            tag = tag_of(versions, date)
        except a4.A4Error as e:
            raise SystemExit(f"LỖI: {e.message}")
    try:
        graph, paths = graph_base(src) if versions is None else graph_at(src, versions, date)
    except ValueError as e:
        raise SystemExit(f"LỖI: {e}")
    checks = check_graph(graph, expect)
    text = format_report(stem, tag, paths, graph, checks)
    print(text, end="")
    a4.write_text(text, report_path(stem, tag))
    print("đã ghi", report_path(stem, tag))
    if a5.failures(checks):
        print("không ghi file dữ liệu vì còn kiểm tra không đạt", file=sys.stderr)
        return 1
    write_jsonl(graph.nodes, nodes_path(stem, tag))
    write_jsonl(graph.edges, edges_path(stem, tag))
    print("đã ghi", nodes_path(stem, tag))
    print("đã ghi", edges_path(stem, tag))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="file md nguồn, dùng để suy stem của các file A1-A3, A6")
    ap.add_argument("--versions", help="a4_<name>_versions.jsonl; có thì dựng đồ thị tại --date từ kết quả A4")
    ap.add_argument("--date", help="YYYY-MM-DD, đi cùng --versions")
    args = ap.parse_args(argv)
    if (args.versions is None) != (args.date is None):
        ap.error("--versions và --date phải đi cùng nhau")
    return run(args.path, args.versions, args.date)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
