"""S_infer: compile the in-force program Π_τ (units in force at date τ) to s(CASP).

exception_of edges are kept as binary facts for provenance, and each distinct target also gets a
unary has_exception/1 fact. Blocking then reads the unary predicate:

    blocked(U) :- has_exception(U).
    holds(U)   :- in_force(U), not blocked(U).

A binary-only rule (blocked(U) :- exception_of(_, U)) makes s(CASP) unroll an existential
`forall` over every exception_of/2 fact when proving not blocked(U); with ten facts on the
labor sample that query no longer terminates within two minutes. Grounding the target set into
has_exception/1 keeps every not blocked(U) goal ground.
A8 rule premises are kept as quoted atoms; grounding legal text to logical atoms is S_know's
job, so here we only care that the .pl stays syntactically valid however the LLM phrased it.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import edges
import law_registry
import versioning

ROOT = edges.ROOT
OUT_DIR = edges.PROCESSED_DIR
DOCS_DIR = ROOT / "docs"

REGISTERED_PREFIXES = frozenset(law.prefix for law in law_registry.LAWS.values())


def unit_prefix(src):
    """Registered id prefix of the source law: blds2015 -> BLDS2015, lld2019_labor -> LLD2019."""
    return law_registry.prefix_for(Path(src).stem)


def with_unit_prefix(code, prefix):
    """Swap a unit id's law prefix for the source law's registered one.

    A1 triples / A4 rows produced before law_registry existed can still carry another law's
    prefix (e.g. BLDS2015.D35 for an lld2019 source); emitting it verbatim makes the .pl
    disagree with its own header. Ids with no registered prefix pass through untouched.
    """
    head, sep, rest = str(code).partition(".")
    return f"{prefix}{sep}{rest}" if sep and head in REGISTERED_PREFIXES else str(code)


def _tag(versions, date):
    if versions is None:
        return None
    stem = Path(versions).stem
    m = re.fullmatch(r"a4_(.+)_versions", stem)
    name = m.group(1) if m else stem
    return f"{name}_{date}"


def atom(x):
    """Safe Prolog constant: single-quoted, escapes embedded quotes/backslashes."""
    return "'" + str(x).replace("\\", "\\\\").replace("'", "\\'") + "'"


def active_codes(src, versions=None, date=None):
    prefix = unit_prefix(src)
    if versions is None:
        return [with_unit_prefix(c, prefix) for c in edges.read_units(src).keys()]
    return [with_unit_prefix(r["id"], prefix)
            for r in versioning.active_rows(versioning.read_jsonl(versions), date)]


def read_rows(path):
    path = Path(path)
    if not path.exists():
        return []
    rows = []
    with open(path, encoding="utf-8", newline="") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def structural_edges(codes):
    active = set(codes)
    out = []
    for code in codes:
        parent = edges.parent_of(code)
        if parent and parent in active:
            out.append((parent, "contains", code))
            out.append((code, "part_of", parent))
    return out

def _resolve_jsonl_path(stage_dir, file_prefix, stem, tag, suffix=".jsonl"):
    """Resolve JSONL path: v3 stage subdir first, legacy flat file as fallback.

    v3_refactor: data/processed/<stage_dir>/<file_prefix>_<stem><tag>.jsonl
    legacy flat: data/processed/<file_prefix>_<stem><tag>.jsonl
    Stage dir and file prefix differ per stage (a3/a3_exceptions, a8/a8_implicit_exceptions),
    so one cannot be derived from the other.
    """
    stem_t = f"{stem}{tag}" if tag else stem
    subdir = edges.PROCESSED_DIR / stage_dir / f"{file_prefix}_{stem_t}{suffix}"
    flat = edges.PROCESSED_DIR / f"{file_prefix}_{stem_t}{suffix}"
    if subdir.exists():
        return subdir
    if flat.exists():
        return flat
    return subdir  # default to the v3 location; a missing file reads as no rows anyway


def exception_rows(src, versions, date):
    """exception_of rows from A3 (in-unit), A6 (general) and A8 (implicit), deduplicated."""
    stem = Path(src).stem
    tag = _tag(versions, date)
    prefix = unit_prefix(src)
    rows, seen = [], set()
    for stage_dir, file_prefix in (("a3", "a3_exceptions"),
                                   ("a6", "a6_exceptions"),
                                   ("a8", "a8_implicit_exceptions")):
        for r in read_rows(_resolve_jsonl_path(stage_dir, file_prefix, stem, tag)):
            for key in ("s", "o"):  # normalize stale cross-law ids coming from older A3/A6/A8 outputs
                if r.get(key):
                    r[key] = with_unit_prefix(r[key], prefix)
            triple = (r.get("s"), r.get("p"), r.get("o"))
            if triple in seen:  # same exception surfaced by more than one stage
                continue
            seen.add(triple)
            rows.append(r)
    return rows

def refers_rows(src):
    prefix = unit_prefix(src)
    rows = read_rows(_resolve_jsonl_path("a2", "a2_refs", Path(src).stem, None))
    for r in rows:
        if r.get("p") == "refers_to" and r.get("o"):
            r["s"], r["o"] = with_unit_prefix(r["s"], prefix), with_unit_prefix(r["o"], prefix)
    return rows


def a8_rules(src, versions, date):
    stem = Path(src).stem
    tag = _tag(versions, date)
    rows = read_rows(OUT_DIR / f"a8_rules_{stem}{'_' + tag if tag else ''}.jsonl")
    prefix = unit_prefix(src)
    for r in rows:  # a rule's source must match its in_force(...) fact
        if r.get("source"):
            r["source"] = with_unit_prefix(r["source"], prefix)
    return rows


def render_program(src, versions=None, date=None, query=None):
    codes = active_codes(src, versions, date)
    active = set(codes)
    tag = _tag(versions, date)
    L = ["% s(CASP) program generated by src/inference.py",
         f"% base: {Path(src).stem}, date: {date or '(base state)'}",
         "% Compile: scasp <file>.pl",
         ":- discontiguous contains/2, part_of/2, refers_to/2.", ""]

    for c in codes:
        L.append(f"in_force({atom(c)}).")
    L.append("")
    for s, p, o in structural_edges(codes):
        L.append(f"{p}({atom(s)}, {atom(o)}).")
    for r in refers_rows(src):
        if r.get("p") == "refers_to" and r["s"] in active and r["o"] in active:
            L.append(f"refers_to({atom(r['s'])}, {atom(r['o'])}).")
    L.append("")

    exc = []
    for r in exception_rows(src, versions, date):
        if r.get("p") == "exception_of" and r.get("o") in active:
            exc.append((r["s"], r["o"]))
            L.append(f"exception_of({atom(r['s'])}, {atom(r['o'])}).")
    L.append("")
    # Unary view of the same edges: the target set, deduplicated and grounded, so that
    # not blocked(U) never needs an existential scan over exception_of/2.
    targets = sorted({o for _, o in exc})
    for o in targets:
        L.append(f"has_exception({atom(o)}).")
    L.append("")

    L.append("% block default rule of U iff some exception targets U (negation-as-failure)")
    L.append("blocked(U) :- has_exception(U).")
    L.append("holds(U) :- in_force(U), not blocked(U).")
    L.append("")

    rules = [r for r in a8_rules(src, versions, date) if r.get("source") in active]
    for r in rules:
        rid = r.get("id") or f"r_{len(L)}"
        body = "".join(f", premise({atom(rid)}, {atom(b)})" for b in r.get("body", []))
        L.append(f"% rule {rid} (source {r.get('source')}): {r.get('head', '')}")
        L.append(f"conclusion({atom(rid)}) :- in_force({atom(r['source'])}){body}, not blocked({atom(r['source'])}).")
        for b in r.get("body", []):
            L.append(f"premise({atom(rid)}, {atom(b)}).")
        L.append("")

    if query:
        L.append(f"?- {query}.")
    return "\n".join(L) + "\n", len(codes), len(exc), len(rules)

def _run_solver(program, query):
    """Execute a live s(CASP) query against the compiled program; return (answer, note).

    Prefers the Ciao `scasp` CLI (or $SCASP), then SWI-Prolog's embedded library(scasp):
    consult the program and run `scasp(Query, [model(M), tree(T)])` to emit both the model
    and the s(CASP) justification tree. A missing solver returns a note instead of crashing,
    so the deterministic fallback is always preserved.
    """
    scasp = shutil.which("scasp") or os.environ.get("SCASP")
    cmd = None
    if scasp:
        cmd = [scasp, str(program)]
    else:
        swipl = shutil.which("swipl")
        if swipl:
            # consult/1 takes a Prolog atom: forward slashes avoid "\p" being read as an escape on Windows.
            p = Path(program).as_posix().replace("'", "\\'")
            goal = (
                "use_module(library(scasp)), consult('%s'), "
                "( catch(scasp(user:%s, [model(M), tree(T)]), E, "
                "        (format('SCASP_ERROR: ~w~n', [E]), fail)) -> "
                "  format('ANSWER: yes~nMODEL:~n', []), writeln(M), "
                "  format('TREE:~n', []), writeln(T) "
                "; format('ANSWER: no (no s(CASP) model — blocked or unprovable)~n', []) ), "
                "halt."
            ) % (p, query)
            cmd = [swipl, "-q", "-g", goal, "-t", "halt"]
    if not cmd:
        return None, "(solver not found — install scasp (set SCASP) or swi-prolog with library(scasp))"
    try:
        cp = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        out = (cp.stdout or "") + (cp.stderr or "")
        return out or "(no output)", ""
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, f"(solver error: {e})"


def run(src, versions=None, date=None, query=None):
    stem = Path(src).stem
    tag = _tag(versions, date)
    program, n_units, n_exc, n_rules = render_program(src, versions, date)
    out = OUT_DIR / f"a9_{stem}{'_' + tag if tag else ''}.pl"
    versioning.write_text(program, out)
    lines = [f"A9 report (s(CASP)): {stem}" + (f" @ {date}" if tag else ""),
             f"in_force units: {n_units} | exception_of: {n_exc} | A8 rules in_force: {n_rules}",
             f"program: {out}",
             "blocking: blocked(U) :- has_exception(U). ; holds(U) :- in_force(U), not blocked(U)."]
    answer = None
    if query:
        answer, note = _run_solver(out, query)
        lines.append(f"query: {query}")
        if answer:
            lines.append("answer:\n" + answer)
        elif note:
            lines.append(note)
    text = "\n".join(lines) + "\n"
    print(text, end="")
    versioning.write_text(text, DOCS_DIR / f"a9_report_{stem}{'_' + tag if tag else ''}.txt")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="source md, used to derive the stem")
    ap.add_argument("--versions", help="a4_<name>_versions.jsonl; time-aware inference at --date")
    ap.add_argument("--date", help="YYYY-MM-DD, required with --versions")
    ap.add_argument("--query", help="s(CASP) query, e.g. holds('BLDS2015.D615.K1')")
    args = ap.parse_args(argv)
    if (args.versions is None) != (args.date is None):
        ap.error("--versions and --date must be passed together")
    if args.date is not None:
        args.date = versioning.parse_iso(args.date).isoformat()
    return run(args.path, args.versions, args.date, args.query)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())