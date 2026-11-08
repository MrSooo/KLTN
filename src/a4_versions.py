"""A4 (L6): kho phiên bản của mọi đơn vị theo thời gian, và vòng nạp văn bản theo ngày hiệu lực.

Chạy: python -I src/a4_versions.py [--until YYYY-MM-DD]
  Nạp BLLĐ gốc rồi từng văn bản (dev) theo ngày hiệu lực; mỗi văn bản là một sự kiện: thêm đơn vị của nó, đọc chỉ thị trong chữ
  (l6_directives.py), mở phiên bản mới, đóng phiên bản cũ. KHÔNG xoá nút: đóng phiên bản bằng effective_to. Chạy hai lần ra file giống hệt.
Đầu ra (data/processed/a4/): versions.jsonl, version_edges.jsonl, pending_links.jsonl, events/<doc_id>.json;
  báo cáo docs/bao_cao_chay/a4/a4_report.txt (số liệu, cờ, chỉ thị chưa hiểu, mốc cổng dev).

Hiệu lực là nửa khoảng [effective_from, effective_to): đang hiệu lực tại T nếu from <= T < to (null là không giới hạn). Văn bản ghi "đến
hết ngày X" thì effective_to = X + 1 ngày. `state`: normal | pending_event (hiệu lực có điều kiện, chưa kích hoạt) | suspended (tạm ngưng /
chưa chắc). `status` (suy ra tại ngày as_of = ngày hiệu lực của sự kiện cuối): in_force | expired | pending_event | suspended | not_yet.
So khớp chữ giữa hai bản dùng text_norm (NFC, hoa/thường, khoảng trắng, kiểu gạch, kiểu đặt dấu thanh, [n]); chỉ khác chuẩn hoá thì
không tạo phiên bản. Quyết định chỗ spec im lặng: docs/quyet_dinh/l6_quyet_dinh.txt.
"""
import argparse
import collections
import datetime
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field, asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import a1_parse as a1
import corpus

A4_DIR_NAME = "a4"
STATES = ("normal", "pending_event", "suspended")
_TONE = (("òa", "oà"), ("óa", "oá"), ("ỏa", "oả"), ("õa", "oã"), ("ọa", "oạ"),
         ("ùy", "uỳ"), ("úy", "uý"), ("ủy", "uỷ"), ("ũy", "uỹ"), ("ụy", "uỵ"))


def text_norm(s):
    """Khoá so sánh hai bản chữ: NFC, casefold, thống nhất kiểu đặt dấu thanh (hòa/hoà, ủy/uỷ), bỏ [n], thống nhất gạch, bỏ mọi
    khoảng trắng (gồm dính chữ và khoảng trắng sau nháy), bỏ dấu câu cuối."""
    s = unicodedata.normalize("NFC", s or "").casefold()
    s = re.sub(r"\[\d+\]", "", s)
    s = s.replace("–", "-").replace("—", "-").replace("−", "-")
    for a, b in _TONE:
        s = s.replace(a, b)
    return re.sub(r"\s+", "", s).rstrip(".;:,")


def iso(d):
    return d.isoformat() if d else None


@dataclass
class Ver:
    id: str
    version: int
    type: str
    number: str
    heading: str | None
    text: str
    parent: str | None
    effective_from: datetime.date | None
    effective_to: datetime.date | None = None
    applies_from: datetime.date | None = None
    state: str = "normal"
    trigger: str | None = None
    source_event: str = ""
    closed_by: str | None = None
    previous_version: int | None = None
    flags: list = field(default_factory=list)
    directive: str | None = None
    footnote: list = field(default_factory=list)

    def in_force(self, d):
        """Có hiệu lực tại ngày d? pending_event và suspended không bao giờ."""
        return (self.state == "normal" and (self.effective_from is None or self.effective_from <= d)
                and (self.effective_to is None or d < self.effective_to))

    def status(self, as_of):
        if self.state != "normal":
            return self.state
        if self.effective_from is not None and self.effective_from > as_of:
            return "not_yet"
        if self.effective_to is not None and self.effective_to <= as_of:
            return "expired"
        return "in_force"

    def to_row(self, as_of):
        r = asdict(self)
        for k in ("effective_from", "effective_to", "applies_from"):
            r[k] = iso(getattr(self, k))
        r["text_norm"] = text_norm(self.text)
        r["status"] = self.status(as_of)
        return r


