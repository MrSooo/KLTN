"""Bước 1.6 giai đoạn B (đặt tên và tái dùng vị từ), PHẦN MÁY (A37): gom chữ, từ nội dung, hàng xóm, chia lượt, ứng viên (phần 1, bước 5 đến 8),
cổng kiểm đầu ra, trạng thái `Run`, sổ vị từ và báo cáo (phần 2, bước 9 và 10). Thiết kế bước 1.6B ở docs/design/steps_1_6_to_1_8.md.

Phần 3a: lời nhắc, lược đồ, lời gửi, bản ghi cache, replay, mẫu đọc tay, file đầu ra. Phần 3b: thư mục làm việc ngoài repo (`--xuat`, `tiep.py`, `--nhap`, HUONG_DAN);
cách vận hành ở docs/operations/llm_sandbox.md. run_all gọi bước này ngay sau 1.6A; checks kiểm lại đầu ra độc lập.
Bảng cụm đã đặt tên ghi ra FILE MỚI, không ghi đè concepts_spans_*.jsonl (`build_words` bỏ qua hàng đã có predicate nên lần chạy sau trên file bị ghi đè sẽ không còn chữ nào).

Chạy: python -I src/concepts_names.py [--doc <doc_id>] [--llm off|replay]
      python -I src/concepts_names.py --xuat <thư mục ngoài repo>      (dựng thư mục làm việc; từ chối nếu 1.6A chưa đủ 204/204 lô)
      python -I src/concepts_names.py --nhap <thư mục> [--de]          (kiểm từng lượt đã làm rồi ghi bản ghi cache; dừng ở lượt lỗi đầu tiên)
  Đọc data/processed/concepts/concepts_spans_<doc>.jsonl (bảng cụm của 1.6A, KHÔNG sửa) và ghi MỚI: concepts_named_<doc>.jsonl (bảng cụm đã điền predicate), concepts_ledger_<doc>.jsonl (sổ vị từ),
  concepts_names_rejected_<doc>.jsonl (chữ bị loại), concepts_names_review_<doc>.jsonl (mẫu đọc tay), và báo cáo docs/run_reports/concepts/concepts_names_report_<doc>.txt.
  off: không đặt tên (predicate toàn null, sổ rỗng). replay: chạy các lượt bằng bản ghi đã lưu ở data/llm_cache/concepts_names/; thiếu bản ghi thì DỪNG ở lượt đó, báo CHƯA ĐỦ, thoát mã 0.
  KHÔNG có live: phần LLM chạy bằng phiên Claude Code (A36, A37). Luật dừng 20% chỉ được IN. Bảng cụm ở chế độ `--llm off` của 1.6A chỉ có cụm từ nút 1.5 nên số đo vô nghĩa; chương trình nói rõ.

Các chỗ mô tả bước im lặng hoặc lệch chữ của mô tả bước (A37 (8)):
  - Cắt 40 hàng xóm trên chữ ĐÃ CÓ TÊN lúc dựng lượt (tức chữ của các lượt trước), không trên mọi chữ (mô tả bước ghi "tính một lần"): xem `candidates`.
    A37 (8)(a) ghi "chữ đứng trước"; cách đọc chặt hơn này vì: chữ cùng lượt chưa có tên, tên `new` của chúng đến CÙNG phản hồi nên thuộc tập cổng cho phép, không thuộc lời gửi.
  - Nhóm 1 (cùng Điều) và nhóm 2 (nối dẫn chiếu hoặc ngoại lệ) khớp theo MỌI nơi chữ ứng viên xuất hiện, không chỉ lần gặp đầu của nó.
  - Cạnh nhóm 2 khớp theo CÂY CON: đích là một Điều thì mọi đơn vị con của Điều đó là hàng xóm (A37 (8), mục mở (i)).
  - Thứ tự "lần gặp đầu": thứ tự đơn vị của `unit_contexts` rồi thứ tự hàng trong đơn vị; file lệch thứ tự đơn vị thì dừng (fail-closed).
  - So `params` như TẬP (`params_key`), một hàm duy nhất dùng cho lọc ứng viên và (phần sau) cổng của `reuse`.
Mọi thứ đi vào lời gửi phải tất định theo byte (khoá cache của phần sau là chữ của lời gửi, mỗi lượt phụ thuộc các lượt trước): không để thứ tự của set lọt vào danh sách.
"""
import argparse
import collections
import datetime
import json
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import concepts as cc
import corpus
import llm_client
import parse
from textutil import text_norm

ROUND_SIZE = 30          # chữ mới tối đa mỗi lượt (cỡ 20 ra 117 lượt, 40 ra 56)
NEIGHBOR_CAP = 40        # hàng xóm giữ lại (chữ đã có tên)
CANDIDATE_CAP = 12       # tên ứng viên tối đa mỗi chữ
EXAMPLES_PER_NAME = 3    # chữ Việt đã dùng tên đó, đưa kèm ứng viên
STOP_SYLLABLES = 30      # âm tiết có mặt ở nhiều chữ nhất, không tính là "từ nội dung"
CONTEXTS_PER_WORD = 2    # số lần gặp đầu gửi kèm LLM làm ngữ cảnh
NO_CANDIDATE_STOP = 0.20  # luật dừng: hơn 20% chữ không có ứng viên thì báo trước khi chạy cả chuỗi lượt


# ---- tham số ----

def params_key(params):
    """Khoá so sánh `params`: TẬP, xếp theo thứ tự W E C J G D A. Lời nhắc 1.6A định nghĩa params là các thực thể cụm nói tới, không quy định thứ tự (WE và EW là một).
    Một hàm cho CẢ lọc ứng viên lẫn cổng `reuse`: hai chỗ so khác nhau thì ứng viên đưa cho LLM bị cổng loại. Chữ cái lạ thì ValueError (cổng 1.6A đã chặn)."""
    return tuple(sorted(set(params), key=cc.PARAMS.index))


# ---- bước 5: gom chữ ----

def build_words(rows, order):
    """Chữ = giá trị `text_norm(span)` của các hàng bảng cụm chưa có tên (predicate null) và không có targets. Mỗi chữ được hỏi MỘT lần, ở nơi nó xuất hiện đầu tiên.
    `order` = {id đơn vị: thứ tự} lấy từ `unit_contexts`. Bảng cụm phải đã theo thứ tự đơn vị (1.6A sắp xếp như vậy); lệch thì dừng chứ không đoán.
    -> list chữ theo thứ tự lần gặp đầu; mỗi chữ: idx, key, surface (dạng chữ ở lần gặp đầu), unit, dieu (nơi gặp đầu), params (khoá params của lần gặp đầu), n (số hàng),
    units, dieus, roles, how, param_variants (số bộ params khác nhau qua các lần gặp), occ (tối đa CONTEXTS_PER_WORD lần gặp đầu: unit, role)."""
    words, by_key, last = [], {}, -1
    for r in rows:
        if r["unit"] not in order:
            raise SystemExit(f"bảng cụm có đơn vị ngoài phạm vi 1.6: {r['unit']}")
        if order[r["unit"]] < last:
            raise SystemExit(f"bảng cụm không theo thứ tự đơn vị ở {r['unit']}: thứ tự 'lần gặp đầu' sẽ sai")
        last = order[r["unit"]]
        if r["targets"] or r.get("predicate") is not None:
            continue
        key = text_norm(r["span"])
        if not key:
            raise SystemExit(f"cụm rỗng sau chuẩn hoá ở {r['unit']}: {r['span']!r}")
        w = by_key.get(key)
        if w is None:
            w = by_key[key] = {"idx": len(words), "key": key, "surface": r["span"], "unit": r["unit"], "dieu": cc.dieu_of(r["unit"]), "params": params_key(r["params"]),
                               "n": 0, "units": set(), "dieus": set(), "roles": set(), "how": set(), "pvars": set(), "occ": []}
            words.append(w)
        w["n"] += 1
        w["units"].add(r["unit"])
        w["dieus"].add(cc.dieu_of(r["unit"]))
        w["roles"].add(r["role"])
        w["how"].add(r["how"])
        w["pvars"].add(params_key(r["params"]))
        if len(w["occ"]) < CONTEXTS_PER_WORD:
            w["occ"].append({"unit": r["unit"], "role": r["role"]})
    for w in words:
        for f in ("units", "dieus", "roles", "how"):
            w[f] = sorted(w[f])
        w["param_variants"] = len(w.pop("pvars"))
    return words


def chu_id(i):
    return f"C{i:04d}"


# ---- bước 6: từ nội dung, hàng xóm ----

def syllables(surface):
    return [w for w, _, _ in cc.tokenize(surface)[0]]


def content_sets(words, top=STOP_SYLLABLES):
    """-> (danh sách âm tiết dừng, [tập từ nội dung của từng chữ]). Âm tiết dừng = `top` âm tiết có mặt ở nhiều CHỮ KHÁC NHAU nhất (hoà thì theo thứ tự chữ cái, để tất định)."""
    per = [syllables(w["surface"]) for w in words]
    df = collections.Counter()
    for s in per:
        df.update(set(s))
    stop = sorted(df, key=lambda s: (-df[s], s))[:top]
    stop_set = set(stop)
    return stop, [frozenset(s) - stop_set for s in per]


