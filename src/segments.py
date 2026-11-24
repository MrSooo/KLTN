"""Bước 0 và máy kiểm của lượt 1 trong 1.6A-v2 (A59, A60; đặc tả ở docs/design/step_1_6a_propositions.md mục 9).

Lượt 1 do LLM gạch ranh giới mệnh đề trong MỘT câu. Module này làm phần máy quanh lời gọi đó:
- trước LLM: cắt câu, tách token, nhận đơn vị nối (khớp dài nhất), đánh dấu chữ dẫn chiếu của 1.2, và thay khối
  "trừ (các) trường hợp quy định tại <chuỗi dẫn chiếu>" bằng dấu giữ chỗ ⟦DCn⟧ (E5: máy quyết, LLM không phải quyết);
- sau LLM: kiểm đầu ra (khớp nguyên văn, khe chỉ có dấu câu / chữ nối / dấu giữ chỗ, không cắt ngang chữ nối nhiều chữ
  hay chữ dẫn chiếu, ap_cho đúng), rồi dựng danh sách đoạn kèm vị trí và chữ nối ở khe trước mỗi đoạn, chèn lại đoạn
  dan_chieu. Chữ nối đứng ngoài đoạn nên lượt 2 chỉ đọc được chúng từ phần dựng này.
Gold cũng là một "đầu ra" và phải qua cùng máy kiểm (mục 9.6). Lời gọi LLM (lệnh goi) đi qua tuyến ckey của lần chạy dò seg_thu_3,
mỗi câu một lời gọi; phản hồi thô lưu theo phiên bản lời nhắc, chạy lại chỉ gọi câu chưa có.

Dùng: python -I -X utf8 src/segments.py kiem <thư mục phan_hoi>   (máy kiểm lên phản hồi khuôn seg_thu_3, in số lỗi theo loại)
      python -I -X utf8 src/segments.py chon                    (chọn 60 câu gold; không ghi đè)
      python -I -X utf8 src/segments.py kiem-gold <file gold>
      python -I -X utf8 src/segments.py goi dev|test|all [tuyến1,tuyến2 thư_mục]  (gọi API cho bộ gold hay cả 993 câu; tốn tiền)
      python -I -X utf8 src/segments.py cham dev|test [thư_mục] (chấm phản hồi đã có với gold, ghi báo cáo)
      python -I -X utf8 src/segments.py dung                    (lần chạy all: máy kiểm, dựng đoạn cho lượt 2, báo cáo)
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


# ---- Lời nhắc lượt 1 (viết theo đặc tả mục 9.3, 9.4). Sửa chữ lời nhắc thì PHẢI nâng PROMPT_VERSION (phản hồi lưu theo phiên bản).
# Ví dụ chỉ lấy từ Điều không có trong hai file gold (mục 9.6): D113, D85, D185, D86, D18.
PROMPT_VERSION = "tach-cau-1"
SYSTEM = """Tách MỘT câu luật tiếng Việt thành các đoạn theo thứ tự. Mỗi đoạn là:
- "menh_de": một việc đúng hoặc sai được (hành vi, sự kiện, trạng thái);
- "dung_chung": phần mà nhiều mệnh đề dùng chung, kèm "ap_cho" là các id mệnh đề nó áp cho.
Chỉ gạch ranh giới, không gán vai, không giải thích.

CHỮ NỐI (danh sách đóng): và, hoặc, hay, nhưng, thì, mà, nếu, khi, sau khi, trước khi, trong khi, sau đó, trường hợp, trong trường hợp, trong trường hợp này, trừ, trừ trường hợp, để, nhằm, "Do" ở đầu câu.
Chữ nối nằm ở chỗ ranh giới giữa hai đoạn thì đứng NGOÀI mọi đoạn: không đoạn nào được mở đầu hay kết thúc bằng chữ nối, và chữ nối không bao giờ là một đoạn. Chữ nối nằm giữa một đoạn (danh sách "A và B", "các trường hợp sau đây") thì vẫn ở trong đoạn.
Dấu ⟦DC1⟧, ⟦DC2⟧... là một dẫn chiếu máy đã cắt sẵn: để nó ngoài mọi đoạn, không chép vào đoạn nào.

