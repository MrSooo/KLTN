"""Bước 1.6B bản làm lại (`names-2`, A39): đặt TÊN VỊ TỪ cho mệnh đề của 1.6A (`propositions.py`) và dựng sổ vị từ 𝒫.

Khác `concepts_names.py` (`names-1`, đọc "cụm" của 1.6A cũ): chữ đầu vào là `menh_de` của các dòng `loai = menh_de`; tham số của vị từ lấy
từ chủ thể và `doi_so` của dòng, giữ THỨ TỰ (chủ thể là tham số, không nằm trong tên: A38 nguyên tắc 3). Phương thức (`phai`, `duoc`, `cam`...)
và cực không nằm trong tên vị từ: 1.6A đã bỏ chúng khỏi `menh_de`, chúng đi theo dòng sang quy tắc ở 1.8.

Phần dùng lại nguyên từ `concepts_names.py` (thuần, không phụ thuộc lời nhắc): hàng xóm (`Neighbors`), chia lượt (`make_rounds`), cạnh nối
(`collect_edges`, `link_map`), cổng hình và dạng tên (`validate_output`, `NAME_RE`, các lý do lỗi), khuôn lời gửi (`user_message`, `round_items`).
Phần viết riêng vì tham số của A39 khác `names-1`:
  - gộp cấp 1 (máy ép cùng tên, không hỏi LLM): cùng `menh_de` chuẩn hoá VÀ cùng chữ ký tham số; cùng chữ khác chữ ký là hai chữ, LLM quyết;
  - lọc ứng viên LỎNG: cùng SỐ tham số, từng vị trí cùng loại hoặc một bên là `?` (`compatible`); cổng `reuse` dùng đúng hàm này;
  - CANDIDATE_CAP 20; lời nhắc `names-2` ("cùng sự kiện pháp lý, khác cách viết thì reuse").

Chạy ở gốc repo (kho con thì đặt KLTN_TAP_CON, A41):
  python -X utf8 -I src/predicates.py [--llm off|replay]       đầu ra bước (đọc 1.6A từ data/llm_cache/propositions/)
  python -X utf8 -I src/predicates.py --xuat <thư mục ngoài repo>   dựng thư mục làm việc cho phiên Claude Code
  python -X utf8 -I src/predicates.py --nhap <thư mục> [--de]       kiểm các lượt rồi ghi bản ghi cache
KHÔNG có live: phần LLM chạy bằng phiên Claude Code (A36), như `names-1`.
"""
import argparse
import collections
import datetime
import gzip
import json
import math
import operator
import os
import unicodedata
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import concepts as cc  # noqa: E402
import concepts_names as cn  # noqa: E402
import corpus  # noqa: E402
import llm_client  # noqa: E402
import parse  # noqa: E402
import propositions as P  # noqa: E402
from textutil import text_norm  # noqa: E402

TASK, ROLE = "predicates", "ten"
# Phiên bản lời nhắc theo lần chạy (như `menh_de.prompt_version`, A47): khoá `ten.prompt_version`, mặc định names-2.1 để replay của các lần chạy cũ giữ nguyên.
#   names-2.1: thêm chữ chủ thể (vai chu_the) và đoạn lời nhắc cho nó (A41).
#   names-2.2 (A61, lần chạy `tach`): ứng viên lọc theo chữ ký DÃY CON (`compatible`), bỏ chữ nối "coi là" ở đầu mệnh đề (`strip_copula`), lời nhắc nói rõ
#     số tham số khác nhau không làm hai chữ thành hai sự kiện. Lý do: 1.8 dịch mọi vị từ thành một ngôi trên chủ thể (đối số khác bỏ qua), nên đòi cùng SỐ
#     tham số không giúp gì cho 1.8 mà chặn cùng sự kiện viết có/không có chủ thể (31/48 nhóm cùng mặt chữ khác tên ở `tach` names-2.1).
PROMPT_VERSION = llm_client.load_config().get("ten.prompt_version", "names-2.1")
LOOSE = PROMPT_VERSION != "names-2.1"
if PROMPT_VERSION not in ("names-2.1", "names-2.2", "names-2.3"):
    raise SystemExit(f"ten.prompt_version = {PROMPT_VERSION!r}, chỉ nhận names-2.1, names-2.2, names-2.3")
# [A63] names-2.3 = names-2.2 cộng ứng viên theo NGHĨA: chữ đã có tên gần nhất theo embedding (ckey `text-embedding-3-small`, 256 chiều)
# đứng đầu danh sách ứng viên, trước hàng xóm theo Điều/dẫn chiếu/chữ chung. Vì sao: hàng xóm cũ xếp chữ cùng Điều trước, nên chữ cùng nghĩa ở
# Điều khác ("sa thải" / "bị xử lý kỷ luật sa thải") thường không lọt 20 ứng viên, LLM đặt tên mới. Embedding chỉ gợi ý; LLM quyết reuse,
# cổng như cũ. Lời nhắc không đổi chữ (đổi phiên bản vì danh sách ứng viên đổi).
SEMANTIC = PROMPT_VERSION == "names-2.3"
# [A63, advisor 27/11] số chữ mới tối đa mỗi lượt, theo lần chạy (khoá `ten.luot_chu_toi_da`; mặc định giữ cn.ROUND_SIZE nên kế hoạch lượt và
# cache của các lần chạy khác không đổi). Vì sao: trên tuyến dịch của tach2, lượt 30 chữ ra tới khoảng 20 nghìn token, quá mốc cổng ckey cắt
# khoảng 9 phút (504); tổng token ra theo tổng số chữ nên lượt nhỏ hơn không làm tổng thời gian dài hơn. Đọc ở `prepare`, dùng chung cho
# --xuat, tiep.py và replay, để kế hoạch lượt lúc nhập khớp lúc dựng.
LUOT_CHU = int(llm_client.load_config().get("ten.luot_chu_toi_da", cn.ROUND_SIZE))
EMBED_MODEL, EMBED_DIM = "text-embedding-3-small", 256
EMBED_PATH = corpus.ROOT / "data" / "llm_cache" / "embeddings" / f"{EMBED_MODEL}-{EMBED_DIM}.json.gz"
SEM_TOP = 30  # láng giềng nghĩa giữ cho mỗi chữ (mọi chữ, lọc "đã có tên" lúc dựng lượt)
SEM_CAP = 10  # tối đa ngần này TÊN đến từ láng giềng nghĩa, phần còn lại của CANDIDATE_CAP là hàng xóm cũ
EFFORT = P.sandbox_model()[1]  # A39: effort high, tuần tự; khoá hop_cat.effort (A46). Model của 1.6B là ten.model (nằm trong khoá cache)
SUBAGENT_MODEL = P.ALIAS.get(llm_client.load_config()[f"{ROLE}.model"], llm_client.load_config()[f"{ROLE}.model"])
CANDIDATE_CAP = 20                          # A39: 12 lên 20 (phỏng đoán: mệnh đề ngắn hơn cụm nên 12 dễ cắt mất ứng viên đúng; chưa đo)
DIR_NAME = "predicates"
SUBJECT_LIST_KIND = "?"  # chủ thể chung ("E" và "W" cùng một chủ ngữ) là MỘT vị trí tham số mà loại không duy nhất: ghi `?` (khớp mọi loại)


