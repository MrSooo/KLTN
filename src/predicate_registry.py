"""Bước 2.6, phần 1.6B (A42): sổ vị từ CHỈ THÊM qua các mốc của kho phiên bản.

Sổ của KB gốc là kết quả 1.6B `names-2.1` của BLLĐ (`predicates.py`), dựng lại bằng replay đúng các lượt đã lưu. Ở mỗi mốc sau (knowledge_units.py),
các KU mới mở (đơn vị của văn bản vừa nạp, phiên bản sửa đổi, đơn vị chèn) mà đã có 1.6A được đặt tên:
  - chữ có khoá gộp cấp 1 (`predicates.word_key`: chữ chuẩn hoá + chữ ký tham số) đã có trong sổ thì nhận ngay tên cũ, không hỏi LLM;
  - chữ mới đi qua các lượt `names-2.1` như 1.6B gốc: ứng viên lấy từ hàng xóm trên MỌI chữ của sổ (cùng Điều, đơn vị nối bằng refers_to
    hoặc exception_of của mọi văn bản, chung từ nội dung); tên đã có không bao giờ bị đổi.
Vì sao chỉ thêm: khoá cache của một lượt 1.6B gồm danh sách ứng viên, tức phụ thuộc trạng thái sổ; đặt tên lại từ đầu cho cả kho thì mọi
lượt cũ trượt cache, và cùng một chữ có thể đổi tên giữa hai lần dựng. Hệ quả cho 2.7: dựng lại toàn bộ dùng chung sổ này (A42).

Một hộp cát cho cả chuỗi mốc: lượt của mốc sau chỉ dựng được khi mốc trước xong (ứng viên phụ thuộc tên vừa đặt). Lượt của KB gốc không nằm
trong hộp cát mà replay từ cache.

Chạy ở gốc repo (kho con thì đặt KLTN_TAP_CON):
  python -X utf8 -I src/predicate_registry.py [--llm off|replay]   ghi sổ (data/processed[_subset]/predicate_registry/)
  python -X utf8 -I src/predicate_registry.py --xuat <thư mục ngoài repo>
  python -X utf8 -I src/predicate_registry.py --nhap <thư mục> [--de]
"""
import argparse
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import concepts_names as cn  # noqa: E402
import corpus  # noqa: E402
import knowledge_units as ku_lib  # noqa: E402
import llm_client  # noqa: E402
import parse  # noqa: E402
import predicates as Pd  # noqa: E402
import propositions as P  # noqa: E402

DIR_NAME = "predicate_registry"


def all_edges(docs):
    """Cạnh nối đơn vị (refers_to của 1.2, exception_of của 1.5) của mọi văn bản: cho hàng xóm nhóm 2 của chữ mới."""
    refs, exc, nodes = collections.defaultdict(list), [], []
    for doc in docs:
        p = corpus.out_dir("refs") / f"refs_mentions_{doc}.jsonl"
        if not p.exists():
            continue
        for r in parse.read_jsonl(p):
            if r["p"] == "refers_to":
                refs[r["s"]].append(r)
        exc += cn.load_exception_rows(doc)
        nodes += parse.read_jsonl(corpus.out_dir("exceptions_general") / f"exceptions_general_conditions_{doc}.jsonl")
    return cn.collect_edges(refs, exc, nodes)


