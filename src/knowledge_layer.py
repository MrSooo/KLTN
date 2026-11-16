"""A8 (S_know): the knowledge layer.

Reads the affected set A(d) — the units in force at date d — and uses the LLM to extract:
  - propositions and their predicates P, each categorized "concept" or "input";
  - implicit exception_of edges (events that disable a rule without being spelled out);
  - inference rules R (head = conclusion, body = list of conditions).
Every LLM output must pass validation; invalid items are moved to the quarantine set Q (kept out of A9).

Input: A1 triples (edges.read_units); optionally A4 output at a date (--versions a4_<name>_versions.jsonl --date YYYY-MM-DD).
Output (data/processed/):
  a8_propositions_<stem>.jsonl, a8_predicates_<stem>.jsonl, a8_implicit_exceptions_<stem>.jsonl,
  a8_rules_<stem>.jsonl, a8_quarantine_<stem>.jsonl and docs/a8_report_<stem>.txt.
When the LLM is unconfigured: extract nothing, write empty files + a note, leave A1-A7 unchanged.

Run: python -I src/knowledge_layer.py <file md> [--versions a4_<name>_versions.jsonl --date YYYY-MM-DD]
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I mode: add the script dir for sibling imports
import edges
import versioning as versioning
import llm

ROOT = edges.ROOT
OUT_DIR = edges.PROCESSED_DIR
DOCS_DIR = ROOT / "docs"

CATEGORIES = ("concept", "input")
METHOD = "implicit"

_SYSTEM = (
    "Bạn phân tích một đơn vị văn bản luật Việt Nam. Trả về ĐÚNG MỘT đối tượng JSON thuần "
    "(không markdown, không giải thích) theo lược đồ:\n"
    '{"propositions":[{"id":"<mã mệnh đề>","text":"<mệnh đề>",'
    '"predicates":[{"subject":"<chủ thể>","predicate":"<vị từ>","category":"concept|input"}],'
    '"source":"<mã đơn vị>"}],'
    '"implicit_exceptions":[{"s":"<mã ngoại lệ>","o":"<mã quy tắc bị ngoại trừ, phải là mã đơn vị đang hiệu lực>",'
    '"evidence":"<đoạn chữ ngầm ngoại lệ>","method":"implicit"}],'
    '"rules":[{"id":"<mã quy tắc>","head":"<kết luận>","body":["<điều kiện>"],"source":"<mã đơn vị>","text":"<chữ luật>"}]}\n'
    "category chỉ nhận 'concept' hoặc 'input'. Mỗi đơn vị có thể có nhiều mệnh đề; không có loại nào thì trả []."
)


def _tag(versions, date):
    if versions is None:
        return None
    stem = Path(versions).stem
    m = re.fullmatch(r"a4_(.+)_versions", stem)
    name = m.group(1) if m else stem
    return f"{name}_{date}"


def propositions_path(src, tag=None):
    return OUT_DIR / f"a8_propositions_{Path(src).stem}{'_' + tag if tag else ''}.jsonl"


def predicates_path(src, tag=None):
    return OUT_DIR / f"a8_predicates_{Path(src).stem}{'_' + tag if tag else ''}.jsonl"


def implicit_exceptions_path(src, tag=None):
    return OUT_DIR / f"a8_implicit_exceptions_{Path(src).stem}{'_' + tag if tag else ''}.jsonl"


def rules_path(src, tag=None):
    return OUT_DIR / f"a8_rules_{Path(src).stem}{'_' + tag if tag else ''}.jsonl"


def quarantine_path(src, tag=None):
    return OUT_DIR / f"a8_quarantine_{Path(src).stem}{'_' + tag if tag else ''}.jsonl"


def report_path(src, tag=None):
    return DOCS_DIR / f"a8_report_{Path(src).stem}{'_' + tag if tag else ''}.txt"


def active_units(src, versions=None, date=None):
    """{unit id: {"type":..., "text":...}} for the in-force units (text-bearing only)."""
    if versions is None:
        units = edges.read_units(src)
        return {c: {"type": u.get("type"), "text": u.get("text")}
                for c, u in units.items() if u.get("text")}
    rows = versioning.read_jsonl(versions)
    active = versioning.active_rows(rows, date)
    return {r["id"]: {"type": r["type"], "text": r.get("text")}
            for r in active if r.get("text")}

def validate_package(data, code, unit_ids, seen_prop, problems, out):
    """Validate one unit's LLM JSON package; bad items go to problems (set Q), valid ones to out."""
    if not isinstance(data, dict):
        problems.append({"source": code, "kind": "package", "row": data, "reason": "gói không phải object"})
        return
    for prop in data.get("propositions", []) or []:
        if not isinstance(prop, dict) or not prop.get("id") or not prop.get("text"):
            problems.append({"source": code, "kind": "proposition", "row": prop, "reason": "thiếu id/text"})
            continue
        if prop["id"] in seen_prop:
            problems.append({"source": code, "kind": "proposition", "row": prop, "reason": f"id {prop['id']!r} trùng"})
            continue
        preds = prop.get("predicates", []) or []
        bad = [p for p in preds if not isinstance(p, dict) or not p.get("subject")
               or not p.get("predicate") or p.get("category") not in CATEGORIES]
        if bad:
            problems.append({"source": code, "kind": "predicate", "row": bad, "reason": "vị từ sai cấu trúc/category"})
            continue
        seen_prop.add(prop["id"])
        out["propositions"].append(prop)
        for p in preds:
            out["predicates"].append({"s": prop["id"], "subject": p["subject"],
                                      "predicate": p["predicate"], "category": p["category"], "source": code})
    for ex in data.get("implicit_exceptions", []) or []:
        if not isinstance(ex, dict) or not ex.get("s") or not ex.get("o"):
            problems.append({"source": code, "kind": "implicit_exception", "row": ex, "reason": "thiếu s/o"})
            continue
        if ex["o"] not in unit_ids:
            problems.append({"source": code, "kind": "implicit_exception", "row": ex,
                             "reason": f"đích {ex['o']!r} không phải đơn vị đang hiệu lực"})
            continue
        out["implicit_exceptions"].append({"s": ex["s"], "p": "exception_of", "o": ex["o"],
                                           "evidence": ex.get("evidence", ""), "method": METHOD, "source": code})
    for rule in data.get("rules", []) or []:
        body = rule.get("body", []) or []
        if not isinstance(rule, dict) or not rule.get("head") or not body or not isinstance(body, list) \
           or any(not isinstance(b, str) or not b for b in body):
            problems.append({"source": code, "kind": "rule", "row": rule, "reason": "head/body sai cấu trúc"})
            continue
        if rule.get("source", code) not in unit_ids:
            problems.append({"source": code, "kind": "rule", "row": rule, "reason": "source không hợp lệ"})
            continue
        rule.setdefault("id", f"r_{code.replace('.', '_')}_{len(out['rules']) + 1}")
        rule["source"] = rule.get("source", code)
        out["rules"].append(rule)


