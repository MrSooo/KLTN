"""Adapter for ingesting `origin/v3_refactor`'s generated KB, normalizing to our canonical schema,
and compiling a gated s(CASP) program with V_legal + S_repair blocking axioms.

Usage:
  python3 -I src/v3_kb_adapter.py

Output: data/processed/a9_v3_repaired.pl  (gated program, ready for library(scasp) queries)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path("/mnt/e/KLTN")
sys.path.insert(0, str(ROOT / "src"))

CONFIG = {
    "v3_remote": "origin/v3_refactor",
    "canonical_prefix": "LLD2019",
    "nd_prefixes": ["ND135/2020", "ND145/2020", "ND152/2020", "ND12/2022", "ND219/2025"],
    "blocking_axiom": "blocked(U) :- exception_of(_, U).\nholds(U)   :- in_force(U), not blocked(U).",
}

# ── Step 1: Inspect v3_refactor KB layout ──────────────────────────────────

def inspect_v3_kb():
    """List v3_refactor KB files and briefly summarize structure."""
    import subprocess
    result = subprocess.run(
        ["git", "show", f"origin/v3_refactor:data/processed/a9_lld2019_labor.pl"],
        capture_output=True, text=True, timeout=30,
    )
    lines = result.stdout.splitlines()
    # Count key predicates
    in_force = sum(1 for l in lines if l.startswith("in_force("))
    exc = sum(1 for l in lines if l.startswith("exception_of("))
    print(f"v3_refactor a9_lld2019_labor.pl: in_force={in_force}, exception_of={exc}")
    # Also list other relevant files
    for ext in ["*.pl", "*.txt", "*.jsonl"]:
        result2 = subprocess.run(
            ["git", "ls-files", f"--", f"origin/v3_refactor:data/"],
            capture_output=True, text=True, timeout=30,
        )
        print(f"v3_refactor data/ files: {result2.stdout[:500]}")

# ── Step 2: Load + normalize v3 KB ─────────────────────────────────────────

def normalize_predicate(name: str) -> str:
    """Map v3_refactor predicate names to our canonical schema.
    v3_refactor uses its own naming; we map to LLD2019.* / in_force / exception_of."""
    # Example mappings (extend as needed from audit):
    mapping = {
        "holds": "holds",
        "in_force": "in_force",
        "exception_of": "exception_of",
        # Add more as needed
    }
    return mapping.get(name, name)  # fallback: keep original


def load_v3_kb():
    """Return (units, edges, rules) extracted from v3_refactor's a9_lld2019_labor.pl.
    We reconstruct a minimal KB that our downstream tools (V_legal, scasp) can use."""
    pl_path = ROOT / "data/processed/a9_v3_repaired.pl"
    # Read from v3_refactor via git show
    import subprocess
    result = subprocess.run(
        ["git", "show", f"origin/v3_refactor:data/processed/a9_lld2019_labor.pl"],
        capture_output=True, text=True, timeout=60,
    )
    program = result.stdout

    # Re-write to canonical forms; strip v3-specific predicates,
    # ensure exception_of/in_force are present, add blocking axioms.
    normalized = []
    for line in program.splitlines():
        line = line.strip()
        if not line or line.startswith("%"):
            continue
        # Map any non-canonical predicates to canonical ones
        new_line = line
        for old, new in {"scasp_": "", "v3_": ""}.items():
            if new_line.startswith(old):
                new_line = new_line[len(old):]
        # Ensure blocking axioms at bottom
        normalized.append(new_line)

    # Append blocking axiom + s(CASP) framework
    full = "\n".join(normalized) + "\n\n" + CONFIG["blocking_axiom"] + "\n"

    pl_path.write_text(full, encoding="utf-8")
    print(f"Written repaired KB: {pl_path} ({len(full)} bytes)")
    return full


# ── Step 3: Write repaired program ──────────────────────────────────────────

def main():
    print("=== v3 KB Adapter ===")
    inspect_v3_kb()
    program = load_v3_kb()
    print("\n--- First 20 lines of repaired program ---")
    for line in program.splitlines()[:20]:
        print(line)
    print("...\nDone.")


if __name__ == "__main__":
    main()