class ChainRun(Pd.Run):
    """`predicates.Run` nối tiếp qua các giai đoạn: giai đoạn 0 là 1.6B gốc của BLLĐ (đã gấp xong bằng replay trước khi tạo hộp cát), mỗi
    giai đoạn sau là một mốc. Chữ mới được NỐI vào cuối danh sách chữ (chỉ số cũ giữ nguyên), sổ giữ nguyên, lượt kế hoạch thêm vào sau.
    Hàng xóm dựng lại trên mọi chữ khi mở giai đoạn: chỉ ảnh hưởng lượt của giai đoạn đó trở đi (lượt cũ đã dựng xong)."""

    def __init__(self, base, stages, edges):
        self.__dict__.update(base.__dict__)
        self.stages, self.edges, self.stage_i = stages, edges, 0
        self.stage_of = {}       # chỉ số chữ -> mốc (chữ của giai đoạn gốc không có)
        self.stage_log = []      # [{epoch, ku, rows, known, new_words}]

    def next_round(self):
        rd = super().next_round()
        while rd is None and self.stage_i < len(self.stages):
            self._open(*self.stages[self.stage_i])
            self.stage_i += 1
            rd = super().next_round()
        return rd

    def _open(self, epoch, rows):
        keys = {w["key"] for w in self.words}
        order = {}
        for r in rows:
            order.setdefault(r["unit"], len(order))
        fresh = [r for r in rows if r["loai"] not in ("menh_de", "chu_the") or not r["span"] or Pd.word_key(r["span"], r["params"]) not in keys]
        new = Pd.build_words(fresh, order)
        base_n = len(self.words)
        for w in new:
            w["idx"] += base_n
            self.stage_of[w["idx"]] = epoch
        self.words.extend(new)
        self.planned.extend([[i + base_n for i in r] for r in cn.make_rounds(new)] if new else [])
        units = sorted({w["unit"] for w in self.words} | set(order))
        self.nb = cn.Neighbors(self.words, cn.link_map(units, self.edges))
        self.ctx = dict(self.ctx, **{r["unit"]: self.ku_ctx[r["ku"]] for r in rows})
        self.stage_log.append({"epoch": epoch.isoformat(), "ku": len({r["ku"] for r in rows}), "rows": len(rows),
                               "known": sum(1 for r in rows if r["loai"] in ("menh_de", "chu_the") and r["span"] and Pd.word_key(r["span"], r["params"]) in keys),
                               "new_words": len(new)})


def stages_from(catalog, cache, base_kus):
    """[(mốc, dòng)]: ở mỗi mốc, các KU xuất hiện LẦN ĐẦU, đã có 1.6A và không thuộc sổ gốc; cùng danh sách KU chưa có 1.6A.
    Sổ gốc = KU mã trần của văn bản gốc (đúng các đơn vị 1.6B gốc đã đặt tên), không phải "mốc đầu": trên kho đầy đủ, ND 90 và ND 28 có hiệu
    lực trước BLLĐ nên mốc đầu không phải BLLĐ."""
    seen = set(base_kus)
    out, missing = [], []
    for e in catalog.epochs:
        rows = []
        for uid, ku in catalog.at[e].items():
            if ku in seen:
                continue
            seen.add(ku)
            if ku not in cache:
                missing.append(ku)
                continue
            rows += ku_lib.ku_rows(catalog.kus[ku], cache[ku])[0]
        if rows:
            out.append((e, rows))
    return out, missing


def prepare():
    """-> (ChainRun đã gấp xong giai đoạn gốc bằng replay, catalog, KU chưa có 1.6A). Giai đoạn gốc thiếu cache thì dừng (sổ gốc phải đủ)."""
    base, _rows, _dropped = Pd.prepare(corpus.BASE_DOC_ID)
    stop = Pd.run_rounds(llm_client.Client("replay"), base)
    if stop:
        raise SystemExit(f"sổ gốc 1.6B chưa đủ: {stop}")
    catalog = ku_lib.Catalog(ku_lib.Store.load(), ku_lib.load_labels())
    cache = P.load_ku_cache()
    stages, missing = stages_from(catalog, cache, set(base.ctx))
    run = ChainRun(base, stages, all_edges(sorted({k["doc"] for k in catalog.kus.values()})))
    run.ku_ctx = {k: v["ctx"] for k, v in catalog.kus.items()}
    return run, catalog, missing


def names_by_key(run):
    """{khoá gộp: tên} của mọi chữ đã có tên."""
    return {run.words[i]["key"]: name for i, name in run.book.name_of.items()}


