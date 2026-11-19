"""Bước 2.6 (cập nhật tầng tri thức theo tập ảnh hưởng) và 2.7 (đối chứng với dựng lại toàn bộ). Quyết định: A42; method.md mục 3.4, Thuật toán 1.

Đầu vào: kho phiên bản (2.3-2.4), KU (knowledge_units.py), 1.6A theo KU (propositions.load_ku_cache), sổ vị từ chỉ thêm (predicate_registry.py),
câu trả lời 1.7 theo cặp KU (implicit_exceptions.PairAnswers), tập ảnh hưởng (affected.py).

Biên dịch một ẢNH CHỤP tại mốc e (`compile_at`): như 1.8 (`rules.compile_units`, `apply_blocks`, `scan`) trên các KU đang hiệu lực, với loại vị
từ tính trên ảnh chụp, cạnh ngoại lệ của mọi văn bản (1.5 đơn vị → đơn vị, con trỏ ngoại lệ của 1.6A, 1.7 đã nhận) và [THÊM] cạnh `overrides`
đang hiệu lực biên dịch như cạnh chặn (văn bản áp dụng thay chặn quy định bị thay trong khoảng hiệu lực, nên câu hỏi về quy định cũ ra "bị bác").
Mã quy tắc = "r" + sha1(đơn vị, đầu, thân không kể literal chặn, cách dựng, KU nguồn), để cùng một quy tắc có cùng mã ở mọi mốc và cả hai chế độ.

Hai chế độ:
  tăng dần (2.6): R là tập quy tắc có khoảng hiệu lực. Ở mỗi mốc e: tính A(e) (2.5); 1.7 chỉ hỏi cặp có ít nhất một đầu trong A(e); biên
     dịch ảnh chụp tại e rồi chỉ THAY các quy tắc có đơn vị nguồn trong A(e) (đóng quy tắc cũ đang mở, mở quy tắc mới); quy tắc khác giữ nguyên
     như ở mốc trước, kể cả literal chặn và cờ cô lập.
  dựng lại toàn bộ (2.7): biên dịch cả ảnh chụp ở mọi mốc, 1.7 hỏi mọi cặp.
2.7 so, ở mọi mốc và mọi ngày của bộ câu hỏi: tập quy tắc hiệu lực (đầu, thân, literal chặn kèm đầu chặn, cờ cô lập) của hai chế độ phải
trùng; mọi cặp 1.7 mà dựng lại toàn bộ cần phải đã được chế độ tăng dần hỏi. Sai khác nào cũng là bằng chứng A(e) thiếu. Bỏ từng quan hệ của
N rồi chạy lại để thấy quan hệ nào cần (bỏ cả N phải làm 2.7 trượt, không thì phép so không chứng minh gì).

Chạy (kho con thì đặt KLTN_TAP_CON): python -X utf8 -I src/update.py
  xuat-1-6a <thư mục> [N lô đầu]   hộp cát 1.6A cho KU chưa có 1.6A   nhap-1-6a <thư mục>
  xuat-1-7 <thư mục>    hộp cát 1.7 cho cặp chế độ tăng dần cần   nhap-1-7 <thư mục>
Ra: data/processed[_subset]/update/: update_rules.jsonl (R của chế độ tăng dần, có khoảng hiệu lực; 1.9 đọc), update_epochs.jsonl (A(e), cặp
1.7 đã hỏi), update_check.jsonl (2.7); báo cáo docs/run_reports[_subset]/update/update_report.txt.
"""
import collections
import datetime
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import affected  # noqa: E402
import corpus  # noqa: E402
import implicit_exceptions as ie  # noqa: E402
import knowledge_units as ku_lib  # noqa: E402
import parse  # noqa: E402
import propositions  # noqa: E402
import rules  # noqa: E402

DIR_NAME = "update"
OVERRIDES_EDGE = "2.3 overrides"


def rule_key(r):
    """Nội dung so của một quy tắc (2.7): mọi thứ trừ khoảng hiệu lực."""
    return json.dumps({k: r[k] for k in ("id", "unit", "head", "body", "how", "source_units", "source_kus", "isolated")}, ensure_ascii=False, sort_keys=True)


def _rid(r):
    body = [x for x in r["body"] if x["atom"] != "blocked"]
    raw = json.dumps([r["unit"], r["head"], body, r["how"], r["source_kus"]], ensure_ascii=False, sort_keys=True)
    return "r" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]


