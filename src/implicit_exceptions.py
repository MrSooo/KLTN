"""Bước 1.7: ngoại lệ ngầm (thiết kế docs/design/steps_1_6_to_1_8.md mục 5). Tìm cặp đơn vị mà một bên là ngoại lệ của bên kia dù không có chữ "trừ".

Cách làm:
  1. Máy dựng cặp: hai đơn vị cùng dùng một vị từ `concept` của sổ 1.6B (`predicates_named_*`). Bỏ cặp tổ tiên/con cháu (cùng nhánh cây: chữ của cha
     là câu dẫn của con nên chung vị từ theo cấu trúc, không phải ngoại lệ) [THÊM, mô tả bước im lặng], và bỏ cặp đã có cạnh exception_of ở 1.5.
     Chỉ tính vị từ của dòng mệnh đề, không tính vị từ chủ thể; bỏ cặp mà vị từ chung là kết luận giống hệt ở hai bên [THÊM, A41].
  2. Đếm cặp; vượt ngân sách chỉ CẢNH BÁO (A41: chạy hết rồi xem ca lỗi).
  3. LLM xét từng cặp với ngữ cảnh như 1.6 (tiêu đề Điều, câu dẫn, chữ đơn vị): a_ngoai_le_cua_b | b_ngoai_le_cua_a | khong, kèm bằng chứng nguyên văn.
  4. Cổng máy: giá trị hợp lệ; bằng chứng là chuỗi con của ngữ cảnh của đơn vị NGOẠI LỆ; hai đầu tồn tại; không trùng cạnh 1.5; không tạo vòng
     (cạnh trong vòng bị loại và liệt kê).
  5. Cạnh nhận mang cờ `llm_proposed`; bật hay tắt ở 1.8 và 1.9.
Phần LLM chạy bằng phiên Claude Code trong thư mục làm việc ngoài repo (A36), lô độc lập như 1.6A (không cần tiep.py).

Chạy (kho con thì đặt KLTN_TAP_CON, A41):
  python -X utf8 -I src/implicit_exceptions.py                  đầu ra bước (đọc kết quả LLM đã nhập; chưa nhập thì 0 cạnh và báo)
  python -X utf8 -I src/implicit_exceptions.py xuat <thư mục>   dựng thư mục làm việc
  python -X utf8 -I src/implicit_exceptions.py nhap <thư mục>   kiểm từng lô rồi ghi data/llm_cache/implicit_exceptions/<doc>[.<tập con>].json
"""
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import concepts as cc  # noqa: E402
import concepts_names as cn  # noqa: E402
import corpus  # noqa: E402
import parse  # noqa: E402
import propositions as P  # noqa: E402

PROMPT_VERSION = "ngoai-le-ngam-2"  # 2: kèm chữ các mục con (đơn vị câu dẫn như D53.K2 chỉ có "trong trường hợp sau đây:")
MODEL, EFFORT, ALIAS = "claude-sonnet-5-5", "high", "sonnet"  # như A39
LOT_SIZE = 10           # cặp mỗi lô
PAIR_BUDGET = 400       # ngân sách cặp: vượt thì cảnh báo (bản cũ đo 108 cặp trên cả BLLĐ)
KETQUA = {"a_ngoai_le_cua_b", "b_ngoai_le_cua_a", "khong"}
DIR_NAME = "implicit_exceptions"
CACHE_DIR = corpus.ROOT / "data" / "llm_cache" / DIR_NAME

