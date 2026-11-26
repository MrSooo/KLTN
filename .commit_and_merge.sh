#!/bin/bash
cd /mnt/e/KLTN
export GIT_EDITOR=true

echo "=== ADDING ALL CHANGES ==="
git add -A
ADD_RC=$?
echo "ADD_EXIT=$ADD_RC"

echo "=== COMMITTING ==="
git commit -m "chore: preserve working tree changes before merging v3_refactor"
COMMIT_RC=$?
echo "COMMIT_EXIT=$COMMIT_RC"

if [ $COMMIT_RC -ne 0 ]; then
  echo "COMMIT FAILED"
  git status --short
  exit 1
fi

echo "=== RUNNING MERGE ==="
export GIT_MERGE_AUTOEDIT=no
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