LUẬT KHÔNG TÁCH (đứng trước luật tách: động từ nằm trong các phần sau thì KHÔNG tách dù có nhiều động từ)
K1. Danh sách danh từ (đối tượng, thuộc tính, căn cứ, nơi chốn, nguyên nhân) giữ một đoạn, kể cả mục có động từ ("vì lý do thành lập, gia nhập công đoàn").
K2. Cụm mô tả một đối tượng KHÁC chủ ngữ giữ trong đoạn, kể cả có động từ hay chữ nối bên trong: "<danh từ> do <cơ quan> ban hành", "<danh từ> mà <ai> <làm gì>", "mức lương trước khi nghỉ thai sản". Đồng vị ngữ, phần chêm của chủ ngữ ("<chủ ngữ> là <vai trò>", "<chủ ngữ>, bao gồm cả <ai>,") giữ cùng chủ ngữ.
K3. Vế có chủ ngữ riêng sau động từ nói/khiến ("cho rằng ...", "hướng dẫn X làm ...", "ép buộc X làm ...") là nội dung của động từ đó: không tách bên trong.
K4. Bổ ngữ không mở đầu bằng chữ nối ("đối với ...", "trên cơ sở ...", "theo ...", "tại ...", "trong thời hạn ...", "trong thời gian ...") giữ trong đoạn nó bổ nghĩa. Câu "Đối với X thì Y" là MỘT đoạn ("thì" nằm trong đoạn); "Đối với X mà <vế có động từ> thì Y" thì tách ở "thì", "Đối với X" đi cùng vế điều kiện.
K5. Cụm "để/nhằm ..." đứng ngay sau danh từ VÀ trước động từ chính là phần tên của danh từ ("Tiền lương để tính trợ cấp thôi việc là ..."): không tách. "Trường hợp" làm danh từ ("là trường hợp <việc>", "các trường hợp <...> bao gồm", "trong trường hợp sau đây", "Trường hợp khác", "trường hợp quy định tại ...") nằm trong đoạn.
K6. Vế "trong trường hợp/khi ..." kẹp GIỮA một mệnh đề (vị ngữ đã bắt đầu trước nó và còn tiếp sau nó) giữ trong mệnh đề đó, vì đoạn phải liền. Định nghĩa dạng công thức ("là tổng ... trừ đi ...") là một mệnh đề.

LUẬT TÁCH
T1. Mỗi việc khác nhau là một mệnh đề. Liệt kê nhiều động từ thì tách từng động từ, kể cả sau "có quyền", "được", "chỉ được", "không được", "có thể" và kể cả cặp ngắn ("sửa đổi, bổ sung" thành hai mệnh đề).
T2. Cụm mục đích "để ...", "nhằm ..." đứng sau động từ chính là mệnh đề riêng ("để", "nhằm" ở ngoài đoạn).
T3. Vế mở đầu bằng chữ nối điều kiện, thời gian, ngoại lệ ("nếu", "khi", "trong khi", "sau khi", "trước khi", "sau đó", "trường hợp", "trong trường hợp", "trừ", "trừ trường hợp", "Do") là mệnh đề riêng, kể cả vế không có động từ ("trừ <danh từ>"). Tính chất của CHÍNH chủ ngữ cũng là mệnh đề riêng ("Người lao động Việt Nam | đi làm việc ở nước ngoài | phải tuân theo ...").
T4. Định nghĩa gồm nhiều sự kiện thì tách từng sự kiện. Câu dẫn ("... sau đây:") tách như câu thường.

ĐOẠN DÙNG CHUNG
D1. Chủ ngữ đứng trước từ HAI mệnh đề trở lên mà nó thật sự tham gia (không cần là bên duy nhất) thì tách thành "dung_chung"; ap_cho chỉ gồm các mệnh đề ĐỨNG SAU nó, kể cả sau chữ nối. Chủ ngữ chỉ đứng trước một mệnh đề thì giữ trong mệnh đề đó.
D2. Chủ ngữ cộng chữ phương thức ("có thể", "chỉ được", "không được", "có quyền") đúng cho MỌI mệnh đề trong ap_cho thì gộp vào cùng một đoạn dùng chung; chỉ đúng cho một phần thì tách thành hai đoạn dùng chung lồng nhau.
D3. Tân ngữ hay bổ ngữ chung của nhiều động từ ghi một lần thành "dung_chung" (có thể đứng sau các mệnh đề nó áp cho). Bổ ngữ đầu câu áp cho nhiều mệnh đề ("Trong thời hạn ..., nếu ... thì ...") cũng thành "dung_chung".

