"""Bước 1.8: quy tắc s(CASP). Máy biên dịch từ 1.6A (mệnh đề, `quy_tac`, `nhom_hoac`, vai, phương thức, cực) và 1.6B (tên vị từ); quy tắc trượt
cổng hoặc bị bộ quét bắt thì giao LLM sửa (A41, chủ đề tài chọn 18/11 thay A33(1)). Thiết kế gốc: docs/design/steps_1_6_to_1_8.md mục 6.

Biên dịch (mọi lựa chọn dưới đây là [THÊM] của agent cho chỗ thiết kế im lặng, ghi ở A41):
  - Mọi vị từ biên dịch MỘT NGÔI trên thực thể chủ thể X; đối số khác bỏ qua (biến không khớp giữa hai đầu cạnh ngoại lệ cho kết quả sai
    mà không báo, S5(4); một ngôi thì "biến của ngoại lệ nằm trong biến của quy tắc gốc" đúng theo cách dựng). Hạn chế: mất quan hệ hai bên.
  - Đầu quy tắc: <phương thức>_<vị từ> với phải, được, cấm, không áp dụng (phai_, duoc_, cam_, khong_ap_dung_); mô tả, định nghĩa (khong) giữ tên
    vị từ. Cực phủ định ở đầu: phủ định cổ điển (-p). Điều kiện có cực phủ định: `not p(X)` (phủ định do thất bại).
  - Thân: điều kiện cùng `quy_tac` (cùng `nhom_hoac` là các phương án, mỗi phương án một quy tắc), ngoại lệ cùng quy tắc thành `not`,
    và vị từ CHỦ THỂ của dòng kết luận (1.6B names-2.1) làm điều kiện canh.
  - Mục con chỉ có điều kiện (câu dẫn là kết luận, mục con là điều kiện, 1.6A luật 5): gắn vào kết luận của tổ tiên gần nhất; `cac_muc_con`
    của dòng câu dẫn là `va` thì gộp mọi mục con vào một thân, còn lại mỗi mục con một quy tắc.
  - Cạnh exception_of (1.5 đơn vị → đơn vị, con trỏ ngoại lệ của 1.6A, 1.7 `llm_proposed`): mọi quy tắc gốc của cây con đích o bị chặn khi
    đầu (khẳng định) của một quy tắc thuộc cây con nguồn s đúng: `blocked(r, X) :- h(X).`; quy tắc gốc thêm `not blocked(r, X)`; và
    `-<đầu gốc>(X) :- blocked(r, X).` cho kết quả "bị bác". Chặn theo VỊ TỪ chứ không theo đơn vị nên quy tắc của văn bản khác (2.6) dùng
    lại cùng vị từ là vào được. Cạnh từ nút điều kiện 1.5 không biên dịch riêng: ngoại lệ đó đã là dòng `ngoai_le` trong chính đơn vị (A33(a)).
Cổng và bộ quét: chỉ dùng vị từ có trong sổ 1.6B; vị từ dưới `not` phải là `input` hoặc có quy tắc định nghĩa (S5(2)), không thì cô lập
quy tắc; trùng lặp; vòng chặn; cặp đầu ngược (p và -p) không có quan hệ chặn; chương trình phải nạp được bằng s(CASP).

Chạy (kho con thì đặt KLTN_TAP_CON): python -X utf8 -I src/rules.py
Ra: data/processed[_subset]/rules/rules_<doc>.jsonl (quy tắc, kèm đơn vị nguồn), rules_<doc>.pl (chương trình), rules_isolated_<doc>.jsonl.
"""
import collections
import itertools
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import concepts_names as cn  # noqa: E402
import corpus  # noqa: E402
import parse  # noqa: E402
import predicates as Pd  # noqa: E402
import propositions as P  # noqa: E402

DIR_NAME = "rules"
SWIPL = "C:/Program Files/swipl/bin/swipl" if sys.platform == "win32" else "swipl"
MODE_PREFIX = {"phai": "phai_", "duoc": "duoc_", "cam": "cam_", "khong_ap_dung": "khong_ap_dung_", "khong": "", "": ""}


def atom(pred, mode):
    return MODE_PREFIX.get(mode or "", "") + pred


def lit_text(lit, var="X"):
    a = f"{'-' if lit.get('neg') else ''}{lit['atom']}({var})"
    return f"not {a}" if lit.get("naf") else a