SYSTEM = """Bạn xét các CẶP đơn vị của văn bản pháp luật lao động Việt Nam. Với mỗi cặp (A, B), quyết định một đơn vị có phải là NGOẠI LỆ của đơn vị kia không.

"B là ngoại lệ của A" khi B nêu một trường hợp cụ thể hơn mà trong trường hợp đó quy định của A KHÔNG áp dụng, hoặc áp dụng khác đi (kết luận khác, miễn, loại trừ), dù chữ không có "trừ" hay dẫn chiếu. Ví dụ: A "người lao động nước ngoài phải có giấy phép lao động", B "người lao động nước ngoài kết hôn với người Việt Nam và sinh sống tại Việt Nam không thuộc diện cấp giấy phép lao động": B là ngoại lệ của A.
KHÔNG phải ngoại lệ: hai quy định bổ sung cho nhau (cùng áp dụng được), một quy định chi tiết hoá quy định kia, hai quy định chỉ cùng chủ đề, hai mục cùng một danh sách. Không chắc thì trả "khong".

ĐẦU VÀO: {"cap": [{"cap_id", "a": {"unit_id", "tieu_de_dieu", "khoan_cha", "chu_don_vi", "cac_muc_con" (nếu có)}, "b": {...}, "vi_tu_chung": [tên vị từ hai bên cùng dùng]}]}.
Đơn vị có cac_muc_con: chu_don_vi là câu dẫn, các trường hợp nằm trong cac_muc_con (chữ của các điểm, theo thứ tự); xét đơn vị cùng cả danh sách. Hai danh sách chỉ "tách rời" khi không trường hợp nào của bên này có thể xảy ra cùng lúc với một trường hợp của bên kia; nếu có thể xảy ra cùng lúc mà hai bên kết luận trái nhau, xét theo chữ luật bên nào phải được áp dụng trong tình huống đó.

ĐẦU RA: chỉ JSON {"cap": [{"cap_id": "...", "ket_qua": "a_ngoai_le_cua_b" | "b_ngoai_le_cua_a" | "khong", "bang_chung": "..."}]}. Mỗi cặp đúng một mục.
- bang_chung: chỉ khi ket_qua khác "khong"; là MỘT chuỗi chép NGUYÊN VĂN, liền, từ tieu_de_dieu, khoan_cha, chu_don_vi hoặc một mục của cac_muc_con của đơn vị LÀ NGOẠI LỆ, nêu trường hợp làm quy định kia không áp dụng.
- Mỗi cặp xét riêng theo chữ của cặp đó."""

HUONG_DAN = """# Việc của bạn

Thư mục này là toàn bộ thế giới của bạn. Bạn (và mọi subagent bạn tạo) chỉ đọc và ghi trong thư mục này. Không mở thư mục cha hay thư mục nào khác, không tìm hiểu dữ liệu đến từ đâu hay dùng vào việc gì.

Có @N@ lô trong `lo/` (`001.json` đến `@N@.json`). Với mỗi lô, làm đúng theo `system.txt`, ghi kết quả vào `out/` cùng số.

## Model
Việc này phải do model `@MODEL@` làm, mức effort `@EFFORT@`. Mỗi subagent đặt tường minh model (tên tắt `@ALIAS@`) và effort `@EFFORT@`. Không đặt được thì dừng và báo người dùng.

## Chia việc
Chia các lô thành khối liền nhau, mỗi khối tối đa 20 lô; mỗi khối giao cho MỘT subagent mới, song song tối đa 4. Lời giao (thay AAA, BBB):
> Đọc `system.txt` một lần. Rồi lần lượt với từng lô NNN từ AAA đến BBB mà `out/NNN.json` chưa có: đọc `lo/NNN.json`, làm đúng theo `system.txt`, ghi kết quả vào `out/NNN.json` là JSON thuần đúng khuôn ở mục "ĐẦU RA" của `system.txt`. Mỗi lô xét riêng. Không đọc hay ghi file nào khác. Cuối cùng trả lời mỗi lô một dòng: NNN, một ký tự tab, rồi ID model chính xác của bạn.

Bạn (phiên chính) KHÔNG tự làm lô nào. Ghi các dòng trả lời vào `nhat_ky.tsv` (dạng `NNN<tab>ID model`).

## Cấm
- Không viết script, regex hay công cụ nào để sinh hoặc sửa đầu ra.
- Không sửa `out/NNN.json` sau khi subagent đã ghi.

## Xong
Báo: số file đã ghi, nội dung `nhat_ky.tsv`, lô nào lỗi.
"""


def ancestors_or_self(uid):
    return set(cn.self_and_ancestors(uid))


