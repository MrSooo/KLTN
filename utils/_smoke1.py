import sys
sys.path.insert(0, "src")
import symbolic_legal_verifier as v

# Smoke test the core primitives.
s0 = v.State(frozenset({"in_force(BLDS2015.D644.K1)", "facts(X)", "facts(Y)"}))
r1 = v.Rule("BLDS2015.D644.K1.R1", "BLDS2015.D644.K1", "holds(X)", ("facts(X)", "facts(Y)"))
step = v.Step("BLDS2015.D644.K1.R1", ("facts(X)", "facts(Y)"), "holds(X)", (), frozenset({
    "in_force(BLDS2015.D644.K1)", "facts(X)", "facts(Y)", "holds(X)"}))
r = v.apply_action(s0, step, r1)
assert r is not None and "holds(X)" in r.fluents, r

print("state_distance(s0, s1) =", v.state_distance(s0, r))
rew = v.reward_sym([step], "holds(X)", {"in_force(BLDS2015.D644.K1)", "facts(X)", "facts(Y)"},
                  [r1], [])
print("R_sym(valid chain) =", rew)
assert rew == 1.0, rew

verdict = v.classify(r, {"holds(X)"}, [])
print("classify =", verdict)
assert verdict == v.CONCLUDED

# Scanner: dead rule + broken link + blocking cycle.
units = {"A", "B", "C"}
rules = [v.Rule("r1", "A", "h1", ()), v.Rule("dead", "Z", "h", ())]
edges_rows = [("A", "contains", "B"), ("A", "contains", "Z")]
exceptions = [("A", "B"), ("B", "C"), ("C", "A")]
errs = v.scan_errors(units, edges_rows, rules, exceptions)
kinds = sorted({e.kind for e in errs})
print("scan kinds =", kinds)
assert v.DEAD_RULE in kinds and v.BROKEN_LINK in kinds and v.BLOCKING_CYCLE in kinds

fb = v.detailed_feedback([step], "holds(X)", {"in_force(BLDS2015.D644.K1)", "facts(X)", "facts(Y)"}, [r1], [], errs)
print("feedback items =", len(fb))
assert fb, "expected feedback"

print("ALL SMOKE TESTS PASSED")