def load(doc_id):
    """-> (1.6A theo đơn vị, tên vị từ theo (đơn vị, dòng), tên chủ thể theo khoá, kiểu vị từ, thứ tự đơn vị)."""
    a = json.loads(P.full_cache_path().read_text(encoding="utf-8"))["units"]
    d = corpus.out_dir("predicates")
    named = parse.read_jsonl(d / f"predicates_named_{doc_id}.jsonl")
    kinds = {p["predicate"]: p["kind"] for p in parse.read_jsonl(d / f"predicates_ledger_{doc_id}.jsonl")}
    pred_of, subj_of = {}, {}
    for r in named:
        if r["loai"] == "menh_de":
            pred_of[(r["unit"], r["row"])] = (r.get("predicate"), r.get("subject_key"))
        elif r["loai"] == "chu_the" and r.get("predicate"):
            subj_of[Pd.word_key(r["span"], ())] = r["predicate"]
    order = {u: k for k, u in enumerate(P.contexts(doc_id))}
    return a, pred_of, subj_of, kinds, order


def unit_groups(uid, rows, pred_of, subj_of):
    """Các nhóm quy_tac của một đơn vị: {q: {"heads": [lit], "conds": [lit], "or": {h: [lit]}, "exc": [lit]}}; dòng thiếu tên vị từ thì bỏ (ghi lý do)."""
    groups, notes = collections.defaultdict(lambda: {"heads": [], "conds": [], "or": collections.defaultdict(list), "exc": []}), []
    for i, d in enumerate(rows):
        if d["loai"] != "menh_de" or not d.get("quy_tac"):
            continue
        name, skey = pred_of.get((uid, i), (None, None))
        if not name:
            notes.append(f"{uid} dòng {i}: chưa có tên vị từ, bỏ")
            continue
        neg = d.get("cuc") == "phu_dinh"
        g = groups[d["quy_tac"]]
        if d["vai"] == "ket_luan":
            g["heads"].append({"atom": atom(name, d.get("phuong_thuc")), "pred": name, "neg": neg, "subject": subj_of.get(skey) if skey else None, "row": i})
        elif d["vai"] == "dieu_kien":
            lit = {"atom": atom(name, d.get("phuong_thuc")), "pred": name, "naf": neg, "row": i}
            (g["or"][d["nhom_hoac"]] if d.get("nhom_hoac") else g["conds"]).append(lit)
        elif d["vai"] == "ngoai_le":
            g["exc"].append({"atom": atom(name, d.get("phuong_thuc")), "pred": name, "naf": True, "row": i})
    return groups, notes


def child_mode(rows):
    """cac_muc_con của dòng câu dẫn (bo_qua cau_dan) của đơn vị, nếu có."""
    for d in rows:
        if d["loai"] == "bo_qua" and d.get("cac_muc_con"):
            return d["cac_muc_con"]
    return None


def bodies(g):
    """Các thân (danh sách literal) của một nhóm: điều kiện chung + một phương án của mỗi nhóm hoặc + ngoại lệ dạng not."""
    alts = [g["or"][h] for h in sorted(g["or"])]
    out = []
    for pick in itertools.product(*alts) if alts else [()]:
        out.append(list(g["conds"]) + list(pick) + list(g["exc"]))
    return out


def compile_units(a, pred_of, subj_of, order):
    """-> (quy tắc [{id, unit, head, body, how}], ghi chú)."""
    rules, notes = [], []
    per_unit = {}
    for uid in sorted(a, key=order.get):
        groups, n = unit_groups(uid, a[uid]["dong"], pred_of, subj_of)
        notes += n
        per_unit[uid] = groups
    # mục con chỉ có điều kiện -> gắn vào tổ tiên gần nhất có kết luận
    orphans = collections.defaultdict(list)  # tổ tiên -> [(đơn vị con, nhóm)]
    for uid, groups in per_unit.items():
        for q, g in groups.items():
            if g["heads"]:
                continue
            anc = next((x for x in cn.self_and_ancestors(uid)[1:] if any(gg["heads"] for gg in per_unit.get(x, {}).values())), None)
            if anc is None:
                notes.append(f"{uid} {q}: chỉ có điều kiện mà không tìm được kết luận ở tổ tiên, bỏ")
            else:
                orphans[anc].append((uid, g))

    def add(uid, head, body, how):
        lits = list(body)
        if head.get("subject") and head["subject"] != head["pred"]:
            lits = [{"atom": head["subject"], "pred": head["subject"], "naf": False, "role": "chu_the"}] + lits
        rules.append({"id": f"r{len(rules) + 1:04d}", "unit": uid, "head": {k: head[k] for k in ("atom", "pred", "neg")}, "body": lits, "how": how})

    for uid in sorted(per_unit, key=order.get):
        for q in sorted(per_unit[uid]):
            g = per_unit[uid][q]
            if not g["heads"]:
                continue
            kids = orphans.get(uid, []) if q == min(qq for qq, gg in per_unit[uid].items() if gg["heads"]) else []
            for head in g["heads"]:
                own = bodies(g)
                if not kids:
                    for b in own:
                        add(uid, head, b, "compiled")
                elif child_mode(a[uid]["dong"]) == "va":
                    merged = [lit for _, kg in kids for lit in bodies(kg)[0]]
                    for b in own:
                        add(uid, head, b + merged, "compiled_children_and")
                else:
                    for kid, kg in kids:
                        for kb in bodies(kg):
                            for b in own:
                                add(kid, head, b + kb, "compiled_child_or")
    return rules, notes


