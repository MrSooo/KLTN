"""Đơn vị tri thức (KU) và mốc ngày của tầng tri thức ở giai đoạn 2 (2.5-2.7, A42). Không phải một bước: thư viện dùng chung của
`affected.py` (2.5) và `update.py` (2.6, 2.7).

KU là một ĐẦU VÀO 1.6A phân biệt: (đơn vị, tiêu đề Điều, câu dẫn của cha, chữ của đơn vị) lấy từ ảnh chụp kho phiên bản (2.3-2.4) tại
một ngày. Vì sao không lấy riêng chữ của đơn vị: 1.6A đọc cả tiêu đề và câu dẫn (A26, A35); sửa câu dẫn của cha thì mục con chữ không đổi
vẫn phải trích lại. Mã KU:
  - `uid` nếu đầu vào trùng ngữ cảnh 1.6A của bản parse (`propositions.contexts`, phiên bản 1): cache 1.6A, 1.6B, 1.7 của BLLĐ giữ nguyên;
  - `uid@h<8 hex>` (sha1 của đầu vào) cho mọi đầu vào khác (phiên bản sửa đổi, đơn vị do văn bản sau chèn như D154.K8a).
Trường `unit` (mã đơn vị trần) và `ku` luôn tách riêng: mọi phép theo cây (`under`, tổ tiên, `link_map`) chỉ dùng `unit`.

Mốc (epoch): mọi ngày có phiên bản ở trạng thái `normal` bắt đầu hoặc hết hiệu lực, và mọi ngày đầu, cuối của cạnh `overrides`
(NQ 66.16: 2027-03-01 là mốc dù không có văn bản nào được nạp ngày đó). Giữa hai mốc liền nhau, ảnh chụp không đổi.

Phạm vi trích (SCOPE_LABELS): như 1.6A (Điều nhãn substantive, definition; Khoản, Điểm có chữ). Đổi phạm vi là đổi một hằng ở đây (A42).
"""
import collections
import datetime
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import concepts  # noqa: E402
import corpus  # noqa: E402
import parse  # noqa: E402
import propositions  # noqa: E402
import textutil  # noqa: E402

SCOPE_LABELS = concepts.IN_SCOPE_LABELS
UNIT_TYPES = concepts.UNIT_TYPES


def _date(s):
    return datetime.date.fromisoformat(s) if s else None


def dieu_of(uid):
    return concepts.dieu_of(uid)


class Store:
    """Kho phiên bản đã ghi (versions.jsonl) và cạnh cập nhật (version_edges.jsonl), chỉ đọc."""

    def __init__(self, rows, edges):
        self.by_uid = collections.OrderedDict()
        for r in rows:
            r = dict(r, effective_from=_date(r["effective_from"]), effective_to=_date(r["effective_to"]))
            self.by_uid.setdefault(r["id"], []).append(r)
        self.order = {u: k for k, u in enumerate(self.by_uid)}
        self.edges = edges
        self.overrides = [dict(e, valid_from=_date(e["valid_from"]), valid_to=_date(e["valid_to"])) for e in edges if e["p"] == "overrides"]

    @classmethod
    def load(cls):
        d = corpus.out_dir("versions")
        return cls(parse.read_jsonl(d / "versions.jsonl"), parse.read_jsonl(d / "version_edges.jsonl"))

    @staticmethod
    def live(v, d):
        return (v["state"] == "normal" and v["effective_from"] is not None and v["effective_from"] <= d
                and (v["effective_to"] is None or d < v["effective_to"]))

    def snapshot(self, d):
        """{uid: phiên bản hiệu lực tại d}, theo thứ tự kho."""
        out = {}
        for uid, vs in self.by_uid.items():
            v = next((x for x in reversed(vs) if self.live(x, d)), None)
            if v is not None:
                out[uid] = v
        return out

    def epochs(self):
        """Các ngày ảnh chụp có thể đổi, tăng dần. Ngày null (pending_event chưa kích hoạt) không là mốc."""
        days = set()
        for vs in self.by_uid.values():
            for v in vs:
                if v["state"] == "normal":
                    days |= {x for x in (v["effective_from"], v["effective_to"]) if x}
        for e in self.overrides:
            days |= {x for x in (e["valid_from"], e["valid_to"]) if x}
        return sorted(days)

    def source_of(self, d):
        """Văn bản gây ra mốc d: phiên bản mở tại d (source_event), phiên bản đóng tại d (closed_by), hoặc cạnh overrides bắt đầu,
        hết hạn tại d. Phiên bản hết hạn theo thời hạn của chính văn bản (NQ 66.16) không có closed_by: lấy văn bản của đơn vị."""
        out = set()
        for vs in self.by_uid.values():
            for v in vs:
                if v["state"] != "normal":
                    continue
                if v["effective_from"] == d:
                    out.add(v["source_event"])
                if v["effective_to"] == d:
                    out.add(v["closed_by"] or v["id"].split(".")[0])
        for e in self.overrides:
            if d in (e["valid_from"], e["valid_to"]):
                out.add(e["source_event"])
        return sorted(out)

    def overrides_at(self, d):
        return [e for e in self.overrides if e["valid_from"] <= d and (e["valid_to"] is None or d < e["valid_to"])]