def collect_edges(refs, exception_rows, nodes):
    """Cạnh nối đơn vị với đơn vị: refers_to của 1.2 (refs: {đơn vị: [cạnh]}) và exception_of của 1.5. Cạnh 1.5 có s là nút điều kiện thì nối với mọi đơn vị chứa nút đó. -> list (a, b) đã sắp xếp."""
    edges = set()
    for s, lst in refs.items():
        for r in lst:
            edges.add((s, r["o"]))
    node_units = {n["id"]: n["units"] for n in nodes}
    for e in exception_rows:
        for u in node_units.get(e["s"], [e["s"]]):
            edges.add((u, e["o"]))
    return sorted(edges)


def link_map(unit_ids, edges):
    """{đơn vị: [đơn vị nối với nó]}, hai chiều, theo CÂY CON: hai id "khớp" nếu bằng nhau hoặc một id là tiền tố cha của id kia (đích là Điều thì mọi khoản con là hàng xóm)."""
    def rel(a, b):
        return a == b or a.startswith(b + ".") or b.startswith(a + ".")
    link = {u: set() for u in unit_ids}
    for a, b in edges:
        for x, y in ((a, b), (b, a)):
            ux = [u for u in unit_ids if rel(u, x)]
            uy = [u for u in unit_ids if rel(u, y)]
            for u in ux:
                link[u].update(v for v in uy if v != u)
    return {u: sorted(s) for u, s in link.items()}


class Neighbors:
    """Hàng xóm của từng chữ, xếp sẵn (chưa cắt): các chữ khác thuộc ÍT NHẤT MỘT nhóm dưới đây (chữ không thuộc nhóm nào không phải hàng xóm), theo ba nhóm nối tiếp (R1, A37 (8)(b)):
    (1) chữ có mặt trong Điều nơi chữ này gặp đầu; (2) chữ có mặt ở đơn vị nối với đơn vị gặp đầu (refers_to, exception_of); (3) chữ chung ít nhất một từ nội dung.
    Trong mỗi nhóm xếp theo số từ nội dung chung giảm dần rồi theo `key` của chữ ứng viên (key khác nhau từng đôi nên không có hoà). Một chữ chỉ nằm ở nhóm đầu tiên nó thuộc về."""

    def __init__(self, words, links, top=STOP_SYLLABLES):
        self.words, self.links = words, links
        self.stop, self.content = content_sets(words, top)
        self.by_dieu, self.by_unit, self.by_syl = collections.defaultdict(list), collections.defaultdict(list), collections.defaultdict(list)
        for j, w in enumerate(words):
            for d in w["dieus"]:
                self.by_dieu[d].append(j)
            for u in w["units"]:
                self.by_unit[u].append(j)
            for s in sorted(self.content[j]):
                self.by_syl[s].append(j)
        self._memo = {}

    def ranked(self, i):
        """[(j, nhóm)] của chữ i, nhóm 1, 2, 3 nối tiếp."""
        if i not in self._memo:
            w, ci = self.words[i], self.content[i]
            g1 = set(self.by_dieu.get(w["dieu"], ())) - {i}
            g2 = set()
            for x in self.links.get(w["unit"], ()):
                g2.update(self.by_unit.get(x, ()))
            g2 -= g1 | {i}
            g3 = set()
            for s in sorted(ci):
                g3.update(self.by_syl[s])
            g3 -= g1 | g2 | {i}
            key = lambda j: (-len(ci & self.content[j]), self.words[j]["key"])
            self._memo[i] = [(j, 1) for j in sorted(g1, key=key)] + [(j, 2) for j in sorted(g2, key=key)] + [(j, 3) for j in sorted(g3, key=key)]
        return self._memo[i]


# ---- bước 7: chia lượt ----

def make_rounds(words, size=ROUND_SIZE):
    """Duyệt Điều theo thứ tự lần gặp đầu; mỗi lượt tối đa `size` chữ mới; gom nguyên các Điều liền nhau cho tới khi thêm Điều kế sẽ vượt `size`; Điều có hơn `size` chữ mới thì
    cắt thành đoạn liền nhau. -> [[chỉ số chữ]]. Phải phủ đủ chữ theo đúng thứ tự (nếu không, thứ tự 'đứng trước' không còn nghĩa), nên sai thì dừng."""
    by_dieu = collections.OrderedDict()
    for i, w in enumerate(words):
        by_dieu.setdefault(w["dieu"], []).append(i)
    rounds, cur = [], []
    for lst in by_dieu.values():
        for a in range(0, len(lst), size):
            seg = lst[a:a + size]
            if cur and len(cur) + len(seg) > size:
                rounds.append(cur)
                cur = []
            cur = cur + seg
    if cur:
        rounds.append(cur)
    if [i for r in rounds for i in r] != list(range(len(words))):
        raise SystemExit("chia lượt không phủ chữ theo thứ tự lần gặp đầu (các chữ mới của một Điều không liền nhau)")
    return rounds


# ---- sổ tên tạm và ứng viên (bước 8, phần máy) ----

class Book:
    """Chữ nào đã có tên nào. Tên có `params` = params của chữ đã đặt nó (`new`); chữ `reuse` phải cùng params (cùng `params_key`). Phần sau thêm cổng và sổ vị từ."""

    def __init__(self, words):
        self.words = words
        self.name_of, self.members, self.name_params = {}, collections.defaultdict(list), {}

    def add(self, i, name):
        if i in self.name_of:
            raise ValueError(f"chữ {chu_id(i)} đã có tên {self.name_of[i]!r}")
        pk = self.words[i]["params"]
        if self.name_params.setdefault(name, pk) != pk:
            raise ValueError(f"tên {name!r} có params {self.name_params[name]} nhưng chữ {chu_id(i)} có params {pk}")
        self.name_of[i] = name
        self.members[name].append(i)


def candidates(words, nb, book, i):
    """Tên ứng viên cho chữ i lúc dựng lượt: lấy NEIGHBOR_CAP hàng xóm đầu tiên ĐÃ CÓ TÊN, đổi sang tên (bỏ tên trùng, giữ thứ tự), giữ tên cùng params, tối đa CANDIDATE_CAP.
    Mỗi ứng viên kèm params và tối đa EXAMPLES_PER_NAME chữ Việt đã dùng tên đó (chữ có chỉ số nhỏ nhất)."""
    pool = [j for j, _ in nb.ranked(i) if j in book.name_of][:NEIGHBOR_CAP]
    out, seen = [], set()
    for j in pool:
        name = book.name_of[j]
        if name in seen:
            continue
        seen.add(name)
        if book.name_params[name] == words[i]["params"]:
            out.append(name)
            if len(out) == CANDIDATE_CAP:
                break
    return [{"ten": n, "params": list(book.name_params[n]), "vi_du": [words[m]["surface"] for m in sorted(book.members[n])[:EXAMPLES_PER_NAME]]} for n in out]


def round_items(words, nb, book, indices, contexts_by_id, notes=None, cands=None):
    """Phần dữ liệu của MỘT lượt (chưa đóng khung lời nhắc): mỗi chữ kèm ngữ cảnh (CONTEXTS_PER_WORD lần gặp đầu) và ứng viên. Tất định theo byte.
    notes: {chỉ số chữ: lý do lỗi lần trước} cho chữ được thử lại, thành trường `loi_lan_truoc` (ở cuối mục). cands: {chỉ số chữ: ứng viên} đã tính sẵn; `Run` tính MỘT lần
    và dùng lại cho cổng kiểm, để cổng so với đúng danh sách LLM đã thấy (không phải danh sách sau khi tên `new` cùng lượt đã vào sổ)."""
    items = []
    for i in indices:
        w = words[i]
        item = {"chu_id": chu_id(i), "chu": w["surface"], "params": list(w["params"]), "vai": w["roles"], "so_lan": w["n"],
                "ngu_canh": [{"don_vi": o["unit"], "vai": o["role"], "tieu_de_dieu": contexts_by_id[o["unit"]]["heading"], "khoan_cha": contexts_by_id[o["unit"]]["chapeau"],
                              "chu_don_vi": contexts_by_id[o["unit"]]["text"]} for o in w["occ"]],
                "ung_vien": cands[i] if cands is not None else candidates(words, nb, book, i)}
        if notes and i in notes:
            item["loi_lan_truoc"] = notes[i]
        items.append(item)
    return items


# ---- bước 9: cổng kiểm đầu ra ----
# Hình đầu ra của LLM cho một lượt (mô tả bước chỉ nói "mỗi chữ đúng một mục reuse: tên hoặc new: tên"; tên khoá do mã đặt):
#   {"chu": [{"chu_id": "C0007", "kieu": "reuse" | "new", "ten": "contract_term_under_1_month"}]}
# `ten` KHÔNG được chuẩn hoá (không cắt khoảng trắng, không hạ chữ hoa): sai thì chữ đó không qua cổng.

