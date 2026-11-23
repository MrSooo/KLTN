import sys, json
sys.path.insert(0, "src")
import cot_rule_extractor as cot
import symbolic_legal_verifier as verifier

# 1) prompt build (deterministic)
sp = cot.system_prompt()
assert "chuyển trạng thái" in sp and "BLDS2015.D644" in sp
cp = cot.chain_prompt("A có được hưởng 2/3 suất không?", 2, ("fact(X)",))
assert "d = 2" in cp and "fact(X)" in cp
print("prompt build OK")

# 2) valid payload parse -> Step
valid = json.dumps({"verdict": "Concluded", "steps": [{
    "step": 1, "rule_id": "BLDS2015.D644.K1.R1",
    "premises": ["fact(X)", "fact(Y)"], "conclusion": "holds(X)",
    "blocks": ["BLDS2015.D644.K1"],
    "resulting_state": ["fact(X)", "fact(Y)", "holds(X)"],
    "exception_depth": 1}]})
steps, verdict, problems = cot.parse_chain(valid)
assert verdict == "Concluded" and len(steps) == 1 and not problems
assert isinstance(steps[0], verifier.Step) and steps[0].rid == "BLDS2015.D644.K1.R1"
print("valid parse OK:", steps[0].rid)

# 3) malformed payload -> quarantine, no crash
bad = json.dumps({"steps": [{"step": 1, "rule_id": "X", "premises": "not-a-list"}]})
steps, verdict, problems = cot.parse_chain(bad)
assert not steps and problems
print("malformed -> quarantined OK:", problems[0].reason)

# 4) deterministic fallback when LLM disabled (monkeypatch, no network)
cot.llm.enabled = lambda: False
steps, verdict, problems = cot.extract_chain("hỏi", depth=2, facts=("fact(X)",))
assert steps == [] and verdict == "" and problems == []
print("LLM-disabled deterministic fallback OK")

print("ALL COT SMOKE TESTS PASSED")