def write_jsonl(rows, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_text(text, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)

def run(src, versions=None, date=None):
    """Extract the knowledge layer, validate, write files; exit 0 when nothing lands in Q."""
    stem = Path(src).stem
    tag = _tag(versions, date)
    units = active_units(src, versions, date)
    out = {"propositions": [], "predicates": [], "implicit_exceptions": [], "rules": []}
    problems, seen_prop = [], set()

    if units and llm.enabled():
        for code, u in units.items():
            prompt = f"Mã đơn vị: {code}\nVăn bản:\n{u['text']}"
            raw = llm.complete(prompt, system=_SYSTEM, temperature=0.0)
            if not raw:
                continue
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as e:
                problems.append({"source": code, "kind": "package", "row": raw, "reason": f"JSON hỏng ({e})"})
                continue
            validate_package(data, code, set(units), seen_prop, problems, out)

    write_jsonl(out["propositions"], propositions_path(src, tag))
    write_jsonl(out["predicates"], predicates_path(src, tag))
    write_jsonl(out["implicit_exceptions"], implicit_exceptions_path(src, tag))
    write_jsonl(out["rules"], rules_path(src, tag))
    write_jsonl(problems, quarantine_path(src, tag))

    lines = [f"A8 báo cáo tầng tri thức: {stem}" + (f" (tại {date})" if tag else ""),
             "file đã đọc: " + ("a1_triples" if versions is None else str(versions)),
             f"đơn vị đang hiệu lực có text: {len(units)}",
             f"LLM: {'bật' if llm.enabled() else 'TẮT (không trích gì)'}",
             "", "== Kết quả ==",
             f"mệnh đề: {len(out['propositions'])} | vị từ: {len(out['predicates'])}",
             f"cạnh exception_of ngầm: {len(out['implicit_exceptions'])} | quy tắc R: {len(out['rules'])}",
             f"tập cách ly Q: {len(problems)}",
             "", "== Kiểm định ==",
             "KẾT LUẬN: " + ("KHÔNG ĐẠT (có đầu ra LLM bị cách ly)" if problems else "ĐẠT")]
    text = "\n".join(lines) + "\n"
    print(text, end="")
    write_text(text, report_path(src, tag))
    print("đã ghi", report_path(src, tag))
    return 1 if problems else 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="file md nguồn, dùng để suy stem của file triples A1")
    ap.add_argument("--versions", help="a4_<name>_versions.jsonl; có thì trích trên các đơn vị đang hiệu lực tại --date")
    ap.add_argument("--date", help="YYYY-MM-DD, đi cùng --versions")
    args = ap.parse_args(argv)
    if (args.versions is None) != (args.date is None):
        ap.error("--versions và --date phải đi cùng nhau")
    if args.date is not None:
        args.date = versioning.parse_iso(args.date).isoformat()
    return run(args.path, args.versions, args.date)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())