NAME_RE = re.compile(r"^[a-z][a-z0-9_]{2,49}$")
NEGATIVE_PREFIXES = ("not_", "no_", "non_")
NEGATIVE_NAMES = ("not", "non")  # [THÊM]: regex đã chốt cho qua hai tên trần này, mà `not` là từ khoá của s(CASP) (1.8)
KINDS = ("reuse", "new")
# Lý do lỗi đi vào LỜI GỬI của lượt thử lại (trường `loi_lan_truoc`), tức vào khoá cache của mọi lượt sau: chữ ở đây là bảng cố định, sửa một chữ sau khi đã chạy thật
# là làm replay hụt từ lượt đó trở đi. Không đưa repr của Python hay nội dung set vào lý do.
REASONS = {
    "thieu_muc": "không có mục nào cho chữ này trong kết quả",
    "lap_muc": "chữ này có nhiều hơn một mục trong kết quả; mỗi chữ phải có đúng một mục",
    "kieu_la": 'kieu "{val}" không hợp lệ; chỉ nhận reuse hoặc new',
    "reuse_ngoai_tap": 'reuse "{val}": tên này không nằm trong danh sách ứng viên đã đưa và không phải tên new đã được nhận cho chữ đứng trước trong cùng lượt',
    "reuse_lech_params": 'reuse "{val}": tên này do chữ khác đặt trong lượt nhưng params khác chữ này',
    "new_sai_dang": 'new "{val}": tên phải khớp ^[a-z][a-z0-9_]{{2,49}}$ (chữ thường không dấu, số, gạch dưới; 3 đến 50 ký tự)',
    "new_phu_dinh": 'new "{val}": vị từ phải ở dạng khẳng định, không được là not hoặc non và không được mở đầu bằng not_, no_, non_',
    "new_da_co": 'new "{val}": tên này đã có trong sổ',
}


def reason_text(code, val=""):
    return REASONS[code].format(val=val[:60])


def validate_output(output, ids):
    """Kiểm HÌNH của đầu ra (không kiểm nghĩa): sai thì ValueError và cả lượt bị loại (như 1.6A). Chữ thiếu mục, lặp mục hay `kieu` lạ KHÔNG phải lỗi hình: cổng xử lý từng chữ."""
    items = output.get("chu") if isinstance(output, dict) else None
    if not isinstance(items, list):
        raise ValueError("thiếu 'chu'")
    for it in items:
        if not isinstance(it, dict) or not isinstance(it.get("chu_id"), str) or it["chu_id"] not in ids:
            raise ValueError(f"chu_id ngoài lượt: {it.get('chu_id') if isinstance(it, dict) else it!r}")
        if not isinstance(it.get("kieu"), str) or not isinstance(it.get("ten"), str):
            raise ValueError(f"'kieu' hoặc 'ten' sai hình ở {it['chu_id']}")


class Run:
    """Trạng thái của giai đoạn B: một PHÉP GẤP THUẦN theo dãy đầu ra từng lượt. Mọi công cụ về sau (`tiep.py`, `--nhap`, `replay`) dựng lại trạng thái bằng cách gọi
    `next_round` rồi `apply` theo đúng thứ tự trên các file `out/`, nên không được có nguồn nào khác ảnh hưởng: không đọc đồng hồ, không đọc file, không nhận chỉ số chữ từ bên ngoài.
    `next_round()` tự tính lượt kế (chữ thử lại đứng đầu, rồi chữ của lượt kế hoạch kế tiếp); `apply(output)` chạy cổng và cập nhật sổ.
    Quy tắc thử lại (mô tả bước 7): chữ lỗi cổng ở lần hỏi thứ nhất được hỏi lại MỘT lần ở đầu lượt kế kèm lý do; lỗi lần hai thì loại.
    [THÊM] Hết lượt kế hoạch mà còn chữ chờ thử lại thì có thêm một lượt CHỈ gồm các chữ đó (mô tả bước im lặng); lượt thử lại có thể vượt ROUND_SIZE chữ."""

    def __init__(self, words, nb, contexts_by_id, rounds):
        self.words, self.nb, self.ctx, self.planned = words, nb, contexts_by_id, rounds
        self.book = Book(words)
        self.n_planned_used = 0
        self.pending = []                   # chữ chờ thử lại, theo chỉ số tăng dần
        self.asked = collections.Counter()  # số lần mỗi chữ đã được hỏi (tính khi áp kết quả)
        self.notes = {}                     # chỉ số chữ -> lý do lỗi lần gần nhất (chữ đang chờ thử lại)
        self.rejected = {}                  # chữ bị loại (lỗi lần hai) -> lý do
        self.decisions = {}                 # chữ -> {"kieu", "ten", "luot", "ung_vien": [tên đã đưa]}
        self.round_log = []                 # mỗi lượt đã áp: {"n", "asked", "failed"}
        self.fail_log = []                  # (lượt, chỉ số chữ, mã lỗi)
        self.current = None                 # lượt đã dựng, chưa áp

    def next_round(self):
        """-> {"n", "indices", "items", "shown"} hoặc None khi hết việc. `shown` = {chỉ số chữ: [tên ứng viên đã đưa]}, tính MỘT lần từ sổ lúc này, và là danh sách duy nhất cổng so."""
        if self.current is not None:
            raise RuntimeError("lượt trước chưa áp kết quả")
        if self.n_planned_used < len(self.planned):
            indices = list(self.pending) + self.planned[self.n_planned_used]
            self.n_planned_used += 1
        elif self.pending:
            indices = list(self.pending)
        else:
            return None
        cands = {i: candidates(self.words, self.nb, self.book, i) for i in indices}
        items = round_items(self.words, self.nb, self.book, indices, self.ctx, notes={i: self.notes[i] for i in self.pending}, cands=cands)
        self.current = {"n": len(self.round_log) + 1, "indices": indices, "items": items, "shown": {i: [c["ten"] for c in cands[i]] for i in indices}}
        return self.current

    def apply(self, output):
        """Chạy cổng từng chữ theo thứ tự trong lượt, ghi tên được nhận vào sổ. -> [(chu_id, mã lỗi, lý do)] của các chữ không qua. Đầu ra sai hình thì ValueError và trạng thái KHÔNG đổi."""
        cur = self.current
        if cur is None:
            raise RuntimeError("chưa có lượt nào được dựng")
        validate_output(output, {chu_id(i) for i in cur["indices"]})
        by_id = collections.defaultdict(list)
        for it in output["chu"]:
            by_id[it["chu_id"]].append(it)
        new_here = {}  # tên `new` đã nhận trong lượt này -> params (chữ đứng sau được `reuse`, nếu cùng params)
        failures = []
        for i in cur["indices"]:
            self.notes.pop(i, None)  # chữ thử lại mà qua cổng thì hết nợ; chữ lỗi lại sẽ được ghi lý do mới ngay dưới
            code, val = self._gate(i, by_id.get(chu_id(i), []), cur["shown"][i], new_here)
            self.asked[i] += 1
            if code is None:
                continue
            text = reason_text(code, val)
            failures.append((chu_id(i), code, text))
            self.fail_log.append((cur["n"], i, code))
            if self.asked[i] >= 2:
                self.rejected[i] = text
            else:
                self.notes[i] = text
        self.pending = sorted(self.notes)  # chữ chờ thử lại luôn nằm trong lượt vừa áp (lượt kế bắt buộc chứa chúng), nên notes chỉ có chữ lỗi lần đầu ở lượt này
        self.round_log.append({"n": cur["n"], "asked": len(cur["indices"]), "failed": len(failures)})
        self.current = None
        return failures

    def _gate(self, i, entries, shown, new_here):
        """-> (mã lỗi hoặc None, giá trị lỗi). Nếu qua cổng thì đã ghi tên vào sổ."""
        if not entries:
            return "thieu_muc", ""
        if len(entries) > 1:
            return "lap_muc", ""
        kieu, ten = entries[0]["kieu"], entries[0]["ten"]
        params = self.words[i]["params"]
        if kieu == "reuse":
            if ten in shown:
                pass
            elif ten in new_here:
                if new_here[ten] != params:
                    return "reuse_lech_params", ten
            else:
                return "reuse_ngoai_tap", ten
        elif kieu == "new":
            if not NAME_RE.match(ten):
                return "new_sai_dang", ten
            if ten in NEGATIVE_NAMES or ten.startswith(NEGATIVE_PREFIXES):
                return "new_phu_dinh", ten
            if ten in self.book.name_params:
                return "new_da_co", ten
            new_here[ten] = params
        else:
            return "kieu_la", kieu
        self.book.add(i, ten)
        self.decisions[i] = {"kieu": kieu, "ten": ten, "luot": self.current["n"], "ung_vien": list(shown)}
        return None, ""

    def early_stop(self):
        """Chuông báo duy nhất vì không thử từng lượt (A37 (6)): sau 3 lượt đầu, quá 30% LƯỢT HỎI (mỗi lần một chữ được hỏi tính một lần) không qua cổng thì báo. -> chuỗi hoặc None."""
        if len(self.round_log) < 3:
            return None
        asked, failed = sum(r["asked"] for r in self.round_log[:3]), sum(r["failed"] for r in self.round_log[:3])
        if failed > 0.30 * asked:
            return f"DỪNG SỚM: {failed}/{asked} lần hỏi ở 3 lượt đầu không qua cổng (quá 30%); báo người dùng, không chạy tiếp"
        return None


