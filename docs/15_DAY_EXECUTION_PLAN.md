# 15-Day Execution Plan: Neuro-Symbolic Legal Reasoning Pipeline

## Overview
This plan spans 15 days from the merge of `v3_refactor` (origin/refactor, `a1–a7` + `a8`/`a9`) into `feature/neuro-symbolic-legal-cot`, with the goal of producing a conference-ready paper with authentic Labor Law benchmark metrics, versioning results, and a dual-path pipeline architecture description.

---

## Days 1–3: Branch Hygiene & Artifact Archiving (Completed)
- [x] Verify branch consistency: `feature/neuro-symbolic-legal-cot` at merge commit `0bd2b55`
- [x] Move legacy `2026-11-21` BLDS artifacts from `results/` to `results/archive_legacy_v2/`
- [x] Keep `docs/papers/*.pdf` untracked
- [x] Confirm both `feature/neuro-symbolic-legal-cot` and `feat/english-dataset` point to same commit

---

## Days 4–6: Live LLM + s(CASP) Benchmark Run (Task 1)
### Goal: Authentic 14-case Labor Law ablation with LLM enabled + versioning pipeline

**Day 4: API & Environment Verification**
- [ ] Verify `.env` LLM credentials (Alibaba Cloud DashScope `qwen3.8-max`)
- [ ] Verify WSL `swipl` at `/usr/bin/swipl`; `s(CASP)` CLI availability
- [ ] Confirm `.venv` packages: `anthropic`, `google-genai` installed
- [ ] Test LLM single-call: `.venv/bin/python -c "from src.llm import llm; print(llm.enabled())"`

**Day 5: Versioning Pipeline on lld2019 + nd135_2020**
- [ ] Execute `python -I src/run_all.py --a8` to run A1–A8 on `blds2015_p4.md` + `lld2019_labor.md`
- [ ] Execute `python -I src/a4_versions.py apply --base data/raw/lld2019_labor.md --amend data/dev_amend/nd135_2020_tuoi_nghi_huu.md --effective-from 2021-01-01 --name lld2019_nd135`
- [ ] Execute `python -I src/a5_checks.py --versions data/processed/a4/lld2019_nd135_2021-01-01_versions.jsonl`
- [ ] Execute `python -I src/a7_graph.py --versions data/processed/a4/lld2019_nd135_2021-01-01_versions.jsonl --date 2021-01-01`
- [ ] Verify broken-link detection and localized rule re-extraction under decree amendments

**Day 6: 14-Case Ablation Benchmark (LLM enabled)**
- [ ] Run 4-arm ablation across all 14 cases in `data/labor/eval_nested_exceptions.jsonl`
- [ ] Arms 1–2: LLM-enabled CoT extraction (Arm 1 no CG/no s(CASP), Arm 2 CG+CoT η=0)
- [ ] Arms 3–4: Iterative η=2 refinement (Arm 3 binary feedback, Arm 4 detailed V_legal + s(CASP) feedback)
- [ ] Compute metrics: Answerable Conclusion Accuracy, Exception-Depth Breakdown (d=1,2,3), Refusal/Abstention Precision/Recall/F1, Mean Convergence Iterations (η̄), Failure Mode Breakdown
- [ ] Overwrite `results/labor_ablation_v3.json` with authentic metrics

---

## Days 7–9: Paper Synchronization (Task 2)
### Goal: Camera-ready paper with real experimental tables

**Day 7: Ablation Study Section in proposal.tex**
- [ ] Add 4-arm ablation table with real metrics from `results/labor_ablation_v3.json`
- [ ] Add Exception Depth Breakdown (d=1,2,3) with concrete examples (D35 K2, D39, D46)
- [ ] Add Quarantine/Abstention metrics (Concluded/Refuted/Insufficient/Quarantined counts)
- [ ] Add Decree Amendment Chain (ND135/2020–ND219/2025) with interval-splitting results
- [ ] Add Dual-Path v3_refactor architecture description (legacy flat vs subdir paths)

**Day 8: 15-Day Execution Plan (docs/15_DAY_EXECUTION_PLAN.md)**
- [ ] Create `docs/15_DAY_EXECUTION_PLAN.md` with day-by-day breakdown
- [ ] Map remaining days (7–15) to scale Labor Law benchmark from 14 dev cases to 80–100 test pairs
- [ ] Cover Decrees 135/2020, 145/2020, 152/2020, 12/2022, 219/2025
- [ ] Finalize camera-ready formatting and concise engineering prose

**Day 9: Paper Polish & Consistency Check**
- [ ] Ensure LaTeX compilation cleanliness (no overfull hboxes, cross-references OK)
- [ ] Verify all numerical values in paper match `results/labor_ablation_v3.json`
- [ ] Confirm Conventional Commit messages are consistent across the branch
- [ ] Check that `docs/papers/*.pdf` remain untracked

---

## Days 10–11: Git Commit & Branch Synchronization (Task 3)
### Goal: Clean final commit and branch alignment

**Day 10: Stage all artifacts**
- [ ] `git add results/labor_ablation_v3.json`
- [ ] `git add paper/proposal.tex`
- [ ] `git add docs/15_DAY_EXECUTION_PLAN.md`
- [ ] `git add` any other generated files (inference outputs, versioning outputs)

**Day 11: Final Commit & Branch Sync**
- [ ] `git commit -m "feat(exp): live LLM+s(CASP) 14-case Labor Law ablation and sync paper metrics"`
- [ ] `git branch -f feat/english-dataset feature/neuro-symbolic-legal-cot`
- [ ] `git status --short` verify clean state (no unintended modifications)
- [ ] Verify `docs/papers/*.pdf` untracked

---

## Days 12–15: Contingency & Polish
- [ ] Address any LaTeX compilation issues from day 7–9
- [ ] Address any JSON metric inconsistencies from day 6
- [ ] Optional: Extend benchmark from 14 to 80–100 test pairs if time permits
- [ ] Prepare conference submission package (source code, data, paper PDF)
- [ ] Final out-brief and knowledge transfer documentation

---
*Plan generated on the day of Step 3 completion. All deliverables conform to the dual-path `v3_refactor` integration architecture.*