def explicit_pairs(doc_id):
    """Cặp (s, o) đơn vị đã có cạnh exception_of ở 1.5. Cạnh từ nút điều kiện quy về mọi đơn vị chứa nút đó (như collect_edges của 1.6B)."""
    _doc, _units, _labels, nodes, _refs = cc.load_inputs(doc_id)
    node_units = {n["id"]: n["units"] for n in nodes}
    out = set()
    for e in cn.load_exception_rows(doc_id):
        for s in node_units.get(e["s"], [e["s"]]):
            out.add((s, e["o"]))
    return out


def build_pairs(doc_id):
    """-> (cặp [(a, b, [vị từ chung])] theo thứ tự tất định, số cặp đã có cạnh 1.5, ngữ cảnh). a < b theo thứ tự đơn vị của 1.6A."""
    ctxs = P.contexts(doc_id)
    order = {u: k for k, u in enumerate(ctxs)}
    d = corpus.out_dir("predicates")
    named = parse.read_jsonl(d / f"predicates_named_{doc_id}.jsonl")
    ledger = {p["predicate"]: p for p in parse.read_jsonl(d / f"predicates_ledger_{doc_id}.jsonl")}
    units_of = collections.defaultdict(set)
    use = collections.defaultdict(set)  # (đơn vị, vị từ) -> {(vai, phương thức, cực)} của các dòng mệnh đề
    for r in named:
        # Vị từ chủ thể không tạo cặp: mọi Khoản cùng chủ thể đều chung nó (ví dụ "người lao động nước ngoài" ở D151-D157).
        if r.get("predicate") and r["loai"] == "menh_de" and ledger.get(r["predicate"], {}).get("kind") == "concept":
            units_of[r["predicate"]].add(r["unit"])
            use[(r["unit"], r["predicate"])].add((r["role"], r["mode"], r["cuc"]))
    shared = collections.defaultdict(set)
    for name, us in units_of.items():
        us = sorted(us, key=order.get)
        for i, a in enumerate(us):
            for b in us[i + 1:]:
                if a in ancestors_or_self(b) or b in ancestors_or_self(a):
                    continue
                # Hai bên cùng kết luận y hệt (cùng phương thức, cùng cực) thì không bên nào lật được bên kia: các mục liệt kê
                # cùng một hệ quả (D156 các trường hợp hết hiệu lực) không phải ngoại lệ của nhau.
                ua, ub = use[(a, name)], use[(b, name)]
                if ua == ub and all(x[0] == "ket_luan" for x in ua):
                    continue
                shared[(a, b)].add(name)
    known = explicit_pairs(doc_id)
    already = {k for k in shared if k in known or (k[1], k[0]) in known}
    pairs = [(a, b, sorted(shared[(a, b)])) for (a, b) in sorted(shared, key=lambda k: (order[k[0]], order[k[1]])) if (a, b) not in already]
    return pairs, len(already), ctxs


def _children_text(uid, ctxs):
    """Chữ các đơn vị con cháu theo thứ tự: câu dẫn ("... trong trường hợp sau đây:") chỉ có nghĩa cùng danh sách của nó."""
    return [c["text"] for u, c in ctxs.items() if u.startswith(uid + ".")]


def _unit_payload(uid, ctxs):
    c = ctxs[uid]
    out = {"unit_id": uid, "tieu_de_dieu": c["heading"], "khoan_cha": c["chapeau"], "chu_don_vi": c["text"]}
    kids = _children_text(uid, ctxs)
    if kids:
        out["cac_muc_con"] = kids
    return out


def lots(pairs, ctxs):
    out = []
    for k in range(0, len(pairs), LOT_SIZE):
        out.append({"cap": [{"cap_id": f"P{k + i:04d}", "a": _unit_payload(a, ctxs), "b": _unit_payload(b, ctxs), "vi_tu_chung": names}
                            for i, (a, b, names) in enumerate(pairs[k:k + LOT_SIZE])]})
    return out


def lot_text(lot):
    return json.dumps(lot, ensure_ascii=False, indent=1) + "\n"


def cache_path(doc_id):
    return CACHE_DIR / (f"{doc_id}.{corpus.SUBSET}.json" if corpus.SUBSET else f"{doc_id}.json")