CHÉP: mọi chữ chép nguyên văn, đúng thứ tự; mọi chữ thuộc đúng một đoạn, trừ dấu câu, chữ nối ở ranh giới và ⟦DCn⟧.

Chỉ trả JSON: {"doan":[{"id":"m1","loai":"menh_de","chu":"..."},{"id":"c1","loai":"dung_chung","chu":"...","ap_cho":["m1"]}]}

Ví dụ 1. Câu: "Người sử dụng lao động có trách nhiệm quy định lịch nghỉ hằng năm sau khi tham khảo ý kiến của người lao động và phải thông báo trước cho người lao động biết."
{"doan":[{"id":"c1","loai":"dung_chung","chu":"Người sử dụng lao động","ap_cho":["m1","m2","m3"]},{"id":"m1","loai":"menh_de","chu":"có trách nhiệm quy định lịch nghỉ hằng năm"},{"id":"m2","loai":"menh_de","chu":"tham khảo ý kiến của người lao động"},{"id":"m3","loai":"menh_de","chu":"phải thông báo trước cho người lao động biết"}]}

Ví dụ 2. Câu: "Người lao động có thể thỏa thuận với người sử dụng lao động để nghỉ hằng năm thành nhiều lần hoặc nghỉ gộp tối đa 03 năm một lần."
{"doan":[{"id":"c1","loai":"dung_chung","chu":"Người lao động","ap_cho":["m1","m2","m3"]},{"id":"m1","loai":"menh_de","chu":"có thể thỏa thuận với người sử dụng lao động"},{"id":"m2","loai":"menh_de","chu":"nghỉ hằng năm thành nhiều lần"},{"id":"m3","loai":"menh_de","chu":"nghỉ gộp tối đa 03 năm một lần"}]}

Ví dụ 3. Câu: "Doanh nghiệp thành viên của thỏa ước lao động tập thể ngành, thỏa ước lao động tập thể có nhiều doanh nghiệp được rút khỏi thỏa ước lao động tập thể khi có sự đồng thuận của tất cả người sử dụng lao động và tổ chức đại diện người lao động tại doanh nghiệp là thành viên của thỏa ước, trừ trường hợp có khó khăn đặc biệt trong hoạt động sản xuất, kinh doanh."
{"doan":[{"id":"c1","loai":"dung_chung","chu":"Doanh nghiệp thành viên của thỏa ước lao động tập thể ngành, thỏa ước lao động tập thể có nhiều doanh nghiệp","ap_cho":["m1","m3"]},{"id":"m1","loai":"menh_de","chu":"được rút khỏi thỏa ước lao động tập thể"},{"id":"m2","loai":"menh_de","chu":"có sự đồng thuận của tất cả người sử dụng lao động và tổ chức đại diện người lao động tại doanh nghiệp là thành viên của thỏa ước"},{"id":"m3","loai":"menh_de","chu":"có khó khăn đặc biệt trong hoạt động sản xuất, kinh doanh"}]}

Ví dụ 4. Câu: "Số lượng trọng tài viên lao động của Hội đồng trọng tài lao động do Chủ tịch Ủy ban nhân dân cấp tỉnh quyết định, ít nhất là 15 người, bao gồm số lượng ngang nhau do các bên đề cử, cụ thể như sau:"
{"doan":[{"id":"c1","loai":"dung_chung","chu":"Số lượng trọng tài viên lao động của Hội đồng trọng tài lao động","ap_cho":["m1","m2","m3"]},{"id":"m1","loai":"menh_de","chu":"do Chủ tịch Ủy ban nhân dân cấp tỉnh quyết định"},{"id":"m2","loai":"menh_de","chu":"ít nhất là 15 người"},{"id":"m3","loai":"menh_de","chu":"bao gồm số lượng ngang nhau do các bên đề cử, cụ thể như sau"}]}

