"""Test bước 1.6 giai đoạn B, phần máy (concepts_names.py): gom chữ, params, từ nội dung, hàng xóm, chia lượt, ứng viên, luật dừng, tất định theo byte.

Không gọi mạng. Số đo trên dữ liệu thật dựng bằng `concepts.process_doc` ở chế độ replay NGAY TRONG TEST (đọc cache đã commit), không đọc data/processed/concepts/:
file đó chỉ còn 40 cụm khi lần chạy cuối là `--llm off` (run_all --tests chạy sau cả hai chế độ).
"""
import collections
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import _harness  # noqa: E402
import concepts as cc  # noqa: E402
import concepts_names as cn  # noqa: E402
import llm_client  # noqa: E402

DOC = "BLLD_45-2019"
X = "X."
_CACHE = {}


def row(unit, span, role="dieu_kien", params=(), targets=(), how="llm", predicate=None):
    return {"unit": X + unit, "span": span, "role": role, "source": "own", "predicate": predicate, "params": list(params), "targets": list(targets), "how": how, "flags": []}


def order_of(*units):
    return {X + u: i for i, u in enumerate(units)}


def raises_exit(fn):
    try:
        fn()
    except SystemExit:
        return True
    return False


# ---- gom chữ ----

def test_words_group_by_text_norm_keep_first_occurrence_and_skip_targets_and_named():
    rows = [row("D1.K1", "hợp đồng có thời hạn", params=["C"]),
            row("D1.K2", "Hợp đồng có thời hạn.", role="chu_the", params=["C"]),
            row("D1.K2", "dẫn chiếu", targets=["X.D5"]),
            row("D2.K1", "đã có tên", predicate="da_co_ten"),
            row("D2.K1", "khác", params=["E", "W"], how="cond_node")]
    words = cn.build_words(rows, order_of("D1.K1", "D1.K2", "D2.K1"))
    assert [w["surface"] for w in words] == ["hợp đồng có thời hạn", "khác"], words
    a, b = words
    assert a["n"] == 2 and a["roles"] == ["chu_the", "dieu_kien"] and a["units"] == ["X.D1.K1", "X.D1.K2"] and a["dieu"] == "X.D1" and a["unit"] == "X.D1.K1"
    assert [o["unit"] for o in a["occ"]] == ["X.D1.K1", "X.D1.K2"]
    assert b["params"] == ("W", "E") and b["how"] == ["cond_node"] and b["idx"] == 1


def test_words_count_param_variants_and_take_params_of_first_occurrence():
    rows = [row("D1.K1", "một chữ", params=["W"]), row("D1.K2", "một chữ", params=["E"]), row("D1.K3", "một chữ", params=["E", "W"])]
    (w,) = cn.build_words(rows, order_of("D1.K1", "D1.K2", "D1.K3"))
    assert w["params"] == ("W",) and w["param_variants"] == 3


def test_words_fail_closed_on_unit_order_and_unknown_unit():
    order = order_of("D1.K1", "D1.K2")
    assert raises_exit(lambda: cn.build_words([row("D1.K2", "a"), row("D1.K1", "b")], order))
    assert raises_exit(lambda: cn.build_words([row("D9.K1", "a")], order))
    assert raises_exit(lambda: cn.build_words([row("D1.K1", " . ")], order))


def test_params_key_is_a_set_in_canonical_order_and_rejects_unknown_letters():
    assert cn.params_key(["E", "W"]) == cn.params_key(["W", "E"]) == ("W", "E")
    assert cn.params_key(["W", "W"]) == ("W",) and cn.params_key([]) == ()
    assert cn.params_key(["A", "D", "C"]) == ("C", "D", "A")
    try:
        cn.params_key(["Z"])
    except ValueError:
        return
    raise AssertionError("chữ cái lạ phải bị từ chối")


# ---- từ nội dung, liên kết, hàng xóm ----

def test_content_sets_drop_the_most_common_syllables_with_alphabetical_tiebreak():
    words = [{"surface": s} for s in ("a b", "a c", "a b d", "b e")]
    stop, content = cn.content_sets(words, top=2)
    assert stop == ["a", "b"], stop  # a và b cùng có mặt ở 3 chữ: hoà thì theo thứ tự chữ cái
    assert content == [frozenset(), frozenset({"c"}), frozenset({"d"}), frozenset({"e"})]


def test_link_map_matches_the_subtree_both_ways_and_never_links_a_unit_to_itself():
    units = [X + u for u in ("D1.K1", "D1.K2", "D2.K1", "D3.K1")]
    link = cn.link_map(units, [(X + "D1.K1", X + "D2")])
    assert link[X + "D1.K1"] == [X + "D2.K1"] and link[X + "D2.K1"] == [X + "D1.K1"] and link[X + "D1.K2"] == [] and link[X + "D3.K1"] == []
    link = cn.link_map(units, [(X + "D1", X + "D1.K2")])  # đích là con của nguồn: hai đơn vị cùng Điều khớp nhau nhưng không tự nối với chính nó
    assert link[X + "D1.K2"] == [X + "D1.K1"] and link[X + "D1.K1"] == [X + "D1.K2"]


def _neighbors_fixture(extra_rows=()):
    rows = [row("D1.K1", "mức lương tối thiểu vùng"), row("D1.K1", "thời giờ làm thêm"),
            row("D2.K1", "tiền lương làm thêm giờ"), row("D2.K2", "xyz"),
            row("D3.K1", "nghỉ hằng năm")] + list(extra_rows)
    rows.sort(key=lambda r: ["D1.K1", "D2.K1", "D2.K2", "D3.K1", "D3.K9"].index(r["unit"][2:]))
    order = order_of("D1.K1", "D2.K1", "D2.K2", "D3.K1", "D3.K9")
    words = cn.build_words(rows, order)
    links = cn.link_map(list(order), [(X + "D2.K1", X + "D3.K1")])
    return words, cn.Neighbors(words, links, top=0)


def test_neighbors_group_order_one_two_three_and_shared_words_inside_a_group():
    words, nb = _neighbors_fixture()
    idx = {w["surface"]: w["idx"] for w in words}
    got = [(words[j]["surface"], g) for j, g in nb.ranked(idx["tiền lương làm thêm giờ"])]
    assert got == [("xyz", 1), ("nghỉ hằng năm", 2), ("thời giờ làm thêm", 3), ("mức lương tối thiểu vùng", 3)], got  # nhóm 3: 3 từ chung trước 1 từ chung
    # 'xyz' không chung từ nào và không có cạnh: chỉ có hàng xóm nhóm 1 (chữ cùng Điều D2); chữ không thuộc nhóm nào không phải hàng xóm; không tự là hàng xóm của mình
    assert nb.ranked(idx["xyz"]) == [(idx["tiền lương làm thêm giờ"], 1)], nb.ranked(idx["xyz"])


def test_neighbors_group_one_matches_any_occurrence_of_the_candidate_not_only_its_first():
    words, nb = _neighbors_fixture([row("D3.K9", "mức lương tối thiểu vùng")])  # chữ này gặp đầu ở D1 nhưng còn có mặt ở D3, Điều của chữ 'nghỉ hằng năm'
    idx = {w["surface"]: w["idx"] for w in words}
    got = dict(nb.ranked(idx["nghỉ hằng năm"]))
    assert got[idx["mức lương tối thiểu vùng"]] == 1, got


