import sys
sys.path.insert(0, "src")
import scasp_feedback_loop as loop
import llm

# Deterministic path: LLM disabled => iterations=0, no crash, no network.
llm.enabled = lambda: False
r = loop.repair("A được hưởng bao nhiêu?", {"holds(A_2/3_suat)"})
assert r["iterations"] == 0 and r["best_reward"] == 0.0 and r["steps"] == []
assert r["note"] == "LLM disabled"
print("repair (LLM disabled) OK:", r)

# format_feedback renders alpha-tagged items.
import symbolic_legal_verifier as v
fb = [v.Feedback(0, "precondition", "premise missing", "add facts"),
      v.Feedback(1, "effect", "effect mismatch", "recompute")]
txt = loop.format_feedback(fb)
assert "[precondition|step 0]" in txt and "[effect|step 1]" in txt
print("format_feedback OK:")
print(txt)

# repair rejects bad eta/depth.
for bad_kwds in ({"eta": 5}, {"depth": 4}):
    try:
        loop.repair("x", {"g"}, **bad_kwds)
        raise AssertionError("should have raised")
    except ValueError:
        pass
print("eta/depth validation OK")

print("ALL FEEDBACK-LOOP SMOKE TESTS PASSED")