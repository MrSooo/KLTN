"""V_legal: symbolic legal verifier — deterministic reward, state distance, and detailed feedback.

Grounds a predicted legal reasoning chain in the bounded concept graph and s(CASP) blocking
semantics WITHOUT calling the LLM or the solver: every function here is pure/deterministic.

Model (PDDL-INSTRUCT, 2509.13351):
  * A legal state s is a set of fluents (in-force provisions + derived atoms).
  * A rule application is an action a = <pre(a), add(a), del(a)>:
      pre(a) = body premises + "source in force and not blocked",
      add(a) = the rule head (conclusion),
      del(a) = units blocked when this rule fires (exception_of(s, o) => blocked(o)).
    A transition is s_i = a_i(s_{i-1}) = (s_{i-1} \\ del(a_i)) U add(a_i).
  * State distance d_state(s, t) = |s △ t| (symmetric difference).

Contracts:
  * R_sym(y|x) in [0,1]: 1 if every step is logically valid and reaches the goal,
    else penalised by alpha_precond / alpha_effect / alpha_goal.
  * classify(...) returns one of four verdicts on the extraction/abstention surface:
      Concluded | Refuted | Insufficient Basis | Quarantined/Out-of-Scope.
  * scan_errors(...) reports the 5 graph-scanner error families:
      dead_rule, duplicate, broken_link, blocking_cycle, contradiction.

Zero dependencies; imported modules (edges/graph/validation/...) are siblings already in src/.
LLM unconfigured => nothing here changes: the verifier never guesses, it only checks.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I mode: sibling imports
import edges  # noqa: E402  (structural/unit helpers)

# ---- penalty weights (sum to 1 => R_sym in [0,1]) ----
ALPHA_PRECOND = 0.5
ALPHA_EFFECT = 0.3
ALPHA_GOAL = 0.2

# ---- five graph-scanner error families (S_scan) ----
DEAD_RULE = "dead_rule"            # rule whose source unit is not in force / can never fire
DUPLICATE = "duplicate"            # repeated (s,p,o) edge or rule id
BROKEN_LINK = "broken_link"        # edge pointing at a unit not in the unit set
BLOCKING_CYCLE = "blocking_cycle"  # exception_of cycle => mutual blocking, nothing can fire
CONTRADICTION = "contradiction"    # two in-force contradictory rules, neither blocks the other

# ---- four-way conclusion on the extraction/abstention surface ----
CONCLUDED = "Concluded"
REFUTED = "Refuted"
INSUFFICIENT = "Insufficient Basis"
QUARANTINED = "Quarantined/Out-of-Scope"


class State(NamedTuple):
    """A legal state: a finite set of fluents (in-force codes + derived atoms)."""
    fluents: frozenset


class Rule(NamedTuple):
    """A (head :- body) defeasible rule bound to an in-force source unit."""
    rid: str
    source: str
    head: str
    body: tuple  # premise atoms (all must hold for the rule to apply)


class Step(NamedTuple):
    """One predicted reasoning step <s_{i-1}, a_i, s_i> produced by the LLM."""
    rid: str          # rule id being applied
    body: tuple       # premises the model claims hold
    add: str          # conclusion atom added
    blocks: tuple     # units this step blocks (destinations of exception_of(source, _))
    state: frozenset  # the model's claimed resulting state (fluents)


class ScanError(NamedTuple):
    """A graph-scanner finding."""
    kind: str
    object: str
    detail: str


class Feedback(NamedTuple):
    """Structured Detailed Verifier Feedback for one step / artifact."""
    step: int
    penalty: str        # "precondition" | "effect" | "goal"
    message: str
    fix_hint: str


def state_distance(s: State, t: State) -> int:
    """d_state(s, t) = |s △ t| = |s \\ t| + |t \\ s|."""
    return len(s.fluents ^ t.fluents)


def apply_action(state: State, step: Step, rule: Rule) -> State | None:
    """Return a_i(s_{i-1}) when the action is applicable, else None (precondition failure).

    Preconditions: every body atom holds in the current state AND the step's head/body
    match the rule under application. Effect: add the head, keep all existing fluents
    (blocking is captured as a label on later steps, not a fluent deletion).
    """
    if not set(step.body).issubset(state.fluents):
        return None
    if rule.head != step.add or rule.body != step.body:
        return None
    return State(frozenset(state.fluents | {step.add}))


def _contradict_pair(h1: str, h2: str) -> bool:
    """True when two rule heads are negation-opposites (one asserts, the other negates).

    Deterministic heuristic over natural-language heads: strip a leading negation marker
    ("không ", "không áp dụng ", "không được ", "bãi bỏ ") and compare the remainder.
    """
    a, b = (h1 or "").strip().lower(), (h2 or "").strip().lower()
    if not a or not b or a == b:
        return False
    for m in ("không áp dụng ", "không được ", "không ", "bãi bỏ "):
        if a.startswith(m) and a[len(m):] == b:
            return True
        if b.startswith(m) and b[len(m):] == a:
            return True
    return False


def scan_errors(units, edges_rows, rules, exceptions) -> list[ScanError]:
    """Deterministic graph scanner (S_scan). Reports the 5 error families.

    units: dict unit_id -> unit (or any iterable of unit ids).
    edges_rows: iterable of (s, p, o). rules: iterable of Rule. exceptions: (s, o) pairs.
    """
    errors: list[ScanError] = []
    unit_ids = set(units)

    seen_rids: set[str] = set()
    for r in rules:
        if r.source not in unit_ids:
            errors.append(ScanError(DEAD_RULE, r.rid, f"source {r.source} not in force"))
        elif not r.head:
            errors.append(ScanError(DEAD_RULE, r.rid, "empty head"))
        if r.rid in seen_rids:
            errors.append(ScanError(DUPLICATE, r.rid, "duplicate rule id"))
        seen_rids.add(r.rid)

    seen_edges: set[tuple] = set()
    for s, p, o in edges_rows:
        key = (s, p, o)
        if key in seen_edges:
            errors.append(ScanError(DUPLICATE, f"{s} {p} {o}", "repeated (s,p,o)"))
        seen_edges.add(key)
        if s not in unit_ids:
            errors.append(ScanError(BROKEN_LINK, f"{s} {p} {o}", f"source {s} unknown"))
        if o not in unit_ids:
            errors.append(ScanError(BROKEN_LINK, f"{s} {p} {o}", f"object {o} unknown"))

    graph_exc: dict[str, set[str]] = {}
    for s, o in exceptions:
        # exception_of(s, o) compiles to blocked(o); o MUST be an in-force unit. The source
        # s may legitimately be a condition node (C_<hash> from A6) or a synthetic implicit
        # exception node (unit.EX<n> from A8), so only the target is checked here.
        if o not in unit_ids:
            errors.append(ScanError(BROKEN_LINK, f"exception_of {s} {o}",
                                    f"target {o} is not an in-force unit"))
        elif s == o:
            errors.append(ScanError(BLOCKING_CYCLE, s, "self-exception"))
        elif s in unit_ids and o in unit_ids:
            graph_exc.setdefault(s, set()).add(o)

    for start in list(graph_exc):
        path, cur = [start], start
        while cur in graph_exc:
            nxt = sorted(graph_exc[cur])[0]
            if nxt in path:
                errors.append(ScanError(BLOCKING_CYCLE,
                                        " -> ".join(path[path.index(nxt):] + [nxt]),
                                        "mutual blocking cycle"))
                break
            path.append(nxt)
            cur = nxt
        else:
            continue
        break

    # contradiction: two in-force rules with opposite heads, neither blocking the other
    block_pairs = set(exceptions)
    for i in range(len(rules)):
        for j in range(i + 1, len(rules)):
            r1, r2 = rules[i], rules[j]
            if _contradict_pair(r1.head, r2.head):
                if (r1.source, r2.source) not in block_pairs and \
                        (r2.source, r1.source) not in block_pairs:
                    errors.append(ScanError(CONTRADICTION, f"{r1.rid} <-> {r2.rid}",
                                            f"opposite heads {r1.head!r} vs {r2.head!r}"))
                    break
        else:
            continue
        break
    return errors


def reward_sym(steps, goal, facts, rules, exceptions,
               alphas=(ALPHA_PRECOND, ALPHA_EFFECT, ALPHA_GOAL)) -> float:
    """R_sym(y|x) in [0,1] for a predicted chain y against facts/query x.

    steps: sequence of Step (the predicted chain). goal: atom or set of atoms.
    facts: initial fluents. rules: iterable/dict of Rule. exceptions: (s, o) pairs.
    """
    ap, ae, ag = alphas
    if not (0.0 <= ap + ae + ag <= 1.0 + 1e-9):
        raise ValueError("penalty weights must sum to <= 1")
    rule_by_id = {r.rid: r for r in rules}
    blocked_sources = {o for _, o in exceptions}
    state = State(frozenset(facts))
    n_pre, n_eff = 0, 0
    for step in steps:
        r = rule_by_id.get(step.rid)
        if r is None:
            n_pre += 1
            continue
        if not set(step.body).issubset(state.fluents):
            n_pre += 1
        if r.source in blocked_sources:
            n_pre += 1  # blocked source cannot fire
        nxt = apply_action(state, step, r)
        if nxt is None or nxt.fluents != step.state:
            n_eff += 1
        state = State(step.state)
    goals = set(goal) if not isinstance(goal, str) else {goal}
    n_goal = 0 if goals.issubset(state.fluents) else 1
    denom_pre = max(1, len(steps))
    reward = 1.0 - ap * (n_pre / denom_pre) - ae * (n_eff / denom_pre) - ag * n_goal
    return max(0.0, min(1.0, reward))


def classify(state: State, goals, quarantine_ids) -> str:
    """Map the final state to one of the four verdicts."""
    goals = set(goals) if not isinstance(goals, str) else {goals}
    qset = set(quarantine_ids)
    if any(g in qset for g in goals):
        return QUARANTINED
    if goals.issubset(state.fluents):
        return CONCLUDED
    if any(("blocked(" + g + ")") in state.fluents or ("refutes(" + g + ")") in state.fluents
           for g in goals):
        return REFUTED
    return INSUFFICIENT


def detailed_feedback(steps, goal, facts, rules, exceptions, found_errors) -> list[Feedback]:
    """Convert step errors + scanner errors into structured Detailed Feedback (alpha-tagged)."""
    fb: list[Feedback] = []
    blocked_sources = {o for _, o in exceptions}
    rule_by_id = {r.rid: r for r in rules}
    state = State(frozenset(facts))
    for i, step in enumerate(steps):
        r = rule_by_id.get(step.rid)
        if r is None:
            fb.append(Feedback(i, "precondition", f"unknown rule {step.rid}",
                               "apply only rules present in the knowledge base"))
            continue
        if not set(step.body).issubset(state.fluents):
            missing = ", ".join(sorted(set(step.body) - state.fluents))
            fb.append(Feedback(i, "precondition", f"premise(s) not established: {missing}",
                               f"establish the missing facts before applying {step.rid}"))
        if r.source in blocked_sources:
            fb.append(Feedback(i, "precondition", f"source {r.source} is blocked by an exception",
                               "do not fire a blocked rule; cite the defeating exception"))
        nxt = apply_action(state, step, r)
        if nxt is None or nxt.fluents != step.state:
            fb.append(Feedback(i, "effect", f"effect of {step.rid} mismatches claimed next state",
                               "recompute s_i = (s_{i-1} \\ del(a_i)) U add(a_i)"))
        state = State(step.state)
    goals = set(goal) if not isinstance(goal, str) else {goal}
    if not goals.issubset(state.fluents):
        fb.append(Feedback(len(steps), "goal", f"goal {sorted(goals)} not reached",
                           "continue the chain until the query is grounded"))
    PENALTY = {DEAD_RULE: "precondition", DUPLICATE: "effect", BROKEN_LINK: "effect",
               BLOCKING_CYCLE: "effect", CONTRADICTION: "effect"}
    for e in found_errors:
        fb.append(Feedback(-1, PENALTY.get(e.kind, "effect"),
                           f"[{e.kind}] {e.object}: {e.detail}",
                           "fix the knowledge base or quarantine the offending artifact"))
    return fb


def _parse_rule(r) -> Rule:
    return Rule(r.get("id", f"r_{r.get('source')}"), r.get("source", ""),
                r.get("head", ""), tuple(r.get("body", [])))


def load_knowledge(src, versions=None, date=None):
    """Return (units, edges_rows, rules, exceptions) for the bounded concept graph."""
    stem = Path(src).stem
    tag = ""
    if versions:
        vs = Path(versions).stem
        name = vs[len("a4_"):-len("_versions")] if vs.startswith("a4_") and vs.endswith("_versions") else vs
        tag = f"_{name}_{date}"
    units = edges.read_units(src)
    unit_ids = set(units)

    def _load(name):
        for p in (edges.PROCESSED_DIR / f"{name}_{stem}{tag}.jsonl",
                  edges.PROCESSED_DIR / f"{name}_{stem}.jsonl"):
            if p.exists():
                return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines()
                        if line.strip()]
        return []

    rules = [_parse_rule(r) for r in _load("a8_rules")]
    exceptions = []
    for name in ("a3_exceptions", "a6_exceptions", "a8_implicit_exceptions"):
        for r in _load(name):
            if r.get("s") and r.get("o"):
                exceptions.append((r.get("s"), r.get("o")))
    return unit_ids, edges.build_edges(units), rules, exceptions


def scan_from_pipeline(src, versions=None, date=None) -> tuple[list[ScanError], set]:
    """Load the real blds2015 pipeline artifacts and run the 5-family scanner over them."""
    unit_ids, edges_rows, rules, exceptions = load_knowledge(src, versions, date)
    return scan_errors(unit_ids, edges_rows, rules, exceptions), unit_ids


def run(src, versions=None, date=None):
    """Scan the pipeline, print the 5 error-family counts and a sample, return exit code."""
    from collections import Counter
    errs, unit_ids = scan_from_pipeline(src, versions, date)
    counts = Counter(e.kind for e in errs)
    print("S_scan (5 error families):")
    for kind in (DEAD_RULE, DUPLICATE, BROKEN_LINK, BLOCKING_CYCLE, CONTRADICTION):
        print(f"  {kind}: {counts.get(kind, 0)}")
    for e in errs[:10]:
        print(f"    - {e.kind} {e.object} :: {e.detail}")
    print(f"units scanned: {len(unit_ids)} | total errors: {len(errs)}")
    return 0 if not errs else 1


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Deterministic symbolic legal verifier scan")
    ap.add_argument("src", help="source md file, used to derive the stem")
    ap.add_argument("--versions", help="a4_<name>_versions.jsonl (optional)")
    ap.add_argument("--date", help="YYYY-MM-DD, required with --versions")
    args = ap.parse_args(argv)
    if (args.versions is None) != (args.date is None):
        ap.error("--versions and --date must be passed together")
    return run(args.src, args.versions, args.date)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())