# ---- bước 10: dựng sổ vị từ ----

REJECTED_STOP = 0.02      # ngưỡng của mẫu đọc tay (A37 (6)): chữ bị loại quá 2% thì dừng và báo người dùng
REVIEW_REUSE_CAP = 150    # số quyết định `reuse` đưa người dùng đọc tay


def self_and_ancestors(uid):
    """[uid, cha, ông...] dừng ở cấp Điều (không lấy id văn bản)."""
    keys, cur = [uid], uid
    while cur.count(".") >= 2:
        cur = cur.rsplit(".", 1)[0]
        keys.append(cur)
    return keys


def build_ledger(words, rows, run):
    """-> (hàng bảng cụm đã điền tên, sổ vị từ). TRẢ DICT MỚI, không sửa `rows` hay `words` (fixture dùng chung của test, và file đầu vào của 1.6A phải giữ nguyên).
    Hàng được điền `predicate` là hàng không có targets mà chữ của nó đã có tên; hàng giữ `params` riêng. Cờ: `reuse_llm` nếu chữ do LLM chọn dùng lại tên; `param_conflict` nếu
    params của hàng khác params của vị từ (không loại). Sổ: kind concept nếu có hàng ket_luan mang tên đó (đơn vị đó là anchors), ngược lại input; surface = chữ Việt của mọi chữ dùng
    tên; used_in = đơn vị có hàng mang tên ở vai khác ket_luan, cộng đơn vị có hàng với targets trỏ tới một neo hoặc tới tổ tiên của neo (theo cây con, như hàng xóm nhóm 2)."""
    by_key = {w["key"]: w["idx"] for w in words}
    out = []
    for r in rows:
        r2 = dict(r, flags=list(r["flags"]))
        if not r["targets"] and r.get("predicate") is None:
            i = by_key.get(text_norm(r["span"]))
            if i is None:
                raise SystemExit(f"hàng bảng cụm không thuộc chữ nào: {r['unit']} {r['span']!r}")
            name = run.book.name_of.get(i)
            if name is not None:
                r2["predicate"] = name
                if run.decisions[i]["kieu"] == "reuse":
                    r2["flags"].append("reuse_llm")
                if params_key(r["params"]) != run.book.name_params[name]:
                    r2["flags"].append("param_conflict")
                r2["flags"] = sorted(set(r2["flags"]))
        out.append(r2)
    anchors = collections.defaultdict(set)
    other_role = collections.defaultdict(set)
    for r in out:
        if r["predicate"] is None:
            continue
        (anchors if r["role"] == "ket_luan" else other_role)[r["predicate"]].add(r["unit"])
    reach = collections.defaultdict(set)  # id đơn vị -> vị từ mà đơn vị đó là neo hoặc tổ tiên của neo
    for name, units in anchors.items():
        for a in units:
            for k in self_and_ancestors(a):
                reach[k].add(name)
    used = collections.defaultdict(set)
    for name, units in other_role.items():
        used[name] |= units
    for r in out:
        for t in r["targets"]:
            for name in reach.get(t, ()):
                used[name].add(r["unit"])
    ledger = []
    for name in sorted(run.book.name_params):
        members = sorted(run.book.members[name])
        ledger.append({"predicate": name, "params": list(run.book.name_params[name]), "kind": "concept" if anchors.get(name) else "input",
                       "anchors": sorted(anchors.get(name, ())), "surface": [words[m]["surface"] for m in members], "used_in": sorted(used.get(name, ()))})
    return out, ledger


def review_reuse_sample(run, words, cap=REVIEW_REUSE_CAP):
    """Mẫu đọc tay phần `reuse` (A37 (6)): toàn bộ nếu không quá `cap`, quá thì chọn đều `cap` theo thứ tự chỉ số chữ. Mỗi mục kèm các chữ Việt ĐÃ dùng tên đó (chỉ số nhỏ hơn).
    Phần mẫu quyết định `new` CHƯA làm: mô tả bước viết "ứng viên có tên chung từ nội dung" mà tên là chữ Anh còn từ nội dung là chữ Việt, nên cần quyết cách hiểu."""
    reuse = sorted(i for i, d in run.decisions.items() if d["kieu"] == "reuse")
    pick = reuse if len(reuse) <= cap else [reuse[(k * len(reuse)) // cap] for k in range(cap)]
    return [{"chu_id": chu_id(i), "chu": words[i]["surface"], "ten": run.decisions[i]["ten"], "don_vi": words[i]["unit"],
             "da_dung_boi": [words[m]["surface"] for m in sorted(run.book.members[run.decisions[i]["ten"]]) if m < i][:EXAMPLES_PER_NAME]} for i in pick]


def names_report_lines(doc_id, run, words, rows_named, ledger):
    n = len(words)
    kinds = collections.Counter(d["kieu"] for d in run.decisions.values())
    undone = n - len(run.decisions) - len(run.rejected)
    extra = len(run.round_log) - len(run.planned)
    lines = [f"1.6B đặt tên và tái dùng vị từ, báo cáo: {doc_id}",
             f"chữ: {n}; lượt đã áp: {len(run.round_log)} (kế hoạch {len(run.planned)}" + (f", cộng {extra} lượt thử lại cuối" if extra > 0 else "") + f"); lần hỏi: {sum(run.asked.values())}",
             f"chữ đã có tên: {len(run.decisions)} (reuse {kinds['reuse']}, new {kinds['new']}); bị loại: {len(run.rejected)} ({100 * len(run.rejected) / max(n, 1):.2f}%)"]
    if undone:
        lines.append(f"!!! CHƯA XONG: {undone} chữ chưa có tên và chưa bị loại (còn lượt chưa chạy)")
    if len(run.rejected) > REJECTED_STOP * n:
        lines.append(f"DỪNG: chữ bị loại hơn {int(REJECTED_STOP * 100)}% (A37 (6)): báo người dùng, không tự sửa lời nhắc hay chạy lại")
    stop = run.early_stop()
    if stop:
        lines.append(stop)
    codes = collections.Counter(c for _, _, c in run.fail_log)
    lines.append("lỗi cổng theo mã: " + (", ".join(f"{c} {k}" for c, k in sorted(codes.items())) if codes else "không có"))
    concept = sum(1 for e in ledger if e["kind"] == "concept")
    lines.append(f"vị từ: {len(ledger)} (concept {concept}, input {len(ledger) - concept})")
    multi = [e for e in ledger if len(e["surface"]) >= 2]
    lines.append(f"vị từ có từ hai chữ Việt trở lên (tái dùng): {len(multi)}")
    lines += [f"  {e['predicate']}: " + " | ".join(e["surface"]) for e in multi]
    conflicts = [r for r in rows_named if "param_conflict" in r["flags"]]
    lines.append(f"hàng có params khác params của vị từ (param_conflict): {len(conflicts)}")
    lines += [f"  {r['unit']} {r['span']!r} -> {r['predicate']}" for r in conflicts]
    lines.append(f"chữ bị loại: {len(run.rejected)}")
    lines += [f"  {chu_id(i)} {words[i]['surface']!r}: {why}" for i, why in sorted(run.rejected.items())]
    return lines


# ---- bước 8 (LLM): lời nhắc, lược đồ, lời gửi, bản ghi cache, chạy các lượt ----

TASK, PROMPT_VERSION, ROLE = "concepts_names", "names-1", "ten"
# Ví dụ của lời nhắc: chữ BỊA (đã grep, không có trong kho luật). Test kiểm các tên ví dụ qua đúng cổng của `Run` (đúng dạng, khẳng định, `reuse` chỉ trỏ tên new đứng trước).
# Ví dụ 2 là diễn đạt khác của CÙNG một nghĩa (không phải ca phải phán đoán); ví dụ 5 cố ý cho `new` để minh hoạ luật chặt "gần nghĩa thì tên mới" (gộp nhầm nặng hơn tách sót, A37).
PROMPT_EXAMPLE = (("thẻ ra vào khu xưởng", "new", "factory_access_card"),
                  ("thẻ dùng để ra vào khu xưởng", "reuse", "factory_access_card"),
                  ("không có thẻ ra vào khu xưởng", "new", "lacks_factory_access_card"),
                  ("thẻ ra vào khu xưởng đã hết hạn", "new", "expired_factory_access_card"),
                  ("có thẻ ra vào khu xưởng", "new", "has_factory_access_card"))
_EXAMPLE_NOTES = ("tên mới", "cùng nghĩa với chữ 1, chỉ khác cách diễn đạt; dùng lại tên do chính bạn đặt cho chữ 1 (đứng trước, cùng params)",
                  "trái nghĩa nên là tên mới; ý phủ định diễn đạt bằng từ khẳng định có nghĩa tương đương",
                  "hẹp hơn chữ 1 nên là tên mới", "nêu việc có thẻ chứ không phải bản thân tấm thẻ: gần nghĩa chứ chưa chắc cùng nghĩa nên là tên mới")
_SYSTEM = """Bạn đặt TÊN cho các cụm chữ lấy từ văn bản pháp luật lao động Việt Nam. Mỗi cụm nêu một điều kiện, một thân phận hoặc một hệ quả. Hai cụm cùng NGHĨA phải mang cùng một tên; hai cụm khác nghĩa phải mang tên khác.

ĐẦU VÀO là danh sách "chu". Mỗi mục có:
- chu_id: mã của chữ. chu: chữ của cụm, nguyên văn.
- params: các thực thể mà cụm nói tới (W người lao động, E người sử dụng lao động, C hợp đồng lao động, J nghề hoặc công việc, G vùng, D ngày hoặc mốc thời gian, A số tiền hoặc số lượng). Rỗng nếu cụm không nói tới thực thể nào.
- vai: các vai cụm từng đóng (chu_the: ai bị nói tới; dieu_kien: khi nào áp dụng; ngoai_le: trừ khi nào; ket_luan: hệ quả). so_lan: số lần chữ này xuất hiện.
- ngu_canh: tối đa hai nơi chữ xuất hiện đầu tiên, mỗi nơi có tieu_de_dieu, khoan_cha, chu_don_vi và vai của cụm ở đó. Chỉ dùng để hiểu nghĩa của chữ; đừng đặt tên theo cả đoạn.
- ung_vien: các tên đã có và cùng params với chữ; mỗi ứng viên kèm params và vài chữ đã dùng tên đó (vi_du).
- loi_lan_truoc: chỉ có khi chữ được hỏi lại; là lý do lần trả lời trước không được nhận. Hãy sửa đúng lỗi đó.

NHIỆM VỤ: với MỖI chữ trong danh sách, trả về đúng MỘT mục gồm chu_id, kieu và ten.
- kieu "reuse": ten là một tên nằm trong ung_vien của chính chữ đó, HOẶC một tên mà bạn đã đặt (kieu "new") cho một chữ đứng TRƯỚC chữ này trong danh sách (theo thứ tự các mục của "chu"; không được trỏ tới chữ đứng sau) và có cùng params với chữ này.
- kieu "new": ten là một tên mới.

KHI NÀO ĐƯỢC "reuse": chỉ khi chữ nêu CÙNG MỘT điều kiện, thân phận hoặc hệ quả với chữ đã dùng tên đó, kể cả khi diễn đạt khác. Gần nghĩa, rộng hơn, hẹp hơn hoặc trái nghĩa đều KHÔNG phải cùng nghĩa: phải đặt tên mới. Chỉ chung vài từ hoặc cùng chủ đề là chưa đủ. Không chắc thì đặt tên mới.

CÁCH ĐẶT TÊN MỚI:
- Tiếng Anh, snake_case: chỉ gồm chữ thường a-z, chữ số và dấu gạch dưới; bắt đầu bằng chữ cái; dài 3 đến 50 ký tự.
- Dạng khẳng định: không mở đầu bằng not_, no_, non_ và không đặt tên là not hay non. Chữ có ý phủ định thì chọn một từ khẳng định có nghĩa tương đương.
- Không ghi params vào tên (params đã được ghi riêng).
- Tên mới không được trùng với bất kỳ tên nào đã có, kể cả tên không nằm trong ung_vien của chữ đó; trùng thì chữ bị hỏi lại sau. Hãy đặt tên đủ cụ thể để ít trùng.

VÍ DỤ (chữ bịa để minh hoạ). Giả sử năm chữ sau đứng theo đúng thứ tự trong danh sách, cùng params và chưa có ứng viên nào:
{VI_DU}

ĐẦU RA: chỉ JSON đúng lược đồ đã cho, không thêm chữ nào khác. Mọi chữ trong danh sách đều phải có đúng một mục; chu_id chép nguyên văn; không thêm mục cho chữ ngoài danh sách."""
SYSTEM = _SYSTEM.replace("{VI_DU}", "\n".join(f'  {n}. "{chu}" -> {kieu} {ten}  ({note})' for n, ((chu, kieu, ten), note) in enumerate(zip(PROMPT_EXAMPLE, _EXAMPLE_NOTES), 1)))
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["chu"],
          "properties": {"chu": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["chu_id", "kieu", "ten"],
                                                            "properties": {"chu_id": {"type": "string"}, "kieu": {"type": "string", "enum": list(KINDS)}, "ten": {"type": "string"}}}}}}