# ---- đầu vào: dòng mệnh đề của 1.6A ----

def signature(row):
    """Chữ ký tham số của một dòng mệnh đề: (loại chủ thể nếu có, loại từng doi_so theo thứ tự). Ví dụ ("E", "W")."""
    ct = row.get("chu_the")
    subj = []
    if ct:
        k = ct.get("loai")
        subj = [k if isinstance(k, str) else SUBJECT_LIST_KIND]
    return tuple(subj + [d.get("loai", "?") for d in row.get("doi_so") or []])


def compatible(a, b):
    """Hai chữ ký có dùng chung một vị từ được không. names-2.1 (A39, lọc lỏng): cùng số tham số, từng vị trí cùng loại hoặc một bên là `?`.
    names-2.2 (A61): chữ ký ngắn hơn là DÃY CON của chữ ký dài hơn (giữ thứ tự, mỗi vị trí ghép được cùng loại hoặc `?`): chữ không nêu chủ thể hay
    một đối số vẫn là cùng sự kiện. Cùng độ dài thì như names-2.1, nên ("E",) và ("W",) vẫn là hai việc khác nhau."""
    if len(a) == len(b) or not LOOSE:
        return len(a) == len(b) and all(x == y or "?" in (x, y) for x, y in zip(a, b))
    short, long_ = (a, b) if len(a) < len(b) else (b, a)
    fit = lambda x, y: x == y or "?" in (x, y)  # noqa: E731
    ok = [True] * (len(long_) + 1)  # ok[j]: short[:i] ghép được vào long_[:j]; quy hoạch động theo i
    for i in range(1, len(short) + 1):
        new = [False] * (len(long_) + 1)
        for j in range(1, len(long_) + 1):
            new[j] = new[j - 1] or (ok[j - 1] and fit(short[i - 1], long_[j - 1]))
        ok = new
    return ok[-1]


COPULA = ("được coi là ", "coi là ")


def strip_copula(span):
    """[names-2.2, A61] Bỏ "coi là"/"được coi là" ở đầu mệnh đề: D42.K1 "coi là thay đổi cơ cấu, công nghệ" (đầu định nghĩa) và D42.K3, D48
    "thay đổi cơ cấu, công nghệ" là cùng một khái niệm; giữ chữ nối thì thành hai vị từ và định nghĩa không nối được với chỗ dùng."""
    if not LOOSE:
        return span
    low = span.lower()
    for c in COPULA:
        if low.startswith(c) and len(span) > len(c):
            return span[len(c):]
    return span


def bad_rows(dong, loi):
    """[A63, user chốt 26/11: "dòng điều kiện lỗi thì bỏ cả quy tắc"] Chỉ số các dòng 1.6A KHÔNG dùng. Trước đây chỉ bỏ đúng dòng lỗi, nên
    quy tắc của nhóm vẫn dựng với ít điều kiện hơn văn bản (nới quy tắc). Nay: dòng lỗi thuộc quy_tac nào thì bỏ mọi dòng của quy_tac đó;
    dòng lỗi không có quy_tac, hay lỗi cấp đơn vị (chỉ số None, ví dụ thiếu ngoại lệ), thì bỏ cả đơn vị. Thà không trả lời còn hơn sai."""
    bad = {i for i, _ in loi}
    if None in bad:
        return set(range(len(dong)))
    qs = {dong[i].get("quy_tac") for i in bad if isinstance(i, int) and i < len(dong)}
    if None in qs:
        return set(range(len(dong)))
    return bad | {i for i, d in enumerate(dong) if d.get("quy_tac") in qs}


def load_rows(ctxs):
    """Dòng của 1.6A, theo thứ tự đơn vị của ngữ cảnh 1.6A. -> (rows, số dòng bỏ vì lỗi cổng 1.6A).
    Mỗi dòng: unit, loai, span (menh_de hoặc trích của con_tro), params (chữ ký), role (vai), targets (chỉ con_tro), mode (phuong_thuc), cuc, quy_tac,
    nhom_hoac, gan_vao, row (chỉ số dòng trong đơn vị). Dòng có lỗi cổng 1.6A không vào bước này (không có nghĩa tin được); bo_qua, chua_ro bỏ."""
    path = P.full_cache_path()
    if not path.exists():
        raise SystemExit(f"chưa có {path}; chạy và nhập 1.6A trước (propositions.py xuat/nhap --tat-ca)")
    data = json.loads(path.read_text(encoding="utf-8"))
    units = data["units"]
    missing = [u for u in ctxs if u not in units]
    if missing:
        raise SystemExit(f"1.6A chưa đủ: thiếu {len(missing)} đơn vị (ví dụ {missing[:3]}); nhập đủ rồi chạy lại")
    rows, dropped = [], 0
    for uid in ctxs:
        dong = units[uid]["dong"]
        bad = {i for i, _ in units[uid]["loi"]}  # chỉ dòng lỗi không được đặt tên; bỏ cả quy tắc làm ở 1.8 (bad_rows, A63) để cache 1.6B không đổi
        for i, d in enumerate(dong):
            if i in bad:
                dropped += 1
                continue
            if d["loai"] not in ("menh_de", "con_tro"):
                continue
            subj = subject_text(d) if d["loai"] == "menh_de" else None
            if subj:
                # [THÊM, A41] chữ chủ thể thành chữ cần đặt tên (như vai chu_the của names-1): không có nó, quy tắc 1.8 không phân biệt được
                # "người lao động nước ngoài" với mọi người lao động. Tham số rỗng: vị từ chủ thể là tính chất của chính thực thể.
                rows.append({"unit": uid, "row": i, "loai": "chu_the", "span": subj, "params": (), "role": "chu_the", "targets": [], "mode": "", "cuc": "",
                             "quy_tac": None, "nhom_hoac": None, "gan_vao": None, "liet_ke": [], "predicate": None, "flags": []})
            rows.append({"unit": uid, "row": i, "loai": d["loai"], "subject_key": word_key(subj, ()) if subj else None, "span": strip_copula(d["menh_de"]) if d["loai"] == "menh_de" else " ".join(d["trich"]),
                         "params": signature(d) if d["loai"] == "menh_de" else (), "role": d["vai"],
                         "targets": (d.get("targets") or []) if d["loai"] == "con_tro" else [], "mode": d.get("phuong_thuc", ""), "cuc": P.effective_cuc(d),
                         "quy_tac": d.get("quy_tac"), "nhom_hoac": d.get("nhom_hoac"), "gan_vao": d.get("gan_vao"), "liet_ke": d.get("liet_ke") or [],
                         "predicate": None, "flags": []})
    return rows, dropped