class Store:
    """Mọi phiên bản của mọi đơn vị, cạnh cập nhật, quan hệ chờ đích. Chỉ thêm, không xoá."""

    def __init__(self):
        self.vers = collections.OrderedDict()   # id -> [Ver]
        self.children = collections.defaultdict(list)
        self.edges = []
        self.pending = []
        self.corrections = []  # loại 20: đính chính, giữ chữ trước và sau, không tạo phiên bản pháp lý
        self.events = []

    # ---- tra cứu ----
    def cur(self, uid):
        v = self.vers.get(uid)
        return v[-1] if v else None

    def open(self, uid):
        """Phiên bản hiện hành (chưa đóng) hoặc None. Phiên bản pending_event / suspended chưa đóng cũng là hiện hành."""
        v = self.cur(uid)
        return v if v is not None and v.effective_to is None else None

    def exists(self, uid):
        return uid in self.vers

    def descendants(self, uid):
        out = []
        for c in self.children.get(uid, []):
            out.append(c)
            out += self.descendants(c)
        return out

    # ---- thay đổi ----
    def add(self, ver):
        if ver.id in self.vers:
            raise ValueError(f"mã đã tồn tại: {ver.id}")
        self.vers[ver.id] = [ver]
        if ver.parent:
            self.children[ver.parent].append(ver.id)
        return ver

    def new_version(self, uid, eff, source, text=None, heading=None, flags=(), directive=None, state="normal", trigger=None):
        """Đóng phiên bản hiện hành tại eff và mở phiên bản kế tiếp. Hai chỉ thị cùng sự kiện sửa một đơn vị thì sửa tại chỗ
        (không tạo phiên bản [d, d) rỗng)."""
        cur = self.cur(uid)
        if cur.effective_from == eff and cur.source_event == source and cur.version > 1 and cur.state == state:
            if text is not None:
                cur.text = text
            if heading is not None:
                cur.heading = heading
            cur.flags += [f for f in flags if f not in cur.flags]
            return cur
        if cur.effective_to is None or cur.effective_to > eff:
            cur.effective_to = eff
            cur.closed_by = source
        new = Ver(uid, cur.version + 1, cur.type, cur.number, cur.heading if heading is None else heading,
                  cur.text if text is None else text, cur.parent, eff, None, None, state, trigger, source, None, cur.version,
                  list(flags), directive, list(cur.footnote))
        self.vers[uid].append(new)
        return new

    def close(self, uid, eff, source, flags=()):
        """Đóng phiên bản hiện hành tại eff (không thay chữ). Trả True nếu có đóng."""
        cur = self.cur(uid)
        if cur is None or (cur.effective_to is not None and cur.effective_to <= eff):
            return False
        cur.effective_to = eff
        cur.closed_by = source
        cur.flags += [f for f in flags if f not in cur.flags]
        return True

    def close_tree(self, uid, eff, source, flags=()):
        n = int(self.close(uid, eff, source, flags))
        for d in self.descendants(uid):
            n += int(self.close(d, eff, source, flags))
        return n

    def add_edge(self, s, p, o, evidence, source, effective, flags=(), **extra):
        self.edges.append({"s": s, "p": p, "o": o, "evidence": evidence, "source_event": source,
                           "effective": iso(effective), "flags": list(flags), **extra})

    # ---- xem tại một ngày ----
    def snapshot(self, date):
        """Mỗi đơn vị một phiên bản đang hiệu lực tại ngày `date` (bỏ đơn vị không có)."""
        out = []
        for vs in self.vers.values():
            v = next((x for x in reversed(vs) if x.in_force(date)), None)
            if v is not None:
                out.append(v)
        return out


def add_doc_units(store, doc, units, eff, term_end=None, footnote_dates=None):
    """Nạp mọi đơn vị của văn bản (từ A1) thành phiên bản 1, hiệu lực từ eff."""
    for uid, u in units.items():
        text = u.get("text") or ""
        flags = ["out_of_scope"] if u.get("scope") == "out_of_scope" else []
        store.add(Ver(uid, 1, u["type"], u["number"], u.get("heading"), text, u.get("parent"), eff, term_end, None, "normal",
                      None, doc.doc_id, None, None, flags, None, list(u.get("footnote", []))))


def order_docs(docs):
    """Sự kiện theo ngày hiệu lực; cùng ngày thì theo ngày ban hành rồi doc_id. Văn bản gốc nạp trước, không là sự kiện."""
    rest = [d for d in docs.values() if d.doc_id != corpus.BASE_DOC_ID]
    return sorted(rest, key=lambda d: (d.ngay_hieu_luc, d.ngay_ban_hanh or datetime.date.min, d.doc_id))


def a4_dir():
    return corpus.out_dir(A4_DIR_NAME)


def write_outputs(store, as_of, events):
    d = a4_dir()
    a1.write_jsonl(d / "versions.jsonl", [v.to_row(as_of) for vs in store.vers.values() for v in vs])
    a1.write_jsonl(d / "version_edges.jsonl", store.edges)
    a1.write_jsonl(d / "pending_links.jsonl", store.pending)
    a1.write_jsonl(d / "corrections.jsonl", store.corrections)
    for ev in events:
        path = d / "events" / f"{ev['doc_id']}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(ev, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def load_versions(path=None):
    """Đọc lại versions.jsonl thành list dict (cho A5/A7)."""
    return a1.read_jsonl(path or a4_dir() / "versions.jsonl")


def main(argv=None):
    import l6_directives as l6
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--until", help="dừng sau sự kiện có ngày hiệu lực <= ngày này (YYYY-MM-DD)")
    args = ap.parse_args(argv)
    until = datetime.date.fromisoformat(args.until) if args.until else None
    docs = corpus.load_manifest()
    ctx = l6.Context.build(docs)
    store = Store()
    base = docs[corpus.BASE_DOC_ID]
    add_doc_units(store, base, ctx.units[base.doc_id], base.ngay_hieu_luc)
    events = [{"doc_id": base.doc_id, "effective_date": iso(base.ngay_hieu_luc), "units_new": len(store.vers), "note": "văn bản gốc, KB ban đầu"}]
    as_of = base.ngay_hieu_luc
    for doc in order_docs(docs):
        if until and doc.ngay_hieu_luc > until:
            break
        ev = l6.apply_event(ctx, store, doc)
        events.append(ev)
        as_of = max(as_of, doc.ngay_hieu_luc)
    write_outputs(store, as_of, events)
    l6.write_report(ctx, store, events, as_of)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()
