"""viewer: trang HTML xem đồ thị tri thức của kho lao động (một file, mở offline). Chỉ đọc file graph, không đổi dữ liệu nào.

Chạy: python -X utf8 -I utils/viewer/viewer.py          (cần src/graph.py đã chạy)
Đầu ra: data/processed/viewer/do_thi.html

Trang mặc định ở mức Điều (khoảng 700 Điều + 18 nút văn bản + phụ lục + nút điều kiện); bấm đúp một Điều / phụ lục để mở Khoản, Điểm, dòng;
lọc theo văn bản; ô chọn ngày dùng khoảng hiệu lực nhúng sẵn trong dữ liệu (mỗi nút có danh sách [từ, đến, trạng thái, phiên bản]) nên đổi ngày
không cần dựng lại file; bật / tắt từng loại cạnh. Cytoscape.js 3.30.2 (MIT) ở utils/viewer/vendor/ được nhúng thẳng, không gọi tài nguyên ngoài.
Đầu cạnh không có nút thì graph đã báo lỗi; ở đây không đoán thêm.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "src"))  # -I không tự thêm thư mục script
import corpus
from l1_parse import read_jsonl

TEMPLATE = HERE / "template.html"
CYTOSCAPE = HERE / "vendor" / "cytoscape.min.js"


def build_data():
    nodes = read_jsonl(corpus.out_dir("graph") / "graph_nodes.jsonl")
    edges = read_jsonl(corpus.out_dir("graph") / "graph_edges.jsonl")
    docs = corpus.load_manifest()
    dates = set()
    for n in nodes:
        for iv in n["intervals"]:
            dates.update(x for x in iv[:2] if x)
    dates.update(e["effective"] for e in edges if e.get("effective"))
    as_of = max(d.ngay_hieu_luc for d in docs.values()).isoformat()
    return {"asOf": as_of, "nodes": nodes, "edges": edges, "dates": sorted(dates | {as_of}),
            "docs": [{"id": d.doc_id, "title": d.ten_ngan} for d in docs.values()]}


def render(data):
    html = TEMPLATE.read_text(encoding="utf-8")
    js = CYTOSCAPE.read_text(encoding="utf-8").replace("</script", "<\\/script")  # không để thẻ đóng script nằm trong dữ liệu / thư viện
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return html.replace("/*CYTOSCAPE*/", js, 1).replace("/*DATA*/", blob, 1)


def main():
    out = corpus.out_dir("viewer") / "do_thi.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    data = build_data()
    out.write_text(render(data), encoding="utf-8", newline="\n")
    print(f"đã ghi {out} ({out.stat().st_size // 1024} KB; {len(data['nodes'])} nút, {len(data['edges'])} cạnh, {len(data['dates'])} mốc ngày)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