def xuat(thu_muc, doc_id=corpus.BASE_DOC_ID):
    d = Path(thu_muc)
    if d.exists() and any(d.iterdir()):
        raise SystemExit(f"{d} đã có nội dung, không ghi đè")
    pairs, n_known, ctxs = build_pairs(doc_id)
    ls = lots(pairs, ctxs)
    warn = f"; CẢNH BÁO: {len(pairs)} cặp vượt ngân sách {PAIR_BUDGET}" if len(pairs) > PAIR_BUDGET else ""
    if not ls:
        return f"không có cặp nào để hỏi (đã bỏ {n_known} cặp có cạnh 1.5); không dựng thư mục"
    (d / "lo").mkdir(parents=True, exist_ok=True)
    (d / "out").mkdir()
    (d / "system.txt").write_text(SYSTEM + "\n", encoding="utf-8", newline="\n")
    for i, lot in enumerate(ls, 1):
        (d / "lo" / f"{i:03d}.json").write_text(lot_text(lot), encoding="utf-8", newline="\n")
    (d / "HUONG_DAN.md").write_text(HUONG_DAN.replace("@N@", f"{len(ls):03d}").replace("@MODEL@", MODEL).replace("@ALIAS@", ALIAS).replace("@EFFORT@", EFFORT),
                                    encoding="utf-8", newline="\n")
    (d / "cau_hinh.json").write_text(json.dumps({"model": MODEL, "effort": EFFORT, "prompt_version": PROMPT_VERSION, "tap_con": corpus.SUBSET}) + "\n", encoding="utf-8")
    return f"đã dựng {d}: {len(ls)} lô, {len(pairs)} cặp (đã bỏ {n_known} cặp có cạnh 1.5){warn}"


def gate(item, pair, ctxs):
    """-> (cạnh (s, o, bằng chứng) hoặc None, lỗi hoặc None)."""
    a, b, _names = pair
    kq = item.get("ket_qua")
    if kq not in KETQUA:
        return None, f"ket_qua lạ {kq!r}"
    if kq == "khong":
        return None, None
    exc, base = (a, b) if kq == "a_ngoai_le_cua_b" else (b, a)
    ev = item.get("bang_chung") or ""
    c = ctxs[exc]
    if not ev or not any(ev in part for part in (c["heading"], c["chapeau"], c["text"], *_children_text(exc, ctxs))):
        return None, "bang_chung không nguyên văn trong ngữ cảnh của đơn vị ngoại lệ"
    return (exc, base, ev), None


def find_cycles(edges):
    """Cạnh nằm trên một vòng của đồ thị có hướng (s -> o). -> tập cạnh (s, o)."""
    g = collections.defaultdict(set)
    for s, o in edges:
        g[s].add(o)

    def reach(x, y):
        seen, st = set(), [x]
        while st:
            n = st.pop()
            if n == y:
                return True
            if n in seen:
                continue
            seen.add(n)
            st += g.get(n, ())
        return False
    return {(s, o) for s, o in edges if reach(o, s)}