# ---- chia lượt ----

def test_make_rounds_packs_whole_dieu_and_splits_a_long_dieu():
    words = [{"dieu": d} for d in ["a"] * 3 + ["b"] * 2 + ["c"] * 4]
    assert cn.make_rounds(words, size=5) == [[0, 1, 2, 3, 4], [5, 6, 7, 8]]
    words = [{"dieu": d} for d in ["a"] * 7 + ["b"] * 3]
    assert cn.make_rounds(words, size=5) == [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]  # đoạn dư 2 chữ của Điều a nhận thêm Điều b (3 chữ) vì vừa 5
    assert cn.make_rounds([], size=5) == []


def test_make_rounds_fails_closed_when_new_words_of_a_dieu_are_not_contiguous():
    assert raises_exit(lambda: cn.make_rounds([{"dieu": "a"}, {"dieu": "b"}, {"dieu": "a"}], size=5))


# ---- sổ tên và ứng viên ----

def test_book_refuses_second_name_and_reuse_with_other_params():
    words = cn.build_words([row("D1.K1", "a1", params=["W"]), row("D1.K1", "a2", params=["E"]), row("D1.K1", "a3", params=["W"])], order_of("D1.K1"))
    book = cn.Book(words)
    book.add(0, "ten_a")
    book.add(2, "ten_a")  # cùng params: được
    assert book.members["ten_a"] == [0, 2] and book.name_params["ten_a"] == ("W",)
    for bad in (lambda: book.add(1, "ten_a"), lambda: book.add(0, "ten_khac")):
        try:
            bad()
        except ValueError:
            continue
        raise AssertionError("phải từ chối")


def test_candidates_use_only_named_neighbours_dedupe_names_filter_params_and_cap_at_twelve():
    rows = [row("D1.K1", f"k{n:02d}", params=["W"]) for n in range(30)] + [row("D9.K1", f"k{n:02d}", params=["W"]) for n in range(30)] + [row("D9.K1", "tau", params=["W"])]
    order = order_of("D1.K1", "D9.K1")
    words = cn.build_words(rows, order)
    nb = cn.Neighbors(words, {u: [] for u in order}, top=0)
    t = words[-1]["idx"]
    assert [j for j, g in nb.ranked(t)] == list(range(30)) and {g for _, g in nb.ranked(t)} == {1}  # 30 chữ k.. cùng Điều D9 với T, xếp theo key
    book = cn.Book(words)
    for n in range(30):  # chữ chẵn 2m và 2m+1 dùng chung tên, nên 30 chữ chỉ cho 15 tên
        book.add(n, f"ten_{n // 2:02d}")
    cands = cn.candidates(words, nb, book, t)
    assert [c["ten"] for c in cands] == [f"ten_{m:02d}" for m in range(12)], [c["ten"] for c in cands]
    assert cands[0]["params"] == ["W"] and cands[0]["vi_du"] == ["k00", "k01"]
    book2 = cn.Book(words)  # chữ chưa có tên không thành ứng viên
    book2.add(5, "chi_mot")
    assert [c["ten"] for c in cn.candidates(words, nb, book2, t)] == ["chi_mot"]


def test_candidates_cut_forty_named_neighbours_before_the_params_filter():
    rows = [row("D1.K1", f"k{n:02d}", params=["E"] if n < 40 else ["W"]) for n in range(60)] + [row("D9.K1", f"k{n:02d}", params=["E"] if n < 40 else ["W"]) for n in range(60)] \
        + [row("D9.K1", "tau", params=["W"])]
    order = order_of("D1.K1", "D9.K1")
    words = cn.build_words(rows, order)
    nb = cn.Neighbors(words, {u: [] for u in order}, top=0)
    t = words[-1]["idx"]
    book = cn.Book(words)
    for n in range(60):
        book.add(n, f"ten_{n:02d}")
    assert cn.candidates(words, nb, book, t) == []  # 40 hàng xóm đầu đều params E; 20 chữ W nằm sau hạng 40 nên bị cắt trước khi lọc params
    book3 = cn.Book(words)
    for n in range(60):
        if n >= 40 or n % 2:
            book3.add(n, f"ten_{n:02d}")  # chỉ 20 chữ E (lẻ) có tên: 40 chỗ gồm 20 chữ E và 20 chữ W
    assert [c["ten"] for c in cn.candidates(words, nb, book3, t)] == [f"ten_{n:02d}" for n in range(40, 52)]


def test_candidate_examples_are_at_most_three_and_come_from_the_lowest_word_indices():
    rows = [row("D1.K1", f"k{n:02d}", params=["W"]) for n in range(6)] + [row("D9.K1", f"k{n:02d}", params=["W"]) for n in range(6)] + [row("D9.K1", "tau", params=["W"])]
    order = order_of("D1.K1", "D9.K1")
    words = cn.build_words(rows, order)
    nb = cn.Neighbors(words, {u: [] for u in order}, top=0)
    book = cn.Book(words)
    for n in (5, 3, 1, 0, 4, 2):  # thêm không theo thứ tự chỉ số
        book.add(n, "chung")
    (c,) = cn.candidates(words, nb, book, words[-1]["idx"])
    assert c["vi_du"] == ["k00", "k01", "k02"]


# ---- luật dừng ----

def test_count_without_candidates_round_basis_ignores_words_of_the_same_round():
    rows = [row("D1.K1", "mot", params=["W"]), row("D1.K2", "hai", params=["W"])]
    order = order_of("D1.K1", "D1.K2")
    words = cn.build_words(rows, order)
    nb = cn.Neighbors(words, {u: [] for u in order}, top=0)
    assert cn.count_without_candidates(words, [[0, 1]], nb, "order") == [0]  # chữ 1 có chữ 0 đứng trước
    assert cn.count_without_candidates(words, [[0, 1]], nb, "round") == [0, 1]  # nhưng cùng lượt thì chưa có tên khi dựng lời gửi
    assert cn.count_without_candidates(words, [[0], [1]], nb, "round") == [0]


def test_report_says_when_the_table_has_no_llm_spans_instead_of_applying_the_stop_rule():
    words = cn.build_words([row("D1.K1", "mot", how="cond_node", role="ngoai_le")], order_of("D1.K1"))
    nb = cn.Neighbors(words, {X + "D1.K1": []}, top=0)
    text = "\n".join(cn.report_lines("X", words, cn.make_rounds(words), nb, 0))
    assert "KHÔNG CÓ CỤM LLM" in text and "chữ không có ứng viên" not in text and "DỪNG:" not in text and "chưa kích hoạt" not in text


# ---- dữ liệu thật (dựng bằng replay trong test) ----

def real():
    """(words, rounds, nb, contexts_by_id) của BLLĐ từ bảng cụm replay 204/204 dựng trong bộ nhớ."""
    if "real" not in _CACHE:
        doc, units, labels, nodes, refs = cc.load_inputs(DOC)
        client = llm_client.Client("replay")
        rows, rejected, uncovered, stats, notes = cc.process_doc(doc.doc_id, units, labels, nodes, refs, client)
        assert stats["batches_ok"] == stats["batches"] == 204, f"cần cache replay đủ 204/204 lô, có {stats['batches_ok']}/{stats['batches']}"
        contexts = cc.unit_contexts(units, labels)
        edges = cn.collect_edges(refs, cn.load_exception_rows(doc.doc_id), nodes)
        words, rounds, nb = cn.prepare(rows, contexts, edges)
        _CACHE["real"] = (rows, words, rounds, nb, {c["id"]: c for c in contexts})
    return _CACHE["real"]