class Snapshot:
    """Một ảnh chụp tại mốc e: KU đang hiệu lực có 1.6A, dòng đã đặt tên, loại vị từ, ngữ cảnh (cho cặp 1.7)."""

    def __init__(self, kn, e):
        self.e = e
        self.live = kn.live(e)
        self.kinds, self.eff = kn.kinds(self.live)
        self.ctxs = {uid: kn.catalog.kus[k]["ctx"] for uid, k in kn.catalog.at[e].items()}
        self.pairs = ie.snapshot_pairs(kn, self.live, self.kinds, kn.store.order)


def compile_at(kn, snap, pairs_used, answers):
    """Biên dịch ảnh chụp. pairs_used: tập (ku a, ku b) mà cạnh 1.7 được dùng (chế độ tăng dần: cặp đã hỏi tới mốc này). -> (quy tắc, ghi chú, cạnh 1.7)."""
    live, order = snap.live, kn.store.order
    a, pred_of, subj_of = {}, {}, {}
    for uid, ku in live.items():
        a[uid] = kn.cache[ku]
        for r in kn.rows(ku):
            if r["loai"] == "menh_de":
                pred_of[(uid, r["row"])] = (r.get("predicate"), r.get("subject_key"))
            elif r["loai"] == "chu_the" and r.get("predicate"):
                subj_of[kn.word_key(r["span"], ())] = r["predicate"]
    out, notes = rules.compile_units(a, pred_of, subj_of, order, snap.eff)
    seen = collections.Counter()
    for r in out:
        r["source_kus"] = [live[u] for u in r["source_units"]]
        r["ku"] = live[r["unit"]]
        rid = _rid(r)
        seen[rid] += 1
        r["id"] = rid if seen[rid] == 1 else f"{rid}_{seen[rid]}"
    edges = {}
    for s, o in sorted(kn.exc15):
        if s.split(".")[1].startswith("D"):
            edges.setdefault((s, o), "1.5")
    for uid, ku in live.items():
        for d in a[uid]["dong"]:
            if d["loai"] == "con_tro" and d.get("vai") == "ngoai_le":
                for t in d.get("targets") or []:
                    edges.setdefault((t, uid), "1.6A con_tro")
    e17 = []
    for pa in snap.pairs:
        ka, kb = live[pa[0]], live[pa[1]]
        if (ka, kb) not in pairs_used:
            continue
        item = answers.get(ka, kb, pa, snap.ctxs)
        if item is None:
            continue
        edge, err = ie.gate(item, pa, snap.ctxs)
        if edge and not err:
            e17.append(edge)
    cyc = ie.find_cycles({(s, o) for s, o in kn.exc15_unit_edges()} | {(s, o) for s, o, _ in e17})
    for s, o, _ev in e17:
        if (s, o) not in cyc:
            edges.setdefault((s, o), rules.LLM_EDGE)
    for ov in kn.store.overrides_at(snap.e):
        edges.setdefault((ov["s"], ov["o"]), OVERRIDES_EDGE)
    rules.apply_blocks(out, edges)
    iso, probs = rules.scan(out, snap.eff)
    for r in out:
        r["isolated"] = iso.get(r["id"])
    return out, notes + probs, [(s, o) for s, o, _ in e17 if (s, o) not in cyc]


class Engine:
    def __init__(self, kn=None, answers=None):
        self.kn = kn or ku_lib.Knowledge()
        self.answers = answers or ie.PairAnswers()
        self.snaps = {e: Snapshot(self.kn, e) for e in self.kn.catalog.epochs}

    def full(self):
        """Dựng lại toàn bộ: {mốc: quy tắc}, {mốc: cặp cần (ku a, ku b)}."""
        R, need = {}, {}
        for e, snap in self.snaps.items():
            pairs = {(snap.live[a], snap.live[b]) for a, b, _ in snap.pairs}
            R[e], _notes, _e17 = compile_at(self.kn, snap, pairs, self.answers)
            need[e] = pairs
        return R, need

    def incremental(self, use=affected.RELATIONS):
        """Chạy tăng dần. -> (R [quy tắc kèm valid_from, valid_to], nhật ký từng mốc)."""
        cat = self.kn.catalog
        R, asked, log, e17_prev = [], set(), [], []
        for i, e in enumerate(cat.epochs):
            snap = self.snaps[e]
            if i == 0:
                A, T, N = set(snap.live), {u: {"ku_mo"} for u in snap.live}, {}
            else:
                T, N, A = affected.affected_at(self.kn, i, e17_prev, use)
            new_pairs = {(snap.live[a], snap.live[b]) for a, b, _ in snap.pairs if a in A or b in A}
            asked |= new_pairs
            compiled, notes, e17 = compile_at(self.kn, snap, asked, self.answers)
            e17_prev = e17
            by_key = {rule_key(r): r for r in compiled if set(r["source_units"]) & A}
            kept_open = set()
            for r in R:
                if r["valid_to"] is None and set(r["source_units"]) & A:
                    k = rule_key(r)
                    if k in by_key:
                        kept_open.add(k)
                    else:
                        r["valid_to"] = e
            for k, r in by_key.items():
                if k not in kept_open:
                    R.append(dict(r, valid_from=e, valid_to=None))
            log.append({"epoch": e.isoformat(), "source": self.kn.store.source_of(e), "T": {u: sorted(v) for u, v in sorted(T.items())},
                        "N": {k: sorted(v) for k, v in N.items()}, "A": sorted(A), "pairs_new": sorted(f"{a}|{b}" for a, b in new_pairs),
                        "notes": notes})
        return R, log, asked

    @staticmethod
    def at(R, d):
        return [r for r in R if r["valid_from"] <= d and (r["valid_to"] is None or d < r["valid_to"])]


