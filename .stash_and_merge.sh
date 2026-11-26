#!/bin/bash
cd /mnt/e/KLTN
export GIT_MERGE_AUTOEDIT=no
export GIT_EDITOR=true

echo "=== STASHING CHANGES ==="
git stash push -u -m "pre-merge-stash-$(date +%Y%m%d-%H%M%S)"
STASH_RC=$?
echo "STASH_EXIT=$STASH_RC"

if [ $STASH_RC -ne 0 ]; then
  echo "STASH FAILED"
  exit 1
fi

echo "=== RUNNING MERGE ==="
git merge origin/v3_refactor --no-ff --no-edit -m "merge(v3_refactor): sync teammate Tu refactored pipeline with neuro-symbolic legal CoT"
MERGE_RC=$?
echo "MERGE_EXIT=$MERGE_RC"

if [ $MERGE_RC -ne 0 ]; then
  echo "=== CONFLICTS DETECTED ==="
  git diff --name-only --diff-filter=U
  git status --short
else
  echo "=== MERGE SUCCESSFUL ==="
  git log --oneline -5
fi