def exception_edges(doc_id, a):
    """Cạnh (s, o) đơn vị → đơn vị: 1.5 (bỏ cạnh từ nút điều kiện), con trỏ ngoại lệ 1.6A, 1.7. -> {(s, o): nguồn}."""
    out = {}
    for e in cn.load_exception_rows(doc_id):
        if e["s"].split(".")[1].startswith("D"):
            out.setdefault((e["s"], e["o"]), "1.5")
    for uid, v in a.items():
        for d in v["dong"]:
            if d["loai"] == "con_tro" and d.get("vai") == "ngoai_le":
                for t in d.get("targets") or []:
                    out.setdefault((t, uid), "1.6A con_tro")
    p = corpus.out_dir("implicit_exceptions") / f"implicit_edges_{doc_id}.jsonl"
    if p.exists():
        for e in parse.read_jsonl(p):
            out.setdefault((e["s"], e["o"]), "1.7 llm_proposed")
    return out


def under(uid, root):
    return uid == root or uid.startswith(root + ".")


def apply_blocks(rules, edges):
    """Thêm `not blocked(r, X)` vào quy tắc gốc, quy tắc chặn và quy tắc bị bác. -> (dòng chương trình thêm, quan hệ chặn [(r, đầu chặn, nguồn)])."""
    extra, rel = [], []
    for (s, o), src in sorted(edges.items()):
        heads = sorted({r["head"]["atom"] for r in rules if under(r["unit"], s) and not r["head"]["neg"]})
        for r in rules:
            if not under(r["unit"], o) or not heads:
                continue
            for h in heads:
                if h == r["head"]["atom"]:
                    continue
                rel.append((r["id"], h, src))
    by_rule = collections.defaultdict(list)
    for rid, h, src in rel:
        by_rule[rid].append((h, src))
    for r in rules:
        if r["id"] in by_rule:
            r["body"] = r["body"] + [{"atom": "blocked", "naf": True, "blocked_by": sorted({h for h, _ in by_rule[r["id"]]})}]
            for h in sorted({h for h, _ in by_rule[r["id"]]}):
                extra.append(f"blocked({r['id']}, X) :- {h}(X).")
            extra.append(f"{'' if r['head']['neg'] else '-'}{r['head']['atom']}(X) :- blocked({r['id']}, X).")
    return extra, rel


def rule_text(r):
    body = []
    for lit in r["body"]:
        body.append(f"not blocked({r['id']}, X)" if lit["atom"] == "blocked" else lit_text(lit))
    head = f"{'-' if r['head']['neg'] else ''}{r['head']['atom']}(X)"
    return f"{head} :- {', '.join(body)}." if body else f"{head}."