def test_real_numbers_match_the_survey_of_14_11():
    rows, words, rounds, nb, _ = real()
    assert len(rows) == 3061 and sum(1 for r in rows if r["targets"]) == 152
    assert len(words) == 1833 and len(rounds) == 76 and sum(map(len, rounds)) == 1833 and max(map(len, rounds)) == 30
    card = "cho chức các có công của dụng hoặc hợp không lao luật làm người pháp quy quyền sử theo thể thỏa thời trong tổ việc và được định đồng động".split()
    assert set(nb.stop) == {cc.norm_token(w) for w in card}, sorted(set(nb.stop) ^ {cc.norm_token(w) for w in card})
    assert sum(1 for w in words if w["param_variants"] > 1) == 12
    assert len(cn.count_without_candidates(words, rounds, nb, "order")) == 141  # số đo A37 (8): chữ đứng trước, cắt 40 và 12, params như tập
    assert len(cn.count_without_candidates(words, rounds, nb, "round")) == 220  # số áp luật dừng: chỉ chữ ở lượt trước (12,0%)


def test_real_rounds_before_the_first_name_have_no_candidates_and_later_ones_do():
    _, words, rounds, nb, ctx = real()
    book = cn.Book(words)
    assert all(it["ung_vien"] == [] for it in cn.round_items(words, nb, book, rounds[0], ctx))
    for r in rounds[:20]:
        for i in r:
            book.add(i, "n_" + "".join(words[i]["params"]) + f"_{i // 4}")
    items = cn.round_items(words, nb, book, rounds[20], ctx)
    assert len(items) == len(rounds[20]) and any(it["ung_vien"] for it in items)
    assert all(len(it["ung_vien"]) <= cn.CANDIDATE_CAP and len(it["ngu_canh"]) <= cn.CONTEXTS_PER_WORD for it in items)


# ---- tất định theo byte ----

def round_bytes(k):
    """Lượt k dựng với sổ tên giả (mọi chữ ở lượt trước đã có tên, chữ cùng params chia nhau tên theo nhóm 4 chỉ số), JSON đã đóng gói."""
    _, words, rounds, nb, ctx = real()
    book = cn.Book(words)
    for r in rounds[:k]:
        for i in r:
            book.add(i, "n_" + "".join(words[i]["params"]) + f"_{i // 4}")
    return json.dumps(cn.round_items(words, nb, book, rounds[k], ctx), ensure_ascii=False, indent=0).encode("utf-8")


def _in_subprocess(call, seed):
    """Chạy `t.<call>` (một hàm trả bytes của file này) trong tiến trình mới với PYTHONHASHSEED=seed."""
    code = f"import sys; sys.path.insert(0, {str(Path(__file__).resolve().parent)!r}); import test_concepts_names as t; sys.stdout.buffer.write(t.{call})"
    env = dict(os.environ, PYTHONHASHSEED=str(seed))  # không dùng -I: -I làm Python bỏ qua PYTHONHASHSEED
    with tempfile.TemporaryDirectory() as tmp:  # cwd trống để không nạp nhầm file cạnh
        res = subprocess.run([sys.executable, "-c", code], cwd=tmp, env=env, capture_output=True, timeout=300)
    assert res.returncode == 0, res.stderr.decode("utf-8", "replace")[-2000:]
    return res.stdout


def test_round_bytes_do_not_depend_on_hash_seed():
    for k in (0, 20):
        a, b = _in_subprocess(f"round_bytes({k})", 1), _in_subprocess(f"round_bytes({k})", 2)
        assert a == b == round_bytes(k), f"lượt {k}: byte đổi theo PYTHONHASHSEED"
        assert len(a) > 3000
    assert round_bytes(20).count(b'"ten"') > 10  # lượt giữa chạy có ứng viên, không phải so hai chuỗi rỗng


# ---- phần 2: cổng kiểm, Run, sổ vị từ ----

def W(n, params=("W",), unit=None):
    return row(unit or f"D1.K{n}", f"c{n}", params=params)


def mini(rows_spec, rounds):
    """-> (words, run) trên dữ liệu nhỏ tự dựng; mọi đơn vị cùng Điều D1 nên là hàng xóm nhóm 1 của nhau."""
    units = list(dict.fromkeys(r["unit"] for r in rows_spec))
    words = cn.build_words(rows_spec, {u: i for i, u in enumerate(units)})
    nb = cn.Neighbors(words, cn.link_map(units, []), top=0)
    ctx = {u: {"id": u, "heading": "tiêu đề", "chapeau": "", "text": "chữ " + u} for u in units}
    return words, cn.Run(words, nb, ctx, rounds)


def out(*items):
    return {"chu": [{"chu_id": c, "kieu": k, "ten": t} for c, k, t in items]}


def test_gate_accepts_new_reuse_of_a_shown_name_and_reuse_of_a_new_name_given_earlier_in_the_same_round():
    words, run = mini([W(0), W(1), W(2)], [[0], [1, 2]])
    r1 = run.next_round()
    assert r1["n"] == 1 and r1["indices"] == [0] and r1["shown"] == {0: []}
    assert run.apply(out(("C0000", "new", "name_a"))) == []
    r2 = run.next_round()
    assert r2["shown"] == {1: ["name_a"], 2: ["name_a"]}
    assert run.apply(out(("C0001", "new", "name_b"), ("C0002", "reuse", "name_b"))) == []  # name_b không nằm trong danh sách đã đưa cho chữ 2, nhưng chữ 1 vừa đặt nó trong cùng lượt
    assert run.book.name_of == {0: "name_a", 1: "name_b", 2: "name_b"} and run.decisions[2]["kieu"] == "reuse" and run.decisions[2]["ung_vien"] == ["name_a"]
    assert run.next_round() is None and not run.rejected


def test_gate_rejects_bad_new_names_with_fixed_reason_codes_and_no_python_repr_in_the_text():
    words, run = mini([W(n) for n in range(7)], [list(range(7))])
    run.next_round()
    fails = run.apply(out(("C0000", "new", "Bad Name"), ("C0001", "new", "ab"), ("C0002", "new", "not_x"), ("C0003", "new", "non"), ("C0004", "new", "good_one"),
                          ("C0005", "new", "good_one"), ("C0006", "maybe", "good_one")))
    assert [(c, k) for c, k, _ in fails] == [("C0000", "new_sai_dang"), ("C0001", "new_sai_dang"), ("C0002", "new_phu_dinh"), ("C0003", "new_phu_dinh"),
                                             ("C0005", "new_da_co"), ("C0006", "kieu_la")], fails
    assert all("'" not in text for _, _, text in fails) and 'new "Bad Name"' in fails[0][2] and "{2,49}" in fails[0][2]
    assert run.book.name_of == {4: "good_one"} and sorted(run.notes) == [0, 1, 2, 3, 5, 6]


def test_gate_fails_only_that_word_when_its_entry_is_missing_or_duplicated():
    words, run = mini([W(0), W(1), W(2)], [[0, 1, 2]])
    run.next_round()
    fails = run.apply(out(("C0000", "new", "aaa_x"), ("C0000", "new", "bbb_x"), ("C0002", "new", "ccc_x")))
    assert [(c, k) for c, k, _ in fails] == [("C0000", "lap_muc"), ("C0001", "thieu_muc")] and run.book.name_of == {2: "ccc_x"}