# ---- hộp cát (một cho cả chuỗi mốc) ----

TIEP_PY = """# Chỉ chạy file này, không mở, không sửa:  @PY@ tiep.py moi   |   @PY@ tiep.py ghi NNN
import os, sys
@ENV@sys.path.insert(0, @SRC@)
import predicate_registry
predicate_registry.tiep_entry(__file__, sys.argv[1:])
"""


def _make():
    run, _cat, _missing = prepare()
    return run


def tiep_entry(script, argv):
    import traceback
    sys.stdout.reconfigure(encoding="utf-8")
    d = Path(script).resolve().parent
    try:
        line = Pd.tiep(d, argv, _make, llm_client.load_config()[f"{Pd.ROLE}.model"])
    except BaseException as e:  # noqa: BLE001
        (d / "loi_tiep.txt").write_text("".join(traceback.format_exception(e)), encoding="utf-8", newline="\n")
        line = "DỪNG: lỗi khi dựng lượt (chi tiết trong loi_tiep.txt); báo người dùng"
    print(line)


def xuat(d):
    d, root = Path(d).resolve(), corpus.ROOT.resolve()
    if d == root or root in d.parents:
        raise SystemExit(f"{d} nằm trong repo; thư mục làm việc phải ở NGOÀI repo (A36)")
    if d.exists() and any(d.iterdir()):
        raise SystemExit(f"{d} đã có nội dung, không ghi đè")
    run, _cat, missing = prepare()
    if missing:
        raise SystemExit(f"còn {len(missing)} KU chưa có 1.6A (ví dụ {missing[:3]}): nhập 1.6A trước, vì lượt 1.6B đổi khi có thêm dòng")
    model = llm_client.load_config()[f"{Pd.ROLE}.model"]
    py = Path(sys.executable).as_posix()
    fill = lambda s: s.replace("@PY@", py).replace("@MODEL@", model).replace("@SUB@", Pd.SUBAGENT_MODEL).replace("@EFFORT@", Pd.EFFORT)  # noqa: E731
    env = f"os.environ['KLTN_TAP_CON'] = {corpus.SUBSET!r}\n" if corpus.SUBSET else ""
    (d / "lo").mkdir(parents=True, exist_ok=True)
    (d / "out").mkdir()
    files = {"HUONG_DAN.md": fill(cn.HUONG_DAN), "system.txt": Pd.SYSTEM + "\n", "schema.json": json.dumps(Pd.SCHEMA, ensure_ascii=False, indent=1) + "\n",
             "tiep.py": fill(TIEP_PY).replace("@ENV@", env).replace("@SRC@", repr(str(Path(__file__).resolve().parent)))}
    for name, text in files.items():
        (d / name).write_text(text, encoding="utf-8", newline="\n")
    return f"đã dựng {d}: {len(run.stages)} mốc có KU mới, {sum(len(r) for _, r in run.stages)} dòng; model {model} effort {Pd.EFFORT}"


def nhap(d, cache_dir=llm_client.CACHE_DIR, de=False):
    cfg = llm_client.load_config()
    model = cfg[f"{Pd.ROLE}.model"]
    run = _make()
    done, st = Pd.fold_dir(d, run, model)
    wrote, same = [], []
    for r in done:
        key = llm_client.cache_key(model, Pd.TASK, Pd.PROMPT_VERSION, Pd.user_message(r["items"]), Pd.SYSTEM, Pd.SCHEMA)
        path = Path(cache_dir) / Pd.TASK / f"{key}.json"
        if path.exists() and not de:
            if json.loads(path.read_text(encoding="utf-8")).get("output") == r["output"]:
                same.append(r["n"])
                continue
            return [f"DỪNG ở lượt {r['n']:03d}: bản ghi đã có mà đầu ra khác (dùng --de để ghi đè); đã ghi {len(wrote)} lượt"], True
        Pd.store_round(cache_dir, cfg, r["items"], r["output"], model=model, request_id=None, usage=None, produced_by="claude_code_sandbox",
                       producer_model_reported=r["model"], effort_reported=r["effort"])
        wrote.append(r["n"])
    bad = st["kind"] in ("lech", "lech_nhac", "lo_thua", "model", "sai_hinh")
    return [f"lượt đã áp: {len(done)}; ghi mới: {len(wrote)}; đã có, cùng đầu ra: {len(same)}",
            f"trạng thái thư mục: {st['kind']} ở lượt {st['n']:03d}" + (f" ({st['msg']})" if st.get("msg") else "") + ("  -> CÓ LỖI" if bad else "")], bad