def subject_text(row):
    """Chữ chủ thể của dòng mệnh đề (chu_the.chu), bỏ khoảng trắng thừa; None nếu không có."""
    ct = row.get("chu_the")
    s = " ".join((ct.get("chu") or "").split()) if isinstance(ct, dict) else ""
    return s or None


def word_key(span, params):
    """Khoá gộp cấp 1 (A39): chữ chuẩn hoá và chữ ký tham số. Cùng chữ khác chữ ký là hai chữ khác nhau (LLM quyết có dùng chung tên không)."""
    return text_norm(span) + "|" + "".join(params)


def build_words(rows, order):
    """Chữ = khoá gộp của các dòng mệnh đề (không có targets). Hỏi MỘT lần, ở lần gặp đầu. Trường như `concepts_names.build_words` để dùng lại
    `Neighbors`, `make_rounds`, `round_items`; params là chữ ký có thứ tự (không phải tập)."""
    words, by_key, last = [], {}, -1
    for r in rows:
        if order[r["unit"]] < last:
            raise SystemExit(f"dòng 1.6A không theo thứ tự đơn vị ở {r['unit']}")
        last = order[r["unit"]]
        if r["loai"] not in ("menh_de", "chu_the") or not r["span"]:  # con_tro (kể cả con_tro không giải được đích) không phải chữ để đặt tên
            continue
        key = word_key(r["span"], r["params"])
        w = by_key.get(key)
        if w is None:
            w = by_key[key] = {"idx": len(words), "key": key, "surface": r["span"], "unit": r["unit"], "dieu": cc.dieu_of(r["unit"]), "params": r["params"],
                               "n": 0, "units": set(), "dieus": set(), "roles": set(), "how": {"llm"}, "occ": [], "param_variants": 1}
            words.append(w)
        w["n"] += 1
        w["units"].add(r["unit"])
        w["dieus"].add(cc.dieu_of(r["unit"]))
        w["roles"].add(r["role"])
        if len(w["occ"]) < cn.CONTEXTS_PER_WORD:
            w["occ"].append({"unit": r["unit"], "role": r["role"]})
    for w in words:
        for f in ("units", "dieus", "roles", "how"):
            w[f] = sorted(w[f])
    return words


# ---- sổ tên tạm, ứng viên, trạng thái lượt ----

class Book(cn.Book):
    """Như `names-1` nhưng tên nhận chữ có chữ ký TƯƠNG THÍCH (không cần bằng) với chữ ký của chữ đặt tên (A39)."""

    def add(self, i, name):
        if i in self.name_of:
            raise ValueError(f"chữ {cn.chu_id(i)} đã có tên {self.name_of[i]!r}")
        pk = self.words[i]["params"]
        if not compatible(self.name_params.setdefault(name, pk), pk):
            raise ValueError(f"tên {name!r} có tham số {self.name_params[name]} không tương thích với chữ {cn.chu_id(i)} ({pk})")
        if len(pk) > len(self.name_params[name]):  # [names-2.2, A61] giữ chữ ký DÀI nhất: () đã nhận (E) thì không nhận (W) nữa
            self.name_params[name] = pk
        self.name_of[i] = name
        self.members[name].append(i)


def candidates(words, nb, book, i):
    """Như `concepts_names.candidates`, lọc bằng `compatible` và trần CANDIDATE_CAP. [A63] names-2.3: tối đa SEM_CAP tên từ láng giềng nghĩa
    đứng trước."""
    pool = [j for j, _ in nb.ranked(i) if j in book.name_of][:cn.NEIGHBOR_CAP]
    sem = getattr(nb, "sem", None)
    if sem is not None:
        first, names = [], set()
        for j in sem[i]:
            if j in book.name_of and book.name_of[j] not in names and compatible(book.name_params[book.name_of[j]], words[i]["params"]):
                names.add(book.name_of[j])
                first.append(j)
                if len(names) == SEM_CAP:
                    break
        pool = first + [j for j in pool if j not in first]
    out, seen = [], set()
    for j in pool:
        name = book.name_of[j]
        if name in seen:
            continue
        seen.add(name)
        if compatible(book.name_params[name], words[i]["params"]):
            out.append(name)
            if len(out) == CANDIDATE_CAP:
                break
    return [{"ten": n, "params": list(book.name_params[n]), "vi_du": [words[m]["surface"] for m in sorted(book.members[n])[:cn.EXAMPLES_PER_NAME]]} for n in out]


class Run(cn.Run):
    """Phép gấp thuần như `names-1` (xem `concepts_names.Run`); chỉ đổi sổ, ứng viên và phép so tham số ở cổng."""

    def __init__(self, words, nb, contexts_by_id, rounds):
        super().__init__(words, nb, contexts_by_id, rounds)
        self.book = Book(words)

    def next_round(self):
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
        items = cn.round_items(self.words, self.nb, self.book, indices, self.ctx, notes={i: self.notes[i] for i in self.pending}, cands=cands)
        self.current = {"n": len(self.round_log) + 1, "indices": indices, "items": items, "shown": {i: [c["ten"] for c in cands[i]] for i in indices}}
        return self.current

    def _gate(self, i, entries, shown, new_here):
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
                if not compatible(new_here[ten], params):
                    return "reuse_lech_params", ten
            else:
                return "reuse_ngoai_tap", ten
        elif kieu == "new":
            if not cn.NAME_RE.match(ten):
                return "new_sai_dang", ten
            if ten in cn.NEGATIVE_NAMES or ten.startswith(cn.NEGATIVE_PREFIXES):
                return "new_phu_dinh", ten
            if ten in self.book.name_params:
                return "new_da_co", ten
            new_here[ten] = params
        else:
            return "kieu_la", kieu
        self.book.add(i, ten)
        self.decisions[i] = {"kieu": kieu, "ten": ten, "luot": self.current["n"], "ung_vien": list(shown)}
        return None, ""


def count_without_candidates(words, rounds, nb):
    """Số chữ TỐI THIỂU không có ứng viên lúc dựng lượt (chỉ tính chữ ở lượt trước), như `names-1` nhưng so bằng `compatible`."""
    round_of = {i: k for k, r in enumerate(rounds) for i in r}
    return [i for i, w in enumerate(words)
            if not any(compatible(words[j]["params"], w["params"]) for j in [j for j, _ in nb.ranked(i) if round_of[j] < round_of[i]][:cn.NEIGHBOR_CAP])]


# ---- lời nhắc names-2 ----