def test_gate_rejects_reuse_outside_the_shown_set_including_a_new_name_that_was_itself_rejected():
    words, run = mini([W(0), W(1), W(2, params=("E",)), W(3)], [[0], [1, 2, 3]])
    run.next_round()
    run.apply(out(("C0000", "new", "name_a")))
    r2 = run.next_round()
    assert r2["shown"] == {1: ["name_a"], 2: [], 3: ["name_a"]}  # chữ 2 có params E nên không thấy tên params W
    fails = run.apply(out(("C0001", "new", "not_bad"), ("C0002", "reuse", "name_a"), ("C0003", "reuse", "not_bad")))
    assert [(c, k) for c, k, _ in fails] == [("C0001", "new_phu_dinh"), ("C0002", "reuse_ngoai_tap"), ("C0003", "reuse_ngoai_tap")], fails  # chữ 3 dựa vào tên của chữ 1 mà chữ 1 bị loại


def test_gate_rejects_reuse_of_a_same_round_new_name_with_other_params():
    words, run = mini([W(0), W(1, params=("E",))], [[0, 1]])
    run.next_round()
    fails = run.apply(out(("C0000", "new", "name_w"), ("C0001", "reuse", "name_w")))
    assert [(c, k) for c, k, _ in fails] == [("C0001", "reuse_lech_params")], fails


def test_retry_goes_first_in_the_next_round_with_the_reason_and_passes_or_is_rejected_on_the_second_failure():
    words, run = mini([W(0), W(1)], [[0], [1]])
    r1 = run.next_round()
    assert "loi_lan_truoc" not in r1["items"][0]
    run.apply(out(("C0000", "new", "Bad Name")))
    assert run.pending == [0] and run.asked[0] == 1
    r2 = run.next_round()
    assert r2["n"] == 2 and r2["indices"] == [0, 1] and r2["items"][0]["loi_lan_truoc"] == cn.reason_text("new_sai_dang", "Bad Name") and "loi_lan_truoc" not in r2["items"][1]
    assert run.apply(out(("C0000", "new", "name_a"), ("C0001", "reuse", "name_a"))) == [] and run.pending == [] and not run.rejected and run.notes == {}
    assert run.next_round() is None
    words, run = mini([W(0), W(1)], [[0], [1]])  # lỗi lần hai thì loại
    run.next_round()
    run.apply(out(("C0000", "new", "Bad Name")))
    run.next_round()
    run.apply(out(("C0000", "new", "Bad Name"), ("C0001", "new", "name_b")))
    assert sorted(run.rejected) == [0] and run.asked[0] == 2 and run.pending == [] and run.next_round() is None


def test_extra_round_with_only_retries_follows_the_last_planned_round():
    words, run = mini([W(0)], [[0]])
    run.next_round()
    run.apply(out(("C0000", "new", "Bad Name")))
    r2 = run.next_round()
    assert r2["n"] == 2 and r2["indices"] == [0] and len(run.planned) == 1
    run.apply(out(("C0000", "new", "Bad Name")))
    assert sorted(run.rejected) == [0] and run.next_round() is None and len(run.round_log) == 2


def test_apply_with_a_wrong_shape_raises_and_leaves_the_state_unchanged():
    words, run = mini([W(0), W(1)], [[0, 1]])
    for bad in ({"chu": [{"chu_id": "C0009", "kieu": "new", "ten": "abc"}]}, {"chu": "x"}, [], {"chu": [{"chu_id": "C0000", "kieu": 1, "ten": "abc"}]}, {"chu": [{"chu_id": ["C0000"], "kieu": "new", "ten": "abc"}]}):
        r = run.next_round() if run.current is None else run.current
        try:
            run.apply(bad)
        except ValueError:
            assert run.current is r and not run.asked and not run.book.name_of and not run.round_log
            continue
        raise AssertionError(f"phải từ chối hình sai: {bad}")
    try:
        run.next_round()
    except RuntimeError:
        pass
    else:
        raise AssertionError("không được dựng lượt mới khi lượt trước chưa áp")
    assert run.apply(out(("C0000", "new", "abc_d"), ("C0001", "new", "abc_e"))) == []
    try:
        run.apply(out())
    except RuntimeError:
        return
    raise AssertionError("không được áp hai lần")


def test_early_stop_only_after_three_rounds_and_only_above_thirty_percent_of_asks():
    bad = lambda ids: out(*[(f"C{i:04d}", "new", "Bad Name") for i in ids])
    words, run = mini([W(n) for n in range(6)], [[0, 1], [2, 3], [4, 5]])
    run.next_round(); run.apply(bad([0, 1]))
    assert run.early_stop() is None  # mới một lượt
    run.next_round(); run.apply(bad([0, 1, 2, 3]))
    run.next_round(); run.apply(bad(run.current["indices"]))
    assert run.early_stop().startswith("DỪNG SỚM")
    words, run = mini([W(n) for n in range(6)], [[0, 1], [2, 3], [4, 5]])
    for ids in ([0, 1], [2, 3], [4, 5]):
        run.next_round()
        run.apply(out(*[(f"C{i:04d}", "new", f"name_{i}") for i in ids]))
    assert run.early_stop() is None


def _ledger_fixture():
    rows = [row("D1.K1", "kl1", role="ket_luan", params=["W"]), row("D1.K1", "dk1", role="dieu_kien", params=["C"]),
            row("D2.K1", "kl1", role="dieu_kien", params=["E", "W"]), row("D2.K2", "ref", role="ngoai_le", targets=["X.D1"], how="cond_node"),
            row("D3.K1", "kl1b", role="dieu_kien", params=["W"])]
    words, run = mini(rows, [[0, 1, 2]])
    run.next_round()
    assert run.apply(out(("C0000", "new", "exempt"), ("C0001", "new", "contract"), ("C0002", "reuse", "exempt"))) == []
    return rows, words, run


def test_ledger_fills_names_flags_and_derives_kind_anchors_surface_and_used_in_without_touching_the_input():
    rows, words, run = _ledger_fixture()
    before = json.dumps(rows, ensure_ascii=False)
    named, ledger = cn.build_ledger(words, rows, run)
    assert json.dumps(rows, ensure_ascii=False) == before and all(r["predicate"] is None for r in rows)  # đầu vào nguyên vẹn
    assert [(r["unit"], r["predicate"], r["flags"]) for r in named] == [("X.D1.K1", "exempt", []), ("X.D1.K1", "contract", []), ("X.D2.K1", "exempt", ["param_conflict"]),
                                                                      ("X.D2.K2", None, []), ("X.D3.K1", "exempt", ["reuse_llm"])]
    contract, exempt = ledger  # sổ xếp theo tên vị từ
    assert contract =={"predicate": "contract", "params": ["C"], "kind": "input", "anchors": [], "surface": ["dk1"], "used_in": ["X.D1.K1"]}
    assert exempt == {"predicate": "exempt", "params": ["W"], "kind": "concept", "anchors": ["X.D1.K1"], "surface": ["kl1", "kl1b"],
                      "used_in": ["X.D2.K1", "X.D2.K2", "X.D3.K1"]}  # X.D2.K2 vào qua targets trỏ tới X.D1, tổ tiên của neo X.D1.K1


