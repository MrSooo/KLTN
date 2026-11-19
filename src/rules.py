"""Bước 1.8: quy tắc s(CASP). Máy biên dịch từ 1.6A (mệnh đề, `quy_tac`, `nhom_hoac`, vai, phương thức, cực) và 1.6B (tên vị từ); quy tắc trượt
cổng hoặc bị bộ quét bắt thì giao LLM sửa (A41, chủ đề tài chọn 18/11 thay A33(1)). Thiết kế gốc: docs/design/steps_1_6_to_1_8.md mục 6.

Biên dịch (mọi lựa chọn dưới đây là [THÊM] của agent cho chỗ thiết kế im lặng, ghi ở A41):
  - Mọi vị từ biên dịch MỘT NGÔI trên thực thể chủ thể X; đối số khác bỏ qua (biến không khớp giữa hai đầu cạnh ngoại lệ cho kết quả sai
    mà không báo, S5(4); một ngôi thì "biến của ngoại lệ nằm trong biến của quy tắc gốc" đúng theo cách dựng). Hạn chế: mất quan hệ hai bên.
  - Đầu quy tắc: <tiền tố phương thức><vị từ>, tiền tố tiếng Anh cho đồng bộ với tên vị từ (user chốt 18/11): phải must_, được may_,
    cấm forbidden_, không áp dụng not_applicable_; mô tả, định nghĩa (khong) giữ tên vị từ.
  - Cực chỉ phủ định NỘI DUNG (đặc tả 1.6A). Đầu có phương thức mà cực phủ định: chèn neg_ sau tiền tố (D151.K1.c "phải không đang chấp hành
    hình phạt" -> must_neg_serving_criminal_sentence; user chốt 18/11). Không dùng -must_p vì `-` dành cho "được miễn do bị ngoại lệ chặn".
    Đầu mô tả có cực phủ định: phủ định cổ điển (-p). Điều kiện có cực phủ định: vị từ input thành `-p(X)` (thế giới mở,
    user chốt 18/11: thiếu sự kiện thì không kết luận), vị từ concept thành `not p(X)`.
  - Vị từ concept chỉ xuất hiện làm kết luận sau tiền tố phương thức thì coi là input (effective_kinds, user chốt 18/11).
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
MODE_PREFIX = {"phai": "must_", "duoc": "may_", "cam": "forbidden_", "khong_ap_dung": "not_applicable_", "khong": "", "": ""}


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
    eff = effective_kinds(named, kinds)
    return a, pred_of, subj_of, eff, order, sorted(k for k in kinds if eff[k] != kinds[k])


def effective_kinds(named, kinds):
    """Vị từ `concept` mà mọi dòng kết luận dùng nó đều có tiền tố phương thức (chỉ là ĐỐI TƯỢNG của nghĩa vụ, quyền, cấm) thì không có quy tắc
    nào định nghĩa chính nó: thực chất là sự kiện người hỏi cung cấp, coi là `input` (user chốt 18/11; ví dụ holds_work_permit: D151.K1.d
    "phải có giấy phép", D153.K2 "không có giấy phép thì bị trục xuất"). Vị từ bị đổi ghi ở báo cáo để soi ca thiếu định nghĩa thật."""
    defined = {r["predicate"] for r in named if r["loai"] == "menh_de" and r.get("predicate") and r["role"] == "ket_luan"
               and not MODE_PREFIX.get(r.get("mode") or "", "")}
    out = dict(kinds)
    for name, k in kinds.items():
        if k == "concept" and name not in defined:
            out[name] = "input"
    return out


def unit_groups(uid, rows, pred_of, subj_of, kinds):
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
            # Có phương thức thì phủ định nằm trong tên (neg_), đầu không mang `-`; đầu mô tả thì phủ định cổ điển.
            modal = bool(MODE_PREFIX.get(d.get("phuong_thuc") or "", ""))
            a = atom(("neg_" + name) if neg and modal else name, d.get("phuong_thuc"))
            g["heads"].append({"atom": a, "pred": name, "neg": neg and not modal, "subject": subj_of.get(skey) if skey else None, "row": i})
        elif d["vai"] == "dieu_kien":
            # Điều kiện phủ định trên vị từ input: phủ định cổ điển -p (thế giới mở, user chốt 18/11): phải có sự kiện nói rõ "không p";
            # thiếu sự kiện thì không kết luận (chưa đủ căn cứ) thay vì coi p sai. Vị từ concept (có quy tắc định nghĩa) giữ `not p`.
            classical = neg and kinds.get(name) == "input"
            lit = {"atom": atom(name, d.get("phuong_thuc")), "pred": name, "naf": neg and not classical, "neg": classical, "row": i}
            (g["or"][d["nhom_hoac"]] if d.get("nhom_hoac") else g["conds"]).append(lit)
        elif d["vai"] == "ngoai_le":
            if neg:  # ngoại lệ phủ định ("trừ khi không ...") mất một lớp phủ định nếu dịch thành `not p`; chưa có ca, báo để xem
                notes.append(f"{uid} dòng {i}: ngoai_le có cực phủ định, dịch thành `not p` mất phủ định, cần xem")
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


def compile_units(a, pred_of, subj_of, order, kinds=None):
    """-> (quy tắc [{id, unit, head, body, how}], ghi chú)."""
    rules, notes = [], []
    per_unit = {}
    for uid in sorted(a, key=order.get):
        groups, n = unit_groups(uid, a[uid]["dong"], pred_of, subj_of, kinds or {})
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

    def add(uid, head, body, how, sources):
        # sources: mọi đơn vị góp chữ cho quy tắc (đơn vị kết luận và đơn vị điều kiện); 1.9 chỉ dùng quy tắc khi mọi đơn vị này còn hiệu lực
        # tại τ với đúng chữ 1.6A đã đọc.
        lits = list(body)
        if head.get("subject") and head["subject"] != head["pred"]:
            lits = [{"atom": head["subject"], "pred": head["subject"], "naf": False, "role": "chu_the"}] + lits
        rules.append({"id": f"r{len(rules) + 1:04d}", "unit": uid, "head": {k: head[k] for k in ("atom", "pred", "neg")}, "body": lits, "how": how,
                      "source_units": sorted(set(sources), key=order.get)})

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
                        add(uid, head, b, "compiled", [uid])
                elif child_mode(a[uid]["dong"]) == "va":
                    merged = [lit for _, kg in kids for lit in bodies(kg)[0]]
                    for b in own:
                        add(uid, head, b + merged, "compiled_children_and", [uid] + [k for k, _ in kids])
                else:
                    for kid, kg in kids:
                        for kb in bodies(kg):
                            for b in own:
                                add(kid, head, b + kb, "compiled_child_or", [uid, kid])
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


LLM_EDGE = "1.7 llm_proposed"


# [THÊM, A43] Hai cách 1.6A ghi cùng một sự kiện "không thuộc diện P": phương thức khong_ap_dung + khẳng định (đầu not_applicable_P, như BLLĐ
# D154.K8) và mô tả + phủ định (đầu -P, như ND 152 Đ7, ND 219 Đ7, D154.K8a). Chặn theo vị từ thì hai cách phải là MỘT khoá chặn: đầu chặn của
# cây con nguồn ở dạng nào thì quy tắc gốc bị chặn bởi cả hai dạng, nếu có quy tắc nào kết luận dạng kia. Chỉ đổi dòng `blocked`, không đổi đầu.
BLOCK_ALIAS = True
NA_PREFIX = MODE_PREFIX["khong_ap_dung"]


def blocker_forms(rule_heads, alias=None):
    """Khoá chặn của một tập đầu (chuỗi: atom, hoặc '-atom' cho đầu phủ định). Có alias: not_applicable_P kéo theo -P và ngược lại."""
    alias = BLOCK_ALIAS if alias is None else alias
    out = set(rule_heads)
    if alias:
        for h in rule_heads:
            if h.startswith(NA_PREFIX):
                out.add("-" + h[len(NA_PREFIX):])
            elif h.startswith("-"):
                out.add(NA_PREFIX + h[1:])
    return out


def head_form(r):
    return ("-" if r["head"]["neg"] else "") + r["head"]["atom"]


def apply_blocks(rules, edges, alias=None):
    """Thêm literal `blocked` (kèm đầu chặn và nguồn cạnh của từng đầu) vào quy tắc gốc. Dòng chặn và dòng bị bác do program_text sinh từ
    literal này, để 1.9 dựng lại chương trình cho từng ngày τ và bật/tắt cạnh 1.7. -> quan hệ chặn [(r, đầu chặn, nguồn)].
    Đầu chặn là đầu khẳng định của cây con nguồn; với BLOCK_ALIAS (A43) thêm đầu -P và dạng tương đương, chỉ khi có quy tắc kết luận dạng đó."""
    rel = []
    concluded = {head_form(r) for r in rules}
    for (s, o), src in sorted(edges.items()):
        own = {head_form(r) for r in rules if under(r["unit"], s)}
        if not (BLOCK_ALIAS if alias is None else alias):
            own = {h for h in own if not h.startswith("-")}
        heads = sorted(h for h in blocker_forms(own, alias) if h in concluded)
        for r in rules:
            if not under(r["unit"], o) or not heads:
                continue
            for h in heads:
                if h in (r["head"]["atom"], head_form(r)):
                    continue
                rel.append((r["id"], h, src))
    by_rule = collections.defaultdict(lambda: collections.defaultdict(set))
    for rid, h, src in rel:
        by_rule[rid][h].add(src)
    for r in rules:
        if r["id"] in by_rule:
            src = {h: sorted(v) for h, v in sorted(by_rule[r["id"]].items())}
            r["body"] = r["body"] + [{"atom": "blocked", "naf": True, "blocked_by": sorted(src), "sources": src}]
    return rel


def active_blockers(r, llm_edges=True):
    """Đầu chặn còn dùng của quy tắc r. llm_edges=False bỏ đầu chỉ đến từ cạnh 1.7 (bật/tắt cạnh llm_proposed, steps_1_6_to_1_8.md mục 5)."""
    for lit in r["body"]:
        if lit["atom"] == "blocked":
            return [h for h in lit["blocked_by"] if llm_edges or any(x != LLM_EDGE for x in lit["sources"][h])]
    return []


def rule_text(r, llm_edges=True):
    body = []
    for lit in r["body"]:
        if lit["atom"] != "blocked":
            body.append(lit_text(lit))
        elif active_blockers(r, llm_edges):
            body.append(f"not blocked({r['id']}, X)")
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
    # Hai phương thức trái nhau trên cùng vị từ mà không quy tắc nào của chúng có quan hệ chặn: cả hai có thể cùng đúng (D53.K2 được dùng
    # lao động thuê lại / D53.K3 cấm) và không có gì phân xử. Chỉ báo, không cô lập: đây là việc của 1.7 hoặc của người đọc.
    atoms = {r["head"]["atom"] for r in rules if not r["head"]["neg"]}
    has_block = {r["head"]["atom"] for r in rules if any(lit["atom"] == "blocked" for lit in r["body"])}
    for pred in sorted({r["head"]["pred"] for r in rules}):
        for x, y in (("may_", "forbidden_"), ("must_", "forbidden_"), ("must_", "must_neg_")):
            a_, b_ = x + pred, y + pred
            if a_ in atoms and b_ in atoms and not ({a_, b_} & has_block):
                probs.append(f"phương thức trái nhau không có quan hệ chặn: {a_} và {b_}")
    g = collections.defaultdict(set)  # vòng chặn: đầu bị chặn -> đầu chặn
    for r in rules:
        for lit in r["body"]:
            for h in lit.get("blocked_by", []):
                g[r["head"]["atom"]].add(h.lstrip("-"))

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


def program_text(rules, iso=(), llm_edges=True):
    """Chương trình s(CASP) từ các quy tắc không bị cô lập: quy tắc, rồi `blocked(r, X) :- h(X).` và `-đầu(X) :- blocked(r, X).`"""
    lines = [":- use_module(library(scasp)).", "% Sinh bởi src/rules.py (bước 1.8); mỗi quy tắc ghi đơn vị nguồn.", ""]
    extra = []
    for r in rules:
        if r["id"] in iso:
            continue
        lines += [f"% {r['id']} {r['unit']} ({r['how']})", rule_text(r, llm_edges)]
        hs = active_blockers(r, llm_edges)
        extra += [f"blocked({r['id']}, X) :- {h}(X)." for h in hs]
        if hs:
            extra.append(f"{'' if r['head']['neg'] else '-'}{r['head']['atom']}(X) :- blocked({r['id']}, X).")
    lines += [""] + extra
    return "\n".join(lines) + "\n"


def main(doc_id=corpus.BASE_DOC_ID):
    if not P.full_cache_path().exists():  # kho chưa chạy 1.6A (kho đầy đủ trước lần chạy cả kho): báo rõ, không coi là lỗi của chuỗi
        print(f"BỎ QUA 1.8: chưa có kết quả 1.6A {P.full_cache_path()}")
        return
    a, pred_of, subj_of, kinds, order, to_input = load(doc_id)
    rules, notes = compile_units(a, pred_of, subj_of, order, kinds)
    edges = exception_edges(doc_id, a)
    rel = apply_blocks(rules, edges)
    iso, probs = scan(rules, kinds)
    d = corpus.out_dir(DIR_NAME)
    d.mkdir(parents=True, exist_ok=True)
    pl = d / f"rules_{doc_id}.pl"
    pl.write_text(program_text(rules, iso), encoding="utf-8", newline="\n")
    ok, msg = check_program(pl)
    parse.write_jsonl(d / f"rules_{doc_id}.jsonl", [dict(r, isolated=r["id"] in iso) for r in rules])
    parse.write_jsonl(d / f"rules_isolated_{doc_id}.jsonl", [{"id": k, "ly_do": v} for k, v in sorted(iso.items())])
    lines = [f"1.8 quy tắc: {doc_id}" + (f" (kho con {corpus.SUBSET})" if corpus.SUBSET else ""),
             f"quy tắc: {len(rules)} (cô lập {len(iso)}); cạnh ngoại lệ dùng: {len(edges)} {dict(collections.Counter(edges.values()))}; quan hệ chặn: {len(rel)}",
             f"nạp s(CASP): {'đạt' if ok else 'LỖI: ' + msg[:300]}",
             f"concept coi là input (chỉ làm đối tượng của phương thức): {len(to_input)} {to_input}",
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