PROMPT_EXAMPLE = (("cấp thẻ ra vào khu xưởng", ["E", "W"], "new", "issue_factory_access_card", "tên mới"),
                  ("phát thẻ ra vào khu xưởng", ["E", "W"], "reuse", "issue_factory_access_card",
                   "cùng một sự kiện với chữ 1, chỉ khác chữ; dùng lại tên do chính bạn đặt cho chữ 1 (đứng trước, tham số tương thích)"),
                  ("thu hồi thẻ ra vào khu xưởng", ["E", "W"], "new", "revoke_factory_access_card", "việc ngược lại, không phải cùng sự kiện: tên mới"),
                  ("cấp thẻ ra vào khu xưởng có thời hạn dưới 30 ngày", ["E", "W"], "new", "issue_short_term_factory_access_card", "hẹp hơn chữ 1: tên mới"),
                  ("có thẻ ra vào khu xưởng", ["W"], "new", "holds_factory_access_card", "nêu tình trạng có thẻ, không phải việc cấp thẻ: tên mới"))
_SYSTEM = """Bạn đặt TÊN VỊ TỪ cho các mệnh đề lấy từ văn bản pháp luật lao động Việt Nam. Mỗi mệnh đề là lõi của một điều đúng/sai được (động từ hoặc tính chất cộng tân ngữ chính); chủ thể, chữ chỉ phương thức (phải, được, cấm), chữ phủ định và bổ ngữ đã được bỏ ra và ghi riêng. Hai mệnh đề nêu CÙNG MỘT sự kiện pháp lý phải mang cùng một tên, kể cả khi viết khác chữ; hai mệnh đề nêu sự kiện khác nhau phải mang tên khác.

ĐẦU VÀO là danh sách "chu". Mỗi mục có:
- chu_id: mã của chữ. chu: chữ của mệnh đề, nguyên văn.
- params: loại các tham số theo THỨ TỰ: vị trí đầu là chủ thể (nếu mệnh đề có chủ thể), các vị trí sau là đối số. W người lao động, E người sử dụng lao động, C hợp đồng, J nghề hoặc công việc, G vùng, D ngày hoặc mốc thời gian, A số tiền hoặc số lượng, ? chưa rõ loại. Rỗng nếu mệnh đề không có chủ thể hay đối số.
- vai: các vai mệnh đề từng đóng (ket_luan: hệ quả; dieu_kien: khi nào áp dụng; ngoai_le: trừ khi nào). so_lan: số lần chữ này xuất hiện.
- ngu_canh: tối đa hai nơi chữ xuất hiện đầu tiên, mỗi nơi có tieu_de_dieu, khoan_cha, chu_don_vi và vai của mệnh đề ở đó. Chỉ dùng để hiểu nghĩa của chữ; đừng đặt tên theo cả đoạn.
- ung_vien: các tên đã có, cùng SỐ tham số và loại tương thích (? khớp mọi loại); mỗi ứng viên kèm params và vài chữ đã dùng tên đó (vi_du).
- loi_lan_truoc: chỉ có khi chữ được hỏi lại; là lý do lần trả lời trước không được nhận. Hãy sửa đúng lỗi đó.

CHỮ CÓ VAI chu_the: chữ là cụm danh từ chỉ một NHÓM chủ thể ("Người lao động nước ngoài làm việc tại Việt Nam", "Doanh nghiệp cho thuê lại lao động"). Tên đặt cho tính chất "thuộc nhóm đó" (ví dụ foreign_worker_in_vietnam). Mệnh đề "là <nhóm đó>" và chữ chủ thể chỉ cùng nhóm đó là cùng một sự kiện: phải reuse. Nhóm rộng hơn hoặc hẹp hơn ("người lao động" so với "người lao động nước ngoài") là tên khác.

NHIỆM VỤ: với MỖI chữ trong danh sách, trả về đúng MỘT mục gồm chu_id, kieu và ten.
- kieu "reuse": ten là một tên nằm trong ung_vien của chính chữ đó, HOẶC một tên mà bạn đã đặt (kieu "new") cho một chữ đứng TRƯỚC chữ này trong danh sách (theo thứ tự các mục của "chu"; không được trỏ tới chữ đứng sau) và có params tương thích với chữ này.
- kieu "new": ten là một tên mới.

KHI NÀO ĐƯỢC "reuse": khi chữ nêu CÙNG MỘT sự kiện pháp lý với chữ đã dùng tên đó: cùng hành vi hoặc tình trạng, cùng đối tượng, cùng phạm vi. Khác cách viết, khác thứ tự từ, dùng từ đồng nghĩa, viết tắt hay viết đầy đủ mà vẫn là một sự kiện thì PHẢI reuse. Gần nghĩa, rộng hơn, hẹp hơn hoặc ngược nghĩa thì KHÔNG phải cùng sự kiện: đặt tên mới. Chỉ chung vài từ hoặc cùng chủ đề là chưa đủ. Không chắc thì đặt tên mới.

CÁCH ĐẶT TÊN MỚI:
- Tiếng Anh, snake_case: chỉ gồm chữ thường a-z, chữ số và dấu gạch dưới; bắt đầu bằng chữ cái; dài 3 đến 50 ký tự.
- Tên nêu sự kiện, không nêu ai làm: không ghi chủ thể, không ghi params vào tên (params đã được ghi riêng). Riêng chữ vai chu_the thì tên chính là nhóm chủ thể.
- Không ghi phương thức vào tên (không must_, may_, allowed_, prohibited_): phương thức được ghi riêng.
- Dạng khẳng định: không mở đầu bằng not_, no_, non_ và không đặt tên là not hay non. Chữ có ý phủ định trong nghĩa thì chọn một từ khẳng định có nghĩa tương đương.
- Tên mới không được trùng với bất kỳ tên nào đã có, kể cả tên không nằm trong ung_vien của chữ đó; trùng thì chữ bị hỏi lại sau. Hãy đặt tên đủ cụ thể để ít trùng.

VÍ DỤ (chữ bịa để minh hoạ). Giả sử năm chữ sau đứng theo đúng thứ tự trong danh sách và chưa có ứng viên nào:
{VI_DU}

ĐẦU RA: chỉ JSON đúng lược đồ đã cho, không thêm chữ nào khác. Mọi chữ trong danh sách đều phải có đúng một mục; chu_id chép nguyên văn; không thêm mục cho chữ ngoài danh sách."""
if LOOSE:  # names-2.2 (A61): ứng viên lọc theo dãy con; chữ khác số tham số vẫn có thể là cùng sự kiện
    _SYSTEM = _SYSTEM.replace(
        "- ung_vien: các tên đã có, cùng SỐ tham số và loại tương thích (? khớp mọi loại); mỗi ứng viên kèm params và vài chữ đã dùng tên đó (vi_du).",
        "- ung_vien: các tên đã có mà params tương thích (một bên có thể thiếu chủ thể hay một vài đối số; ? khớp mọi loại); mỗi ứng viên kèm params và vài chữ đã dùng tên đó (vi_du).")
    _SYSTEM = _SYSTEM.replace(
        "Gần nghĩa, rộng hơn, hẹp hơn hoặc ngược nghĩa",
        "Chữ không nêu chủ thể hay đối số mà chữ kia có nêu (params ngắn hơn) KHÔNG vì thế mà là sự kiện khác. Gần nghĩa, rộng hơn, hẹp hơn hoặc ngược nghĩa")
    assert "params tương thích (một bên" in _SYSTEM and "params ngắn hơn" in _SYSTEM