def test_review_sample_lists_reuse_decisions_with_earlier_users_and_is_evenly_spaced_beyond_the_cap():
    rows, words, run = _ledger_fixture()
    assert cn.review_reuse_sample(run, words) == [{"chu_id": "C0002", "chu": "kl1b", "ten": "exempt", "don_vi": "X.D3.K1", "da_dung_boi": ["kl1"]}]
    words, run = mini([W(n) for n in range(10)], [list(range(10))])  # 10 quyết định reuse tự dựng, để thử chọn đều khi vượt cap
    run.decisions = {i: {"kieu": "reuse", "ten": "exempt"} for i in range(10)}
    run.book.members["exempt"] = list(range(10))
    got = [s["chu_id"] for s in cn.review_reuse_sample(run, words, cap=4)]
    assert got == ["C0000", "C0002", "C0005", "C0007"], got


def test_report_flags_too_many_rejected_and_unfinished_runs():
    words, run = mini([W(0), W(1)], [[0], [1]])
    run.next_round(); run.apply(out(("C0000", "new", "Bad Name")))
    text = "\n".join(cn.names_report_lines("X", run, words, [], []))
    assert "CHƯA XONG: 2 chữ" in text and "DỪNG:" not in text and "new_sai_dang 1" in text
    run.next_round(); run.apply(out(("C0000", "new", "Bad Name"), ("C0001", "new", "name_b")))
    text = "\n".join(cn.names_report_lines("X", run, words, [], []))
    assert "DỪNG: chữ bị loại hơn 2%" in text and "chữ bị loại: 1" in text and "CHƯA XONG" not in text


# ---- phần 2 trên dữ liệu thật, LLM giả ----

BAD_TWICE = {50, 120, 333}