Ví dụ 5. Câu: "Không tuân thủ đúng quy trình thương lượng, ký kết thỏa ước lao động tập thể."
{"doan":[{"id":"m1","loai":"menh_de","chu":"Không tuân thủ đúng quy trình thương lượng, ký kết thỏa ước lao động tập thể"}]}

Ví dụ 6. Câu: "Người lao động trực tiếp giao kết hợp đồng lao động, ⟦DC1⟧."
{"doan":[{"id":"m1","loai":"menh_de","chu":"Người lao động trực tiếp giao kết hợp đồng lao động"}]}"""
EXAMPLE_UNITS = ("D113.K4", "D85.K2", "D185.K2", "D86.K2.c", "D18.K1")
MODEL = "dungcsnd113/gemini-flash-3.8"  # tuyến của seg_thu_3 (A59: "ckey – Gemini Flash route", upstream chưa kiểm)
# Tuyến dự phòng (user chỉ định 24/11 khi tuyến chính báo "model is not available"): chỉ dùng khi tuyến chính rớt, và chỉ sau khi đo
# lại lời nhắc không đổi trên bộ phát triển (2 vòng) và bộ kiểm tra với cùng ngưỡng (A60). Upstream cũng chưa kiểm.
MODEL_DU_PHONG = "trikiet2045/gemini-3.8-flash-high"
RUN_DIR = ROOT / "data/sandbox_runs/segments"
LUONG = 8  # số câu gọi cùng lúc (4 lúc đo dev/test; 8 từ khi chạy cả bộ bằng tuyến dự phòng chậm, 24/11; máy chủ cho 60 lượt/phút)
STOP_AFTER_FAILS = 6  # như sandbox_api: lỗi API liền nhau ngần này câu thì dừng, chạy lại lệnh sau là làm tiếp câu còn thiếu


def _gold(bo):
    return json.loads((GOLD_DEV if bo == "dev" else GOLD_TEST).read_text(encoding="utf-8"))


def goi(bo, models=(MODEL,), thu_muc=None):
    """Gọi API cho từng câu của một bộ gold (hay "all"), 4 luồng; câu đã có phản hồi ở thư mục này thì bỏ qua (chạy lại chỉ bù câu lỗi
    mạng). Lượt cụt (stop_reason khác end_turn) không lưu, như llm_client. models: thứ tự tuyến; tuyến đầu báo 404 hay hết lần thử thì
    sang tuyến sau. File lưu ghi tuyến đã trả lời (`model`). thu_muc: tên thư mục con thay cho tên bộ (đo tuyến khác không đè lần đầu)."""
    import os
    import time
    import urllib.request
    from concurrent.futures import ThreadPoolExecutor
    import llm_client
    base = llm_client.load_config()["api.base_url"].rstrip("/")
    key = os.environ.get("CKEY_API_KEY")
    if not key:
        raise SystemExit("chưa có CKEY_API_KEY trong biến môi trường")
    out_dir = RUN_DIR / PROMPT_VERSION / (thu_muc or bo)
    out_dir.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / PROMPT_VERSION / "system.txt").write_text(SYSTEM, encoding="utf-8")

    hong = [0]  # số câu lỗi liền nhau; tới STOP_AFTER_FAILS thì máy chủ coi như đang hỏng (24/11: tuyến Gemini trả 404 hàng loạt)

    def one(c):
        path = out_dir / (c["sid"].replace("#", "_") + ".json")
        if path.exists():
            return c["sid"], "co_san"
        if hong[0] >= STOP_AFTER_FAILS:
            return c["sid"], "bỏ qua: máy chủ đang lỗi"
        st = _one(c, path)
        hong[0] = hong[0] + 1 if st.startswith("lỗi") else 0
        return c["sid"], st

    def _one(c, path):
        err = ""
        for model in models:
            body = json.dumps({"model": model, "max_tokens": 16000, "system": SYSTEM,
                               "messages": [{"role": "user", "content": "Câu: \"" + c["cau_gui"] + "\""}]}, ensure_ascii=False).encode("utf-8")
            req = urllib.request.Request(base + "/v1/messages", data=body, method="POST", headers={
                "Authorization": f"Bearer {key}", "Content-Type": "application/json", "anthropic-version": "2023-06-01"})
            for lan in range(1, 4):
                try:
                    with urllib.request.urlopen(req, timeout=300) as r:
                        data = json.loads(r.read().decode("utf-8"))
                    if data.get("stop_reason") != "end_turn":
                        return f"cụt {data.get('stop_reason')} ({model})"
                    path.write_text(json.dumps({"cau_gui": c["cau_gui"], "phien_ban": PROMPT_VERSION, "model": model, "phan_hoi": data},
                                               ensure_ascii=False, indent=1), encoding="utf-8")
                    return f"ok ({model})"
                except Exception as e:  # lỗi mạng, 429, 5xx: chờ rồi thử lại; 404 (tuyến không có) thì sang tuyến sau ngay
                    err = f"{model}: {str(e)[:100]}"
                    if getattr(e, "code", None) == 404:
                        break
                    time.sleep(10 * lan)
        return f"lỗi {err}"

    if bo == "all":  # cả 993 câu BLLĐ, gọi lại cả câu gold (không chép phản hồi cũ) để có mẫu thứ hai đo độ ổn định
        import propositions
        cau = [{"sid": p["sid"], "cau_gui": p["cau_gui"]} for p in all_sentences(propositions.contexts())]
    else:
        cau = _gold(bo)["cau"]
    with ThreadPoolExecutor(LUONG) as ex:
        for sid, st in ex.map(one, cau):
            if st != "co_san":
                print(sid, st, flush=True)


def _shape(placed):
    """Dạng so sánh của một đầu ra đã định vị: các đoạn (loai, từ, đến) và ap_cho đổi id thành khoảng token."""
    span = {d["id"]: (d["tu"], d["den"]) for d in placed}
    doan = tuple((d["loai"], d["tu"], d["den"]) for d in placed)
    ap = tuple(sorted((span[d["id"]], tuple(sorted(span[x] for x in d["ap_cho"]))) for d in placed if d["loai"] == "dung_chung"))
    return doan, ap


def _doc(path):
    """Phản hồi đã lưu thành dict đầu ra; không phải JSON thì ValueError."""
    data = json.loads(path.read_text(encoding="utf-8"))["phan_hoi"]
    return data, parse_reply("".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"))


def dung():
    """Lần chạy cả bộ luật (thư mục all/): chạy máy kiểm từng câu, ghi các đoạn đã dựng (build) của câu qua máy kiểm làm đầu
    vào lượt 2 (doan_luot1.json) và báo cáo bao_cao_all.md. Câu không qua máy kiểm KHÔNG sửa tay, không gọi lại: ghi vào danh
    sách để lượt 2 xử lý (cùng chính sách một lần gọi như lúc đo 35/40). Cũng chấm lại 60 câu gold trên lần gọi này."""
    import propositions
    preps = all_sentences(propositions.contexts())
    src = RUN_DIR / PROMPT_VERSION / "all"
    qua, hong, thieu, co, vnd, theo_model = {}, [], [], {}, 0.0, {}
    for p in preps:
        path = src / (p["sid"].replace("#", "_") + ".json")
        if not path.exists():
            thieu.append(p["sid"])
            continue
        data = {}
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            data = raw["phan_hoi"]
            m = raw.get("model", MODEL)  # file trước khi có tuyến dự phòng không ghi model: đều là tuyến chính
            theo_model[m] = theo_model.get(m, 0) + 1
            data, out = _doc(path)
            errs, flags, placed = check(p, out)
        except (ValueError, KeyError) as e:  # file hỏng hay trả lời không phải JSON: báo, không dừng cả lần dựng
            errs, flags, placed = [f"khuôn: không đọc được ({str(e)[:60]})"], [], []
        vnd += ((data.get("usage") or {}).get("x_ckey") or {}).get("cost") or 0
        if errs:
            hong.append((p["sid"], errs))
            continue
        for f in flags:
            k = re.sub(r"^\w+: ", "", f)
            co[k] = co.get(k, 0) + 1
        qua[p["sid"]] = {"cau": p["cau"], "cau_gui": p["cau_gui"], "co": flags, "model": m,
                         "doan": [{k: d[k] for k in ("id", "loai", "chu", "ap_cho", "khe_truoc") if k in d} for d in build(p, placed)]}
    (src.parent / "doan_luot1.json").write_text(json.dumps({"phien_ban": PROMPT_VERSION, "so_cau": len(preps), "qua": len(qua),
                                                            "cau": qua}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    loai = {}
    for _, errs in hong:
        for e in errs:
            k = re.sub(r"^\w+: ", "", e).split(" '")[0].split(" [")[0]
            loai[k] = loai.get(k, 0) + 1
    gold = [cham(b, "all", ghi=False) for b in ("dev", "test")]
    lines = [f"# Lượt 1 `{PROMPT_VERSION}` trên cả BLLĐ ({len(preps)} câu, mỗi câu gọi một lần)\n",
             f"- qua máy kiểm: {len(qua)}/{len(preps)}; không qua: {len(hong)}; thiếu phản hồi: {len(thieu)}",
             f"- chi phí: {vnd:.1f} VND; phản hồi theo tuyến: " + ", ".join(f"{k} {v}" for k, v in sorted(theo_model.items())),
             "- chấm lại gold trên lần gọi này (lần gọi thứ hai của cùng câu, cùng lời nhắc):"]
    lines += [f"  - {g['bo']}: khớp {g['khop']}/{g['n']} (lần đầu {g['lan_dau']}/{g['n']}; thiếu phản hồi {g['thieu']}), đổi kết quả khớp/không khớp ở "
              f"{len(g['doi'])} câu {g['doi']}; điểm cắt {g['prec']:.3f}/{g['rec']:.3f}" for g in gold]
    lines += ["\n## Loại lỗi máy kiểm (đếm theo lỗi, một câu có thể nhiều lỗi)\n"]
    lines += [f"- {v} {k}" for k, v in sorted(loai.items(), key=lambda x: -x[1])]
    lines += ["\n## Cờ trên câu qua (chỉ cảnh báo)\n"] + [f"- {v} {k}" for k, v in sorted(co.items(), key=lambda x: -x[1])]
    lines += ["\n## Câu không qua máy kiểm (để lượt 2 xử lý; không sửa tay)\n"]
    lines += [f"- {sid}: {'; '.join(e)}" for sid, e in hong] + [f"- {sid}: THIẾU PHẢN HỒI" for sid in thieu]
    (src.parent / "bao_cao_all.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:8]))


def cham(bo, nguon=None, ghi=True):
    """Chấm phản hồi đã có với gold (mục 9.6): câu khớp hoàn toàn (ranh giới, loai, ap_cho); riêng ranh giới (cùng các khoảng
    đoạn); độ chính xác và độ phủ của điểm cắt (vị trí token đầu/cuối đoạn). Lỗi ap_cho báo riêng với lỗi ranh giới.
    nguon="all": chấm phản hồi của lần chạy cả bộ luật thay vì thư mục của bộ, và so với lần đầu (câu đổi khớp/không khớp)."""
    import propositions
    preps = {p["sid"]: p for p in all_sentences(propositions.contexts())}
    out_dir = RUN_DIR / PROMPT_VERSION / (nguon or bo)
    lan_dau = set()
    if nguon:
        for line in (RUN_DIR / PROMPT_VERSION / f"cham_{bo}.md").read_text(encoding="utf-8").splitlines():
            if line.startswith("### ") and line.endswith("— khớp"):
                lan_dau.add(line[4:].split(" — ")[0])
    khop_ids, vang = set(), set()  # vang: câu chưa có phản hồi, không tính là "đổi kết quả"
    rows, n, khop, ranh_gioi, loi_may, thieu, vnd = [], 0, 0, 0, 0, 0, 0.0
    tp = fp = fn = 0
    for c in _gold(bo)["cau"]:
        n += 1
        p = preps[c["sid"]]
        g = _shape(check(p, {"doan": c["doan"]})[2])
        path = out_dir / (c["sid"].replace("#", "_") + ".json")
        if not path.exists():
            thieu += 1
            vang.add(c["sid"])
            rows.append(f"### {c['sid']} — THIẾU PHẢN HỒI\n")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))["phan_hoi"]
        vnd += ((data.get("usage") or {}).get("x_ckey") or {}).get("cost") or 0
        try:
            out = parse_reply("".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"))
            errs, _, placed = check(p, out)
        except ValueError:
            out, errs, placed = {"doan": []}, ["khuôn: không phải JSON"], []
        gcut = {x for _, a, b in g[0] for x in (a, b)}
        if errs:
            loi_may += 1
            ket = "MÁY KIỂM LỖI: " + "; ".join(errs)
            fn += len(gcut)
        else:
            pr = _shape(placed)
            pcut = {x for _, a, b in pr[0] for x in (a, b)}
            tp, fp, fn = tp + len(gcut & pcut), fp + len(pcut - gcut), fn + len(gcut - pcut)
            same_rg = [(a, b) for _, a, b in pr[0]] == [(a, b) for _, a, b in g[0]]
            ranh_gioi += same_rg
            if pr == g:
                khop += 1
                khop_ids.add(c["sid"])
                ket = "khớp"
            elif same_rg and pr[0] == g[0]:
                ket = "ĐÚNG RANH GIỚI, SAI ap_cho"
            elif same_rg:
                ket = "ĐÚNG RANH GIỚI, SAI loai/ap_cho"
            else:
                ket = "SAI RANH GIỚI"
        lines = [f"### {c['sid']} — {ket}", f"> {c['cau_gui']}", "", "gold: " + " · ".join(
            (f"**{d['id']}** \"{d['chu']}\" → {','.join(d['ap_cho'])}" if d["loai"] == "dung_chung" else f"{d['id']} \"{d['chu']}\"") for d in c["doan"])]
        if ket != "khớp":
            lines.append("model: " + " · ".join(
                (f"**{d.get('id')}** \"{d.get('chu')}\" → {','.join(d.get('ap_cho') or [])}" if d.get("loai") == "dung_chung"
                 else f"{d.get('id')} \"{d.get('chu')}\"") for d in out.get("doan", [])))
        rows.append("\n".join(lines) + "\n")
    prec = tp / (tp + fp) if tp + fp else 0
    rec = tp / (tp + fn) if tp + fn else 0
    head = (f"# Chấm lượt 1 `{PROMPT_VERSION}` trên bộ {bo} ({n} câu){', thư mục ' + nguon if nguon else ''}\n\n"
            f"- khớp hoàn toàn: {khop}/{n}\n- đúng ranh giới (bỏ qua loai, ap_cho): {ranh_gioi}/{n}\n- máy kiểm lỗi: {loi_may}; thiếu phản hồi: {thieu}\n"
            f"- điểm cắt: độ chính xác {prec:.3f}, độ phủ {rec:.3f}\n- chi phí: {vnd:.1f} VND\n\n")
    if not ghi:
        return {"bo": bo, "n": n, "khop": khop, "lan_dau": len(lan_dau), "thieu": thieu, "doi": sorted((khop_ids ^ lan_dau) - vang), "prec": prec, "rec": rec}
    (RUN_DIR / PROMPT_VERSION / (f"cham_{bo}_{nguon}.md" if nguon else f"cham_{bo}.md")).write_text(head + "\n".join(rows), encoding="utf-8")
    print(head)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    cmd = sys.argv[1:2]
    if cmd == ["goi"] and len(sys.argv) in (3, 5) and sys.argv[2] in ("dev", "test", "all"):
        # goi <bộ> [model1,model2 thư_mục]: đo tuyến khác vào thư mục riêng, hay chạy all với tuyến dự phòng
        if len(sys.argv) == 5:
            goi(sys.argv[2], tuple(sys.argv[3].split(",")), sys.argv[4])
        else:
            goi(sys.argv[2])
        raise SystemExit(0)
    if cmd == ["cham"] and len(sys.argv) in (3, 4) and sys.argv[2] in ("dev", "test"):
        cham(sys.argv[2], *sys.argv[3:4])
        raise SystemExit(0)
    if cmd == ["dung"] and len(sys.argv) == 2:
        dung()
        raise SystemExit(0)
    if cmd == ["kiem"] and len(sys.argv) == 3:
        kiem(sys.argv[2])
    elif cmd == ["chon"] and len(sys.argv) == 2:
        chon()
    elif cmd == ["kiem-gold"] and len(sys.argv) == 3:
        kiem_gold(sys.argv[2])
    else:
        raise SystemExit(__doc__)
