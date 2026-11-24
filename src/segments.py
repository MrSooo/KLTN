"""Bước 0 và máy kiểm của lượt 1 trong 1.6A-v2 (A59, A60; đặc tả ở docs/design/step_1_6a_propositions.md mục 9).

Lượt 1 do LLM gạch ranh giới mệnh đề trong MỘT câu. Module này làm phần máy quanh lời gọi đó:
- trước LLM: cắt câu, tách token, nhận đơn vị nối (khớp dài nhất), đánh dấu chữ dẫn chiếu của 1.2, và thay khối
  "trừ (các) trường hợp quy định tại <chuỗi dẫn chiếu>" bằng dấu giữ chỗ ⟦DCn⟧ (E5: máy quyết, LLM không phải quyết);
- sau LLM: kiểm đầu ra (khớp nguyên văn, khe chỉ có dấu câu / chữ nối / dấu giữ chỗ, không cắt ngang chữ nối nhiều chữ
  hay chữ dẫn chiếu, ap_cho đúng), rồi dựng danh sách đoạn kèm vị trí và chữ nối ở khe trước mỗi đoạn, chèn lại đoạn
  dan_chieu. Chữ nối đứng ngoài đoạn nên lượt 2 chỉ đọc được chúng từ phần dựng này.
Không gọi LLM. Gold cũng là một "đầu ra" và phải qua cùng máy kiểm (mục 9.6).

Dùng: python -I -X utf8 src/segments.py kiem <thư mục phan_hoi>   (chạy máy kiểm lên các phản hồi đã có, in số lỗi theo loại)
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

# Mục 9.4. Có trong tập chỉ nghĩa là được đứng ngoài đoạn ở ranh giới; giữa đoạn vẫn là chữ thường.
CONNECTORS = ("và", "hoặc", "hay", "nhưng", "thì", "mà", "nếu", "khi", "sau khi", "trước khi", "trong khi", "sau đó", "trường hợp",
              "trong trường hợp", "trong trường hợp này", "trừ", "trừ trường hợp", "do", "để", "nhằm")
# Chữ nối nối danh từ trong danh sách cũng hay gặp, nên không dùng để chia tầng câu gold (mục 9.6).
LIST_CONNECTORS = {("và",), ("hoặc",), ("hay",)}
# Được đứng cuối đoạn vì là âm tiết của từ ghép hay gặp ở cuối đoạn: "khấu trừ", "các trường hợp".
END_EXEMPT = {"trừ", "trường hợp"}
# Mục 9.4: "do" chỉ là chữ nối khi mở đầu câu ("Do thiên tai, ..."); giữa câu "do X quyết định" là vị ngữ hay cụm mô tả (luật 4).
_SENTENCE_START_ONLY = {("do",)}
_UNITS = sorted((tuple(c.split()) for c in CONNECTORS), key=len, reverse=True)  # khớp dài nhất trước
# "trường hợp" là danh từ, không phải chữ nối, khi theo sau là: "quy định tại" (luật 7 (b)); "sau đây", "như sau" (luật 7 (a),
# câu dẫn); "khác" ("Trường hợp khác do hai bên thỏa thuận", mục liệt kê).
_NOT_UNIT_AFTER = (("quy", "định", "tại"), ("sau", "đây"), ("như", "sau"), ("khác",))


def _noun_truong_hop(words, j):
    """Sau "trường hợp" (kết thúc ở chỉ số j) là một trong các cụm trên."""
    return any(tuple(words[j:j + len(n)]) == n for n in _NOT_UNIT_AFTER)

TOKEN = re.compile(r"⟦DC\d+⟧|\w+|[^\w\s]")
PLACEHOLDER = re.compile(r"⟦DC\d+⟧", re.IGNORECASE)  # token đã hạ chữ thường thành ⟦dc1⟧
# Mục 9.2: câu = dòng, hoặc sau dấu chấm có chữ hoa theo sau (giống lần chạy dò seg_thu_3, để số câu so được: 993).
SPLIT = re.compile(r"\n+|(?<=\.)\s+(?=[A-ZĐÀ-Ỹ])")
# "các" sau "tại" thuộc chuỗi dẫn chiếu nhưng 1.2 không ghi vào cụm (D45.K1 "tại các khoản 4, 5, 6, 7 và 8 Điều 34").
_LEAD_E5 = re.compile(r"trừ (các )?trường hợp quy định tại (các )?", re.IGNORECASE)
_CHAIN_SEP = re.compile(r"(, | và | hoặc )")
LONG_WORDS = 15  # cờ đọc tay, như seg_thu_3


def _nfc(s):
    return unicodedata.normalize("NFC", s or "")


def tokens(s):
    """[(chữ thường, vị trí đầu, vị trí cuối)] theo ký tự của s."""
    return [(m.group(0).lower(), m.start(), m.end()) for m in TOKEN.finditer(_nfc(s))]


def _is_word(t):
    return t[0].isalnum() and not PLACEHOLDER.fullmatch(t)


def connector_units(toks):
    """Các đơn vị nối trong câu, quét trái sang phải, khớp dài nhất, không chồng nhau: [(i, j)] theo chỉ số token.
    Vì sao quét trước một lần cho cả câu: "trước khi" phải là một khối thì mới bắt được ranh giới cắt ngang "trước | khi" (E1)."""
    words = [t[0] for t in toks]
    out, i = [], 0
    while i < len(words):
        for u in _UNITS:
            if u in _SENTENCE_START_ONLY and i > 0:
                continue
            if tuple(words[i:i + len(u)]) == u and not (u[-1] == "hợp" and _noun_truong_hop(words, i + len(u))):
                out.append((i, i + len(u)))
                i += len(u)
                break
        else:
            i += 1
    return out


def sentences(text):
    return [s.strip() for s in SPLIT.split(text or "") if s.strip()]


def _e5_blocks(cau, refs):
    """Các khối E5 trong câu: (đầu, cuối) theo ký tự. Khối = chữ dẫn "trừ (các) trường hợp quy định tại" cộng chuỗi cụm dẫn
    chiếu của 1.2 liền sau, nối bằng ", ", " và ", " hoặc ". Không có cụm nào của 1.2 liền sau thì không phải khối (1.2 chưa
    giải được đích): để nguyên cho LLM theo luật 7, không đoán."""
    cums = sorted({r["cum"] for r in refs}, key=len, reverse=True)
    out = []
    for m in _LEAD_E5.finditer(cau):
        pos, end = m.end(), None
        while True:
            hit = next((c for c in cums if cau.startswith(c, pos)), None)
            if not hit:
                break
            end = pos + len(hit)
            sep = _CHAIN_SEP.match(cau, end)
            if not sep or not any(cau.startswith(c, sep.end()) for c in cums):
                break
            pos = sep.end()
        if end is not None:
            out.append((m.start(), end))
    return out


def prepare(sid, cau, refs):
    """Câu sẵn sàng gửi lượt 1: cau_gui (khối E5 đã thay bằng ⟦DCn⟧), dc ({dấu giữ chỗ: chữ gốc}), các khoảng token của chữ
    dẫn chiếu còn lại (không được cắt ngang) và của đơn vị nối."""
    cau = _nfc(cau)
    blocks = _e5_blocks(cau, refs)
    dc, parts, last = {}, [], 0
    for n, (a, b) in enumerate(blocks, 1):
        key = f"⟦DC{n}⟧"
        dc[key] = cau[a:b]
        parts += [cau[last:a], key]
        last = b
    gui = "".join(parts) + cau[last:]
    toks = tokens(gui)
    ref_spans = []
    for r in refs:
        for m in re.finditer(re.escape(_nfc(r["cum"])), gui):
            idx = [k for k, t in enumerate(toks) if t[1] >= m.start() and t[2] <= m.end()]
            if idx:
                ref_spans.append((idx[0], idx[-1] + 1))
    return {"sid": sid, "cau": cau, "cau_gui": gui, "dc": dc, "toks": toks,
            "units": connector_units(toks), "ref_spans": sorted(set(ref_spans))}


def all_sentences(contexts):
    """Mọi câu của các đơn vị 1.6A, đã chuẩn bị: [prepare(...)]. sid = "<đơn vị>#<thứ tự câu từ 1>" như seg_thu_3."""
    out = []
    for uid, ctx in contexts.items():
        for i, s in enumerate(sentences(ctx["text"]), 1):
            out.append(prepare(f"{uid}#{i}", s, ctx.get("refs", [])))
    return out


def _cuts(spans, a, b):
    """Khoảng nào trong spans bị ranh giới đoạn [a, b) cắt ngang (một phần trong, một phần ngoài)."""
    return [(i, j) for i, j in spans if (i < a < j) or (i < b < j)]


def check(prep, out):
    """Máy kiểm mục 9.5. Trả (lỗi, cờ, các đoạn đã định vị). Lỗi là danh sách chuỗi; rỗng nghĩa là câu qua.
    Đoạn đã định vị: dict của đoạn cộng `tu`, `den` (chỉ số token trong cau_gui) và `khe_truoc` (chữ nối ở khe trước)."""
    errs, flags = [], []
    doan = out.get("doan") if isinstance(out, dict) else None
    if not isinstance(doan, list) or not doan:
        return ["khuôn: thiếu danh sách doan"], flags, []
    toks, words = prep["toks"], [t[0] for t in prep["toks"]]
    unit_at = {i: (i, j) for i, j in prep["units"]}
    ids = [d.get("id") for d in doan]
    if len(set(ids)) != len(ids):
        errs.append(f"khuôn: id trùng {ids}")
    menh = {d.get("id") for d in doan if d.get("loai") == "menh_de"}
    placed, i = [], 0
    for d in doan:
        if d.get("loai") not in ("menh_de", "dung_chung"):
            errs.append(f"{d.get('id')}: loai lạ {d.get('loai')!r}")
            continue
        t = [x[0] for x in tokens(d.get("chu", ""))]
        if not t:
            errs.append(f"{d.get('id')}: chu rỗng")
            continue
        j, gap = i, []
        # Khe: chỉ được bỏ qua dấu câu, dấu giữ chỗ và nguyên một đơn vị nối. Thử khớp đoạn trước khi bỏ qua.
        while j < len(words) and words[j:j + len(t)] != t:
            if not _is_word(words[j]):
                j += 1
            elif j in unit_at:
                a, b = unit_at[j]
                gap.append(" ".join(words[a:b]))
                j = b
            else:
                break
        if words[j:j + len(t)] != t:
            errs.append(f"{d.get('id')}: không khớp nguyên văn tại '{' '.join(words[i:i + 6])} ...'")
            break  # lỗi đầu đủ để biết câu hỏng; các lỗi sau chỉ là hệ quả
        a, b = j, j + len(t)
        inner = [(x, y) for x, y in prep["units"] if a <= x and y <= b]
        if inner and inner[0][0] == a:
            errs.append(f"{d.get('id')}: mở đầu bằng chữ nối '{' '.join(words[inner[0][0]:inner[0][1]])}'")
        if inner and inner[-1][1] == b and " ".join(words[inner[-1][0]:b]) not in END_EXEMPT:
            errs.append(f"{d.get('id')}: kết thúc bằng chữ nối '{' '.join(words[inner[-1][0]:b])}'")
        for x, y in _cuts(prep["units"], a, b):
            errs.append(f"{d.get('id')}: cắt ngang chữ nối '{' '.join(words[x:y])}'")
        for x, y in _cuts(prep["ref_spans"], a, b):
            errs.append(f"{d.get('id')}: cắt ngang dẫn chiếu '{' '.join(words[x:y])}'")
        if any(PLACEHOLDER.fullmatch(w) for w in words[a:b]):
            errs.append(f"{d.get('id')}: chứa dấu giữ chỗ dẫn chiếu")
        if d.get("loai") == "dung_chung":
            ap = d.get("ap_cho")
            if not ap or not isinstance(ap, list) or any(x not in menh for x in ap):
                errs.append(f"{d.get('id')}: ap_cho sai {ap}")
            elif len(ap) == 1:
                flags.append(f"{d.get('id')}: dung_chung áp cho một mệnh đề")
        elif len(t) >= LONG_WORDS:
            flags.append(f"{d.get('id')}: mệnh đề từ {LONG_WORDS} chữ")
        placed.append(dict(d, tu=a, den=b, khe_truoc=gap))
        i = b
    else:
        tail = [w for w in words[i:] if _is_word(w)]
        # Phần đuôi cũng là khe: chỉ được còn dấu câu, dấu giữ chỗ, đơn vị nối.
        k = i
        while k < len(words):
            if not _is_word(words[k]):
                k += 1
            elif k in unit_at:
                k = unit_at[k][1]
            else:
                errs.append(f"chữ bị bỏ ở cuối: {' '.join(tail)}")
                break
    return errs, flags, placed


def build(prep, placed):
    """Danh sách đoạn cuối của lượt 1 (cho lượt 2): đoạn theo thứ tự, đoạn dan_chieu chèn vào chỗ ⟦DCn⟧ với chữ gốc."""
    words = [t[0] for t in prep["toks"]]
    marks = [(k, w) for k, w in enumerate(words) if PLACEHOLDER.fullmatch(w)]
    keys = {k.lower(): v for k, v in prep["dc"].items()}
    out, n = [], 0
    for d in placed + [None]:
        stop = d["tu"] if d else len(words)
        while marks and marks[0][0] < stop:
            k, w = marks.pop(0)
            n += 1
            out.append({"id": f"d{n}", "loai": "dan_chieu", "chu": keys[w], "tu": k, "den": k + 1, "khe_truoc": []})
        if d:
            out.append(d)
    return out


def parse_reply(text):
    """Chữ trả lời của model (có thể bọc ```json) thành dict; không phải JSON thì ValueError."""
    text = re.sub(r"^```(json)?|```$", "", (text or "").strip()).strip()
    return json.loads(text)


def kiem(folder):
    """Chạy máy kiểm lên các phản hồi lượt 1 đã lưu (khuôn seg_thu_3: {cau, phan_hoi}). Chỉ để xem máy kiểm bắt gì trên
    dữ liệu thật; các phản hồi cũ không biết ⟦DCn⟧ và chữ nối mới nên lỗi ở đây KHÔNG phải số đo của đặc tả mới."""
    import propositions
    preps = {p["sid"]: p for p in all_sentences(propositions.contexts())}
    dem, mau, qua, tong = {}, {}, 0, 0
    for f in sorted(Path(folder).glob("*.json")):
        sid = f.stem.rsplit("_", 1)
        sid = f"{sid[0]}#{sid[1]}"
        if sid not in preps:
            continue
        tong += 1
        data = json.loads(f.read_text(encoding="utf-8"))["phan_hoi"]
        try:
            out = parse_reply("".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"))
            errs = check(preps[sid], out)[0]
        except ValueError:
            errs = ["khuôn: không phải JSON"]
        qua += not errs
        for e in errs:
            loai = re.sub(r"^\w+: ", "", e).split(" '")[0].split(" [")[0]
            dem[loai] = dem.get(loai, 0) + 1
            mau.setdefault(loai, []).append(sid)
    print(f"{tong} câu, qua {qua}")
    for k, v in sorted(dem.items(), key=lambda x: -x[1]):
        print(f"{v:5}  {k}  ví dụ {mau[k][:3]}")


ROOT = Path(__file__).resolve().parent.parent
GOLD_DEV = ROOT / "data/eval_dev/segment_gold_dev.json"
GOLD_TEST = ROOT / "data/eval_dev/segment_gold_test.json"
SEED = 20261124
# Mục 9.6: mỗi bộ 1/3 câu không có đơn vị nối, 2/3 câu có (trong đó có câu dẫn). (thường, có nối, trong đó câu dẫn tối thiểu)
QUOTA = {"dev": (13, 27, 2), "test": (7, 13, 1)}
_UNIT_NAME = re.compile(r"\bD\d+(?:\.K\d+)?(?:\.[a-zđ]+)?\b")


def used_units(unit_ids):
    """Đơn vị đã "dùng" (mục 9.6): agent đã đọc đầu ra hoặc đã nêu tên khi soạn luật. Tính bằng máy, không chọn tay, để bộ
    kiểm tra sạch đến mức kiểm được. Nêu tên một Điều/khoản thì loại cả các đơn vị con (bảo thủ: thà mất câu còn hơn lọt)."""
    names = set()
    texts = [ROOT / "docs/decisions.md", ROOT / "docs/design/step_1_6a_propositions.md", ROOT / "tests/test_segments.py"]
    # bao_cao.md liệt kê MỌI câu của lần chạy dò (báo cáo đầy đủ), không phải danh sách câu agent đã đọc: không quét.
    texts += [p for p in (ROOT / "data/sandbox_runs").glob("seg_thu_*/*.md") if p.name != "bao_cao.md"]
    texts += list((ROOT / "data/sandbox_runs").glob("seg_thu_*/*.txt"))
    for p in texts:
        names |= set(_UNIT_NAME.findall(p.read_text(encoding="utf-8")))
    tong = json.loads((ROOT / "data/sandbox_runs/seg_thu_3/tong_hop.json").read_text(encoding="utf-8"))
    for ids in tong["mau"].values():
        names |= {i.split("#")[0].split(".", 1)[1] for i in ids}
    for line in (ROOT / "data/sandbox_runs/seg_thu_3/scope_phrase_labels.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        names.add(line.split("\t")[1].split("_")[0])
    # Đơn vị agent đọc trong phiên làm đặc tả mà không file nào ghi tên (in ra qua grep, mẫu lỗi, tra tay).
    for line in (ROOT / "data/sandbox_runs/seg_thu_3/session_read_units.txt").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            names.add(line.strip())
    # Bộ khó ghi theo Điều ("BLLD D3"); Điều của văn bản khác không thuộc kho câu ở đây.
    panel = json.loads((ROOT / "data/eval_dev/proposition_panel.json").read_text(encoding="utf-8"))
    names |= {lot["dieu"].split()[1] for lot in panel["lots"] if lot["dieu"].startswith("BLLD ")}
    out = set()
    for u in unit_ids:
        short = u.split(".", 1)[1]
        if any(short == n or short.startswith(n + ".") for n in names):
            out.add(u)
    return out


def _tang(p):
    """Tầng của câu: "và/hoặc/hay" không tính vì phần lớn nối danh từ trong danh sách (câu một mệnh đề lọt tầng "có nối")."""
    words = [t[0] for t in p["toks"]]
    if all(tuple(words[i:j]) in LIST_CONNECTORS for i, j in p["units"]):
        return "thuong"
    return "cau_dan" if p["cau"].rstrip().endswith(":") else "noi"


def chon():
    """Chọn 60 câu gold (40 phát triển, 20 kiểm tra) bằng hạt giống cố định, ghi khung gold (doan rỗng) để agent soạn.
    Mỗi Điều góp tối đa một câu cho cả hai bộ: các khoản cùng Điều hay cùng khuôn chữ ("Ít nhất 45 ngày nếu ..."), nên chỉnh lời
    nhắc trên một khoản ở bộ phát triển sẽ làm khoản kia ở bộ kiểm tra dễ giả. Không ghi đè file đã có (gold đã soạn là dữ liệu)."""
    import random
    import propositions
    if GOLD_DEV.exists() or GOLD_TEST.exists():
        raise SystemExit(f"đã có {GOLD_DEV.name} hoặc {GOLD_TEST.name}: không ghi đè")
    preps = all_sentences(propositions.contexts())
    units = {p["sid"].split("#")[0] for p in preps}
    bo = used_units(units)
    pool = [p for p in preps if p["sid"].split("#")[0] not in bo]
    rng = random.Random(SEED)
    rng.shuffle(pool)
    by = {}
    for p in pool:
        by.setdefault(_tang(p), []).append(p)
    print(f"đơn vị {len(units)}, loại {len(bo)}, câu còn {len(pool)}: " + ", ".join(f"{k} {len(v)}" for k, v in sorted(by.items())))
    taken = set()

    def lay(tang, n):
        out = []
        for p in by.get(tang, []):
            u = ".".join(p["sid"].split("#")[0].split(".")[:2])  # mã Điều
            if len(out) == n:
                break
            if u not in taken:
                taken.add(u)
                out.append(p)
        if len(out) < n:
            raise SystemExit(f"tầng {tang} thiếu câu: cần {n}, có {len(out)}")
        return out

    for name, path in (("dev", GOLD_DEV), ("test", GOLD_TEST)):
        thuong, noi, dan = QUOTA[name]
        chosen = lay("thuong", thuong) + lay("cau_dan", dan) + lay("noi", noi - dan)
        doc = {"bo": name, "dac_ta": "A60", "hat_giong": SEED,
               "cau": [{"sid": p["sid"], "tang": _tang(p), "cau_gui": p["cau_gui"], "kho": [], "doan": []}
                       for p in sorted(chosen, key=lambda p: p["sid"])]}
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"ghi {path.relative_to(ROOT)}: {len(chosen)} câu")


def kiem_gold(path):
    """Chạy máy kiểm lên một file gold; câu chưa soạn (doan rỗng) tính riêng. Thoát mã 1 nếu có câu lỗi."""
    import propositions
    preps = {p["sid"]: p for p in all_sentences(propositions.contexts())}
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    bad, empty = 0, 0
    for c in doc["cau"]:
        if not c["doan"]:
            empty += 1
            continue
        e = check(preps[c["sid"]], {"doan": c["doan"]})[0]
        if e:
            bad += 1
            print(c["sid"], e)
    print(f"{len(doc['cau'])} câu, chưa soạn {empty}, lỗi {bad}")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    cmd = sys.argv[1:2]
    if cmd == ["kiem"] and len(sys.argv) == 3:
        kiem(sys.argv[2])
    elif cmd == ["chon"] and len(sys.argv) == 2:
        chon()
    elif cmd == ["kiem-gold"] and len(sys.argv) == 3:
        kiem_gold(sys.argv[2])
    else:
        raise SystemExit(__doc__)