def fake_policy(rd, inject, last):
    """LLM giả: mặc định `reuse` ứng viên đầu, không có ứng viên thì `new`; chữ chỉ số chia hết cho 5 thì dùng lại tên `new` của chữ trước (cùng params) trong lượt.
    inject=True thêm lỗi cố định: chữ BAD_TWICE luôn tên sai; chữ i%40==7 và chữ cuối của kho (`last`, nằm ở lượt kế hoạch cuối nên buộc có lượt thử lại thứ 77) sai lần hỏi đầu
    (xen kẽ sai dạng và tên phủ định); chữ i%40==8 `reuse` tên phủ định kia ở lần hỏi đầu."""
    res, new_by_params = [], {}
    for it in rd["items"]:
        i, cid, pk = int(it["chu_id"][1:]), it["chu_id"], tuple(it["params"])
        first = "loi_lan_truoc" not in it
        if inject and i in BAD_TWICE:
            res.append((cid, "new", "Bad Name"))
        elif inject and first and (i % 40 == 7 or i == last):
            res.append((cid, "new", "not_thing" if (i // 40) % 2 else "Bad Name"))
        elif inject and first and i % 40 == 8:
            res.append((cid, "reuse", "not_thing"))
        elif it["ung_vien"]:
            res.append((cid, "reuse", it["ung_vien"][0]["ten"]))
        elif i % 5 == 0 and pk in new_by_params:
            res.append((cid, "reuse", new_by_params[pk]))
        else:
            name = f"ten_{i:04d}"
            new_by_params[pk] = name
            res.append((cid, "new", name))
    return out(*res)


def full_fake_run(inject):
    rows, words, rounds, nb, ctx = real()
    run = cn.Run(words, nb, ctx, rounds)
    while True:
        rd = run.next_round()
        if rd is None:
            return run, rows, words
        run.apply(fake_policy(rd, inject, len(words) - 1))


def test_full_fake_run_without_failures_names_every_word_in_76_rounds_and_reuses_names():
    run, rows, words = full_fake_run(False)
    assert len(run.round_log) == 76 and not run.rejected and max(run.asked.values()) == 1 and len(run.book.name_of) == len(words) == 1833 and not run.fail_log
    kinds = collections.Counter(d["kieu"] for d in run.decisions.values())
    assert kinds["reuse"] > cn.REVIEW_REUSE_CAP and kinds["new"] > 100
    assert any(d["kieu"] == "reuse" and d["ten"] not in d["ung_vien"] for d in run.decisions.values())  # đường `reuse` tên new cùng lượt có đi qua
    named, ledger = cn.build_ledger(words, rows, run)
    assert all(r["predicate"] for r in named if not r["targets"]) and all(r["predicate"] is None for r in rows)  # fixture dùng chung không bị sửa
    assert len(ledger) == len(run.book.name_params) < 1833 and any(len(e["surface"]) >= 2 for e in ledger)
    assert len(cn.review_reuse_sample(run, words)) == cn.REVIEW_REUSE_CAP


def test_full_fake_run_with_injected_failures_goes_through_retry_rejection_dependency_and_the_extra_round():
    run, rows, words = full_fake_run(True)
    _, _, rounds, _, _ = real()
    assert rounds[-1][-1] == len(words) - 1  # chữ cuối của kho nằm ở lượt kế hoạch cuối và bị chèn lỗi lần đầu, nên phải có lượt thử lại thứ 77
    assert len(run.round_log) == 77 and run.round_log[-1]["asked"] == run.round_log[-2]["failed"]  # lượt 77 chỉ gồm chữ lỗi lần đầu ở lượt 76
    assert set(run.rejected) == BAD_TWICE and max(run.asked.values()) == 2
    assert all((i in run.book.name_of) != (i in run.rejected) for i in range(len(words))) and len(run.book.name_of) + len(run.rejected) == 1833
    codes = collections.Counter(c for _, _, c in run.fail_log)
    assert codes["new_sai_dang"] > 0 and codes["new_phu_dinh"] > 0 and codes["reuse_ngoai_tap"] > 0, codes
    named, ledger = cn.build_ledger(words, rows, run)
    rejected_keys = {words[i]["key"] for i in run.rejected}
    assert all((r["predicate"] is None) == (bool(r["targets"]) or cn.text_norm(r["span"]) in rejected_keys) for r in named)  # chỉ hàng có targets và hàng của chữ bị loại không có tên
    text = "\n".join(cn.names_report_lines("X", run, words, named, ledger))
    assert "CHƯA XONG" not in text and "DỪNG" not in text and "chữ bị loại: 3" in text
    assert all(r["predicate"] is None for r in rows)


def ledger_bytes():
    run, rows, words = full_fake_run(True)
    named, ledger = cn.build_ledger(words, rows, run)
    blob = {"ledger": ledger, "rows": named, "fail": run.fail_log, "rejected": sorted(run.rejected), "decisions": [[i, d] for i, d in sorted(run.decisions.items())]}
    return json.dumps(blob, ensure_ascii=False).encode("utf-8")


def test_ledger_bytes_after_a_full_run_with_failures_do_not_depend_on_hash_seed():
    a, b = _in_subprocess("ledger_bytes()", 1), _in_subprocess("ledger_bytes()", 2)
    assert a == b == ledger_bytes() and len(a) > 100000


# ---- phần 3a: lời nhắc, lời gửi, cache, replay, mẫu đọc tay, file đầu ra ----

def test_prompt_is_neutral_and_its_example_obeys_the_gate_and_is_not_from_the_law():
    # lời nhắc VÀ các câu lý do lỗi (chúng vào lời gửi của lượt thử lại nên LLM cũng đọc) không được lộ chữ về dự án
    texts = [cn.SYSTEM] + [cn.reason_text(code, "ten_mau") for code in cn.REASONS]
    for text in texts:
        low = text.lower()
        for w in ("cache", "api", "casp", "pipeline", "dự án", "bước", "replay", "claude", "sonnet", "concepts", "kltn", "1.6", "a37", "đồ án"):
            assert w not in low, f"lộ chữ về dự án: {w!r} trong {text[:60]!r}"
    assert "cùng params" in cn.SYSTEM and "đối lập" not in cn.SYSTEM  # reuse tên new cùng lượt đòi cùng params (cổng reuse_lech_params); không gợi đặt tên bằng nghĩa ngược
    assert "{VI_DU}" not in cn.SYSTEM and all(chu in cn.SYSTEM and ten in cn.SYSTEM for chu, _, ten in cn.PROMPT_EXAMPLE)
    words, run = mini([row(f"D1.K{n}", chu, params=["W"]) for n, (chu, _, _) in enumerate(cn.PROMPT_EXAMPLE)], [list(range(len(cn.PROMPT_EXAMPLE)))])
    run.next_round()
    assert run.apply(out(*[(f"C{n:04d}", kieu, ten) for n, (_, kieu, ten) in enumerate(cn.PROMPT_EXAMPLE)])) == []  # đúng dạng, khẳng định, reuse chỉ trỏ tên new đứng trước
    blob = " ".join(p.read_text(encoding="utf-8").lower() for p in (Path(__file__).resolve().parent.parent / "data" / "raw" / "labor").rglob("*.txt"))
    assert blob and not any(chu.lower() in blob or ten in blob for chu, _, ten in cn.PROMPT_EXAMPLE), "ví dụ của lời nhắc phải là chữ bịa, không có trong kho luật"


def test_user_message_is_one_stable_utf8_serialisation_of_the_items():
    items = [{"chu_id": "C0001", "chu": "hợp đồng", "ung_vien": []}]
    assert cn.user_message(items) == json.dumps({"chu": items}, ensure_ascii=False, indent=0) and "hợp đồng" in cn.user_message(items)
    assert cn.user_message(items) == cn.user_message(json.loads(json.dumps(items)))


def test_replay_through_the_real_cache_matches_the_direct_fake_run():
    cfg = llm_client.load_config()
    _, words, rounds, nb, ctx = real()
    direct = cn.Run(words, nb, ctx, rounds)
    with tempfile.TemporaryDirectory() as tmp:
        n = 0
        while True:
            rd = direct.next_round()
            if rd is None:
                break
            output = fake_policy(rd, True, len(words) - 1)
            cn.store_round(tmp, cfg, rd["items"], output)  # cùng hàm mà `--nhap` (phần 3b) sẽ gọi, nên ghi và đọc không lệch khoá
            direct.apply(output)
            n += 1
        client = llm_client.Client("replay", config=cfg, cache_dir=tmp)
        replayed = cn.Run(words, nb, ctx, rounds)
        assert cn.run_rounds(client, replayed) is None
        assert client.hits == n == 77 and client.calls == 0
        assert replayed.decisions == direct.decisions and replayed.rejected == direct.rejected and replayed.round_log == direct.round_log and replayed.fail_log == direct.fail_log


def test_replay_stops_at_the_first_missing_round_and_the_report_says_it_is_unfinished():
    cfg = {"ten.model": "m-ten"}
    with tempfile.TemporaryDirectory() as tmp:
        words, run = mini([W(0), W(1)], [[0], [1]])
        assert "lượt 1 thiếu bản ghi đã lưu hoặc bản ghi sai hình" in cn.run_rounds(llm_client.Client("replay", config=cfg, cache_dir=tmp), run) and run.round_log == [] and run.current is not None
        words, probe = mini([W(0), W(1)], [[0], [1]])
        cn.store_round(tmp, cfg, probe.next_round()["items"], out(("C0000", "new", "name_a")))  # chỉ có lượt 1
        words, run = mini([W(0), W(1)], [[0], [1]])
        stop = cn.run_rounds(llm_client.Client("replay", config=cfg, cache_dir=tmp), run)
        assert stop.startswith("CHƯA ĐỦ: lượt 2") and len(run.round_log) == 1 and run.book.name_of == {0: "name_a"}
        assert "CHƯA XONG: 1 chữ" in "\n".join(cn.names_report_lines("X", run, words, [], []))


def test_replay_treats_a_stored_record_of_wrong_shape_as_missing_and_moves_it_to_rejected():
    cfg = {"ten.model": "m-ten"}
    with tempfile.TemporaryDirectory() as tmp:
        words, probe = mini([W(0)], [[0]])
        path = cn.store_round(tmp, cfg, probe.next_round()["items"], {"chu": "không phải danh sách"})
        words, run = mini([W(0)], [[0]])
        stop = cn.run_rounds(llm_client.Client("replay", config=cfg, cache_dir=tmp), run)
        assert "sai hình" in stop and not path.exists() and (path.parent / "_rejected" / path.name).exists() and run.current is not None


def test_results_of_an_untouched_run_have_no_names_and_an_empty_ledger_and_outputs_are_written_where_asked():
    rows = [W(0), W(1)]
    words, run = mini(rows, [[0, 1]])
    files = cn.result_files(words, rows, run, run.nb)
    assert [r["predicate"] for r in files["named"]] == [None, None] and files["ledger"] == [] and files["rejected"] == [] and files["review"] == []
    with tempfile.TemporaryDirectory() as tmp:
        paths = {k: Path(tmp) / "sub" / f"{k}.txt" for k in ("named", "ledger", "rejected", "review", "report")}
        cn.write_outputs(paths, files, ["dòng một", "dòng hai"])
        assert len(paths["named"].read_text(encoding="utf-8").splitlines()) == 2 and paths["ledger"].read_text(encoding="utf-8") == "" and paths["report"].read_text(encoding="utf-8") == "dòng một\ndòng hai\n"


def test_review_new_sample_uses_the_approved_near_twin_measure_and_only_names_the_llm_could_see():
    spans = [row("D1.K1", "alpha beta gamma", params=["W"]), row("D1.K2", "alpha beta gamma delta", params=["W"]), row("D1.K3", "zzz yyy", params=["W"]),
             row("D1.K4", "qqq", params=["W"]), row("D1.K5", "beta gamma delta alpha epsilon", params=["W"]), row("D1.K6", "alpha beta gamma delta epsilon", params=["W"])]
    words, run = mini(spans, [[0], [1, 2, 3, 4, 5]])
    run.next_round(); run.apply(out(("C0000", "new", "name_a")))
    run.next_round(); run.apply(out(("C0001", "reuse", "name_a"), ("C0002", "new", "name_c"), ("C0003", "new", "name_d"), ("C0004", "new", "name_e"), ("C0005", "new", "name_f")))
    sample = cn.review_new_sample(run, words, run.nb)
    # C0002 không có song sinh; C0003 chỉ có một từ nội dung. C0004 và C0005 giống C0000 (3/5 = 0,6, đúng ngưỡng). C0001 cũng dùng name_a và giống hơn (4/5) nhưng được đặt ở CÙNG lượt, lúc quyết định LLM chưa thấy nó,
    # nên không được tính là song sinh; nếu tính thì song_sinh của hai chữ này có thêm "alpha beta gamma delta"
    twin = [{"ten": "name_a", "chu": "alpha beta gamma"}]
    assert [(s["chu_id"], s["song_sinh"]) for s in sample] == [("C0004", twin), ("C0005", twin)], sample
    assert [s["chu_id"] for s in cn.review_new_sample(run, words, run.nb, cap=1)] == ["C0004"]
    assert cn.review_new_sample(run, words, cn.Neighbors(words, run.nb.links, top=100)) == []  # mọi âm tiết thành âm tiết dừng: không chữ nào đủ hai từ nội dung, không chia cho 0


# ---- phần 3b: thư mục làm việc (xuat, tiep, nhap) ----

M = "m-ten"
CFG = {"ten.model": M}


def real_make():
    _, words, rounds, nb, ctx = real()
    return lambda: cn.Run(words, nb, ctx, rounds)


def write_out(wd, n, output, model=M, effort=cn.EFFORT):
    (wd / "out" / f"{n:03d}.json").write_text(json.dumps(output, ensure_ascii=False), encoding="utf-8")
    with open(wd / "nhat_ky.tsv", "a", encoding="utf-8") as f:
        f.write(f"{n:03d}\t{model}\t{effort}\n")


def answer(wd, n):
    """Đầu ra giả (có chèn lỗi cổng) cho lo/NNN.json, đọc đúng file subagent sẽ đọc."""
    return fake_policy({"items": json.loads((wd / "lo" / f"{n:03d}.json").read_text(encoding="utf-8"))["chu"]}, True, -1)


def workdir_six_rounds(tmp):
    """Dựng thư mục làm việc trên dữ liệu thật, chạy 6 lượt qua tiep (lượt 2 sai hình lần đầu), lượt 7 khai model sai. -> (wd, các dòng tiep đã in)."""
    make, wd = real_make(), Path(tmp) / "wd"
    assert cn.xuat(wd, make, M, DOC).startswith("đã dựng")
    lines = []
    for n in range(1, 8):
        lines.append(cn.tiep(wd, ["moi"], make, M))
        if n == 2:
            write_out(wd, n, {"chu": "không phải danh sách"})
            lines.append(cn.tiep(wd, ["ghi", "002"], make, M))
            assert not (wd / "out" / "002.json").exists()  # đã cất sang out_sai/
        write_out(wd, n, answer(wd, n), model=M if n < 7 else "model-khac")
        lines.append(cn.tiep(wd, ["ghi", f"{n:03d}"], make, M))
    return wd, lines


def test_workdir_loop_writes_rounds_one_by_one_redoes_a_wrong_shape_and_stops_on_a_wrong_model():
    with tempfile.TemporaryDirectory() as tmp:
        wd, lines = workdir_six_rounds(tmp)
        assert [l.split(":")[0] for l in lines] == ["LƯỢT 001", "ĐÃ NHẬN 001", "LƯỢT 002", "SAI HÌNH 002", "ĐÃ NHẬN 002"] + sum(([f"LƯỢT {n:03d}", f"ĐÃ NHẬN {n:03d}"] for n in range(3, 7)), []) + ["LƯỢT 007", "DỪNG"], lines
        assert (wd / "out_sai" / "002_lan1.json").exists() and "model-khac" in lines[-1]
        assert cn.tiep(wd, ["ghi", "006"], real_make(), M).startswith("ĐÃ NHẬN 006")  # gọi lại cho lượt đã nhận chỉ báo lại
        assert cn.tiep(wd, ["ghi", "009"], real_make(), M).startswith("DỪNG: lượt 007: nhat_ky ghi model")  # chuỗi dừng ở 007: báo lý do thật
        # đúng model mà effort khác "high" (cột duy nhất ghi lại A37 (7)) cũng DỪNG
        (wd / "nhat_ky.tsv").write_text((wd / "nhat_ky.tsv").read_text(encoding="utf-8") + f"007\t{M}\tmedium\n", encoding="utf-8")
        assert "effort 'medium'" in cn.tiep(wd, ["ghi", "007"], real_make(), M)
        # lo/NNN.json đúng từng byte bằng lời gửi của lần chạy trực tiếp (thứ đi vào khoá cache)
        direct = real_make()()
        for n in range(1, 7):
            rd = direct.next_round()
            assert (wd / "lo" / f"{n:03d}.json").read_text(encoding="utf-8") == cn.user_message(rd["items"])
            direct.apply(answer(wd, n))
        # sai hình lần hai ở cùng lượt thì DỪNG
        (wd / "nhat_ky.tsv").write_text((wd / "nhat_ky.tsv").read_text(encoding="utf-8") + f"007\t{M}\t{cn.EFFORT}\n", encoding="utf-8")
        for k in (1, 2):
            (wd / "out" / "007.json").write_text("{không phải json", encoding="utf-8")
            line = cn.tiep(wd, ["ghi", "007"], real_make(), M)
            assert line.startswith("SAI HÌNH 007" if k == 1 else "DỪNG: lượt 007 sai hình lần hai"), line


def test_nhap_stores_every_accepted_round_and_replay_of_that_cache_reproduces_the_fold():
    with tempfile.TemporaryDirectory() as tmp:
        wd, _ = workdir_six_rounds(tmp)
        cache = Path(tmp) / "cache"
        lines, bad = cn.nhap(wd, real_make(), CFG, cache_dir=cache)
        assert bad and "ghi mới: 6" in lines[0] and "model" in lines[1], lines  # lượt 7 khai model sai: không ghi, báo lỗi
        recs = [json.loads(p.read_text(encoding="utf-8")) for p in (cache / cn.TASK).glob("*.json")]
        assert len(recs) == 6 and all(r["produced_by"] == "claude_code_sandbox" and r["producer_model_reported"] == M and r["effort_reported"] == cn.EFFORT for r in recs)
        folded = real_make()()
        done, _ = cn.fold_dir(wd, folded, M)
        replayed = real_make()()
        stop = cn.run_rounds(llm_client.Client("replay", config=CFG, cache_dir=cache), replayed)
        assert stop.startswith("CHƯA ĐỦ: lượt 7") and len(done) == 6
        assert replayed.decisions == folded.decisions and replayed.fail_log == folded.fail_log and replayed.notes == folded.notes and folded.fail_log  # có lỗi cổng thật đi qua đường thử lại
        # nhập lại: không ghi gì; bản ghi bị đổi đầu ra: DỪNG, trừ khi --de
        assert "ghi mới: 0; đã có, cùng đầu ra: 6" in cn.nhap(wd, real_make(), CFG, cache_dir=cache)[0][0]
        p = sorted((cache / cn.TASK).glob("*.json"))[0]
        rec = json.loads(p.read_text(encoding="utf-8"))
        rec["output"] = {"chu": []}
        p.write_text(json.dumps(rec), encoding="utf-8")
        lines, bad = cn.nhap(wd, real_make(), CFG, cache_dir=cache)
        assert bad and lines[0].startswith("DỪNG ở lượt") and "đầu ra khác" in lines[0]
        assert "ghi mới: 6" in cn.nhap(wd, real_make(), CFG, cache_dir=cache, de=True)[0][0]


def test_a_changed_lo_file_stops_tiep_and_nhap_at_that_round():
    with tempfile.TemporaryDirectory() as tmp:
        wd, _ = workdir_six_rounds(tmp)
        p = wd / "lo" / "003.json"
        p.write_text(p.read_text(encoding="utf-8") + " ", encoding="utf-8")
        assert cn.tiep(wd, ["moi"], real_make(), M).startswith("DỪNG: lo/003.json khác lượt dựng lại")
        lines, bad = cn.nhap(wd, real_make(), CFG, cache_dir=Path(tmp) / "cache")
        assert bad and "ghi mới: 2" in lines[0] and "lech ở lượt 003" in lines[1]
        # lời nhắc của thư mục khác lời nhắc của repo (repo sửa lời nhắc sau khi dựng thư mục): không ghi lượt nào
        assert cn.tiep(wd, ["ghi", "006"], real_make(), M).startswith("DỪNG: lo/003.json khác")  # ghi một lượt sau chỗ hỏng: báo đúng lý do
        s = wd / "system.txt"
        s.write_text(s.read_text(encoding="utf-8").replace("TÊN", "tên", 1), encoding="utf-8", newline="\n")
        assert cn.tiep(wd, ["moi"], real_make(), M) == cn.tiep(wd, ["ghi", "006"], real_make(), M) == "DỪNG: system.txt khác bản đang dùng; báo người dùng"
        lines, bad = cn.nhap(wd, real_make(), CFG, cache_dir=Path(tmp) / "cache2")
        assert bad and "ghi mới: 0" in lines[0] and not (Path(tmp) / "cache2").exists()


def test_xuat_refuses_inside_the_repo_a_non_empty_folder_and_the_twenty_percent_stop_rule():
    words, run = mini([W(0), W(1)], [[0, 1]])  # một lượt: không chữ nào có ứng viên (100%)
    repo = Path(__file__).resolve().parent.parent
    with tempfile.TemporaryDirectory() as tmp:
        assert raises_exit(lambda: cn.xuat(repo / "khong_duoc", lambda: run, M, DOC)) and not (repo / "khong_duoc").exists()
        (Path(tmp) / "a").mkdir()
        (Path(tmp) / "a" / "x").write_text("x")
        assert raises_exit(lambda: cn.xuat(Path(tmp) / "a", lambda: run, M, DOC))
        assert raises_exit(lambda: cn.xuat(Path(tmp) / "b", lambda: run, M, DOC)) and not (Path(tmp) / "b").exists()  # luật dừng: không ghi gì


def test_xuat_files_are_filled_neutral_and_the_tiep_stub_runs_in_a_fresh_process():
    with tempfile.TemporaryDirectory() as tmp:
        wd = Path(tmp) / "wd"
        cn.xuat(wd, real_make(), M, DOC)
        guide = (wd / "HUONG_DAN.md").read_text(encoding="utf-8")
        assert "@" not in guide and M in guide and cn.EFFORT in guide and f"model `{cn.SUBAGENT_MODEL}`" in guide
        assert (wd / "system.txt").read_text(encoding="utf-8") == cn.SYSTEM + "\n" and json.loads((wd / "schema.json").read_text(encoding="utf-8")) == cn.SCHEMA
        lines = ["LƯỢT 001: x", cn._line([], {"kind": "lech", "n": 1}, None, wd), cn._line([], {"kind": "model", "n": 1, "msg": "m"}, None, wd), cn._line([], {"kind": "lo_thua", "n": 1}, None, wd)]
        for text in [guide] + lines:  # tên model (sonnet) thì phải có: phiên chính cần nó để đặt tham số subagent
            low = text.lower()
            for w in ("cache", "api", "casp", "pipeline", "dự án", "bước", "replay", "concepts", "kltn", "1.6", "a37", "đồ án", "repo", "luật"):
                assert w not in low, f"lộ chữ về dự án: {w!r}"
        # tiep.py thật chạy được trong tiến trình mới, cwd là thư mục làm việc (đường của phiên Claude Code); in đúng một dòng
        res = subprocess.run([sys.executable, "tiep.py", "moi"], cwd=wd, capture_output=True, timeout=300)
        out_lines = res.stdout.decode("utf-8").strip().splitlines()
        assert res.returncode == 0 and len(out_lines) == 1 and out_lines[0].startswith("LƯỢT 001") and (wd / "lo" / "001.json").exists(), res.stderr.decode("utf-8", "replace")[-1500:]


def test_tiep_entry_turns_any_error_into_one_neutral_line_and_a_detail_file():
    import contextlib
    import io
    with tempfile.TemporaryDirectory() as tmp:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            cn.tiep_entry(Path(tmp) / "tiep.py", ["moi"], "KHONG_CO_VAN_BAN")
        assert buf.getvalue().strip() == "DỪNG: lỗi khi dựng lượt (chi tiết trong loi_tiep.txt); báo người dùng"
        assert "KHONG_CO_VAN_BAN" in (Path(tmp) / "loi_tiep.txt").read_text(encoding="utf-8")


def test_fresh_run_builds_the_span_table_from_the_cache_and_never_reads_the_spans_file_on_disk():
    real_read = cn.parse.read_jsonl
    seen = []

    def guarded(p):
        seen.append(Path(p).name)
        assert not Path(p).name.startswith("concepts_spans_"), "fresh_run không được đọc concepts_spans_*.jsonl (run_all --llm off ghi đè file đó)"
        return real_read(p)
    cn.parse.read_jsonl = guarded
    try:
        run = cn.fresh_run(DOC)
    finally:
        cn.parse.read_jsonl = real_read
    _, words, rounds, _, _ = real()
    assert [w["key"] for w in run.words] == [w["key"] for w in words] and run.planned == rounds and seen


# ---- phần 4: checks của 1.6B ----

def test_checks_accept_a_full_fake_run_and_catch_each_broken_invariant():
    import checks
    run, rows, words = full_fake_run(True)
    named, ledger = cn.build_ledger(words, rows, run)
    units = {r["unit"]: {} for r in rows}
    assert checks.names_problems(rows, units, named, ledger) == []
    empty_named, empty_ledger = cn.build_ledger(words, rows, cn.Run(words, run.nb, run.ctx, run.planned))
    assert checks.names_problems(rows, units, empty_named, empty_ledger) == []  # chưa có lượt nào: vẫn sạch
    i = next(k for k, r in enumerate(named) if r["predicate"])
    j = next(k for k, r in enumerate(named) if r["targets"])
    other = next(e["predicate"] for e in ledger if e["predicate"] != named[i]["predicate"])
    broken = {"cùng chữ khác tên": lambda n, l: n[i].update(predicate=other),
              "hàng có targets có tên": lambda n, l: n[j].update(predicate=other),
              "tên phủ định": lambda n, l: [r.update(predicate="not_" + r["predicate"]) for r in n if r["predicate"] == named[i]["predicate"]],
              "sổ thiếu một tên": lambda n, l: l.pop(),
              "hàng đổi chữ": lambda n, l: n[i].update(span=n[i]["span"] + " x"),
              "anchors sai": lambda n, l: l[0].update(kind="concept" if l[0]["kind"] == "input" else "input")}
    for why, f in broken.items():
        n2, ledger2 = [dict(r) for r in named], [dict(e) for e in ledger]
        f(n2, ledger2)
        assert checks.names_problems(rows, units, n2, ledger2), f"checks không bắt: {why}"


if __name__ == "__main__":
    _harness.run(globals())
