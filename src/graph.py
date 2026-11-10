"""graph: đồ thị tri thức gộp của cả kho lao động, kèm khoảng hiệu lực của từng nút.

Chạy: python -I src/graph.py        (cần l1, l2, l3, l4, l5 và l6 đã chạy)
Đầu ra (data/processed/graph/):
  graph_nodes.jsonl  {id, type, doc, label, heading, text (<=240 ký tự), parent, intervals [[from,to,state,version]], label_class, flags, ...}
                  type: document | chuong | muc | dieu | khoan | diem | pl | pl_muc | pl_row | dieu_kien | external
  graph_edges.jsonl  cạnh ngữ nghĩa {s, p, o, evidence, source, ...}. Cạnh cấu trúc không ghi: cha của mỗi nút nằm ở khoá `parent`.
Báo cáo: docs/bao_cao_chay/graph/graph_report.txt (số nút/cạnh theo loại, đầu cạnh không có nút, số thành phần liên thông ở mức Điều).

Nguồn cạnh: refers_to (L2), exception_of (L5 tường minh tường minh, L5 chung ngoại lệ chung), based_on / details (L3), amends / replaces / repeals /
expires_by_topic / overrides / supplements_list / pending_on / ends_when_replaced / triggers / consolidates (L6). Đầu cạnh là văn bản
(doc_id) hoặc văn bản ngoài kho (external:<số hiệu>) thì có nút document / external riêng. Nút không bị xoá: đơn vị hết hiệu lực vẫn có
nút, chỉ khoảng hiệu lực đóng lại. Quyết định chỗ spec im lặng: docs/quyet_dinh/l6_checks_graph_viewer_quyet_dinh.txt (mục D).
"""
import collections
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import l1_parse as l1
import l6_versions as l6v
import corpus

GRAPH_DIR_NAME = "graph"
TEXT_CHARS = 240


def short_label(row):
    t, n = row["type"], row["number"]
    return {"chuong": f"Ch.{n}", "muc": f"M{n}", "dieu": f"Đ{n}", "khoan": f"K{n}", "diem": n, "pl": f"PL {n}",
            "pl_muc": n, "pl_row": f"R{n}"}.get(t, n)


