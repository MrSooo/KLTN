#!/bin/bash
set -e
cd /mnt/e/KLTN

echo "=== CHECKING MERGE_HEAD ==="
if [ -f .git/MERGE_HEAD ]; then
    echo "MERGE_HEAD exists - merge in progress"
    cat .git/MERGE_HEAD
else
    echo "No MERGE_HEAD - no merge in progress"
fi

echo ""
echo "=== CURRENT HEAD ==="
git rev-parse HEAD
git log --oneline -1

echo ""
echo "=== ATTEMPTING MERGE ==="
git merge origin/v3_refactor --no-ff -m "merge(v3_refactor): sync teammate Tu refactored pipeline with neuro-symbolic legal CoT" 2>&1 || {
    echo "MERGE FAILED with exit code $?"
    echo "Checking for conflicts..."
    git status --short
    exit 1
}

echo ""
echo "=== MERGE SUCCESSFUL ==="
git log --oneline -5
echo ""
git status --short
