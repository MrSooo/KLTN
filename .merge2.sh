#!/bin/bash
cd /mnt/e/KLTN
export GIT_MERGE_AUTOEDIT=no
export GIT_EDITOR=true
echo "=== PRE-MERGE STATUS ==="
git status --short
echo "=== RUNNING MERGE ==="
git merge origin/v3_refactor --no-ff --no-edit -m "merge(v3_refactor): sync teammate Tu refactored pipeline with neuro-symbolic legal CoT"
MERGE_RC=$?
echo "MERGE_EXIT=$MERGE_RC"
if [ $MERGE_RC -ne 0 ]; then
  echo "=== CONFLICTS DETECTED ==="
  git diff --name-only --diff-filter=U
  git status --short
fi
echo "=== POST-MERGE LOG ==="
git log --oneline -5
