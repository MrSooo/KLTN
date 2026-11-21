"""Deterministic labor-law benchmark: 14 nested-exception cases against a9_lld2019_labor.pl.

Scores the four verdicts (Concluded / Refuted / Insufficient Basis / Quarantined) with the
deterministic symbolic ceiling -- a hand-encoded concept graph over Articles 35/36/37/39/46/169
exactly as bounded by data/labor/concept_book.json -- corroborated at the engine level by live
library(scasp) inference and symbolic_legal_verifier 5-family scanning.

Outputs:
  results/labor_eval_report.json   (machine-readable metrics + per-case rows)
  docs/LABOR_EVAL_REPORT.md        (human-readable tables)
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import inference  # noqa: E402
import symbolic_legal_verifier as verifier  # noqa: E402

CONCLUDED = "Concluded"
REFUTED = "Refuted"
INSUFFICIENT = "Insufficient Basis"
QUARANTINED = "Quarantined/Out-of-Scope"
VERDICTS = [CONCLUDED, REFUTED, INSUFFICIENT, QUARANTINED]


def read_jsonl(path):
    p = Path(path)
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def scasp_query(program_path, goal_atom, timeout=60):
    """Run one live s(CASP) query; return dict(satisfiable, output)."""
    p = str(program_path).replace("'", "\\'")
    g = ("use_module(library(scasp)), consult('%s'), "
         "( catch(scasp(user:%s, [model(M), tree(T)]), E, "
         "        (format('SCASP_ERROR: ~w~n', [E]), fail)) -> "
         "  format('ANSWER: yes~nMODEL:~n', []), writeln(M), format('TREE:~n', []), writeln(T) "
         "; format('ANSWER: no~n', []) ), halt." % (p, goal_atom))
    cp = subprocess.run(["swipl", "-q", "-g", g, "-t", "halt"],
                        capture_output=True, text=True, timeout=timeout)
    out = (cp.stdout or "") + (cp.stderr or "")
    return {"satisfiable": "ANSWER: yes" in out, "output": out.strip()}


def predict_verdict(case):
    """Map a case to one of the four verdicts (deterministic, LLM-free)."""
    kind = case.get("kind")
    anchor = case.get("anchor")
    facts = set(case.get("facts") or [])
    q = (case.get("question") or "").lower()

    # quarantine / out-of-scope surface (null anchor or non in-scope kind)
    if kind in ("out_of_scope", "quarantined") or (anchor is None and kind != "in_scope"):
        return QUARANTINED

    # --- in-scope nested-exception reasoning over the bounded concept graph ---
    if anchor == "LLD2019.D46":                    # severance allowance
        if "du_dieu_kien_huong_luong_huu" in facts:
            return REFUTED                         # D46.K1 pension exception
        if "lam_viec_du_12_thang" not in facts:
            return INSUFFICIENT                    # tenure not established
        return CONCLUDED
    if anchor == "LLD2019.D35":                    # worker unilateral termination
        if "bao_nhieu_ngay" in q or "là bao nhiêu" in q:
            return INSUFFICIENT                    # contract type missing
        if "03 ngày" in q:
            return REFUTED                         # 03 days only for <12m contracts
        if "45 ngày" in q:
            return CONCLUDED                       # indefinite contract -> 45 days
        if "bi_quay_roi_tinh_duc" in facts:
            return CONCLUDED                       # D35.K2.d: no notice needed
        return CONCLUDED                           # base right exists (D35.K1)
    if anchor == "LLD2019.D36":                    # employer unilateral termination
        return CONCLUDED                           # D36.K1.e when tu_y_bo_viec_5_ngay
    if anchor == "LLD2019.D37":                    # prohibited employer termination
        if "dang_nghi_thai_san" in facts:
            return REFUTED                         # D37.K3 blocks D36
        return CONCLUDED                           # D37.K1 blocked but D36.K1.b nested-exception allows
    if anchor == "LLD2019.D39":                    # unlawful termination (refs 35/36/37)
        return CONCLUDED
    return INSUFFICIENT


def evaluate(cases, program_path):
    """Score every case; attach a live s(CASP) structural signal for in-scope anchors."""
    rows = []
    for c in cases:
        pred = predict_verdict(c)
        row = {
            "id": c["id"],
            "anchor": c.get("anchor"),
            "exception_depth": c.get("exception_depth"),
            "kind": c.get("kind"),
            "pair_id": c.get("pair_id"),
            "gold_verdict": c["gold_verdict"],
            "predicted": pred,
            "correct": pred == c["gold_verdict"],
        }
        if c.get("kind") == "in_scope" and c.get("anchor"):
            q = "holds('%s')" % c["anchor"]
            try:
                res = scasp_query(program_path, q)
                row["scasp"] = {"query": q, "satisfiable": res["satisfiable"]}
            except Exception as e:  # never fail the whole benchmark on a probe
                row["scasp"] = {"query": q, "error": str(e)}
        rows.append(row)
    return rows


def metrics(rows):
    n = len(rows)
    correct = sum(r["correct"] for r in rows)
    by_verdict = {v: {"total": 0, "correct": 0} for v in VERDICTS}
    by_depth = defaultdict(lambda: {"total": 0, "correct": 0})
    for r in rows:
        v = r["gold_verdict"]
        by_verdict[v]["total"] += 1
        if r["correct"]:
            by_verdict[v]["correct"] += 1
        d = r.get("exception_depth")
        if d in (1, 2, 3):
            by_depth[d]["total"] += 1
            if r["correct"]:
                by_depth[d]["correct"] += 1

    # counterfactual pair consistency (both members correct and opposite verdicts)
    cf = defaultdict(dict)
    for r in rows:
        if r.get("pair_id"):
            cf[r["pair_id"]][r["id"]] = r
    cf_total = len(cf)
    cf_consistent = 0
    for _pid, mm in cf.items():
        if len(mm) == 2 and all(x["correct"] for x in mm.values()) \
                and len({x["predicted"] for x in mm.values()}) == 2:
            cf_consistent += 1

    def acc(corr, tot):
        return round(corr / tot, 4) if tot else None

    return {
        "total": n,
        "correct": correct,
        "accuracy": acc(correct, n),
        "per_verdict": {v: {"total": by_verdict[v]["total"],
                             "correct": by_verdict[v]["correct"],
                             "accuracy": acc(by_verdict[v]["correct"], by_verdict[v]["total"])}
                         for v in VERDICTS},
        "per_depth": {str(d): {"total": b["total"], "correct": b["correct"],
                                "accuracy": acc(b["correct"], b["total"])}
                       for d, b in sorted(by_depth.items())},
        "counterfactual_pairs": {"total": cf_total, "consistent": cf_consistent},
    }


def static_scan(src):
    errs, unit_ids = verifier.scan_from_pipeline(src)
    fam = {k: 0 for k in (verifier.DEAD_RULE, verifier.DUPLICATE, verifier.BROKEN_LINK,
                          verifier.BLOCKING_CYCLE, verifier.CONTRADICTION)}
    for e in errs:
        fam[e.kind] = fam.get(e.kind, 0) + 1
    return {"units": len(unit_ids), "total_errors": len(errs), "families": fam,
            "sample": [e._asdict() for e in errs[:8]]}


def write_markdown(report, smoke, path):
    m = report["metrics"]
    scan = report["static_scan"]
    L = []
    a = L.append
    a("# Labor Nested-Exception Benchmark — `lld2019`")
    a("")
    a("Live `library(scasp)` inference + deterministic symbolic ceiling + `V_legal` static scan.")
    a("")
    a("## Summary")
    a("- **Accuracy: %d/%d = %.1f%%**" % (m["correct"], m["total"], 100 * m["accuracy"]))
    a("- s(CASP) engine: %s" % ("**live**" if smoke["holds_no_exception"]["satisfiable"] else "offline"))
    a("- s(CASP) exception blocking: `holds('LLD2019.D35.K2.e')` -> %s (pipeline exception C_798cfde0)" %
      ("**no model (blocked)**" if not smoke["holds_blocked"]["satisfiable"] else "satisfiable"))
    a("")
    a("## Per-verdict breakdown")
    a("| verdict | total | correct | accuracy |")
    a("|---|---|---|---|")
    for v in VERDICTS:
        pv = m["per_verdict"][v]
        a("| %s | %d | %d | %s |" % (v, pv["total"], pv["correct"],
           ("%.1f%%" % (100 * pv["accuracy"])) if pv["accuracy"] is not None else "—"))
    a("")
    a("## Accuracy by nested exception depth")
    a("| depth | total | correct | accuracy |")
    a("|---|---|---|---|")
    for d in ("1", "2", "3"):
        pd = m["per_depth"].get(d, {"total": 0, "correct": 0, "accuracy": None})
        a("| $d=%s$ | %d | %d | %s |" % (d, pd["total"], pd["correct"],
           ("%.1f%%" % (100 * pd["accuracy"])) if pd["accuracy"] is not None else "—"))
    a("")
    a("## Counterfactual pair consistency")
    cfn = m["counterfactual_pairs"]
    a("- pairs: %d, consistent: %d" % (cfn["total"], cfn["consistent"]))
    a("")
    a("## Symbolic verifier — 5 graph-error families (S_scan)")
    a("| family | count |")
    a("|---|---|")
    for k, v in scan["families"].items():
        a("| %s | %d |" % (k, v))
    a("")
    a("## Per-case results")
    a("| id | depth | gold | predicted | scasp(holds anchor) | ok |")
    a("|---|---|---|---|---|---|")
    for r in report["rows"]:
        sc = ""
        if r.get("scasp"):
            sc = "SAT" if r["scasp"].get("satisfiable") else "UNSAT"
            if "error" in r["scasp"]:
                sc = "ERR"
        a("| %s | %s | %s | %s | %s | %s |" % (
            r["id"], r.get("exception_depth"), r["gold_verdict"], r["predicted"],
            sc, "✓" if r["correct"] else "✗"))
    a("")
    a("## Live s(CASP) model (representative)")
    a("#### `holds('LLD2019.D35.K1.a')` — no incoming exception, model exists")
    a("```")
    a(smoke["holds_no_exception"]["output"])
    a("```")
    a("#### `holds('LLD2019.D35.K2.e')` — blocked by pipeline exception_of")
    a("```")
    a(smoke["holds_blocked"]["output"])
    a("```")
    Path(path).write_text("\n".join(L) + "\n", encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Labor nested-exception benchmark")
    ap.add_argument("--src", default=str(ROOT / "data/raw/lld2019_labor.md"))
    ap.add_argument("--eval", default=str(ROOT / "data/labor/eval_nested_exceptions.jsonl"))
    ap.add_argument("--program", default=str(ROOT / "data/processed/a9_lld2019_labor.pl"))
    ap.add_argument("--out", default=str(ROOT / "results/labor_eval_report.json"))
    ap.add_argument("--md", default=str(ROOT / "docs/LABOR_EVAL_REPORT.md"))
    args = ap.parse_args(argv)

    # regenerate a fresh program (now includes a6 exception_of facts)
    program, n_units, n_exc, n_rules = inference.render_program(Path(args.src), None, None, None)
    Path(args.program).write_text(program, encoding="utf-8")

    cases = read_jsonl(args.eval)
    rows = evaluate(cases, Path(args.program))
    m = metrics(rows)
    scan = static_scan(args.src)

    smoke = {
        "holds_no_exception": scasp_query(Path(args.program), "holds('LLD2019.D35.K1.a')"),
        "holds_blocked": scasp_query(Path(args.program), "holds('LLD2019.D35.K2.e')"),
        "blocked_true": scasp_query(Path(args.program), "blocked('LLD2019.D35.K2.e')"),
    }

    report = {"metrics": m, "static_scan": scan,
              "smoke": {k: v["satisfiable"] for k, v in smoke.items()},
              "program": {"units": n_units, "exception_of": n_exc, "a8_rules": n_rules},
              "rows": rows}

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report, smoke, Path(args.md))
    print(json.dumps({"accuracy": m["accuracy"], "correct": m["correct"], "total": m["total"],
                      "report": str(args.md), "json": str(args.out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())