"""A8: trang HTML xem đồ thị A7 để duyệt và demo. Chỉ đọc file A7, không đổi dữ liệu nào.

Trạng thái gốc: python -I utils/a8/a8_viz.py <file md nguồn>
  Đọc data/processed/a7/a7_<stem>_{nodes,edges}.jsonl (chạy a7_graph.py trước), ghi data/processed/a8/a8_<stem>.html.
Tại một ngày: python -I utils/a8/a8_viz.py <file md nguồn> --versions data/processed/a4/<name>/a4_<name>_versions.jsonl --date YYYY-MM-DD
  Đọc a7_<stem>_<name>_<date>_{nodes,edges}.jsonl (chạy a7_graph.py cùng tham số trước), ghi a8_<stem>_<name>_<date>.html.

Trang là MỘT file: dữ liệu nhúng dạng JSON, khung giao diện ở utils/a8/a8_template.html, thư viện Cytoscape.js (MIT) ở
utils/a8/vendor/cytoscape.min.js được nhúng thẳng vào, nên mở bằng trình duyệt không cần mạng.

Cách vẽ: đồ thị nút tròn, cạnh thẳng, bố cục force-directed tự viết trong khung (không thêm thư viện; vị trí đầu là cây tròn đồng tâm,
xác định, nên cùng dữ liệu thì cùng hình). Hiện đủ mọi nút. Cạnh cấu trúc (cha -> con, vẽ mờ, có công tắc tắt) và cạnh ngữ nghĩa
(refers_to, exception_of, same_text_as, amends / replaces / repeals, vẽ bằng màu). contains / part_of không gửi sang trang: cha của
mỗi nút nằm ở khoá "parent", trang tự dựng cạnh cấu trúc từ đó.
Nút ngoài cây (nút điều kiện, văn bản sửa đổi, đơn vị đã đóng) chỉ nối bằng cạnh ngữ nghĩa. Đích của cạnh treo / historical không còn là nút
trong A7 (7b), nên A8 thêm nút "da_dong" cho chúng; cha của nút này suy từ mã khi mã có từ ba đoạn trở lên và cha còn trong đồ thị.
Spec không nói thì ValueError, CLI thoát 1, không ghi file: thiếu file A7, p lạ, một nút có hai part_of, đầu cạnh không phải
nút mà cạnh không phải treo / historical.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))  # -I không tự thêm thư mục script
import a2_edges as a2
import a4_versions as a4
import a7_graph as a7

A8_DIR = Path(__file__).resolve().parent
OUT_DIR = a2.PROCESSED_DIR / "a8"  # test đổi sang thư mục tạm
TEMPLATE = A8_DIR / "a8_template.html"
CYTOSCAPE = A8_DIR / "vendor" / "cytoscape.min.js"

CLOSED = "da_dong"  # type của nút dựng cho đích đã đóng
SEMANTIC_P = ("refers_to", "exception_of", "same_text_as") + a7.AMEND_P  # p mà trang biết vẽ
NODE_KEYS = ("id", "type", "number", "heading", "text", "status", "kind", "source_line", "version", "effective_from",
             "co_quan", "ngay_ban_hanh", "hieu_luc")
EDGE_KEYS = ("s", "p", "o", "evidence", "evidences", "method", "status", "sources")


def html_path(stem, tag=None):
    return OUT_DIR / (f"a8_{stem}_{tag}.html" if tag else f"a8_{stem}.html")


def ghost_parent(code, ids):
    """Cha của nút đã đóng: bỏ đoạn cuối của mã nếu mã có từ ba đoạn (Khoản, Điểm) và cha còn trong đồ thị; còn lại None.
    Mã hai đoạn (Điều) không suy được Chương của nó từ mã nên không có cha."""
    parts = code.split(".")
    if len(parts) < 3:
        return None
    parent = ".".join(parts[:-1])
    return parent if parent in ids else None


def build_view(nodes, edges):
    """Dữ liệu cho trang: {"nodes": [...], "edges": [...]}. Nút giữ thứ tự file và thêm khoá parent (None nếu ngoài cây); cạnh chỉ
    gồm cạnh ngữ nghĩa. Nút da_dong cho đầu cạnh không phải nút nối ở cuối."""
    ids = {n["id"] for n in nodes}
    parent = {}
    for e in edges:
        if e["p"] != "part_of":
            continue
        if e["s"] in parent:
            raise ValueError(f"{e['s']} có hơn một part_of")
        parent[e["s"]] = e["o"]
    out_nodes = [{**{k: n[k] for k in NODE_KEYS if k in n}, "parent": parent.get(n["id"])} for n in nodes]
    sem = []
    closed = {}
    for e in edges:
        if e["p"] in a7.STRUCTURAL:
            continue
        if e["p"] not in SEMANTIC_P:
            raise ValueError(f"cạnh {e['s']} {e['p']} {e['o']}: trang chưa biết vẽ p này (có: {', '.join(SEMANTIC_P)})")
        for end in (e["s"], e["o"]):
            if end not in ids and end not in closed:
                if e["status"] not in (a7.DANGLING, a7.HISTORICAL):
                    raise ValueError(f"cạnh {e['s']} {e['p']} {e['o']}: {end} không phải nút mà cạnh có status {e['status']!r}")
                closed[end] = {"id": end, "type": CLOSED, "number": None, "heading": None, "text": None, "status": "closed",
                               "parent": ghost_parent(end, ids)}
        sem.append({k: e[k] for k in EDGE_KEYS if k in e})
    return {"nodes": out_nodes + list(closed.values()), "edges": sem}


def script_safe(js):
    """Chuỗi nhúng vào <script>: không được chứa '</script' (kể cả khác hoa thường) hay '<!--'."""
    low = js.lower()
    if "</script" in low or "<!--" in low:
        raise ValueError("nội dung nhúng chứa '</script' hoặc '<!--'")
    return js


def render_html(view, title, meta, template, cytoscape_js):
    """Thay ba chỗ giữ chỗ của khung. Dữ liệu JSON thoát '<' để không đóng thẻ script sớm; thư viện chèn sau cùng để chữ
    __DATA__ nếu có trong thư viện không bị thay."""
    for key in ("__TITLE__", "__DATA__", "__CYTOSCAPE__"):
        if template.count(key) != 1:
            raise ValueError(f"khung phải có đúng một {key}, thấy {template.count(key)}")
    data = json.dumps({"meta": meta, **view}, ensure_ascii=False).replace("<", "\\u003c")
    title = title.replace("&", "&amp;").replace("<", "&lt;")
    return (template.replace("__TITLE__", title).replace("__DATA__", data)
            .replace("__CYTOSCAPE__", script_safe(cytoscape_js)))


def run(src, versions=None, date=None):
    stem = Path(src).stem
    tag = None
    if versions is not None:
        try:
            tag = a7.tag_of(versions, a4.parse_iso(date).isoformat())
        except a4.A4Error as e:
            raise SystemExit(f"LỖI: {e.message}")
    paths = (a7.nodes_path(stem, tag), a7.edges_path(stem, tag))
    for p in paths:
        if not p.exists():
            hint = f"python -I src/a7_graph.py {src}" + (f" --versions {versions} --date {date}" if tag else "")
            raise SystemExit(f"LỖI: chưa có {p.name}; chạy trước: {hint}")
    nodes, edges = a4.read_jsonl(paths[0]), a4.read_jsonl(paths[1])
    try:
        view = build_view(nodes, edges)
        meta = {"stem": stem, "tag": tag, "date": date, "n_nodes": len(nodes), "n_edges": len(edges)}
        title = f"Đồ thị {stem}" + (f" tại {date}" if date else "")
        page = render_html(view, title, meta, TEMPLATE.read_text(encoding="utf-8"), CYTOSCAPE.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise SystemExit(f"LỖI: thiếu {Path(e.filename).name}; thư viện tải bằng: curl -L -o utils/a8/vendor/cytoscape.min.js "
                         "https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.30.2/cytoscape.min.js")
    except ValueError as e:
        raise SystemExit(f"LỖI: {e}")
    out = html_path(stem, tag)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8", newline="\n")
    n_closed = sum(1 for n in view["nodes"] if n["type"] == CLOSED)
    print(f"{len(view['nodes'])} nút ({n_closed} đã đóng), {len(view['edges'])} cạnh ngữ nghĩa -> {out}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="file md nguồn, dùng để suy stem của file A7")
    ap.add_argument("--versions", help="a4_<name>_versions.jsonl; có thì xem đồ thị tại --date")
    ap.add_argument("--date", help="YYYY-MM-DD, đi cùng --versions")
    args = ap.parse_args(argv)
    if (args.versions is None) != (args.date is None):
        ap.error("--versions và --date phải đi cùng nhau")
    return run(args.path, args.versions, args.date)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