def compare(eng, R_inc, asked, R_full, need, dates):
    """2.7. -> danh sách sai khác [{ngay, loai, ...}]; rỗng là đạt."""
    out = []
    cat = eng.kn.catalog
    for d in sorted(set(cat.epochs) | set(dates)):
        e = cat.epoch_of(d)
        if e is None:
            continue
        inc = {rule_key(r): r for r in Engine.at(R_inc, d)}
        full = {rule_key(r): r for r in R_full[e]}
        for k in sorted(set(full) - set(inc)):
            out.append({"ngay": d.isoformat(), "loai": "thieu_o_tang_dan", "id": full[k]["id"], "unit": full[k]["unit"]})
        for k in sorted(set(inc) - set(full)):
            out.append({"ngay": d.isoformat(), "loai": "thua_o_tang_dan", "id": inc[k]["id"], "unit": inc[k]["unit"]})
        for a, b in sorted(need[e] - asked):
            out.append({"ngay": d.isoformat(), "loai": "cap_1_7_chua_hoi", "a": a, "b": b})
    return out


def dev_questions():
    p = corpus.ROOT / "data" / "eval_dev" / f"{corpus.SUBSET}_questions.json" if corpus.SUBSET else None
    if p is None or not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8"))["cau_hoi"]


def dev_dates():
    return [datetime.date.fromisoformat(q["ngay"]) for q in dev_questions()]


def basis_lines(R):
    """Mốc kiểm của bộ câu hỏi dev (không phải số đo): tại ngày τ của từng câu, mỗi căn cứ chuẩn có bao nhiêu quy tắc trong Π_τ; với căn cứ
    đầu (quy tắc gốc, ví dụ D151.K1.d), các đầu chặn của nó và căn cứ chuẩn nào kết luận một đầu chặn đó (đường duy nhất để quy định miễn của
    nghị định chặn được quy tắc của luật là cùng atom đầu, vì cạnh details chỉ ở mức văn bản)."""
    out = []
    for q in dev_questions():
        if not q.get("can_cu"):
            continue
        rs = [r for r in Engine.at(R, datetime.date.fromisoformat(q["ngay"])) if not r.get("isolated")]
        per = {u: [r for r in rs if ku_lib.rel(r["unit"], u)] for u in q["can_cu"]}
        blockers = sorted({h for r in per[q["can_cu"][0]] for x in r["body"] if x["atom"] == "blocked" for h in x["blocked_by"]})
        hits = [u for u in q["can_cu"][1:] if any(r["head"]["atom"] in blockers and not r["head"]["neg"] for r in per[u])]
        out.append(f"    {q['id']} {q['ngay']} ({q['dap_an']}): " + ", ".join(f"{u.split('.', 1)[1] if u.startswith(corpus.BASE_DOC_ID) else u} {len(v)}" for u, v in per.items())
                   + (f"; đầu chặn của căn cứ đầu: {blockers}; căn cứ khác kết luận đầu chặn: {hits or 'KHÔNG'}" if len(q["can_cu"]) > 1 else ""))
    return out


def _row(r):
    return dict(r, valid_from=r["valid_from"].isoformat(), valid_to=r["valid_to"].isoformat() if r["valid_to"] else None)