def load_labels():
    return {r["id"]: r["label"] for r in parse.read_jsonl(corpus.out_dir("article_type") / "article_type_labels.jsonl")}


def contexts_at(snap, labels):
    """{uid: {heading, chapeau, text}} của mọi đơn vị trong phạm vi tại một ảnh chụp: đúng luật của `concepts.unit_contexts` (A26, A35),
    nhưng đọc tiêu đề Điều và chữ cha từ chính ảnh chụp (cha bị sửa thì câu dẫn của con đổi theo)."""
    out = {}
    for uid, v in snap.items():
        if v["type"] not in UNIT_TYPES or not (v["text"] or "").strip() or "out_of_scope" in v["flags"]:
            continue
        dieu = dieu_of(uid)
        if labels.get(dieu) not in SCOPE_LABELS:
            continue
        parent = snap.get(v["parent"]) if v["parent"] else None
        lead_in = parent if parent is not None and (v["type"] == "diem" or (v["type"] == "khoan" and parent["type"] == "dieu")) else None
        out[uid] = {"heading": (snap.get(dieu) or {}).get("heading") or "", "chapeau": (lead_in or {}).get("text") or "", "text": v["text"]}
    return out


def ctx_key(c):
    return json.dumps([c["heading"], c["chapeau"], c["text"]], ensure_ascii=False)


class Catalog:
    """Mọi KU của kho: dựng từ ảnh chụp ở từng mốc. ku_at(d) -> {uid: mã KU} của các đơn vị trong phạm vi tại d."""

    def __init__(self, store, labels):
        self.store, self.labels = store, labels
        self.base = {}     # uid -> ngữ cảnh parse (propositions.contexts, có dan_chieu), theo văn bản
        for doc in sorted({u.split(".")[0] for u in store.by_uid}):
            if not (corpus.out_dir("refs") / f"refs_mentions_{doc}.jsonl").exists():
                continue
            self.base.update(propositions.contexts(doc))
        self.kus = {}      # mã KU -> {ku, unit, doc, ctx (heading, chapeau, text, refs), first}
        self.at = {}       # mốc -> {uid: mã KU}
        for d in store.epochs():
            cur = {}
            for uid, c in contexts_at(store.snapshot(d), labels).items():
                ku = self._ku_id(uid, c)
                if ku not in self.kus:
                    b = self.base.get(uid)
                    refs = b["refs"] if b is not None and b["text"] == c["text"] else []  # chữ mới chưa qua 1.2: không có dẫn chiếu (A42)
                    self.kus[ku] = {"ku": ku, "unit": uid, "doc": uid.split(".")[0], "first": d, "ctx": dict(c, id=uid, refs=refs)}
                cur[uid] = ku
            self.at[d] = cur
        self.epochs = sorted(self.at)

    def _ku_id(self, uid, c):
        b = self.base.get(uid)
        if b is not None and ctx_key(b) == ctx_key(c):
            return uid
        return f"{uid}@h{hashlib.sha1(ctx_key(c).encode('utf-8')).hexdigest()[:8]}"

    def epoch_of(self, d):
        """Mốc lớn nhất <= d (ảnh chụp hiệu lực tại d), hoặc None nếu d trước mọi mốc."""
        best = None
        for e in self.epochs:
            if e <= d:
                best = e
        return best

    def ku_at(self, d):
        e = self.epoch_of(d)
        return dict(self.at[e]) if e else {}

    def changed_at(self, i):
        """KU mở hoặc đóng ở mốc thứ i (so với mốc trước). -> (mở, đóng)."""
        cur = set(self.at[self.epochs[i]].values())
        prev = set(self.at[self.epochs[i - 1]].values()) if i else set()
        return sorted(cur - prev), sorted(prev - cur)


# ---- tri thức theo ảnh chụp: dòng đã đặt tên, loại vị từ, cạnh (dùng chung cho 2.5, 2.6, 2.7) ----

def ku_rows(ku, entry):
    """Dòng 1.6B của một KU, đúng như `predicates.load_rows` (chủ thể thành chữ riêng, bỏ dòng lỗi cổng 1.6A). -> (rows, số dòng bỏ)."""
    import predicates
    rows, dropped = [], 0
    bad = {i for i, _ in entry["loi"]}
    uid = ku["unit"]
    for i, d in enumerate(entry["dong"]):
        if i in bad:
            dropped += 1
            continue
        if d["loai"] not in ("menh_de", "con_tro"):
            continue
        subj = predicates.subject_text(d) if d["loai"] == "menh_de" else None
        if subj:
            rows.append({"unit": uid, "ku": ku["ku"], "row": i, "loai": "chu_the", "span": subj, "params": (), "role": "chu_the", "targets": [], "mode": "", "cuc": "",
                         "quy_tac": None, "nhom_hoac": None, "gan_vao": None, "liet_ke": [], "predicate": None, "flags": []})
        rows.append({"unit": uid, "ku": ku["ku"], "row": i, "loai": d["loai"], "subject_key": predicates.word_key(subj, ()) if subj else None,
                     "span": d["menh_de"] if d["loai"] == "menh_de" else " ".join(d["trich"]),
                     "params": predicates.signature(d) if d["loai"] == "menh_de" else (), "role": d["vai"],
                     "targets": (d.get("targets") or []) if d["loai"] == "con_tro" else [], "mode": d.get("phuong_thuc", ""), "cuc": d.get("cuc", ""),
                     "quy_tac": d.get("quy_tac"), "nhom_hoac": d.get("nhom_hoac"), "gan_vao": d.get("gan_vao"), "liet_ke": d.get("liet_ke") or [],
                     "predicate": None, "flags": []})
    return rows, dropped