SYSTEM = _SYSTEM.replace("{VI_DU}", "\n".join(f'  {n}. "{chu}" params {json.dumps(p)} -> {kieu} {ten}  ({note})'
                                              for n, (chu, p, kieu, ten, note) in enumerate(PROMPT_EXAMPLE, 1)))
SCHEMA = cn.SCHEMA  # cùng hình đầu ra với names-1: {"chu": [{"chu_id", "kieu", "ten"}]}
user_message = cn.user_message


# ---- cache, replay ----

def store_round(cache_dir, cfg, items, output, **extra):
    """Ghi bản ghi cache của MỘT lượt đúng khoá mà replay (`Client.ask`) tìm. `--nhap` gọi chính hàm này để ghi và đọc không lệch khoá."""
    user, model = user_message(items), cfg[f"{ROLE}.model"]
    key = llm_client.cache_key(model, TASK, PROMPT_VERSION, user, SYSTEM, SCHEMA)
    path = Path(cache_dir) / TASK / f"{key}.json"
    record = {"task": TASK, "prompt_version": PROMPT_VERSION, "role": ROLE, "requested_model": model,
              "created": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "system": SYSTEM, "user": user, "output": output, **extra}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    return path


GOP_CHU = bool(llm_client.load_config().get("ten.gop_chu", 0))  # [A61] máy gộp tên của chữ cùng mặt chữ; chỉ lần chạy bật khoá (tach)
GOP_CHU_KEO_TIENG = 4  # [A62] từ ngần này tiếng mới kéo theo chữ khác mặt chữ đã dùng lại tên bị gộp (merge_same_text)
GOP_CHU_MIN_TIENG = 3  # chữ ngắn hơn có ca mơ hồ: "tổ chức" (danh từ, động từ), "thực hiện", "thành lập" (đo 25/11: 9 nhóm ngắn)


def merge_same_text(run, min_tieng=GOP_CHU_MIN_TIENG):
    """[A61, user chốt 25/11: việc của máy] Sau khi mọi lượt đã áp: các chữ cùng `text_norm` (bỏ qua chữ ký tham số) và >= min_tieng tiếng
    dùng MỘT tên. Lý do: 1.8 dịch mọi vị từ thành một ngôi trên chủ thể X, chủ thể là vị từ canh riêng, nên tên không cần mã hoá W hay E; chữ
    giống hệt mà khác tên (D5 với D6 "thành lập tổ chức nghề nghiệp"; "theo hợp đồng lao động"; LLM đặt lại tên khác giữa hai lần chạy) làm
    mất liên kết. Tên giữ: tên có nhiều lần xuất hiện nhất (tổng `n` của chữ), hoà thì tên của chữ gặp đầu. Không gọi LLM.
    -> [(tên giữ, [tên bị gộp])]."""
    groups = collections.defaultdict(list)
    for i, w in enumerate(run.words):
        if i in run.book.name_of and len(w["surface"].split()) >= min_tieng:
            groups[text_norm(w["surface"])].append(i)
    merged = []
    for idx in groups.values():
        names = {run.book.name_of[i] for i in idx}
        if len(names) < 2:
            continue
        weight = collections.Counter()
        first = {}
        for n in names:
            for m in run.book.members[n]:
                weight[n] += run.words[m]["n"]
                first[n] = min(first.get(n, m), m)
        keep = sorted(names, key=lambda n: (-weight[n], first[n]))[0]
        gone = sorted(names - {keep})
        same = set(idx)
        drag = len(run.words[idx[0]]["surface"].split()) >= GOP_CHU_KEO_TIENG
        for n in gone:
            # A61: chữ khác mặt chữ mà LLM đã dùng lại tên bị gộp cũng chuyển theo (cùng khái niệm). [A62] Chỉ làm thế khi mặt chữ chung đủ
            # dài; chữ ngắn đa nghĩa ("hết thời hạn", 3 tiếng) kéo cả "hợp đồng hết hạn" lẫn "giấy phép lao động hết thời hạn" vào một tên
            # (time_limit_expires), nên chỉ chuyển đúng mặt chữ đó.
            moved = [m for m in run.book.members[n] if drag or m in same]
            rest = [m for m in run.book.members[n] if m not in moved]
            for m in moved:
                run.book.name_of[m] = keep
                run.book.members[keep].append(m)
            if rest:
                run.book.members[n] = rest
            else:
                run.book.members.pop(n)
                run.book.name_params.pop(n, None)
        merged.append((keep, gone))
    return merged


def run_rounds(client, run, merge=True):
    """Chạy tới hết bằng replay. -> None nếu xong, hoặc chuỗi báo dừng (thiếu bản ghi). Xong, bật GOP_CHU và `merge` thì máy gộp tên cùng mặt chữ.
    Sổ vị từ 2.6 (chỉ thêm) gọi với merge=False cho phần KU: gộp ở đó có thể xoá một tên gốc mà quy tắc gốc đang dùng (advisor 25/11)."""
    while True:
        rd = run.next_round()
        if rd is None:
            if GOP_CHU and merge:
                run.merged = merge_same_text(run)
            return None
        ids = {cn.chu_id(i) for i in rd["indices"]}
        try:
            rec = client.ask(TASK, PROMPT_VERSION, SYSTEM, user_message(rd["items"]), SCHEMA, role=ROLE,
                             validate=lambda out, ids=ids: cn.validate_output(out, ids), label=f"lượt {rd['n']}")
        except llm_client.CacheMiss:
            return f"CHƯA ĐỦ: lượt {rd['n']} thiếu bản ghi đã lưu hoặc bản ghi sai hình; các lượt sau chưa chạy"
        run.apply(rec["output"])


# ---- [A63] embedding cho ứng viên theo nghĩa ----

def _embed_key(text):
    return unicodedata.normalize("NFC", text or "").strip().lower()


def load_embeddings():
    if not EMBED_PATH.exists():
        return {}
    with gzip.open(EMBED_PATH, "rt", encoding="utf-8") as f:
        return json.load(f)["vec"]