# ---- đầu ra bước ----

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--llm", choices=("off", "replay"), default="off")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--xuat", metavar="THU_MUC")
    g.add_argument("--nhap", metavar="THU_MUC")
    ap.add_argument("--de", action="store_true")
    args = ap.parse_args(argv)
    if not P.full_cache_path().exists():
        print(f"BỎ QUA sổ vị từ 2.6: chưa có kết quả 1.6A {P.full_cache_path()}")
        return
    if args.xuat:
        print(xuat(args.xuat))
        return
    if args.nhap:
        lines, bad = nhap(args.nhap, de=args.de)
        print("\n".join(lines))
        raise SystemExit(1 if bad else 0)
    d = corpus.out_dir(DIR_NAME)
    if args.llm == "off":
        # Như 1.6B ở chế độ off (không đặt tên): ghi sổ RỖNG để bước sau không đọc nhầm sổ của lần replay trước.
        d.mkdir(parents=True, exist_ok=True)
        parse.write_jsonl(d / "predicate_registry_words.jsonl", [])
        (d / "predicate_registry_names.json").write_text(json.dumps({"names": {}, "params": {}, "surface": {}}) + "\n", encoding="utf-8", newline="\n")
        print("2.6 sổ vị từ: LLM TẮT, sổ rỗng")
        return
    run, catalog, missing = prepare()
    base_words = len(run.words)
    stop = Pd.run_rounds(llm_client.Client("replay"), run)
    names = names_by_key(run)
    out = []
    for i, w in enumerate(run.words):
        dec = run.decisions.get(i)
        out.append({"key": w["key"], "surface": w["surface"], "params": list(w["params"]), "predicate": run.book.name_of.get(i),
                    "stage": run.stage_of[i].isoformat() if i in run.stage_of else "goc", "kieu": dec["kieu"] if dec else None,
                    "rejected": run.rejected.get(i)})
    parse.write_jsonl(d / "predicate_registry_words.jsonl", out)
    params = {n: list(p) for n, p in run.book.name_params.items()}
    surface = {n: run.words[min(m)]["surface"] for n, m in run.book.members.items()}
    (d / "predicate_registry_names.json").write_text(json.dumps({"names": names, "params": params, "surface": surface}, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                                                     encoding="utf-8", newline="\n")
    lines = [f"2.6 sổ vị từ chỉ thêm (names {Pd.PROMPT_VERSION})" + (f" (kho con {corpus.SUBSET})" if corpus.SUBSET else ""),
             f"chữ của sổ gốc: {base_words}; chữ thêm ở các mốc: {len(run.words) - base_words}; tên: {len(run.book.name_params)}; chữ bị loại: {len(run.rejected)}",
             f"KU chưa có 1.6A (chưa đặt tên): {len(missing)}"]
    for s in run.stage_log:
        lines.append(f"  mốc {s['epoch']}: {s['ku']} KU, {s['rows']} dòng, {s['known']} chữ đã có trong sổ, {s['new_words']} chữ mới")
    reuse = collections.Counter(run.decisions[i]["kieu"] for i in run.stage_of if i in run.decisions)
    lines.append(f"quyết định LLM ở các mốc: {dict(sorted(reuse.items()))}")
    if stop:
        lines.append(stop)
    rp = corpus.report_dir(DIR_NAME) / "predicate_registry_report.txt"
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()
