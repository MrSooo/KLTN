# Graph Report - KLTN  (2026-11-20)

## Corpus Check
- 75 files · ~185,424 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 2)

## Summary
- 1792 nodes · 3822 edges · 101 communities (77 shown, 24 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 117 edges (avg confidence: 0.85)
- Token cost: 559,828 input · 0 output

## Community Hubs (Navigation)
- Concept Names Tests
- Proposition & Rule Tests
- LLM Step Tests
- Concept Names Ledger
- Predicate Extraction 1.6B
- Sandbox API Runner
- Directive Reading 2.3
- Reference Resolution 1.2
- Implicit Exceptions 1.7
- Proposition Extraction 1.6A
- Step CLIs & Graph Checks
- Date-aware Answering 1.9
- Corpus & Document Model
- Demo Chat & Viewer UI
- Rare Directive Tests
- KB Linking 2.2
- Sandbox API Tests
- Cross-step Checks
- Concept Extraction 1.6
- Concept Step Tests
- s(CASP) Rule Compilation
- Links/ArticleType/Exception Tests
- Incremental Update 2.6-2.7
- Versions & Directives Tests
- Rare Directive Handling
- Paper Writing Style Rules
- QA Server KB
- Pipeline Design Principles
- Method Formalization (Paper)
- LLM Client Core
- Reference Tests
- Contributor & AI Rules
- Parser Tests
- Parse Data Model
- Proposition Design 1.6A
- General Exceptions 1.5
- Line Parser 1.1
- Decisions A42-A49 (Update/QA)
- Report Renderer
- s(CASP) Query Runner
- Version Store 2.4
- Answering Tests
- QA Server Tests
- Update Tests
- Decisions A27-A38 (Predicates)
- Concept Names Cache I/O
- LLM Output Parsing
- Check Expectations
- Concept Names Rounds
- Run-all Orchestrator
- Knowledge Unit Edges
- Directive Text Application
- Explicit Exceptions 1.5
- LLM Config & Errors
- Parser Tokenizer
- Predicate Registry
- Directive Event Dates
- Overview Steps 1.1-1.5
- Version Operators
- Two-phase Model K
- LLM Steps Overview
- QA & Conflict Model
- Affected Set 2.5
- Header & Date Extraction
- Proposition Diffing
- Directive Types & Survey
- KU Catalog & Epochs
- KU Version Snapshots
- Text Normalization
- LLM Sandbox Operations
- Step Context Loader
- Decisions: Knowledge Steps
- Cache File Naming
- Decision Log Foundations
- Equation Forms B-F
- Article Type 1.4
- KU Contexts
- Predicate Chain Runs
- QA HTTP Handler
- Update Algorithm Docs
- Method Section & Conflicts
- LLM Heartbeat
- Proposition Sandbox Lots
- Consolidated Text VBHN_125
- Design Findings 1.x
- LLM Reproducibility
- Subset Chain Script
- Base KB Scope
- Exception Trigger Tests
- Terminology Rules
- Unit ID Scheme
- General Exception Tests
- Form K Algorithms

## God Nodes (most connected - your core abstractions)
1. `out_dir()` - 38 edges
2. `Client` - 24 edges
3. `read_jsonl()` - 24 edges
4. `main()` - 22 edges
5. `main()` - 21 edges
6. `write_jsonl()` - 21 edges
7. `checks()` - 20 edges
8. `mini()` - 20 edges
9. `out()` - 20 edges
10. `run()` - 19 edges

## Surprising Connections (you probably didn't know these)
- `Machine gate on LLM output` --semantically_similar_to--> `LLM proposes, machine checks; no human reviewer`  [INFERRED] [semantically similar]
  README.md → docs/overview.md
- `process_doc()` --indirect_call--> `out()`  [INFERRED]
  src/concepts.py → tests/test_concepts_names.py
- `run_rounds()` --indirect_call--> `out()`  [INFERRED]
  src/concepts_names.py → tests/test_concepts_names.py
- `bare_kb()` --indirect_call--> `key()`  [INFERRED]
  tests/test_qa_server.py → src/directives_rare.py
- `llm_propose()` --indirect_call--> `out()`  [INFERRED]
  src/links.py → tests/test_concepts_names.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Nguyên tắc cổng máy, không LLM kiểm LLM** — docs_decisions_a6, docs_decisions_a14, docs_decisions_a15, docs_decisions_a25, docs_decisions_a30 [EXTRACTED 1.00]
- **Chuỗi sửa lời nhắc 1.6A cho lần chạy ckey (menh-de-4 đến menh-de-7)** — docs_decisions_a47, docs_decisions_a50, docs_decisions_a51, docs_decisions_a52, docs_decisions_ckey_runs [EXTRACTED 1.00]
- **Bộ máy cập nhật 2.5-2.7 theo mốc** — docs_decisions_a42, docs_decisions_knowledge_unit, docs_decisions_epoch, docs_decisions_affected_set, docs_decisions_predicate_registry, docs_decisions_pi_tau [EXTRACTED 1.00]
- **Giai đoạn 1 lớp cấu trúc và quan hệ pháp lý (1.1-1.5, không LLM)** — docs_design_steps_1_1_to_1_5_buoc_1_1_parse, docs_design_steps_1_1_to_1_5_buoc_1_2_refs, docs_design_steps_1_1_to_1_5_buoc_1_3_delegation, docs_design_steps_1_1_to_1_5_buoc_1_4_article_type, docs_design_steps_1_1_to_1_5_buoc_1_5_exceptions [EXTRACTED 1.00]
- **Lớp tri thức: mệnh đề, sổ vị từ, ngoại lệ ngầm, quy tắc s(CASP)** — docs_design_step_1_6a_propositions_menh_de, docs_design_steps_1_6_to_1_8_so_vi_tu_1_6b, docs_design_steps_1_6_to_1_8_buoc_1_7, docs_design_steps_1_6_to_1_8_buoc_1_8 [EXTRACTED 1.00]
- **Cập nhật tăng dần và đối chứng (2.5-2.7)** — docs_design_steps_2_5_to_2_7_knowledge_unit, docs_design_steps_2_5_to_2_7_tap_anh_huong, docs_design_steps_2_5_to_2_7_trich_lai, docs_design_steps_2_5_to_2_7_doi_chung, docs_design_steps_2_5_to_2_7_so_vi_tu_chi_them [EXTRACTED 1.00]
- **LLM proposes, machine gate checks** — readme_machine_gate, docs_overview_two_principles, docs_overview_syllable_gate, docs_overview_isolation, docs_operations_llm_sandbox_xuat_nhap [INFERRED 0.85]
- **Phase 2 update engine steps 2.1-2.7** — docs_overview_step_2_1, docs_overview_step_2_2, docs_overview_step_2_3, docs_overview_step_2_4, docs_overview_step_2_5, docs_overview_step_2_6, docs_overview_step_2_7, docs_reference_method_update_algorithm [EXTRACTED 1.00]
- **Cache-keyed reproducible LLM runs** — readme_llm_client, readme_llm_cache, contributing_prompt_version, readme_llm_modes, docs_llm_config_cache_reproducibility [INFERRED 0.85]
- **Update pipeline layers S_str, S_upd, S_know composed into Update(K,d)** — method_writing_guide_update_composition, method_writing_guide_structural_layer, method_writing_guide_update_engine, method_writing_guide_knowledge_layer [EXTRACTED 1.00]
- **Date-indexed validity chain: version -> status -> Pi_tau -> answer** — method_writing_guide_version_tuple, method_writing_guide_status_function_sigma, method_writing_guide_program_pi_tau, method_writing_guide_blocking_rule, method_writing_guide_four_outcomes [EXTRACTED 1.00]
- **Equation forms A-K of the cookbook** — scientific_paper_writing_cookbook_form_a_definition, scientific_paper_writing_cookbook_form_b_typed_mapping, scientific_paper_writing_cookbook_form_c_pipeline_composition, scientific_paper_writing_cookbook_form_d_scoring_function, scientific_paper_writing_cookbook_form_e_constraint, scientific_paper_writing_cookbook_form_f_logical_rule, scientific_paper_writing_cookbook_form_g_state_transformation, scientific_paper_writing_cookbook_form_h_ordering, scientific_paper_writing_cookbook_form_i_objective, scientific_paper_writing_cookbook_form_j_evaluation_metric, scientific_paper_writing_cookbook_form_k_equation_algorithm_link [EXTRACTED 1.00]
- **Date-based visibility filtering in viewer** — utils_viewer_template_active, utils_viewer_template_shown, utils_viewer_template_visible, utils_viewer_template_displayof, utils_viewer_template_displayofparent, utils_viewer_template_validity_intervals [EXTRACTED 1.00]
- **Demo question-answer flow** — utils_demo_index_send, utils_demo_index_api_hoi, utils_demo_index_answer, utils_demo_index_verdict, utils_demo_index_wirecites [EXTRACTED 1.00]

## Communities (101 total, 24 thin omitted)

### Community 0 - "Concept Names Tests"
Cohesion: 0.06
Nodes (61): answer(), fake_policy(), full_fake_run(), _in_subprocess(), ledger_bytes(), _ledger_fixture(), mini(), _neighbors_fixture() (+53 more)

### Community 1 - "Proposition & Rule Tests"
Cohesion: 0.05
Nodes (30): run(), ctxs(), errors(), gold(), leaks(), _llm_from_gold(), row(), test_bo_truong_rong_va_liet_ke() (+22 more)

### Community 2 - "LLM Step Tests"
Cohesion: 0.06
Nodes (29): anthropic_module(), claude_client(), edges(), fake_anthropic_module(), fake_client(), call(), reply(), run_script() (+21 more)

### Community 3 - "Concept Names Ledger"
Cohesion: 0.06
Nodes (21): Book, build_ledger(), build_words(), candidates(), chu_id(), count_without_candidates(), names_report_lines(), near_twins() (+13 more)

### Community 4 - "Predicate Extraction 1.6B"
Cohesion: 0.07
Nodes (22): cache_key(), Book, build_ledger(), build_words(), candidates(), compatible(), count_without_candidates(), fold_dir() (+14 more)

### Community 5 - "Sandbox API Runner"
Cohesion: 0.07
Nodes (10): expected_model(), is_object(), main(), Runner, FakeApi, make(), test_llm_live_caches_and_replay_returns_same_record(), test_llm_off_and_replay_miss_never_touch_network() (+2 more)

### Community 6 - "Directive Reading 2.3"
Cohesion: 0.10
Nodes (24): amending(), conditional(), dev_gates(), gate(), directive_doc(), effect_statements(), expire_date(), _flex() (+16 more)

### Community 7 - "Reference Resolution 1.2"
Cohesion: 0.08
Nodes (19): find_doc_tail(), overrides(), build_structure_edges(), chain_targets(), code_segment(), DocTail, enclosing(), extract() (+11 more)

### Community 8 - "Implicit Exceptions 1.7"
Cohesion: 0.11
Nodes (21): ancestors_or_self(), build_pairs(), cache_path(), _children_text(), explicit_pairs(), find_cycles(), gate(), ku_cache_path() (+13 more)

### Community 9 - "Proposition Extraction 1.6A"
Cohesion: 0.11
Nodes (21): _apply(), _bo_ngu_keys(), contexts(), _enum(), gate_unit(), gemini(), gemini_schema(), _in_ctx() (+13 more)

### Community 10 - "Step CLIs & Graph Checks"
Cohesion: 0.09
Nodes (22): main(), main(), update_rules_problems(), write_outputs(), get_doc(), load_manifest(), mark_word(), report_dir() (+14 more)

### Community 11 - "Date-aware Answering 1.9"
Cohesion: 0.12
Nodes (24): cache_path(), classify(), _classify(), contradicted(), fact_lines(), fired_rules(), fired_units(), gate() (+16 more)

### Community 12 - "Corpus & Document Model"
Cohesion: 0.08
Nodes (15): Doc, doc_id_from_path(), in_subset(), _kept(), landmark(), parse_date(), subset_jumps(), _subset_spec() (+7 more)

### Community 13 - "Demo Chat & Viewer UI"
Cohesion: 0.09
Nodes (31): Demo chat UI (Trợ lý Luật Lao động), add() message append, answer() render reasoner result, /api/hoi endpoint (cau_hoi, ngay), /api/info endpoint (hom_nay, vi_du), grow() textarea autosize, hello() welcome screen, send() POST question (+23 more)

### Community 14 - "Rare Directive Tests"
Cohesion: 0.15
Nodes (27): fake_ctx(), fake_doc(), fake_ev(), fake_units(), fires(), pending_store(), store_with(), test_12_decree_that_only_cites_the_same_number_stays_pending() (+19 more)

### Community 15 - "KB Linking 2.2"
Cohesion: 0.11
Nodes (17): based_on_links(), decide_llm(), details_links(), dieu_of(), head_phrase(), key_phrases(), keyword_candidates(), lead_tail() (+9 more)

### Community 16 - "Sandbox API Tests"
Cohesion: 0.15
Nodes (17): client(), env_key, FakeResponse, lot_dir(), reply(), server(), urlopen(), test_ckey_rejects_cut_output_and_non_json_without_caching() (+9 more)

### Community 17 - "Cross-step Checks"
Cohesion: 0.14
Nodes (18): checks(), names_files_problems(), load_inputs(), collect_edges(), fresh_run(), load_exception_rows(), main(), output_paths() (+10 more)

### Community 18 - "Concept Extraction 1.6"
Cohesion: 0.13
Nodes (16): attach_targets(), cond_node_rows(), dieu_of(), find_all(), gate_span(), locate(), main(), make_batches() (+8 more)

### Community 19 - "Concept Step Tests"
Cohesion: 0.13
Nodes (18): ctx(), FakeClient, real(), test_batches_are_deterministic_in_document_order_and_bounded(), test_gate_rejects_bad_role_and_bad_params(), test_gate_rejects_span_not_in_context_and_partial_words(), test_khoan_under_a_dieu_lead_in_gets_it_as_chapeau_and_other_units_are_unchanged(), test_llm_exception_span_nested_in_node_is_dropped_by_position_but_a_separate_one_stays() (+10 more)

### Community 20 - "s(CASP) Rule Compilation"
Cohesion: 0.10
Nodes (15): active_blockers(), apply_blocks(), atom(), blocker_forms(), bodies(), child_mode(), compile_units(), effective_kinds() (+7 more)

### Community 21 - "Links/ArticleType/Exception Tests"
Cohesion: 0.08
Nodes (7): exceptions(), test_article_type_domain_headings_stay_substantive(), test_article_type_real_effect_and_authority_headings_kept(), test_exceptions_explicit_rule2_needs_list_tail_not_midsentence_tru(), test_exceptions_general_noun_family_on_blld(), test_exceptions_general_two_triggers_split_by_semicolon_or_clash(), test_exceptions_milestones_on_blld()

### Community 22 - "Incremental Update 2.6-2.7"
Cohesion: 0.14
Nodes (12): head_form(), basis_lines(), compare(), compile_at(), dev_dates(), dev_questions(), Engine, main() (+4 more)

### Community 23 - "Versions & Directives Tests"
Cohesion: 0.12
Nodes (18): chain(), mini_store(), test_chain_is_deterministic_on_disk(), test_conditional_effect_pending_event(), test_consolidation_vbhn125(), test_dev_gates_all_pass(), test_law_2012_documents_are_flagged_not_linked_to_2019(), test_nd70_changes_on_nd152() (+10 more)

### Community 24 - "Rare Directive Handling"
Cohesion: 0.10
Nodes (12): Node, apply_rare(), correct(), _date(), mark_parent_changed(), possible_replacement(), key(), renumber() (+4 more)

### Community 25 - "Paper Writing Style Rules"
Cohesion: 0.12
Nodes (19): Banned phrase list and structural lint, Rules and blocking relation 1.8 b_{e,r} with src(b)=src(e) (Eq.10), DRAFT_PAPER_METHODS_LATEX.pdf, Method writing guide (Section 3-4 self-writing guide), Page budget (S3 ~2.5 pages, S4 ~4 pages, ~283 lines), Placeholder markers ([CHỜ QUYẾT], [CHỜ CODE], [CẦN SỐ], [KIỂM], [CẦN TRÍCH DẪN]), Source trace table (paragraph to repo file, status 16/11), Prompt for AI agent writing paper drafts (+11 more)

### Community 26 - "QA Server KB"
Cohesion: 0.15
Nodes (5): KB, walk(), node(), main(), unit_name()

### Community 27 - "Pipeline Design Principles"
Cohesion: 0.13
Nodes (21): Thiết kế pipeline (pipeline_design.md), Bước 2.2 Nối vào KB (links.py), Câu hỏi thiết kế còn mở (Δ chưa lấp, câu hỏi cổng, N một bước, tám Điều lệch VBHN_125), Khuôn cạnh chung {s, p, o, evidence, how, flags} (A12), Khuôn mô tả một bước (6 mục), Cổng âm tiết và cổng nguyên văn trich, Bước 1.1 đến 1.5: mô tả chi tiết, A24: họ 'trừ <danh từ>' (nới quy tắc được chấp thuận) (+13 more)

### Community 28 - "Method Formalization (Paper)"
Cohesion: 0.11
Nodes (23): Affected set A(d) = T(d) U N(T(d)) (Eq.7), Date-aware QA (4.4): question to facts F_q, Gap caused by unfilled Delta (insufficient vs NAF wrong answer), details link acceptance condition (target in Delta, keyword in target) (Eq.5), Four outcomes ans(q,tau): concluded, rebutted, insufficient, no_answer (Eq.11), Implicit exceptions 1.7, KB definition K = (D, U, V, E, Delta, P, R) (Definition 1), Knowledge layer S_know (4.3): propositions, predicate registry, implicit exceptions, rules (+15 more)

### Community 30 - "Reference Tests"
Cohesion: 0.12
Nodes (10): find_in(), test_chain_split_after_this_and_new_dieu(), test_elided_dieu_shared_by_previous_group(), test_list_of_numbers_and_this(), test_phu_luc_refs(), test_semicolon_and_cua_between_items(), test_suffix_numbers_and_letter_points(), test_tail_name_full_title_not_truncated() (+2 more)

### Community 31 - "Contributor & AI Rules"
Cohesion: 0.14
Nodes (13): CLAUDE.md (AI assistant instructions), CONTRIBUTING.md (Contribution guide), Pipeline overview via Article 35, Article 35 running example (unilateral termination), Three layers: symbolic, LLM+gate, hybrid, Section 3.5 'other model re-extracts to check' (not implemented, A25), Roadmap, Project status (+5 more)

### Community 32 - "Parser Tests"
Cohesion: 0.17
Nodes (11): ids(), run_parser(), test_chuong_title_next_line_and_wrapped(), test_footer_noi_nhan_is_dropped(), test_footnote_markers_and_zone(), test_ids_with_suffix_and_dd(), test_number_with_dots_is_not_khoan(), test_numbering_jump_is_reported() (+3 more)

### Community 33 - "Parse Data Model"
Cohesion: 0.15
Nodes (11): Anomaly, parse_document(), Parsed, Payload, read_lines(), rebuild_wage_tables(), report_text(), run_doc() (+3 more)

### Community 34 - "Proposition Design 1.6A"
Cohesion: 0.16
Nodes (18): Bước 1.6A: tách mệnh đề (propositions.py), Đường chạy A39: Sonnet qua Claude Code, hộp cát, luật dừng, Luật tách mệnh đề (10 luật trong lời nhắc), Mệnh đề (loai: menh_de, con_tro, bo_qua, chua_ro), Lời nhắc menh-de-3 (đóng băng), Phương thức (duoc/phai/cam/khong_ap_dung/khong) và cực, Bộ thí điểm 30 đơn vị (gold_draft, so sánh Sonnet/Gemini), Nút điều kiện (dieu_kien: cu_the, tuy_nghi, dan_chieu_mo) (+10 more)

### Community 35 - "General Exceptions 1.5"
Cohesion: 0.16
Nodes (11): check_general(), _clause(), clause_of(), condition_id(), condition_kind(), exceptions_general_dir(), find_general(), main() (+3 more)

### Community 36 - "Line Parser 1.1"
Cohesion: 0.22
Nodes (3): has_lower(), is_title_line(), Parser

### Community 37 - "Decisions A42-A49 (Update/QA)"
Cohesion: 0.18
Nodes (9): Tập ảnh hưởng T(e), N(·), A(e), Mốc (epoch) của bộ máy cập nhật, Lỗ hổng 2.7: phụ thuộc toàn cục A43 × A42, Đơn vị tri thức (KU), Tiền tố phương thức must_/may_/forbidden_/not_applicable_/neg_, Π_τ - tập quy tắc hiệu lực tại ngày τ, Sổ vị từ chỉ thêm (predicate_registry), Mệnh đề (menh_de) - dòng ra 1.6A (+1 more)

### Community 38 - "Report Renderer"
Cohesion: 0.24
Nodes (9): inline(), main(), parse_blocks(), render(), render_block(), render_list(), render_table(), slug() (+1 more)

### Community 39 - "s(CASP) Query Runner"
Cohesion: 0.15
Nodes (5): scasp_query(), check_program(), claude_code(), explain_gate(), extract_json()

### Community 41 - "Answering Tests"
Cohesion: 0.29
Nodes (14): classify(), facts(), has_swipl(), kb(), lit(), rule(), test_answering_blocked_is_rejected_with_exception_ground(), test_answering_contradicted_condition_is_rejected_q10() (+6 more)

### Community 42 - "QA Server Tests"
Cohesion: 0.16
Nodes (10): bare_kb(), Doc, ok(), test_qa_server_explain_falls_back_when_gate_fails_or_llm_errors(), test_qa_server_gate_accepts_article_named_in_basis_text(), test_qa_server_gate_dates_are_not_document_numbers(), test_qa_server_gate_rejects_article_or_document_outside_basis(), test_qa_server_gate_rejects_citation_outside_basis_and_bad_shape() (+2 more)

### Community 43 - "Update Tests"
Cohesion: 0.21
Nodes (11): case_exception(), case_tree(), check(), knowledge(), md(), NoAnswers, test_knowledge_units_ku_by_context_and_term_end(), test_predicate_registry_groups_amended_and_inserted_units_by_dieu() (+3 more)

### Community 44 - "Decisions A27-A38 (Predicates)"
Cohesion: 0.22
Nodes (4): Các lần chạy ckey, ckey2, ckey3, ckey4, Tiêu chí nghiệm thu / luật dừng đăng ký trước, Đóng băng lời nhắc / khoá cache theo chữ lời nhắc, Hộp cát (thư mục làm việc ngoài repo cho LLM)

### Community 45 - "Concept Names Cache I/O"
Cohesion: 0.15
Nodes (8): fold_dir(), _line(), nhap(), read_log(), store_round(), tiep(), tiep_entry(), user_message()

### Community 46 - "LLM Output Parsing"
Cohesion: 0.13
Nodes (5): InvalidOutput, key_is_set(), stderr_log(), strip_fence(), tokens_in_out()

### Community 47 - "Check Expectations"
Cohesion: 0.13
Nodes (6): Expect, independent_counts(), lead_in_text(), names_problems(), residue_problems(), version_problems()

### Community 48 - "Concept Names Rounds"
Cohesion: 0.13
Nodes (6): content_sets(), link_map(), make_rounds(), Neighbors, prepare(), syllables()

### Community 49 - "Run-all Orchestrator"
Cohesion: 0.19
Nodes (5): llm_flag(), run(), run_steps(), step_tests(), StepError

### Community 51 - "Directive Text Application"
Cohesion: 0.19
Nodes (6): apply_node(), child_id(), line_only_dieu(), supplements(), text_norm(), Ver

### Community 52 - "Explicit Exceptions 1.5"
Cohesion: 0.27
Nodes (8): check_exceptions(), children_of(), exceptions_explicit_dir(), find_exceptions(), find_triggers(), kind_of(), main(), run_doc()

### Community 53 - "LLM Config & Errors"
Cohesion: 0.18
Nodes (6): CacheMiss, check_models(), LLMError, load_config(), provider_of(), QuotaReached

### Community 54 - "Parser Tokenizer"
Cohesion: 0.15
Nodes (4): diem_code(), next_letter_ok(), next_number_ok(), Unit

### Community 55 - "Predicate Registry"
Cohesion: 0.27
Nodes (8): main(), _make(), names_by_key(), nhap(), prepare(), stages_from(), tiep_entry(), xuat()

### Community 56 - "Directive Event Dates"
Cohesion: 0.23
Nodes (6): apply_event(), check_triggers(), consolidation_compare(), dates_in(), Ev, own_effective()

### Community 57 - "Overview Steps 1.1-1.5"
Cohesion: 0.18
Nodes (11): Condition node (cu_the / tuy_nghi / dan_chieu_mo), Step 1.1 Parse, Step 1.2 References (refers_to), Step 1.3 Delegation clauses, Step 1.4 Article type, Step 1.5 Explicit exceptions, Step 2.1 Process new document, Step 2.2 Link into KB (based_on, details) (+3 more)

### Community 58 - "Version Operators"
Cohesion: 0.24
Nodes (8): Version operators close/open (Eq.6), Form G: state transformation KB^{t+1} = T_Delta(KB^t), add_doc_units(), iso(), main(), new_version(), order_docs(), write_outputs()

### Community 60 - "Two-phase Model K"
Cohesion: 0.25
Nodes (11): Bước 1.9 Hỏi đáp theo ngày (φ và ¬φ, bốn kết quả), Bước 2.4 Áp chỉ thị lên phiên bản (versions.py), Giai đoạn 1: dựng KB gốc từ BLLĐ (bước 1.1-1.9), Giai đoạn 2: Update(K, d) khi có văn bản mới (bước 2.1-2.7), Mô hình K = (D, U, V, E, Δ, P, R), Π_τ: quy tắc hiệu lực tại ngày τ, không bị cô lập, Bước 2.5, 2.6, 2.7: tập ảnh hưởng, trích lại, đối chứng, Bước 2.7 đối chứng tăng dần với dựng lại toàn bộ (+3 more)

### Community 61 - "LLM Steps Overview"
Cohesion: 0.22
Nodes (8): tiep.py sequential replay driver, Step 1.6A Propositions, Step 1.6B Predicate registry, Step 1.7 Implicit exceptions, Three acceptance numbers of 1.6A, M1 Finish 1.6A, M2 Rewrite 1.6B (names-2), M3 Step 1.7

### Community 62 - "QA & Conflict Model"
Cohesion: 0.20
Nodes (9): Four answer types (concluded, refuted, insufficient, no answer), Step 1.8 s(CASP) rules, Step 1.9 Date-aware QA, KB model K=(D,U,V,E,Delta,P,R), Program at date Pi_tau, s(CASP), M4 Step 1.8 s(CASP), M5 Step 1.9 and question set (+1 more)

### Community 63 - "Affected Set 2.5"
Cohesion: 0.24
Nodes (5): affected_at(), _edge_hits(), report_lines(), touched(), rel()

### Community 64 - "Header & Date Extraction"
Cohesion: 0.20
Nodes (3): find_vn_date(), extract_header(), Resolver

### Community 65 - "Proposition Diffing"
Cohesion: 0.25
Nodes (8): diff_row(), diff_unit(), _fmt(), _key(), _kieu(), match_rows(), so(), syllables()

### Community 66 - "Directive Types & Survey"
Cohesion: 0.20
Nodes (9): Directive types 1-26, Types 11-12 conditional effect (pending/triggers), Type 15 consolidation update (VBHN_125), Type 10 topic-based expiry, Labor Code survey, 8 Articles differ BLLD vs 125/VBHN, Work-permit exemption chain D151->D154->ND 152/70/219, 45-day expert work-permit example (ND 219 vs 152) (+1 more)

### Community 69 - "Text Normalization"
Cohesion: 0.24
Nodes (3): scan_source(), main(), normalize()

### Community 70 - "LLM Sandbox Operations"
Cohesion: 0.22
Nodes (8): ckey.<key> overrides under KLTN_LLM_RUN=ckey, LLM roles: chinh, kiem, trich, ten, hop_cat, api, LLM sandbox operations, sandbox_api.py (API runner replacing Claude Code), Out-of-repo working directory (hop cat), Unfinished: 204-batch run of 1.6A (A39 path), ckey separate run (DeepSeek via sandbox_api), lldnn subset (tap con)

### Community 71 - "Step Context Loader"
Cohesion: 0.31
Nodes (6): Context, load_payloads(), load_units(), output_dir(), triples_path(), load_all_units()

### Community 73 - "Cache File Naming"
Cohesion: 0.29
Nodes (4): cache_name(), cache_tag(), full_cache_path(), load_ku_cache()

### Community 74 - "Decision Log Foundations"
Cohesion: 0.29
Nodes (5): Sổ quyết định (decisions.md), llm_client: nơi duy nhất gọi API, cache sha256, chế độ off/replay/live (BA2), Phần III. Số đo và quan sát (S1-S7), Điều kiện phủ định trên vị từ input: -p (thế giới mở), S5. Thử s(CASP): ngoại lệ lồng, vị từ không tồn tại, phủ định thật

### Community 75 - "Equation Forms B-F"
Cohesion: 0.29
Nodes (7): Proposition extraction 1.6A f_prop with syllable gate (Eq.8), Form B: typed mapping f: X -> Y with type check, Form C: pipeline composition, Form D: scoring function (cosine similarity with threshold), Form F: logical rule with exceptions, Infer as fixpoint of immediate consequence operator T_R, PAPER_03: Integrating LLM with Symbolic Reasoning for KG-Driven Legal Query System (Dang et al.)

### Community 77 - "KU Contexts"
Cohesion: 0.33
Nodes (3): contexts_at(), _date(), dieu_of()

### Community 79 - "QA HTTP Handler"
Cohesion: 0.38
Nodes (5): make_handler(), do_GET(), do_POST(), _send(), public_view()

### Community 81 - "Update Algorithm Docs"
Cohesion: 0.47
Nodes (6): Step 2.5 Affected set A(d), Step 2.6 Re-extract for A(d), Step 2.7 Incremental vs rebuild check, Affected set A(d)=T(d) U N(T(d)), Algorithm 1: Update(K,d), Gap: A42 affected set misses BLOCK_ALIAS (A43) global dependency

### Community 82 - "Method Section & Conflicts"
Cohesion: 0.33
Nodes (5): Method (sections 3.1-3.6), Cross-document conflict (Article 58, Law 64/2025), Form H: lexicographic priority ordering (Lex Superior > Specialis > Posterior), Form J: evaluation metric (IRAC score, per-question vs per-group average), PAPER_04: Neuro-Symbolic Framework for Verified Legal Inference of RAG-based AI (Dang et al.)

### Community 84 - "Proposition Sandbox Lots"
Cohesion: 0.33
Nodes (3): ku_lots(), ku_xuat(), sandbox_model()

### Community 86 - "Design Findings 1.x"
Cohesion: 0.40
Nodes (5): Bước 2.3 Đọc chỉ thị (directives.py), Bước 1.4 article_type: nhãn Điều theo regex tiêu đề, Nhãn effect_transition, Khối trích dẫn (parse_payloads), không là đơn vị, PHÁT HIỆN 1: mẫu tiêu đề đẩy nhầm 6 Điều khỏi substantive (A21)

### Community 87 - "LLM Reproducibility"
Cohesion: 0.40
Nodes (4): LLM configuration (machine-read), xuat / nhap export-import cycle, data/llm_cache (tracked LLM responses), llm_client.py (single LLM call site)

### Community 88 - "Subset Chain Script"
Cohesion: 0.70
Nodes (4): Invoke-Api(), Invoke-Replay(), Test-Nhap(), Write-Log()

## Knowledge Gaps
- **51 isolated node(s):** `BLLĐ 45/2019 (Bộ luật Lao động)`, `Mã đơn vị (doc_id.Cxx/Mn/Dn/Kn/điểm/PL)`, `PHÁT HIỆN 1: mẫu tiêu đề đẩy nhầm 6 Điều khỏi substantive (A21)`, `PHÁT HIỆN 2: except_list_pattern sai 23/23, trigger nhiễu (A22)`, `PHÁT HIỆN 3: target_name chờ đích bị cắt (A23)` (+46 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 626 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Structural layer S_str (4.1): units, references, Delta, explicit exceptions` connect `Method Formalization (Paper)` to `Pipeline Design Principles`, `KB Linking 2.2`?**
  _High betweenness centrality (0.207) - this node is a cross-community bridge._
- **What connects `BLLĐ 45/2019 (Bộ luật Lao động)`, `Mã đơn vị (doc_id.Cxx/Mn/Dn/Kn/điểm/PL)`, `PHÁT HIỆN 1: mẫu tiêu đề đẩy nhầm 6 Điều khỏi substantive (A21)` to the rest of the system?**
  _51 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Concept Names Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.063568010936432 - nodes in this community are weakly interconnected._
- **Why does `Update(K,d) = S_know o S_upd o S_str (Eq.4) with Figure 1` connect `Method Formalization (Paper)` to `Equation Forms B-F`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Should `Proposition & Rule Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.05048076923076923 - nodes in this community are weakly interconnected._
- **Why does `Version v = (u, text, [t_from, t_to), mu) (Eq.1)` connect `Method Formalization (Paper)` to `Decision Log Foundations`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Should `LLM Step Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.06184012066365008 - nodes in this community are weakly interconnected._