def fetch_embeddings(texts):
    """Gọi ckey cho các chữ chưa có vector, ghi thêm vào cache (đọc lại là ra y hệt, replay không gọi mạng). -> số chữ đã gọi."""
    import os
    import urllib.request
    vec = load_embeddings()
    need = sorted({_embed_key(t) for t in texts} - set(vec))
    if not need:
        return 0
    key = os.environ.get("CKEY_API_KEY")
    if not key:
        raise SystemExit("chưa có CKEY_API_KEY trong biến môi trường")
    base = llm_client.load_config()["api.base_url"].rstrip("/")
    cost = 0.0
    for k in range(0, len(need), 500):
        body = json.dumps({"model": EMBED_MODEL, "input": need[k:k + 500], "dimensions": EMBED_DIM}).encode("utf-8")
        req = urllib.request.Request(base + "/v1/embeddings", body, {"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                                                    "User-Agent": llm_client.USER_AGENT})
        with urllib.request.urlopen(req, timeout=300) as r:
            d = json.loads(r.read().decode("utf-8"))
        for x in d["data"]:
            vec[need[k + x["index"]]] = [round(v, 5) for v in x["embedding"]]
        cost += ((d.get("usage") or {}).get("x_ckey") or {}).get("cost") or 0
    EMBED_PATH.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(EMBED_PATH, "wt", encoding="utf-8") as f:
        json.dump({"model": EMBED_MODEL, "dimensions": EMBED_DIM, "vec": dict(sorted(vec.items()))}, f, ensure_ascii=False, separators=(",", ":"))
    print(f"embedding: gọi {len(need)} chữ, {cost:.1f} VND; cache {len(vec)} chữ ({EMBED_PATH})")
    return len(need)


SEM_MEMO_DIR = corpus.ROOT / "data" / "processed" / "_memo"  # đã gitignore (đầu ra dựng lại được)


def semantic_neighbors(words):
    """{i: [j]} SEM_TOP chữ gần nhất theo cosine (mọi chữ khác, xếp giảm dần, hoà theo key). Thiếu vector thì dừng: chạy --nhung trước.
    [27/11] Phép tính mất khoảng 32 giây (Python thuần, 2.441 chữ) mà tiep.py gọi hai lần mỗi lượt 1.6B; kết quả chỉ phụ thuộc
    (key, chữ, vector từng chữ, SEM_TOP) nên được lưu ở SEM_MEMO_DIR, khoá bằng sha256 của đúng các đầu vào đó; hụt thì tính như cũ."""
    import hashlib
    vec = load_embeddings()
    missing = [w["surface"] for w in words if _embed_key(w["surface"]) not in vec]
    if missing:
        raise SystemExit(f"names-2.3: {len(missing)} chữ chưa có embedding (ví dụ {missing[:3]}); chạy `predicates.py --nhung` (gọi ckey) trước")
    sig = hashlib.sha256(json.dumps([SEM_TOP, [[w["key"], w["surface"], vec[_embed_key(w["surface"])]] for w in words]],
                                    ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()
    memo = SEM_MEMO_DIR / f"sem_neighbors_{sig[:32]}.json"
    if memo.exists():
        try:
            return {int(i): js for i, js in json.loads(memo.read_text(encoding="utf-8")).items()}
        except (ValueError, OSError):
            pass  # file hỏng (ví dụ ghi dở): tính lại
    out = _semantic_neighbors(words, vec)
    SEM_MEMO_DIR.mkdir(parents=True, exist_ok=True)
    tmp = memo.with_suffix(f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    tmp.replace(memo)  # ghi nguyên tử: tiến trình khác đọc cùng lúc không thấy file dở
    return out


def _semantic_neighbors(words, vec):
    unit = []
    for w in words:
        v = vec[_embed_key(w["surface"])]
        n = math.sqrt(sum(x * x for x in v)) or 1.0
        unit.append([x / n for x in v])
    out = {}
    for i, a in enumerate(unit):
        sims = sorted(((-sum(map(operator.mul, a, b)), words[j]["key"], j) for j, b in enumerate(unit) if j != i))
        out[i] = [j for _s, _k, j in sims[:SEM_TOP]]
    return out


# ---- dựng Run ----

def prepare(doc_id=None):
    """-> (Run mới, rows, số dòng bỏ vì lỗi cổng 1.6A). Ngữ cảnh và thứ tự đơn vị lấy đúng như 1.6A (`propositions.contexts`)."""
    doc_id = doc_id or corpus.BASE_DOC_ID
    ctxs = P.contexts(doc_id)
    rows, dropped = load_rows(ctxs)
    order = {u: k for k, u in enumerate(ctxs)}
    words = build_words(rows, order)
    _doc, _units, _labels, nodes, refs = cc.load_inputs(doc_id)
    edges = cn.collect_edges(refs, cn.load_exception_rows(doc_id), nodes)
    nb = cn.Neighbors(words, cn.link_map(list(ctxs), edges))
    if SEMANTIC:
        nb.sem = semantic_neighbors(words)
    return Run(words, nb, ctxs, cn.make_rounds(words, LUOT_CHU)), rows, dropped


# ---- thư mục làm việc ngoài repo (như names-1, A36) ----

def fold_dir(d, run, model):
    """Gấp các lượt đã làm trong d vào `run`, như `concepts_names.fold_dir` nhưng với lời nhắc names-2. -> (done, status)."""
    d, log, done = Path(d), cn.read_log(d), []
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
        except ValueError as e:
            return done, {"kind": "sai_hinh", "n": n, "msg": str(e)[:200]}
        done.append({"n": n, "items": rd["items"], "output": output, "model": m, "effort": eff, "failures": failures})


def tiep(d, argv, make, model):
    """Lệnh của tiep.py (moi | ghi NNN), như `concepts_names.tiep`."""
    d = Path(d)
    run = make()
    done, st = fold_dir(d, run, model)
    if argv == ["moi"]:
        if st["kind"] == "moi":
            (d / "lo").mkdir(exist_ok=True)
            (d / "lo" / f"{st['n']:03d}.json").write_text(user_message(st["round"]["items"]), encoding="utf-8", newline="\n")
        return cn._line(done, st, run, d)
    if len(argv) == 2 and argv[0] == "ghi" and argv[1].isdigit():
        n = int(argv[1])
        if done and done[-1]["n"] == n:
            f = done[-1]["failures"]
            tail = "" if st["kind"] in ("moi", "cho") else "; " + cn._line(done, st, run, d)
            return f"ĐÃ NHẬN {n:03d}: {len(done[-1]['items']) - len(f)}/{len(done[-1]['items'])} chữ qua, {len(f)} không qua; chạy `tiep.py moi`" + tail
        if st["kind"] in ("lech", "lech_nhac", "lo_thua", "model", "dung_som") or st["n"] == n:
            return cn._line(done, st, run, d)
        return f"DỪNG: lượt đang chờ nhận là {st['n']:03d}, không phải {n:03d}; báo người dùng"
    return "DỪNG: lệnh lạ; chỉ có `tiep.py moi` và `tiep.py ghi NNN`"


def tiep_entry(script, argv, doc_id):
    """Điểm vào của tiep.py. Lỗi in MỘT dòng trung tính, chi tiết vào loi_tiep.txt (chữ của repo không vào ngữ cảnh phiên chính)."""
    import traceback
    sys.stdout.reconfigure(encoding="utf-8")
    d = Path(script).resolve().parent
    try:
        line = tiep(d, argv, lambda: prepare(doc_id)[0], llm_client.load_config()[f"{ROLE}.model"])
    except BaseException as e:  # noqa: BLE001
        (d / "loi_tiep.txt").write_text("".join(traceback.format_exception(e)), encoding="utf-8", newline="\n")
        line = "DỪNG: lỗi khi dựng lượt (chi tiết trong loi_tiep.txt); báo người dùng"
    print(line)


# Cùng vòng lặp với names-1 (HUONG_DAN của concepts_names); chỉ khác tiep.py gọi module này và mang theo tập con (A41):
# phiên trong thư mục làm việc không có biến môi trường KLTN_TAP_CON nên tiep.py tự đặt.
TIEP_PY = """# Chỉ chạy file này, không mở, không sửa:  @PY@ tiep.py moi   |   @PY@ tiep.py ghi NNN
import os, sys
@ENV@sys.path.insert(0, @SRC@)
import predicates
predicates.tiep_entry(__file__, sys.argv[1:], @DOC@)
"""


def xuat(d, doc_id):
    """Dựng thư mục làm việc ngoài repo; từ chối nếu thư mục trong repo, đã có nội dung, hoặc luật dừng 20% chữ không có ứng viên kích hoạt."""
    d, root = Path(d).resolve(), corpus.ROOT.resolve()
    if d == root or root in d.parents:
        raise SystemExit(f"{d} nằm trong repo; thư mục làm việc phải ở NGOÀI repo (A36)")
    if d.exists() and any(d.iterdir()):
        raise SystemExit(f"{d} đã có nội dung, không ghi đè")
    run, _rows, _dropped = prepare(doc_id)
    empty = count_without_candidates(run.words, run.planned, run.nb)
    # Luật 20% chỉ CẢNH BÁO, không chặn (A41, chủ đề tài 18/11: chạy hết pipeline để dựng KB rồi mới quay lại xem ca lỗi).
    # Chữ không có ứng viên chắc chắn thành tên mới, nên tỉ lệ cao báo trước tái dùng thấp và ít cặp cho 1.7; xem số đo sau khi chạy.
    warn = (f"; CẢNH BÁO: quá {int(cn.NO_CANDIDATE_STOP * 100)}% chữ không có ứng viên, tái dùng sẽ thấp"
            if len(empty) > cn.NO_CANDIDATE_STOP * len(run.words) else "")
    model = llm_client.load_config()[f"{ROLE}.model"]
    py = Path(sys.executable).as_posix()  # tuyệt đối (phiên ngoài repo không có venv trên PATH), dấu / để khớp quy tắc quyền Bash(...) của claude -p
    fill = lambda s: s.replace("@PY@", py).replace("@MODEL@", model).replace("@SUB@", SUBAGENT_MODEL).replace("@EFFORT@", EFFORT)  # noqa: E731
    # tiep.py chạy trong thư mục làm việc, không mang biến môi trường của người dựng: ghi cứng kho con và lần chạy LLM (A41, A46)
    env = "".join(f"os.environ[{k!r}] = {v!r}\n" for k, v in (("KLTN_TAP_CON", corpus.SUBSET), ("KLTN_LLM_RUN", corpus.LLM_RUN)) if v)
    (d / "lo").mkdir(parents=True, exist_ok=True)
    (d / "out").mkdir()
    files = {"HUONG_DAN.md": fill(cn.HUONG_DAN), "system.txt": SYSTEM + "\n", "schema.json": json.dumps(SCHEMA, ensure_ascii=False, indent=1) + "\n",
             "tiep.py": fill(TIEP_PY).replace("@ENV@", env).replace("@SRC@", repr(str(Path(__file__).resolve().parent))).replace("@DOC@", repr(doc_id))}
    for name, text in files.items():
        (d / name).write_text(text, encoding="utf-8", newline="\n")
    return f"đã dựng {d}: {len(run.planned)} lượt kế hoạch, {len(run.words)} chữ, model {model} effort {EFFORT}; chữ không có ứng viên (tối thiểu): {len(empty)}/{len(run.words)}{warn}"


def nhap(d, doc_id, cache_dir=llm_client.CACHE_DIR, de=False):
    """Gấp d rồi ghi bản ghi cache cho mọi lượt đã áp. Bản ghi đã có mà đầu ra khác thì DỪNG (trừ khi de). -> (dòng báo, có lỗi không)."""
    cfg = llm_client.load_config()
    model = cfg[f"{ROLE}.model"]
    done, st = fold_dir(d, prepare(doc_id)[0], model)
    wrote, same = [], []
    for r in done:
        key = llm_client.cache_key(model, TASK, PROMPT_VERSION, user_message(r["items"]), SYSTEM, SCHEMA)
        path = Path(cache_dir) / TASK / f"{key}.json"
        if path.exists() and not de:
            if json.loads(path.read_text(encoding="utf-8")).get("output") == r["output"]:
                same.append(r["n"])
                continue
            return [f"DỪNG ở lượt {r['n']:03d}: bản ghi đã có mà đầu ra khác (dùng --de để ghi đè); đã ghi {len(wrote)} lượt"], True
        store_round(cache_dir, cfg, r["items"], r["output"], model=model, request_id=None, usage=None, produced_by="claude_code_sandbox",
                    producer_model_reported=r["model"], effort_reported=r["effort"])
        wrote.append(r["n"])
    bad = st["kind"] in ("lech", "lech_nhac", "lo_thua", "model", "sai_hinh")
    return [f"lượt đã áp: {len(done)}; ghi mới: {len(wrote)}; đã có, cùng đầu ra: {len(same)}",
            f"trạng thái thư mục: {st['kind']} ở lượt {st['n']:03d}" + (f" ({st['msg']})" if st.get("msg") else "") + ("  -> CÓ LỖI" if bad else "")], bad


# ---- sổ vị từ ----

def build_ledger(words, rows, run):
    """-> (dòng đã điền predicate, sổ vị từ 𝒫). Như `concepts_names.build_ledger`: kind `concept` nếu có dòng ket_luan mang tên (đơn vị đó là anchors),
    ngược lại `input` (dữ kiện người hỏi khai); used_in = đơn vị dùng tên ở vai khác ket_luan, cộng đơn vị có con_tro trỏ tới neo (theo cây con).
    Dòng giữ params riêng; cờ `param_conflict` nếu params của dòng khác params của vị từ (tương thích nhưng không bằng)."""
    by_key = {w["key"]: w["idx"] for w in words}
    out = []
    for r in rows:
        r2 = dict(r, params=list(r["params"]), flags=list(r["flags"]))
        if r["loai"] in ("menh_de", "chu_the") and r["span"]:
            i = by_key[word_key(r["span"], r["params"])]
            name = run.book.name_of.get(i)
            if name is not None:
                r2["predicate"] = name
                if run.decisions[i]["kieu"] == "reuse":
                    r2["flags"].append("reuse_llm")
                if tuple(r["params"]) != run.book.name_params[name]:
                    r2["flags"].append("param_conflict")
                r2["flags"] = sorted(set(r2["flags"]))
        out.append(r2)
    anchors, other = collections.defaultdict(set), collections.defaultdict(set)
    for r in out:
        if r["predicate"]:
            (anchors if r["role"] == "ket_luan" else other)[r["predicate"]].add(r["unit"])
    reach = collections.defaultdict(set)
    for name, units in anchors.items():
        for a in units:
            for k in cn.self_and_ancestors(a):
                reach[k].add(name)
    used = collections.defaultdict(set)
    for name, units in other.items():
        used[name] |= units
    for r in out:
        for t in r["targets"]:
            for name in reach.get(t, ()):
                used[name].add(r["unit"])
    ledger = [{"predicate": n, "params": list(run.book.name_params[n]), "kind": "concept" if anchors.get(n) else "input", "anchors": sorted(anchors.get(n, ())),
               "surface": [words[m]["surface"] for m in sorted(run.book.members[n])], "used_in": sorted(used.get(n, ()))} for n in sorted(run.book.name_params)]
    return out, ledger


def metrics(words, ledger, run):
    """Số đo kết nối (A39): tái dùng do LLM (chữ `reuse` / chữ có tên) và tái dùng tổng (chữ có tên trên số tên); vị từ dùng ở từ 2 Điều;
    cặp khác Điều chung vị từ `concept` (số đo bản cũ; KHÔNG phải số cặp 1.7 hỏi LLM: implicit_exceptions.build_pairs lọc thêm)."""
    named = len(run.book.name_of)
    reuse = sum(1 for d in run.decisions.values() if d["kieu"] == "reuse")
    dieus_of = collections.defaultdict(set)
    units_of = collections.defaultdict(set)
    for i, name in run.book.name_of.items():
        dieus_of[name] |= set(words[i]["dieus"])
        units_of[name] |= set(words[i]["units"])
    pairs = set()
    for p in ledger:
        if p["kind"] != "concept":
            continue
        us = sorted(units_of[p["predicate"]])
        pairs |= {(a, b) for x, a in enumerate(us) for b in us[x + 1:] if cc.dieu_of(a) != cc.dieu_of(b)}
    return {"chu": len(words), "chu_co_ten": named, "reuse_llm": reuse, "ten": len(run.book.name_params),
            "vi_tu_o_tu_2_dieu": sum(1 for s in dieus_of.values() if len(s) >= 2), "cap_ung_vien_1_7": len(pairs),
            "concept": sum(1 for p in ledger if p["kind"] == "concept"), "input": sum(1 for p in ledger if p["kind"] == "input")}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--doc", default=corpus.BASE_DOC_ID)
    ap.add_argument("--llm", choices=("off", "replay"), default="off")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--xuat", metavar="THU_MUC")
    g.add_argument("--nhap", metavar="THU_MUC")
    g.add_argument("--nhung", action="store_true", help="[A63] gọi ckey lấy embedding cho mọi chữ của 1.6A (names-2.3), ghi cache")
    ap.add_argument("--de", action="store_true")
    args = ap.parse_args(argv)
    if args.nhung:
        ctxs = P.contexts(args.doc)
        rows, _dropped = load_rows(ctxs)
        words = build_words(rows, {u: k for k, u in enumerate(ctxs)})
        fetch_embeddings([w["surface"] for w in words])
        return
    if args.xuat:
        print(xuat(args.xuat, args.doc))
        return
    if args.nhap:
        lines, bad = nhap(args.nhap, args.doc, de=args.de)
        print("\n".join(lines))
        raise SystemExit(1 if bad else 0)
    if not P.full_cache_path().exists():  # kho chưa chạy 1.6A (kho đầy đủ trước lần chạy cả kho): báo rõ, không coi là lỗi của chuỗi
        print(f"BỎ QUA 1.6B: chưa có kết quả 1.6A {P.full_cache_path()}")
        return
    run, rows, dropped = prepare(args.doc)
    stop = run_rounds(llm_client.Client("replay"), run) if args.llm == "replay" else None
    named, ledger = build_ledger(run.words, rows, run)
    m = metrics(run.words, ledger, run)
    lines = [f"1.6B {PROMPT_VERSION}: {args.doc}" + (f" (kho con {corpus.SUBSET})" if corpus.SUBSET else ""),
             f"dòng 1.6A dùng: {len(rows)} (mệnh đề {sum(1 for r in rows if r['loai'] == 'menh_de')}, con trỏ {sum(1 for r in rows if r['loai'] == 'con_tro')}, chủ thể {sum(1 for r in rows if r['loai'] == 'chu_the')}); bỏ vì lỗi cổng 1.6A: {dropped}",
             f"chữ (gộp cấp 1): {m['chu']}; lượt kế hoạch: {len(run.planned)}",
             "LLM TẮT: không đặt tên" if args.llm == "off" else
             f"chữ có tên: {m['chu_co_ten']}; reuse do LLM chọn: {m['reuse_llm']} ({100 * m['reuse_llm'] / max(m['chu_co_ten'], 1):.1f}%); "
             f"vị từ: {m['ten']} (concept {m['concept']}, input {m['input']}); chữ bị loại: {len(run.rejected)}",
             f"vị từ dùng ở từ 2 Điều: {m['vi_tu_o_tu_2_dieu']}; cặp khác Điều chung vị từ concept (chưa lọc như 1.7): {m['cap_ung_vien_1_7']}"]
    if stop:
        lines.append(stop)
    if getattr(run, "merged", None) is not None:  # [A61] chỉ khi bật ten.gop_chu: báo cáo của lần chạy khác không đổi
        lines.append(f"máy gộp tên cùng mặt chữ (>= {GOP_CHU_MIN_TIENG} tiếng): {len(run.merged)} nhóm, bớt {sum(len(g) for _, g in run.merged)} tên")
        lines += [f"  {k} <- {', '.join(g)}" for k, g in run.merged]
    d = corpus.out_dir(DIR_NAME)
    parse.write_jsonl(d / f"predicates_named_{args.doc}.jsonl", named)
    parse.write_jsonl(d / f"predicates_ledger_{args.doc}.jsonl", ledger)
    parse.write_jsonl(d / f"predicates_rejected_{args.doc}.jsonl",
                      [{"chu_id": cn.chu_id(i), "chu": run.words[i]["surface"], "ly_do": why} for i, why in sorted(run.rejected.items())])
    rp = corpus.report_dir(DIR_NAME) / f"predicates_report_{args.doc}.txt"
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))
    if stop:
        raise SystemExit(1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()