def user_message(items):
    """Lời gửi của một lượt. MỘT nơi tuần tự hoá duy nhất: khoá cache của lượt, `lo/NNN.json` của thư mục làm việc và `--nhap` (phần 3b) đều dùng đúng chuỗi này, nên một byte khác là lệch khoá."""
    return json.dumps({"chu": items}, ensure_ascii=False, indent=0)


def store_round(cache_dir, cfg, items, output, **extra):
    """Ghi bản ghi cache của MỘT lượt đúng khoá mà `Client.ask` (replay) sẽ tìm: model `ten.model`, TASK, PROMPT_VERSION, lời gửi `user_message(items)`, SYSTEM, SCHEMA.
    `--nhap` (phần 3b) phải gọi chính hàm này (thêm produced_by... qua `extra`), để ghi và đọc không thể lệch khoá. -> đường dẫn file."""
    user = user_message(items)
    model = cfg[f"{ROLE}.model"]
    key = llm_client.cache_key(model, TASK, PROMPT_VERSION, user, SYSTEM, SCHEMA)
    path = Path(cache_dir) / TASK / f"{key}.json"
    record = {"task": TASK, "prompt_version": PROMPT_VERSION, "role": ROLE, "requested_model": model,
              "created": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "system": SYSTEM, "user": user, "output": output, **extra}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    return path


def run_rounds(client, run):
    """Chạy `run` tới hết bằng cách hỏi `client` (chế độ replay: chỉ đọc cache). -> None nếu xong, hoặc một chuỗi báo dừng. Thiếu bản ghi và bản ghi sai hình
    (bị `Client` chuyển sang _rejected/ rồi coi như chưa có) đều ra CacheMiss, nên thông báo nói cả hai. Dừng ở lượt k thì `run.current` còn đó và các lượt sau chưa chạy."""
    while True:
        rd = run.next_round()
        if rd is None:
            return None
        ids = {chu_id(i) for i in rd["indices"]}
        try:
            rec = client.ask(TASK, PROMPT_VERSION, SYSTEM, user_message(rd["items"]), SCHEMA, role=ROLE, validate=lambda out, ids=ids: validate_output(out, ids), label=f"lượt {rd['n']}")
        except llm_client.CacheMiss:
            return f"CHƯA ĐỦ: lượt {rd['n']} thiếu bản ghi đã lưu hoặc bản ghi sai hình (đã chuyển sang _rejected/ nếu có); các lượt sau chưa chạy"
        run.apply(rec["output"])


# ---- mẫu đọc tay phần `new`, đầu ra, báo cáo ----

NEAR_TWIN = 0.6        # ngưỡng chung từ nội dung (Jaccard) của "ứng viên gần như song sinh" (A37 (8), (12))
REVIEW_NEW_CAP = 50    # số quyết định `new` đưa người dùng đọc tay


def near_twins(run, words, nb, i):
    """[(tên, chỉ số chữ)] của các 'ứng viên gần như song sinh' cho quyết định của chữ i: thành viên của các tên ĐÃ ĐƯA cho chữ i mà đã được đặt tên ở lượt TRƯỚC lượt này (sau đó mới có thì LLM chưa thấy),
    cùng params (tập), chung từ nội dung từ NEAR_TWIN trở lên (Jaccard). Chữ i phải có từ hai từ nội dung. Cùng thước đo "bạn từ gần" ở A37 (12)."""
    d, ci = run.decisions[i], nb.content[i]
    if len(ci) < 2:
        return []
    found = []
    for name in d["ung_vien"]:
        for m in sorted(run.book.members[name]):
            if run.decisions[m]["luot"] >= d["luot"] or words[m]["params"] != words[i]["params"]:
                continue
            if len(ci & nb.content[m]) / len(ci | nb.content[m]) >= NEAR_TWIN:  # ci có từ hai phần tử nên hợp khác rỗng, không chia cho 0
                found.append((name, m))
    return found