def nhap(thu_muc, doc_id=corpus.BASE_DOC_ID):
    d = Path(thu_muc)
    cfg = json.loads((d / "cau_hinh.json").read_text(encoding="utf-8"))
    if cfg.get("tap_con") != corpus.SUBSET or cfg.get("prompt_version") != PROMPT_VERSION or (d / "system.txt").read_text(encoding="utf-8") != SYSTEM + "\n":
        raise SystemExit("hộp cát dựng với tập con hoặc lời nhắc khác code hiện tại: không nhập")
    pairs, _n_known, ctxs = build_pairs(doc_id)
    ls = lots(pairs, ctxs)
    if not (d / "nhat_ky.tsv").exists():
        raise SystemExit(f"{d} chưa có nhat_ky.tsv: phiên chưa chạy xong, không nhập")
    log = {int(p[0]): p[1].strip() for p in (line.split("\t") for line in (d / "nhat_ky.tsv").read_text(encoding="utf-8").splitlines()) if len(p) >= 2 and p[0].strip().isdigit()}
    answers, bad = {}, []
    for n, lot in enumerate(ls, 1):
        f = d / "out" / f"{n:03d}.json"
        if (d / "lo" / f"{n:03d}.json").read_text(encoding="utf-8") != lot_text(lot):
            bad.append((n, "lo/ khác đầu vào hiện tại"))
            continue
        if not f.exists() or log.get(n) != MODEL:
            bad.append((n, f"chưa có out hoặc nhat_ky báo {log.get(n)!r}"))
            continue
        try:
            items = {it["cap_id"]: it for it in json.loads(f.read_text(encoding="utf-8"))["cap"]}
        except (ValueError, KeyError, TypeError) as e:
            bad.append((n, f"sai hình: {e}"))
            continue
        want = {c["cap_id"] for c in lot["cap"]}
        if set(items) != want:
            bad.append((n, f"cap_id lệch: thiếu {sorted(want - set(items))}, thừa {sorted(set(items) - want)}"))
            continue
        answers.update(items)
    out = cache_path(doc_id)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"prompt_version": PROMPT_VERSION, "model": MODEL, "effort": EFFORT, "answers": answers}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"ghi {out}: {len(answers)} cặp có trả lời")
    for n, why in bad:
        print(f"  lô {n:03d} KHÔNG nhận: {why}")


def run(doc_id=corpus.BASE_DOC_ID):
    pairs, n_known, ctxs = build_pairs(doc_id)
    p = cache_path(doc_id)
    answers = json.loads(p.read_text(encoding="utf-8"))["answers"] if p.exists() else {}
    known = explicit_pairs(doc_id)
    accepted, rejected, asked = [], [], []
    for k, pair in enumerate(pairs):
        cid = f"P{k:04d}"
        item = answers.get(cid)
        asked.append({"cap_id": cid, "a": pair[0], "b": pair[1], "vi_tu_chung": pair[2], "ket_qua": item.get("ket_qua") if item else None})
        if item is None:
            continue
        edge, err = gate(item, pair, ctxs)
        if err:
            rejected.append({"cap_id": cid, "ly_do": err, "tra_loi": item})
        elif edge and (edge[0], edge[1]) not in known:
            accepted.append(edge)
    cyc = find_cycles({(s, o) for s, o in known} | {(s, o) for s, o, _ in accepted})
    edges = []
    for s, o, ev in accepted:
        if (s, o) in cyc:
            rejected.append({"cap": [s, o], "ly_do": "tạo vòng với cạnh 1.5 hoặc cạnh 1.7 khác"})
        else:
            edges.append({"s": s, "p": "exception_of", "o": o, "evidence": ev, "how": "llm", "flags": ["llm_proposed"], "rule": "implicit"})
    d = corpus.out_dir(DIR_NAME)
    parse.write_jsonl(d / f"implicit_pairs_{doc_id}.jsonl", asked)
    parse.write_jsonl(d / f"implicit_edges_{doc_id}.jsonl", edges)
    parse.write_jsonl(d / f"implicit_rejected_{doc_id}.jsonl", rejected)
    lines = [f"1.7 ngoại lệ ngầm: {doc_id}" + (f" (kho con {corpus.SUBSET})" if corpus.SUBSET else ""),
             f"cặp cùng vị từ concept (bỏ tổ tiên/con cháu): {len(pairs) + n_known}; đã có cạnh 1.5: {n_known}; hỏi LLM: {len(pairs)}"
             + (f" (CẢNH BÁO: vượt ngân sách {PAIR_BUDGET})" if len(pairs) > PAIR_BUDGET else ""),
             f"có trả lời: {sum(1 for x in asked if x['ket_qua'])}; nhận: {len(edges)}; loại: {len(rejected)}"
             + ("" if p.exists() or not pairs else "; CHƯA NHẬP kết quả LLM")]
    lines += [f"  {e['s']} exception_of {e['o']}: {e['evidence'][:80]}" for e in edges]
    rp = corpus.report_dir(DIR_NAME) / f"implicit_report_{doc_id}.txt"
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    cmd = sys.argv[1:2]
    if cmd == ["xuat"]:
        print(xuat(sys.argv[2]))
    elif cmd == ["nhap"]:
        nhap(sys.argv[2])
    else:
        run()