def build():
    docs = corpus.load_manifest()
    versions = l6v.load_versions()
    by = collections.defaultdict(list)
    for r in versions:
        by[r["id"]].append(r)
    labels = {r["id"]: r["label"] for r in l1.read_jsonl(corpus.out_dir("l4") / "l4_labels.jsonl")}
    nodes, edges = collections.OrderedDict(), []

    ver_edges = l1.read_jsonl(l6v.l6_dir() / "version_edges.jsonl")
    doc_end = {}
    for e in ver_edges:
        if e["p"] == "replaces" and e["o"] in docs:
            doc_end[e["o"]] = e["effective"]
    for d in docs.values():
        nodes[d.doc_id] = {"id": d.doc_id, "type": "document", "doc": d.doc_id, "label": d.so_hieu, "heading": d.ten_ngan,
                           "text": "", "parent": None, "level": d.level, "doc_type": d.doc_type, "number": d.so_hieu,
                           "intervals": [[d.ngay_hieu_luc.isoformat(), doc_end.get(d.doc_id), "normal", 1]],
                           "label_class": None, "flags": ["consolidation"] if d.is_consolidation else []}
    for uid, vs in by.items():
        last = vs[-1]
        nodes[uid] = {"id": uid, "type": last["type"], "doc": uid.split(".")[0], "label": short_label(last), "heading": last["heading"] or "",
                      "text": (last["text"] or "")[:TEXT_CHARS], "parent": last["parent"],
                      "number": last["number"],
                      "intervals": [[v["effective_from"], v["effective_to"], v["state"], v["version"]] for v in vs],
                      "label_class": labels.get(uid), "flags": sorted({f for v in vs for f in v["flags"]}),
                      "status": last["status"]}
    for uid, n in nodes.items():  # Điều / Chương không có cha thì cha là nút văn bản
        if n["type"] != "document" and n["parent"] is None:
            n["parent"] = n["doc"]
    graph_docs = [d for d in docs if not docs[d].is_consolidation]  # bản hợp nhất không có nút đơn vị riêng (chỉ tạo phiên bản trên BLLĐ)
    for d in graph_docs:
        for r in l1.read_jsonl(corpus.out_dir("l5_general") / f"l5_general_conditions_{d}.jsonl"):
            nodes[r["id"]] = {"id": r["id"], "type": "dieu_kien", "doc": d, "label": "điều kiện", "heading": r["kind"], "text": r["text"][:TEXT_CHARS],
                              "parent": None, "kind": r["kind"], "number": "", "intervals": [], "label_class": None, "flags": []}

    def add(s, p, o, evidence, source, **extra):
        edges.append({"s": s, "p": p, "o": o, "evidence": (evidence or "")[:160], "source": source, **extra})

    for d in graph_docs:
        for r in l1.read_jsonl(corpus.out_dir("l2") / f"l2_refs_{d}.jsonl"):
            add(r["s"], "refers_to", r["o"], r["evidence"], "l2")
        for r in l1.read_jsonl(corpus.out_dir("l5_explicit") / f"l5_explicit_exceptions_{d}.jsonl"):
            add(r["s"], "exception_of", r["o"], r["evidence"], "l5_explicit", method=r["method"])
        for r in l1.read_jsonl(corpus.out_dir("l5_general") / f"l5_general_exceptions_{d}.jsonl"):
            add(r["s"], "exception_of", r["o"], r["evidence"], "l5_general", method=r["method"])
    for r in l1.read_jsonl(corpus.out_dir("l3") / "l3_links.jsonl"):
        add(r["s"], r["p"], r["o"], r["evidence"], "l3", flags=r.get("flags", []), how=r.get("how"))
    for e in ver_edges:
        extra = {k: e[k] for k in ("effective", "flags", "valid_from", "valid_to", "topic") if k in e}
        add(e["s"], e["p"], e["o"], e["evidence"], "l6", **extra)

    for e in edges:  # nút ngoài kho cho đầu cạnh external:<số hiệu>
        for end in (e["s"], e["o"]):
            if end not in nodes:
                if not end.startswith("external:"):
                    raise ValueError(f"đầu cạnh không có nút: {end} ({e['p']})")
                nodes[end] = {"id": end, "type": "external", "doc": end, "label": end[9:], "heading": "văn bản ngoài kho", "text": "", "parent": None,
                              "number": end[9:], "intervals": [], "label_class": None, "flags": []}
    return docs, nodes, edges


def dieu_components(nodes, edges):
    """Số thành phần liên thông ở mức Điều / văn bản, theo cạnh ngữ nghĩa (gộp đầu cạnh lên Điều chứa nó)."""
    def top(i):
        n = nodes[i]
        while n["type"] not in ("dieu", "document", "pl", "dieu_kien", "external") and n["parent"] in nodes:
            n = nodes[n["parent"]]
        return n["id"]
    parent = {i: i for i, n in nodes.items() if n["type"] in ("dieu", "document", "pl", "dieu_kien", "external")}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for e in edges:
        a, b = top(e["s"]), top(e["o"])
        if a in parent and b in parent:
            parent[find(a)] = find(b)
    return len({find(x) for x in parent})


def main():
    docs, nodes, edges = build()
    d = corpus.out_dir(GRAPH_DIR_NAME)
    l1.write_jsonl(d / "graph_nodes.jsonl", list(nodes.values()))
    l1.write_jsonl(d / "graph_edges.jsonl", edges)
    ty = collections.Counter(n["type"] for n in nodes.values())
    ep = collections.Counter(e["p"] for e in edges)
    comps = dieu_components(nodes, edges)
    report = ["graph báo cáo", f"nút: {len(nodes)} {dict(ty)}", f"cạnh ngữ nghĩa: {len(edges)} {dict(ep)}",
              f"thành phần liên thông (mức Điều/văn bản/phụ lục/điều kiện): {comps}",
              f"đơn vị còn hiệu lực ở ngày cuối: {sum(1 for n in nodes.values() if n.get('status') == 'in_force')}; "
              f"đã hết hiệu lực: {sum(1 for n in nodes.values() if n.get('status') == 'expired')}; "
              f"chờ sự kiện: {sum(1 for n in nodes.values() if n.get('status') == 'pending_event')}; "
              f"tạm ngưng: {sum(1 for n in nodes.values() if n.get('status') == 'suspended')}"]
    path = corpus.report_dir(GRAPH_DIR_NAME) / "graph_report.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(report) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(report))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()