def main():
    if not propositions.full_cache_path().exists():
        print(f"BỎ QUA 2.6-2.7: chưa có kết quả 1.6A {propositions.full_cache_path()}")
        return
    if not (corpus.out_dir("predicate_registry") / "predicate_registry_names.json").exists():
        print("BỎ QUA 2.6-2.7: chưa có sổ vị từ 2.6 (predicate_registry.py chạy với --llm replay)")
        return
    cmd = sys.argv[1:2]
    eng = Engine()
    if cmd in (["xuat-1-6a"], ["nhap-1-6a"]):
        kus = [k for k in sorted(eng.kn.catalog.kus.values(), key=lambda k: (k["first"], eng.kn.store.order[k["unit"]])) if k["ku"] not in eng.kn.cache]
        if cmd == ["xuat-1-6a"]:
            if len(sys.argv) > 3:  # chỉ N lô đầu (luật dừng A39: soát sau 60 lô rồi mới làm tiếp)
                kus = [k for lot in propositions.ku_lots(kus)[:int(sys.argv[3])] for k in lot]
            print(propositions.ku_xuat(sys.argv[2], kus))
        else:
            raise SystemExit(1 if propositions.ku_nhap(sys.argv[2], eng.kn.catalog.kus) else 0)
        return
    R_inc, log, asked = eng.incremental()
    if cmd in (["xuat-1-7"], ["nhap-1-7"]):
        if cmd == ["nhap-1-7"]:
            raise SystemExit(1 if ie.ku_nhap(sys.argv[2]) else 0)
        needed, seen = [], set()
        for e, snap in eng.snaps.items():
            for pa in snap.pairs:
                ka, kb = snap.live[pa[0]], snap.live[pa[1]]
                if (ka, kb) in asked and (ka, kb) not in seen and eng.answers.get(ka, kb, pa, snap.ctxs) is None:
                    seen.add((ka, kb))
                    needed.append((ka, kb, pa, ie.pair_payload(pa, snap.ctxs)))
        print(ie.ku_xuat(sys.argv[2], needed) if needed else "không có cặp 1.7 nào cần hỏi")
        return
    R_full, need = eng.full()
    dates = dev_dates()
    diffs = compare(eng, R_inc, asked, R_full, need, dates)
    ablate = {}
    for rel in affected.RELATIONS + ("ca_N",):
        use = () if rel == "ca_N" else tuple(x for x in affected.RELATIONS if x != rel)
        R2, _log2, asked2 = eng.incremental(use)
        ablate[rel] = compare(eng, R2, asked2, R_full, need, dates)
    d = corpus.out_dir(DIR_NAME)
    parse.write_jsonl(d / "update_rules.jsonl", [_row(r) for r in R_inc])
    parse.write_jsonl(d / "update_epochs.jsonl", log)
    parse.write_jsonl(d / "update_check.jsonl", diffs)
    cat = eng.kn.catalog
    no16a = [k for k in cat.kus if k not in eng.kn.cache]
    lines = [f"2.6-2.7 cập nhật tầng tri thức" + (f" (kho con {corpus.SUBSET})" if corpus.SUBSET else ""),
             f"mốc: {len(cat.epochs)}; KU: {len(cat.kus)} (chưa có 1.6A: {len(no16a)}); quy tắc trong R (tăng dần, mọi khoảng): {len(R_inc)}"]
    for row in log:
        n_open = len(Engine.at(R_inc, datetime.date.fromisoformat(row["epoch"])))
        lines.append(f"mốc {row['epoch']} ({', '.join(row['source'])}): |T| {len(row['T'])}, |A| {len(row['A'])} "
                     f"(N: {', '.join(f'{k} {len(v)}' for k, v in row['N'].items()) or '-'}); cặp 1.7 mới hỏi {len(row['pairs_new'])}; quy tắc hiệu lực {n_open}")
    lines.append(f"2.7 đối chứng (tăng dần với A(e) so với dựng lại toàn bộ, {len(set(cat.epochs) | set(dates))} ngày): "
                 + ("ĐẠT" if not diffs else f"TRƯỢT, {len(diffs)} sai khác {dict(collections.Counter(x['loai'] for x in diffs))}"))
    for x in diffs[:20]:
        lines.append(f"    {x}")
    lines.append("2.7 bỏ từng quan hệ của N (số sai khác; 0 nghĩa là trên kho này quan hệ đó không cần):")
    for rel, df in ablate.items():
        units = sorted({x.get("unit") or x.get("a") for x in df})
        lines.append(f"    bỏ {rel}: {len(df)} sai khác" + (f", đơn vị ví dụ {units[:4]}" if df else ""))
    if dev_questions():
        lines.append("căn cứ chuẩn của bộ câu hỏi dev trong Π_τ (số quy tắc không cô lập theo căn cứ):")
        lines += basis_lines(R_inc)
    rp = corpus.report_dir(DIR_NAME) / "update_report.txt"
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))
    if diffs:
        raise SystemExit(1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
