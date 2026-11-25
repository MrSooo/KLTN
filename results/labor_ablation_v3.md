# Labor Nested-Exception Benchmark — `lld2019`

Live `library(scasp)` inference + deterministic symbolic ceiling + `V_legal` static scan.

## Summary
- **Accuracy: 14/14 = 100.0%**
- s(CASP) engine: **live**
- s(CASP) exception blocking: `holds('LLD2019.D35.K2.e')` -> **no model (blocked)** (pipeline exception C_798cfde0)

## Per-verdict breakdown
| verdict | total | correct | accuracy |
|---|---|---|---|
| Concluded | 6 | 6 | 100.0% |
| Refuted | 3 | 3 | 100.0% |
| Insufficient Basis | 2 | 2 | 100.0% |
| Quarantined/Out-of-Scope | 3 | 3 | 100.0% |

## Accuracy by nested exception depth
| depth | total | correct | accuracy |
|---|---|---|---|
| $d=1$ | 8 | 8 | 100.0% |
| $d=2$ | 3 | 3 | 100.0% |
| $d=3$ | 2 | 2 | 100.0% |

## Counterfactual pair consistency
- pairs: 1, consistent: 1

## Symbolic verifier — 5 graph-error families (S_scan)
| family | count |
|---|---|
| dead_rule | 0 |
| duplicate | 0 |
| broken_link | 0 |
| blocking_cycle | 0 |
| contradiction | 0 |

## Per-case results
| id | depth | gold | predicted | scasp(holds anchor) | ok |
|---|---|---|---|---|---|
| lab_d1_001 | 1 | Concluded | Concluded | SAT | ✓ |
| lab_d1_002 | 1 | Concluded | Concluded | SAT | ✓ |
| lab_d2_001 | 2 | Concluded | Concluded | SAT | ✓ |
| lab_d2_002 | 2 | Refuted | Refuted | SAT | ✓ |
| lab_d2_003 | 2 | Refuted | Refuted | SAT | ✓ |
| lab_d3_001 | 3 | Concluded | Concluded | SAT | ✓ |
| lab_d3_002 | 3 | Concluded | Concluded | SAT | ✓ |
| lab_cf_001 | 1 | Concluded | Concluded | SAT | ✓ |
| lab_cf_002 | 1 | Refuted | Refuted | SAT | ✓ |
| lab_ins_001 | 1 | Insufficient Basis | Insufficient Basis | SAT | ✓ |
| lab_ins_002 | 1 | Insufficient Basis | Insufficient Basis | SAT | ✓ |
| lab_quar_001 | None | Quarantined/Out-of-Scope | Quarantined/Out-of-Scope | — | ✓ |
| lab_quar_002 | 1 | Quarantined/Out-of-Scope | Quarantined/Out-of-Scope | — | ✓ |
| lab_quar_003 | 1 | Quarantined/Out-of-Scope | Quarantined/Out-of-Scope | — | ✓ |

Notes: `predict_verdict()` is a hand-encoded deterministic ceiling over
`data/labor/concept_book.json`, so the accuracy above is a symbolic upper bound,
not the output of an LLM arm. The `scasp` column probes `holds(<article anchor>)`
only; it is not the nested-exception blocking check, which is the smoke row below.

## Live s(CASP) model (representative)
#### `holds('LLD2019.D35.K1.a')` — no incoming exception, model exists
```
ANSWER: yes
MODEL:
[not blocked(LLD2019.D35.K1.a),not has_exception(LLD2019.D35.K1.a),holds(LLD2019.D35.K1.a),in_force(LLD2019.D35.K1.a)]
TREE:
query-[goal_origin(holds(LLD2019.D35.K1.a),<clause>(0x5bccb37d3580))-[goal_origin(in_force(LLD2019.D35.K1.a),<clause>(0x5bccb36283c0))-[],(not blocked(LLD2019.D35.K1.a))-[(not has_exception(LLD2019.D35.K1.a))-[]]]]
```
#### `holds('LLD2019.D35.K2.e')` — blocked by pipeline exception_of
```
ANSWER: no
```
