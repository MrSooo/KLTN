import subprocess, sys

# Git show for v3_refactor KB files
files = [
    'data/processed/a9_lld2019_labor.pl',
    'data/processed/a9_lld2019_labor.txt',
    'data/labor/eval_nested_exceptions.jsonl',
    'data/labor/concept_book.json',
]

for f in files:
    try:
        cp = subprocess.run(
            ['git', 'show', f'origin/v3_refactor:{f}'],
            capture_output=True, text=True, timeout=30
        )
        print(f"=== {f} ===")
        print((cp.stdout or "")[:2000])
        print(f"RC={cp.returncode}")
    except Exception as e:
        print(f"=== {f} === ERROR: {e}")
    print()
PYTHON_SCRIPT