def review_new_sample(run, words, nb, cap=REVIEW_NEW_CAP):
    """Mẫu đọc tay phần `new` (A37 (12), phương án B): chọn đều `cap` trong các quyết định `new` mà chữ có ứng viên gần như song sinh; ít hơn `cap` thì lấy hết.
    Mẫu thiên về chỗ có thể sót gộp, nên KHÔNG ước lượng được tỉ lệ sai chung của mọi quyết định `new`."""
    pool = sorted(i for i, d in run.decisions.items() if d["kieu"] == "new" and near_twins(run, words, nb, i))
    pick = pool if len(pool) <= cap else [pool[(k * len(pool)) // cap] for k in range(cap)]
    return [{"chu_id": chu_id(i), "chu": words[i]["surface"], "ten": run.decisions[i]["ten"], "don_vi": words[i]["unit"],
             "song_sinh": [{"ten": n, "chu": words[m]["surface"]} for n, m in near_twins(run, words, nb, i)[:EXAMPLES_PER_NAME]]} for i in pick]


def result_files(words, rows, run, nb):
    """-> {"named", "ledger", "rejected", "review"}: bốn danh sách dòng sẽ ghi ra file. Run chưa chạy lượt nào (chế độ off) thì predicate toàn null và sổ rỗng."""
    named, ledger = build_ledger(words, rows, run)
    return {"named": named, "ledger": ledger,
            "rejected": [{"chu_id": chu_id(i), "chu": words[i]["surface"], "ly_do": why} for i, why in sorted(run.rejected.items())],
            "review": [dict(r, loai="reuse") for r in review_reuse_sample(run, words)] + [dict(r, loai="new") for r in review_new_sample(run, words, nb)]}


def output_paths(doc_id):
    """File đầu ra MỚI; KHÔNG ghi đè concepts_spans_* (đầu vào của bước này, và `build_words` bỏ qua hàng đã có predicate)."""
    d = corpus.out_dir(cc.DIR_NAME)
    return {"named": d / f"concepts_named_{doc_id}.jsonl", "ledger": d / f"concepts_ledger_{doc_id}.jsonl", "rejected": d / f"concepts_names_rejected_{doc_id}.jsonl",
            "review": d / f"concepts_names_review_{doc_id}.jsonl", "report": corpus.report_dir(cc.DIR_NAME) / f"concepts_names_report_{doc_id}.txt"}


def write_outputs(paths, files, lines):
    for k in ("named", "ledger", "rejected", "review"):
        parse.write_jsonl(paths[k], files[k])
    paths["report"].parent.mkdir(parents=True, exist_ok=True)
    paths["report"].write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


# ---- phần 3b: thư mục làm việc ngoài repo cho phiên Claude Code (mô tả bước 1.6 mục 4b) ----
# Vòng lặp: `tiep.py moi` dựng lo/NNN.json -> subagent ghi out/NNN.json -> phiên ghi nhat_ky.tsv -> `tiep.py ghi NNN` kiểm. `--nhap` ghi bản ghi cache.
# KHÔNG có trang_thai.json (lệch mô tả bước, [THÊM]): mỗi lệnh dựng lại trạng thái từ đầu bằng cách gấp các out/ theo thứ tự (Run là phép gấp thuần, cả chuỗi dưới 2 giây),
# nên không có nguồn sự thật thứ hai để lệch với out/.

EFFORT = "high"           # mức effort của subagent (A37 (7)); không nằm trong khoá cache nên phiên ghi tay vào cột 3 của nhat_ky.tsv
SUBAGENT_MODEL = "sonnet"  # giá trị tham số model của Agent tool; ID đầy đủ phải bằng ten.model


def fresh_run(doc_id):
    """Run mới trên bảng cụm của 1.6A dựng lại TRONG BỘ NHỚ bằng replay (không đọc concepts_spans_*.jsonl: `run_all --llm off` ghi đè file đó bằng bảng chỉ có cụm nút 1.5,
    chạy test giữa chừng là chữ đổi). Từ chối nếu 1.6A chưa đủ bản ghi mọi lô. 1.2, 1.4, 1.5 đọc từ đĩa vì không phụ thuộc LLM."""
    doc, units, labels, nodes, refs = cc.load_inputs(doc_id)
    rows, _rej, _unc, stats, _notes = cc.process_doc(doc.doc_id, units, labels, nodes, refs, llm_client.Client("replay"))
    if stats["batches"] == 0 or stats["batches_ok"] != stats["batches"]:
        raise SystemExit(f"1.6A chưa đủ: {stats['batches_ok']}/{stats['batches']} lô có bản ghi; chưa chạy được 1.6B")
    contexts = cc.unit_contexts(units, labels)
    words, rounds, nb = prepare(rows, contexts, collect_edges(refs, load_exception_rows(doc.doc_id), nodes))
    return Run(words, nb, {c["id"]: c for c in contexts}, rounds)


def read_log(d):
    """nhat_ky.tsv -> {số lượt: (ID model, effort)}. Dòng sau đè dòng trước (lượt làm lại sau khi sai hình). Dòng không bắt đầu bằng số thì bỏ qua."""
    log, p = {}, Path(d) / "nhat_ky.tsv"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            f = [x.strip() for x in line.split("\t")]
            if f and f[0].isdigit():
                log[int(f[0])] = (f[1] if len(f) > 1 else "", f[2] if len(f) > 2 else "")
    return log


def fold_dir(d, run, model):
    """Gấp các lượt đã làm trong thư mục d vào `run` (Run mới). -> (done, status).
    done: [{"n", "items", "output", "model", "effort", "failures"}] các lượt đã áp, theo thứ tự.
    status["kind"]: "moi" (lượt n chưa có lo; status["round"] là lượt đã dựng) · "cho" (có lo, chưa có out) · "thieu_nhat_ky" · "het" (hết việc) ·
    dừng: "lech_nhac" (system.txt hoặc schema.json khác bản của repo) · "lech" (lo/NNN khác lượt dựng lại) · "lo_thua" · "model" (model hoặc effort khai khác) · "sai_hinh" · "dung_som".
    Mỗi lo/NNN.json phải TRÙNG TỪNG BYTE với lời gửi dựng lại: đó là chữ subagent đã đọc, và là chữ đi vào khoá cache lúc `--nhap`."""
    d, log, done = Path(d), read_log(d), []
    # lời nhắc hoặc lược đồ của repo đổi sau khi dựng thư mục: các out/ cũ làm theo chữ cũ, `--nhap` mà ghi chúng dưới khoá của chữ mới là sai âm thầm
    for name, want in (("system.txt", SYSTEM + "\n"), ("schema.json", json.dumps(SCHEMA, ensure_ascii=False, indent=1) + "\n")):
        if not (d / name).exists() or (d / name).read_text(encoding="utf-8") != want:
            return done, {"kind": "lech_nhac", "n": 1, "msg": name}
    while True:
        stop = run.early_stop()
        if stop:
            return done, {"kind": "dung_som", "n": len(done) + 1, "msg": stop}
        rd = run.next_round()
        n = len(done) + 1
        lo, outp = d / "lo" / f"{n:03d}.json", d / "out" / f"{n:03d}.json"
        if rd is None:
            return done, {"kind": "lo_thua" if lo.exists() else "het", "n": n}
        if not lo.exists():
            return done, {"kind": "moi", "n": n, "round": rd}
        if lo.read_text(encoding="utf-8") != user_message(rd["items"]):
            return done, {"kind": "lech", "n": n}
        if not outp.exists():
            return done, {"kind": "cho", "n": n}
        if n not in log:
            return done, {"kind": "thieu_nhat_ky", "n": n}
        m, eff = log[n]
        if m != model or eff != EFFORT:
            return done, {"kind": "model", "n": n, "msg": f"nhat_ky ghi model {m!r} effort {eff!r}, cần {model!r} effort {EFFORT!r}"}
        try:
            output = json.loads(outp.read_text(encoding="utf-8"))
            failures = run.apply(output)
        except ValueError as e:  # JSON hỏng hoặc sai hình: apply đã để trạng thái nguyên (run.current còn đó)
            return done, {"kind": "sai_hinh", "n": n, "msg": str(e)[:200]}
        done.append({"n": n, "items": rd["items"], "output": output, "model": m, "effort": eff, "failures": failures})


def _line(done, st, run, d):
    """Một dòng trung tính cho phiên chính (không nhắc dự án, bước, cache). Sai hình: cất out/NNN.json sang out_sai/ để giao lại; lần hai thì DỪNG."""
    n, k = st["n"], st["kind"]
    if k == "moi":
        return f"LƯỢT {n:03d}: đã ghi lo/{n:03d}.json ({len(st['round']['indices'])} chữ); giao lượt {n:03d} cho một subagent mới"
    if k == "cho":
        return f"CHỜ {n:03d}: đã có lo/{n:03d}.json, chưa có out/{n:03d}.json; giao lượt {n:03d} cho một subagent mới"
    if k == "thieu_nhat_ky":
        return f"THIẾU NHẬT KÝ {n:03d}: ghi dòng trả lời của subagent vào nhat_ky.tsv rồi chạy lại `tiep.py ghi {n:03d}`"
    if k == "het":
        return f"HẾT: {len(done)} lượt đã nhận; {len(run.book.name_of)} chữ có tên, {len(run.rejected)} chữ bị loại; báo người dùng"
    if k == "sai_hinh":
        bad = Path(d) / "out_sai"
        bad.mkdir(exist_ok=True)
        first = bad / f"{n:03d}_lan1.json"
        target = first if not first.exists() else bad / f"{n:03d}_lan2.json"
        (Path(d) / "out" / f"{n:03d}.json").replace(target)
        if target is first:
            return f"SAI HÌNH {n:03d}: {st['msg']}; đã cất sang out_sai/; giao lại lượt {n:03d} cho một subagent MỚI"
        return f"DỪNG: lượt {n:03d} sai hình lần hai ({st['msg']}); báo người dùng"
    if k == "lech":
        return f"DỪNG: lo/{n:03d}.json khác lượt dựng lại (file bị sửa hoặc dữ liệu nguồn đã đổi); báo người dùng"
    if k == "lech_nhac":
        return f"DỪNG: {st['msg']} khác bản đang dùng; báo người dùng"
    if k == "lo_thua":
        return f"DỪNG: có lo/{n:03d}.json mà đã hết việc; báo người dùng"
    if k == "model":
        return f"DỪNG: lượt {n:03d}: {st['msg']}; báo người dùng"
    return st["msg"]  # dung_som: Run.early_stop đã viết sẵn câu DỪNG SỚM


def tiep(d, argv, make, model):
    """Lệnh của tiep.py. argv = ["moi"] hoặc ["ghi", "NNN"]. make() -> Run mới. -> một dòng."""
    d = Path(d)
    run = make()
    done, st = fold_dir(d, run, model)
    if argv[:1] == ["moi"] and len(argv) == 1:
        if st["kind"] == "moi":
            (d / "lo").mkdir(exist_ok=True)
            (d / "lo" / f"{st['n']:03d}.json").write_text(user_message(st["round"]["items"]), encoding="utf-8", newline="\n")
        return _line(done, st, run, d)
    if argv[:1] == ["ghi"] and len(argv) == 2 and argv[1].isdigit():
        n = int(argv[1])
        if done and done[-1]["n"] == n:  # gọi lại ghi cho lượt vừa nhận (kể cả sau khi đã `moi` lượt kế) chỉ báo lại, không đổi gì
            f = done[-1]["failures"]
            tail = "" if st["kind"] in ("moi", "cho") else "; " + _line(done, st, run, d)
            return f"ĐÃ NHẬN {n:03d}: {len(done[-1]['items']) - len(f)}/{len(done[-1]['items'])} chữ qua, {len(f)} không qua; chạy `tiep.py moi`" + tail
        if st["kind"] in ("lech", "lech_nhac", "lo_thua", "model", "dung_som"):  # chuỗi dừng trước lượt NNN: báo đúng lý do, không báo "lượt đang chờ"
            return _line(done, st, run, d)
        if st["n"] == n:  # sai_hinh chỉ xử (cất file) khi đúng lượt được gọi
            return _line(done, st, run, d)
        return f"DỪNG: lượt đang chờ nhận là {st['n']:03d}, không phải {n:03d}; báo người dùng"
    return "DỪNG: lệnh lạ; chỉ có `tiep.py moi` và `tiep.py ghi NNN`"


def tiep_entry(script, argv, doc_id):
    """Điểm vào của tiep.py trong thư mục làm việc. Mọi lỗi in MỘT dòng trung tính, chi tiết ghi vào loi_tiep.txt (để chữ của repo không vào ngữ cảnh phiên chính)."""
    import traceback
    if hasattr(sys.stdout, "reconfigure"):  # Windows: console mặc định không phải UTF-8
        sys.stdout.reconfigure(encoding="utf-8")
    d = Path(script).resolve().parent
    try:
        line = tiep(d, argv, lambda: fresh_run(doc_id), llm_client.load_config()[f"{ROLE}.model"])
    except BaseException as e:  # noqa: BLE001  gồm cả SystemExit (1.6A chưa đủ); KeyboardInterrupt cũng dừng gọn
        (d / "loi_tiep.txt").write_text("".join(traceback.format_exception(e)), encoding="utf-8", newline="\n")
        line = "DỪNG: lỗi khi dựng lượt (chi tiết trong loi_tiep.txt); báo người dùng"
    print(line)


HUONG_DAN = """# Việc của bạn

Thư mục này là toàn bộ thế giới của bạn. Bạn (và mọi subagent bạn tạo) chỉ đọc và ghi trong thư mục này. Không mở thư mục cha hay thư mục nào khác. Không mở, không sửa `tiep.py` và `loi_tiep.txt` (chỉ chạy `tiep.py`). Không tìm hiểu dữ liệu đến từ đâu hay dùng vào việc gì: bạn không cần biết, và biết sẽ làm lệch kết quả.

Việc gồm nhiều LƯỢT nối tiếp. Mỗi lượt là một file `lo/NNN.json`: danh sách cụm chữ cần đặt tên. Lượt sau phụ thuộc kết quả lượt trước, nên `lo/` chỉ có các lượt đã tới và `tiep.py` dựng lượt kế. Không bao giờ làm hai lượt cùng lúc.

## Vòng lặp (bạn là phiên chính; bạn KHÔNG tự làm lượt nào)
1. Chạy `@PY@ tiep.py moi`. Nó in đúng một dòng:
   - `LƯỢT NNN ...` hoặc `CHỜ NNN ...`: sang 2 với số NNN đó.
   - `THIẾU NHẬT KÝ NNN ...`: làm 3 cho lượt NNN rồi sang 4.
   - `HẾT ...`: việc xong; báo người dùng và dừng.
   - `DỪNG ...` hoặc dòng nào khác: dừng ngay, chép nguyên dòng đó cho người dùng, không làm gì thêm.
2. Giao lượt NNN cho MỘT subagent MỚI (Agent tool), đặt tường minh tham số model `@SUB@` và effort `@EFFORT@`. Không tạo được subagent, hoặc không đặt được model hay effort, thì dừng và báo người dùng. Lời giao chỉ gồm đúng thế này (thay NNN):
   > Đọc `system.txt`, `schema.json` và `lo/NNN.json` trong thư mục làm việc. Làm đúng theo `system.txt` cho danh sách trong `lo/NNN.json` và ghi kết quả vào `out/NNN.json` là JSON thuần đúng lược đồ trong `schema.json` (đúng tên trường, không đổi tên, không thêm trường). Không đọc hay ghi file nào khác. Cuối cùng chỉ trả lời đúng một dòng: NNN, một ký tự tab, rồi ID model chính xác của bạn.
3. Thêm vào CUỐI `nhat_ky.tsv` (tạo file nếu chưa có) một dòng: dòng trả lời của subagent, một ký tự tab, rồi `@EFFORT@`. Tức là `NNN<tab>ID model<tab>@EFFORT@`. Ghi đúng ID subagent trả, kể cả khi nó khác `@MODEL@`. Không sửa dòng cũ.
4. Chạy `@PY@ tiep.py ghi NNN`. Nó in đúng một dòng:
   - `ĐÃ NHẬN NNN ...`: quay lại 1 (nếu dòng có thêm `HẾT` hay `DỪNG` thì làm theo phần đó như ở 1).
   - `SAI HÌNH NNN ...`: đầu ra đã được cất sang `out_sai/`; giao lại lượt NNN cho một subagent MỚI như 2, rồi làm 3 và 4.
   - `THIẾU NHẬT KÝ NNN ...`: làm 3 rồi chạy lại 4.
   - `DỪNG ...` hoặc dòng nào khác: dừng ngay, chép nguyên dòng đó cho người dùng.

Chia việc qua nhiều phiên là bình thường: phiên mới đọc file này rồi bắt đầu từ 1; `tiep.py` tự biết đang ở lượt nào.

## Model
Subagent phải là model `@MODEL@` (tham số model `@SUB@`), effort `@EFFORT@`.

## Cấm
- Không viết script, regex hay công cụ nào để sinh hoặc sửa đầu ra. Mọi tên do subagent đọc chữ mà chọn.
- Không sửa `lo/`, `out/`, `out_sai/`, `system.txt`, `schema.json`, `tiep.py` (chỉ subagent ghi `out/NNN.json` của lượt nó được giao).
- Không chạy lại một lượt đã nhận. Không đọc nhiều lượt cùng nhau để so sánh hay làm cho đều.

## Khi dừng
Báo người dùng: số lượt đã nhận, nguyên văn dòng cuối `tiep.py` in, lượt nào lỗi.
"""

TIEP_PY = """# Chỉ chạy file này, không mở, không sửa:  @PY@ tiep.py moi   |   @PY@ tiep.py ghi NNN
import sys
sys.path.insert(0, @SRC@)
import concepts_names
concepts_names.tiep_entry(__file__, sys.argv[1:], @DOC@)
"""


def _py():
    return "python" if sys.platform == "win32" else "python3"


def xuat(d, make, model, doc_id, root=corpus.ROOT):
    """Dựng thư mục làm việc. Từ chối (không ghi gì) nếu: thư mục nằm trong repo; đã có nội dung; luật dừng 20% chữ không có ứng viên kích hoạt; 1.6A chưa đủ (trong make)."""
    d, root = Path(d).resolve(), Path(root).resolve()
    if d == root or root in d.parents:
        raise SystemExit(f"{d} nằm trong repo; thư mục làm việc phải ở NGOÀI repo (A36)")
    if d.exists() and any(d.iterdir()):
        raise SystemExit(f"{d} đã có nội dung, không ghi đè")
    run = make()
    empty = count_without_candidates(run.words, run.planned, run.nb, "round")
    if len(empty) > NO_CANDIDATE_STOP * len(run.words):
        raise SystemExit(f"DỪNG: {len(empty)}/{len(run.words)} chữ không có ứng viên, quá {int(NO_CANDIDATE_STOP * 100)}%; báo người dùng trước khi chạy")
    (d / "lo").mkdir(parents=True, exist_ok=True)
    (d / "out").mkdir()
    fill = lambda s: s.replace("@PY@", _py()).replace("@MODEL@", model).replace("@SUB@", SUBAGENT_MODEL).replace("@EFFORT@", EFFORT)  # noqa: E731
    files = {"HUONG_DAN.md": fill(HUONG_DAN), "system.txt": SYSTEM + "\n", "schema.json": json.dumps(SCHEMA, ensure_ascii=False, indent=1) + "\n",
             "tiep.py": fill(TIEP_PY).replace("@SRC@", repr(str(Path(__file__).resolve().parent))).replace("@DOC@", repr(doc_id))}
    for name, text in files.items():
        (d / name).write_text(text, encoding="utf-8", newline="\n")
    return f"đã dựng {d}: {len(run.planned)} lượt kế hoạch, {len(run.words)} chữ, model yêu cầu {model} effort {EFFORT}; chữ không có ứng viên (tối thiểu): {len(empty)}"


def nhap(d, make, cfg, cache_dir=llm_client.CACHE_DIR, de=False):
    """Gấp thư mục d (cùng `fold_dir` với tiep.py) rồi ghi bản ghi cache cho mọi lượt đã áp bằng `store_round`. Bản ghi đã có: cùng đầu ra thì bỏ qua; khác thì DỪNG (trừ khi de=True),
    vì một lượt mang hai đầu ra làm các lượt sau dựng từ trạng thái khác nhau. -> (dòng báo, có lỗi không)."""
    model = cfg[f"{ROLE}.model"]
    done, st = fold_dir(d, make(), model)
    wrote, same = [], []
    for r in done:
        key = llm_client.cache_key(model, TASK, PROMPT_VERSION, user_message(r["items"]), SYSTEM, SCHEMA)
        path = Path(cache_dir) / TASK / f"{key}.json"
        if path.exists() and not de:
            if json.loads(path.read_text(encoding="utf-8")).get("output") == r["output"]:
                same.append(r["n"])
                continue
            return [f"DỪNG ở lượt {r['n']:03d}: bản ghi đã có mà đầu ra khác (dùng --de để ghi đè); đã ghi {len(wrote)} lượt: {wrote}"], True
        store_round(cache_dir, cfg, r["items"], r["output"], model=model, request_id=None, usage=None, produced_by="claude_code_sandbox",
                    producer_model_reported=r["model"], effort_reported=r["effort"])
        wrote.append(r["n"])
    bad = st["kind"] in ("lech", "lech_nhac", "lo_thua", "model", "sai_hinh")
    lines = [f"lượt đã áp: {len(done)}; ghi mới: {len(wrote)}; đã có, cùng đầu ra: {len(same)}",
             f"trạng thái thư mục: {st['kind']} ở lượt {st['n']:03d}" + (f" ({st['msg']})" if st.get("msg") else "") + ("  -> CÓ LỖI, các lượt từ đây chưa ghi" if bad else "")]
    return lines, bad


# ---- luật dừng ----

def count_without_candidates(words, rounds, nb, basis):
    """Chữ không có ứng viên, số TỐI THIỂU: giả định mọi chữ ở lượt trước đều đã có tên (mỗi chữ một tên riêng; gộp tên không làm chữ nào hết ứng viên). Chữ bị cổng loại ở lần chạy
    thật không có tên, nên số thật có thể CAO hơn số này (ứng viên thật ít hơn).
    basis="round": chỉ tính chữ ở lượt TRƯỚC (đúng lúc dựng lời gửi; số áp luật dừng 20%). basis="order": mọi chữ đứng trước theo thứ tự lần gặp đầu (cận lỏng hơn, là số đo ở A37 (8))."""
    round_of = {i: k for k, r in enumerate(rounds) for i in r}
    empty = []
    for i, w in enumerate(words):
        ok = (lambda j: round_of[j] < round_of[i]) if basis == "round" else (lambda j: j < i)
        pool = [j for j, _ in nb.ranked(i) if ok(j)][:NEIGHBOR_CAP]
        if not any(words[j]["params"] == w["params"] for j in pool):
            empty.append(i)
    return empty


# ---- đọc đầu vào, báo cáo ----

def prepare(rows, contexts, edges):
    """-> (words, rounds, nb)."""
    order = {c["id"]: i for i, c in enumerate(contexts)}
    words = build_words(rows, order)
    return words, make_rounds(words), Neighbors(words, link_map([c["id"] for c in contexts], edges))


def load_exception_rows(doc_id):
    rows = []
    for step, name in (("exceptions_general", "exceptions_general_edges"), ("exceptions_explicit", "exceptions_explicit_edges")):
        p = corpus.out_dir(step) / f"{name}_{doc_id}.jsonl"
        if not p.exists():
            raise SystemExit(f"chưa có {p.name}; chạy src/run_all.py trước")
        rows += parse.read_jsonl(p)
    return rows


def report_lines(doc_id, words, rounds, nb, n_llm_rows):
    sizes = [len(r) for r in rounds]
    lines = [f"1.6B giai đoạn B, số đo trước khi hỏi LLM: {doc_id}",
             f"chữ khác nhau chưa đặt tên: {len(words)}; lượt: {len(rounds)} (chữ mỗi lượt: nhỏ nhất {min(sizes, default=0)}, trung vị {statistics.median(sizes) if sizes else 0}, lớn nhất {max(sizes, default=0)})",
             f"âm tiết dừng ({STOP_SYLLABLES}): " + " ".join(nb.stop),
             f"chữ có params khác nhau giữa các lần gặp: {sum(1 for w in words if w['param_variants'] > 1)} (dùng params của lần gặp đầu)"]
    if n_llm_rows == 0:
        lines.append("BẢNG CỤM KHÔNG CÓ CỤM LLM (chế độ off hoặc chưa replay): số đo ứng viên vô nghĩa, không áp luật dừng. Chạy `python -I src/run_all.py --llm replay` rồi chạy lại.")
        return lines
    n = len(words)
    by_round, by_order = count_without_candidates(words, rounds, nb, "round"), count_without_candidates(words, rounds, nb, "order")
    lines += [f"chữ không có ứng viên, chỉ tính chữ ở lượt trước (số TỐI THIỂU, giả định mọi chữ trước đều có tên; số áp luật dừng): {len(by_round)}/{n} ({100 * len(by_round) / n:.1f}%)",
              f"  so sánh: tính mọi chữ đứng trước theo thứ tự (số đo ở A37 (8)): {len(by_order)}/{n} ({100 * len(by_order) / n:.1f}%)",
              ("DỪNG: hơn " if len(by_round) > NO_CANDIDATE_STOP * n else "luật dừng: không quá ") + f"{int(NO_CANDIDATE_STOP * 100)}% chữ không có ứng viên"
              + (" (báo người dùng trước khi chạy cả chuỗi lượt)" if len(by_round) > NO_CANDIDATE_STOP * n else " (chưa kích hoạt)")]
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--doc", default=corpus.BASE_DOC_ID)
    ap.add_argument("--llm", choices=("off", "replay"), default="off",
                    help="off: không đặt tên (predicate toàn null, sổ rỗng); replay: đọc bản ghi đã lưu. KHÔNG có live: phần LLM của giai đoạn B chạy bằng phiên Claude Code (A36, A37)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--xuat", metavar="THU_MUC", help="dựng thư mục làm việc ngoài repo cho phiên Claude Code (không ghi đầu ra của bước)")
    g.add_argument("--nhap", metavar="THU_MUC", help="kiểm các lượt trong thư mục làm việc rồi ghi bản ghi cache (không ghi đầu ra của bước)")
    ap.add_argument("--de", action="store_true", help="với --nhap: cho ghi đè bản ghi đã có mà đầu ra khác")
    args = ap.parse_args(argv)
    if args.xuat or args.nhap:
        cfg = llm_client.load_config()
        make = lambda: fresh_run(args.doc)  # noqa: E731
        if args.xuat:
            print(xuat(args.xuat, make, cfg[f"{ROLE}.model"], args.doc))
            return
        lines, bad = nhap(args.nhap, make, cfg, de=args.de)
        print("\n".join(lines))
        if bad:
            raise SystemExit(1)
        return
    doc, units, labels, nodes, refs = cc.load_inputs(args.doc)
    spans_path = corpus.out_dir(cc.DIR_NAME) / f"concepts_spans_{doc.doc_id}.jsonl"
    if not spans_path.exists():
        raise SystemExit(f"chưa có {spans_path.name}; chạy src/concepts.py trước")
    rows = parse.read_jsonl(spans_path)
    contexts = cc.unit_contexts(units, labels)
    words, rounds, nb = prepare(rows, contexts, collect_edges(refs, load_exception_rows(doc.doc_id), nodes))
    run = Run(words, nb, {c["id"]: c for c in contexts}, rounds)
    lines = report_lines(doc.doc_id, words, rounds, nb, sum(1 for r in rows if r["how"] == "llm"))
    stop = run_rounds(llm_client.Client("replay"), run) if args.llm == "replay" else None
    files = result_files(words, rows, run, nb)
    if args.llm == "off":
        lines.append("LLM TẮT: giai đoạn B không đặt tên; predicate toàn null, sổ vị từ rỗng")
    else:
        lines += names_report_lines(doc.doc_id, run, words, files["named"], files["ledger"])
        if stop:
            lines.append(stop)
    write_outputs(output_paths(doc.doc_id), files, lines)
    print("\n".join(lines))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()