def rel(a, b):
    """Hai mã khớp theo cây: bằng nhau hoặc một bên là tổ tiên của bên kia (mã văn bản là tổ tiên của mọi đơn vị của nó)."""
    return a == b or a.startswith(b + ".") or b.startswith(a + ".")


class Knowledge:
    """Mọi đầu vào của tầng tri thức ở giai đoạn 2, đọc một lần: kho phiên bản, KU, 1.6A theo KU, sổ vị từ 2.6, cạnh tĩnh của 1.2, 1.5, 2.2."""

    def __init__(self):
        import predicates
        import propositions as props
        self.store = Store.load()
        self.labels = load_labels()
        self.catalog = Catalog(self.store, self.labels)
        self.cache = props.load_ku_cache()
        p = corpus.out_dir("predicate_registry") / "predicate_registry_names.json"
        reg = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"names": {}, "params": {}, "surface": {}}
        self.names, self.surface = reg["names"], reg["surface"]
        self.word_key = predicates.word_key
        self._rows = {}
        docs = sorted({k["doc"] for k in self.catalog.kus.values()} | {u.split(".")[0] for u in self.store.by_uid})
        self.refs, self.exc15, self.details = [], [], []
        node_units = {}
        for doc in docs:
            rp = corpus.out_dir("refs") / f"refs_mentions_{doc}.jsonl"
            if rp.exists():
                self.refs += [(r["s"], r["o"]) for r in parse.read_jsonl(rp) if r["p"] == "refers_to"]
            np_ = corpus.out_dir("exceptions_general") / f"exceptions_general_conditions_{doc}.jsonl"
            if np_.exists():
                node_units.update({n["id"]: n["units"] for n in parse.read_jsonl(np_)})
            for step, name in (("exceptions_general", "exceptions_general_edges"), ("exceptions_explicit", "exceptions_explicit_edges")):
                ep = corpus.out_dir(step) / f"{name}_{doc}.jsonl"
                if ep.exists():
                    self.exc15 += [(e["s"], e["o"]) for e in parse.read_jsonl(ep)]
        self.node_units = node_units
        lp = corpus.out_dir("links") / "links_edges.jsonl"
        if lp.exists():
            self.details = [(e["s"], e["o"]) for e in parse.read_jsonl(lp) if e["p"] == "details"]

    def rows(self, ku):
        """Dòng đã đặt tên của một KU (predicate theo khoá gộp trong sổ); KU chưa có 1.6A thì []."""
        if ku not in self._rows:
            if ku not in self.cache:
                self._rows[ku] = []
            else:
                rows = ku_rows(self.catalog.kus[ku], self.cache[ku])[0]
                for r in rows:
                    if r["loai"] in ("menh_de", "chu_the") and r["span"]:
                        r["predicate"] = self.names.get(self.word_key(r["span"], tuple(r["params"])))
                self._rows[ku] = rows
        return self._rows[ku]

    def live(self, e):
        """{uid: KU} tại mốc e, chỉ KU đã có 1.6A."""
        return {u: k for u, k in self.catalog.at[e].items() if k in self.cache}

    def kinds(self, live):
        """(loại theo sổ 1.6B, loại đã điều chỉnh cho 1.8) TÍNH TRÊN ẢNH CHỤP: concept khi có dòng ket_luan đang hiệu lực mang tên đó
        (như `predicates.build_ledger`); đã điều chỉnh theo `rules.effective_kinds`. Vị từ chỉ được định nghĩa bởi đơn vị đã hết hiệu lực
        thì trở lại input (A42)."""
        import rules
        named, kinds = [], {}
        for u, k in live.items():
            for r in self.rows(k):
                if r.get("predicate"):
                    named.append(r)
                    kinds.setdefault(r["predicate"], "input")
                    if r["loai"] == "menh_de" and r["role"] == "ket_luan":
                        kinds[r["predicate"]] = "concept"
        return kinds, rules.effective_kinds(named, kinds)

    def uses(self, ku):
        """Tên vị từ một KU dùng (mọi vai, gồm vị từ chủ thể)."""
        return {r["predicate"] for r in self.rows(ku) if r.get("predicate")}

    def exc15_unit_edges(self):
        """Cạnh 1.5 đơn vị → đơn vị (cạnh từ nút điều kiện quy về mọi đơn vị chứa nút), dùng cho 2.5 và cặp 1.7."""
        out = set()
        for s, o in self.exc15:
            for x in self.node_units.get(s, [s]):
                out.add((x, o))
        return out