def scan(rules, kinds):
    """-> (quy tắc cô lập {id: lý do}, vấn đề báo cáo)."""
    defined = {r["head"]["atom"] for r in rules}
    iso, probs = {}, []
    for r in rules:
        # Thân rỗng: đầu đúng cho mọi X (thường là câu nêu giá trị không có chủ thể, ví dụ D155 "thời hạn tối đa 02 năm").
        if not r["body"]:
            iso[r["id"]] = "thân rỗng: không có chủ thể hay điều kiện, đầu đúng cho mọi X"
        for lit in r["body"]:
            if lit["atom"] == "blocked":
                continue
            if lit.get("naf") and lit["atom"] not in defined and kinds.get(lit["pred"]) != "input":
                iso[r["id"]] = f"{lit['atom']} dưới not mà không có quy tắc và không phải input (luôn đúng, S5(2))"
    seen = {}
    for r in rules:
        key = (r["head"]["atom"], r["head"]["neg"], tuple(sorted(lit_text(x) for x in r["body"] if x["atom"] != "blocked")))
        if key in seen:
            probs.append(f"trùng: {r['id']} giống {seen[key]}")
        seen.setdefault(key, r["id"])
    heads = {(r["head"]["atom"], r["head"]["neg"]) for r in rules}
    for atom_, neg in heads:
        if not neg and (atom_, True) in heads:
            blocked = any(lit["atom"] == "blocked" for r in rules if r["head"]["atom"] == atom_ and not r["head"]["neg"] for lit in r["body"])
            if not blocked:
                probs.append(f"đầu ngược không có quan hệ chặn: {atom_} và -{atom_}")
    g = collections.defaultdict(set)  # vòng chặn: đầu bị chặn -> đầu chặn
    for r in rules:
        for lit in r["body"]:
            for h in lit.get("blocked_by", []):
                g[r["head"]["atom"]].add(h)

    def reach(x, y, seen=None):
        seen = seen or set()
        if x == y:
            return True
        seen.add(x)
        return any(reach(n, y, seen) for n in g.get(x, ()) if n not in seen)
    for x in list(g):
        for y in g[x]:
            if reach(y, x):
                probs.append(f"vòng chặn: {x} <-> {y}")
    return iso, probs


def check_program(path):
    """Nạp chương trình bằng s(CASP). -> (ok, thông báo lỗi)."""
    cp = subprocess.run([SWIPL, "-q", "-g", f"consult('{Path(path).as_posix()}'), halt", "-t", "halt(1)"], capture_output=True, text=True, encoding="utf-8")
    msg = (cp.stdout + cp.stderr).strip()
    return cp.returncode == 0 and "error" not in msg.lower(), msg


def program_text(rules, extra, iso):
    lines = [":- use_module(library(scasp)).", "% Sinh bởi src/rules.py (bước 1.8); mỗi quy tắc ghi đơn vị nguồn.", ""]
    keep = [r for r in rules if r["id"] not in iso]
    ids = {r["id"] for r in keep}
    for r in keep:
        lines += [f"% {r['id']} {r['unit']} ({r['how']})", rule_text(r)]
    lines += [""] + [x for x in extra if any(f"({i}," in x for i in ids)]
    return "\n".join(lines) + "\n"


def main(doc_id=corpus.BASE_DOC_ID):
    a, pred_of, subj_of, kinds, order = load(doc_id)
    rules, notes = compile_units(a, pred_of, subj_of, order)
    edges = exception_edges(doc_id, a)
    extra, rel = apply_blocks(rules, edges)
    iso, probs = scan(rules, kinds)
    d = corpus.out_dir(DIR_NAME)
    d.mkdir(parents=True, exist_ok=True)
    pl = d / f"rules_{doc_id}.pl"
    pl.write_text(program_text(rules, extra, iso), encoding="utf-8", newline="\n")
    ok, msg = check_program(pl)
    parse.write_jsonl(d / f"rules_{doc_id}.jsonl", [dict(r, isolated=r["id"] in iso) for r in rules])
    parse.write_jsonl(d / f"rules_isolated_{doc_id}.jsonl", [{"id": k, "ly_do": v} for k, v in sorted(iso.items())])
    lines = [f"1.8 quy tắc: {doc_id}" + (f" (kho con {corpus.SUBSET})" if corpus.SUBSET else ""),
             f"quy tắc: {len(rules)} (cô lập {len(iso)}); cạnh ngoại lệ dùng: {len(edges)} {dict(collections.Counter(edges.values()))}; quan hệ chặn: {len(rel)}",
             f"nạp s(CASP): {'đạt' if ok else 'LỖI: ' + msg[:300]}",
             f"bộ quét: {len(probs)} vấn đề"] + [f"  {p}" for p in probs] + [f"  cô lập {k}: {v}" for k, v in sorted(iso.items())] + [f"  ghi chú: {n}" for n in notes]
    rp = corpus.report_dir(DIR_NAME) / f"rules_report_{doc_id}.txt"
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
