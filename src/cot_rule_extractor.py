"""S_cot: Concept-Bounded Legal Logical CoT extractor (prompt templates + deterministic parser).

Forces the LLM to emit explicit legal state transitions <s_{i-1}, a_i, s_i> across
exception depths d in {1, 2, 3}, bounded by a Concept Book for Articles 621/626/644
(eligibility to inherit, the testator's rights, and compulsory heirs). The chain can
then be scored by symbolic_legal_verifier.reward_sym and repaired by scasp_feedback_loop.

Contract mirrors knowledge_layer: the payload is schema-checked, anything malformed is
quarantined, and an unconfigured LLM yields an empty (deterministic) chain — never a guess.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I mode: sibling imports
import llm  # noqa: E402

# ---- Bounded Concept Graph (Concept Book) for the inheritance corpus ----
# Authorised concepts (the only atoms the CoT may introduce) + the 5 provision anchors.
CONCEPT_BOOK = {
    "articles": ("BLDS2015.D621", "BLDS2015.D626", "BLDS2015.D644"),
    "concepts": (
        "quyền hưởng di sản",                 # right to inherit
        "quyền của người lập di chúc",        # testator's rights
        "người thừa kế không phụ thuộc di chúc",  # compulsory heir
        "hai phần ba suất thừa kế",           # 2/3 of a statutory share
        "không được quyền hưởng di sản",      # ineligible to inherit
        "từ chối nhận di sản",                # refusal of inheritance
        "truất quyền hưởng di sản",           # disinheritance
        "phân định phần di sản",              # apportionment of shares
        "di tặng", "thờ cúng",                # gift / worship reservation
        "giao nghĩa vụ",                      # impose obligations
    ),
    "exception_depths": ("1", "2", "3"),
}

# Provision anchors with their normative meaning, for grounding the prompt. (Not legal
# advice; mirrors the statute's own headings used throughout src/ knowledge extraction.)
ARTICLE_BOOK = {
    "BLDS2015.D621": "Người không được quyền hưởng di sản (bị kết án xâm phạm tính mạng, "
                     "ngược đãi, vi phạm nghĩa vụ nuôi dưỡng).",
    "BLDS2015.D626": "Quyền của người lập di chúc (chỉ định người thừa kế, truất quyền, "
                     "phân định phần di sản, di tặng/thờ cúng, giao nghĩa vụ).",
    "BLDS2015.D644": "Người thừa kế không phụ thuộc vào nội dung của di chúc "
                     "(hai phần ba suất; không áp dụng với người từ chối nhận di sản "
                     "hoặc không được quyền hưởng di sản).",
}

DEPTH_HINT = {
    1: "lớp quy tắc gốc (vd. Điều 644 khoản 1: người hưởng 2/3 suất)",
    2: "lớp ngoại lệ (vd. Điều 644 khoản 2: không áp dụng với Điều 620/621)",
    3: "lớp ngoại lệ lồng (căn Điều 620 hoặc Điều 621 để chặn hoặc khôi phục kết luận)",
}


class Problem(NamedTuple):
    """A quarantined/malformed CoT payload record (mirrors knowledge_layer.problems)."""
    source: str
    kind: str
    row: str
    reason: str


def system_prompt():
    anchors = "\n".join(f"- {k}: {ARTICLE_BOOK[k]}" for k in CONCEPT_BOOK["articles"])
    concepts = ", ".join(CONCEPT_BOOK["concepts"])
    return (
        "Bạn là một kỹ sư pháp lý hình thức. Trả về ĐÚNG MỘT đối tượng JSON thuần "
        "(không markdown, không giải thích) theo lược đồ:\n"
        '{"steps":[{"step":<int>,"rule_id":"<mã quy tắc, vd BLDS2015.D644.K1.R1>",'
        '"premises":["<nguyên tử đã được chứng minh>"],'
        '"conclusion":"<kết luận>","blocks":["<mã đơn vị bị chặn>"],'
        '"resulting_state":["<tập nguyên tử sau bước>"],"exception_depth":<1|2|3>}],"'
        '"verdict":"Concluded|Refuted|Insufficient Basis|Quarantined/Out-of-Scope"}\n'
        "Mỗi bước là một chuyển trạng thái pháp lý hiện s_{i} = a_i(s_{i-1}) = "
        "(s_{i-1} \\ del(a_i)) ∪ add(a_i): premises là điều kiện trước khi áp quy tắc, "
        "conclusion là kết luận được thêm, resulting_state là tập nguyên tử đầy đủ sau bước.\n"
        "Chỉ dùng các khái niệm trong sách khái niệm: [" + concepts + "].\n"
        "Các điều neo:\n" + anchors + "\n"
        "Không bịa quy tắc: chỉ áp quy tắc có mã nằm trong văn bản. Không có bước nào thì steps = []."
    )


def chain_prompt(question, depth, facts=()):
    """Build the user prompt forcing explicit state transitions <s_{i-1}, a_i, s_i>."""
    facts_txt = "\n".join(f"- {f}" for f in facts) or "(không có)"
    return (
        f"Câu hỏi: {question}\n"
        f"Độ sâu ngoại lệ yêu cầu: d = {depth} ({DEPTH_HINT.get(depth, '')})\n"
        "Sự kiện đã biết:\n" + facts_txt + "\n\n"
        "Hãy lập chuỗi lập luận pháp lý dạng chuyển trạng thái ⟨s_{i-1}, a_i, s_i⟩, "
        "tối đa ở lớp ngoại lệ d nói trên, rồi cho kết luận cuối (verdict)."
    )


def parse_chain(raw, source="question"):
    """Schema-check one CoT payload; return (steps, verdict, problems).

    steps are symbolic_legal_verifier.Step (rid, body, add, blocks, state). Malformed
    payloads never crash — they become Problem records (quarantine) instead.
    """
    import symbolic_legal_verifier as verifier

    steps, verdict, problems = [], "", []
    if not raw:
        return steps, verdict, problems
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        problems.append(Problem(source, "package", raw, f"JSON hỏng ({e})"))
        return [], "", problems
    verdict = data.get("verdict", "") if isinstance(data, dict) else ""
    for row in data.get("steps", []) if isinstance(data, dict) else []:
        if not isinstance(row, dict):
            problems.append(Problem(source, "step", json.dumps(row, ensure_ascii=False),
                                    "step không phải đối tượng"))
            continue
        need = ("rule_id", "premises", "conclusion", "blocks", "resulting_state")
        if any(k not in row for k in need):
            problems.append(Problem(source, "step", json.dumps(row, ensure_ascii=False),
                                    f"thiếu khoá {'/'.join(need)}"))
            continue
        if any(not isinstance(row[k], list) for k in ("premises", "blocks", "resulting_state")):
            problems.append(Problem(source, "step", json.dumps(row, ensure_ascii=False),
                                    "premises/blocks/resulting_state phải là danh sách"))
            continue
        depth = row.get("exception_depth")
        if depth not in (1, 2, 3):
            problems.append(Problem(source, "step", json.dumps(row, ensure_ascii=False),
                                    "exception_depth phải là 1|2|3"))
            continue
        steps.append(verifier.Step(
            row["rule_id"], tuple(row["premises"]), row["conclusion"],
            tuple(row["blocks"]), frozenset(row["resulting_state"])))
    return steps, verdict, problems


def extract_chain(question, depth=1, facts=(), temperature=0.0):
    """Produce a concept-bounded CoT chain for a question. Returns (steps, verdict, problems).

    Deterministic fallback: when the LLM is unconfigured, returns an empty chain and lets
    the caller (scasp_feedback_loop) decide — it never invents a legal step.
    """
    if depth not in (1, 2, 3):
        raise ValueError("depth must be in {1,2,3}")
    if not llm.enabled():
        return [], "", []
    raw = llm.complete(chain_prompt(question, depth, facts), system=system_prompt(),
                       temperature=temperature)
    if not raw:
        return [], "", []
    return parse_chain(raw, source=question[:60])


def run(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Concept-bounded legal CoT extractor")
    ap.add_argument("question", help="legal question to reason about")
    ap.add_argument("--depth", type=int, choices=(1, 2, 3), default=2,
                    help="max exception depth to request (default 2)")
    ap.add_argument("--fact", action="append", default=[], help="repeatable --fact <atom>")
    args = ap.parse_args(argv)
    steps, verdict, problems = extract_chain(args.question, args.depth, tuple(args.fact))
    print(f"verdict: {verdict or '(empty)'} | depth: {args.depth} | steps: {len(steps)} | problems: {len(problems)}")
    for i, s in enumerate(steps, 1):
        print(f"  s_{i-1} -> [{s.rid}] -> s_{i}: {sorted(s.state)}")
    for p in problems:
        print(f"  [quarantine] {p.source} :: {p.reason}")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(run())