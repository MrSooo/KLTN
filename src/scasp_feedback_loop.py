"""S_repair: the eta-iteration verifier-guided repair loop.

Orchestration: extract a concept-bounded legal CoT chain (S_cot), verify it (V_legal),
turn every failure into structured Detailed Feedback, and re-prompt the LLM for up to
eta in {1,2,3} iterations. Feeds the graph-scanner errors and s(CASP) blocking semantics
from symbolic_legal_verifier back into the prompt, so each round repairs preconditions,
effects, and goal attainment (PDDL-INSTRUCT alpha_precond/alpha_effect/alpha_goal).

Contract: LLM unconfigured => empty result with iterations=0 (never a guessed conclusion).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I mode: sibling imports
import llm  # noqa: E402
import symbolic_legal_verifier as verifier  # noqa: E402
import cot_rule_extractor as cot  # noqa: E402


def format_feedback(feedback_items) -> str:
    """Render Detailed Feedback items as a compact, re-injectable text block."""
    lines = []
    for f in feedback_items:
        step = f.step if f.step is not None and f.step >= 0 else "-"
        lines.append(f"[{f.penalty}|step {step}] {f.message} => {f.fix_hint}")
    return "\n".join(lines) or "(không có phản hồi)"


def repair(question, goal, facts=(), rules=(), exceptions=(),
           units=(), edges_rows=(), depth=2, eta=2, temperature=0.0):
    """Run the eta-iteration symbolic feedback loop.

    Returns a dict:
      best_reward, steps, verdict, iterations, history (per-round reward+feedback),
      and note (set when the LLM is disabled).
    """
    if depth not in (1, 2, 3):
        raise ValueError("depth must be in {1,2,3}")
    if eta not in (1, 2, 3):
        raise ValueError("eta must be in {1,2,3}")

    if not llm.enabled():
        return {"best_reward": 0.0, "steps": [], "verdict": "",
                "iterations": 0, "history": [], "note": "LLM disabled"}

    goals = goal
    prompt_base = cot.chain_prompt(question, depth, facts)
    fb_text = ""
    best_reward, best_steps, best_verdict = 0.0, [], ""
    history = []

    for it in range(1, eta + 1):
        prompt = prompt_base
        if fb_text:
            prompt += "\n\nPHẢN HỒI CHI TIẾT (vòng trước, hãy sửa):\n" + fb_text
        raw = llm.complete(prompt, system=cot.system_prompt(), temperature=temperature)
        steps, verdict, problems = cot.parse_chain(raw, source=question[:60])

        errors = verifier.scan_errors(units, edges_rows, rules, exceptions)
        reward = verifier.reward_sym(steps, goals, facts, rules, exceptions)
        fb = verifier.detailed_feedback(steps, goals, facts, rules, exceptions, errors)
        history.append({"iteration": it, "reward": reward,
                        "feedback": [f._asdict() if hasattr(f, "_asdict") else f for f in fb]})

        if reward >= best_reward:
            best_reward, best_steps, best_verdict = reward, steps, verdict
        if reward >= 1.0 or not fb:
            break
        fb_text = format_feedback(fb)

    return {"best_reward": best_reward, "steps": best_steps, "verdict": best_verdict,
            "iterations": len(history), "history": history}


def run(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Verifier-guided symbolic feedback loop (eta iterations)")
    ap.add_argument("question", help="legal question to reason about")
    ap.add_argument("--src", default="data/raw/blds2015_p4.md",
                    help="source md that anchors the bounded concept graph (default p4)")
    ap.add_argument("--goal", action="append", default=[], help="repeatable --goal <atom>")
    ap.add_argument("--fact", action="append", default=[], help="repeatable --fact <atom>")
    ap.add_argument("--depth", type=int, choices=(1, 2, 3), default=2)
    ap.add_argument("--eta", type=int, choices=(1, 2, 3), default=2)
    args = ap.parse_args(argv)

    units, edges_rows, rules, exceptions = verifier.load_knowledge(args.src)
    result = repair(args.question, set(args.goal), facts=tuple(args.fact),
                    rules=rules, exceptions=exceptions, units=units, edges_rows=edges_rows,
                    depth=args.depth, eta=args.eta)
    print(json.dumps({
        "question": args.question, "verdict": result["verdict"],
        "best_reward": round(result["best_reward"], 4),
        "iterations": result["iterations"], "steps": len(result["steps"]),
        "note": result.get("note", ""),
        "history": [{"iteration": h["iteration"], "reward": round(h["reward"], 4)}
                    for h in result["history"]]},
        ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(run())