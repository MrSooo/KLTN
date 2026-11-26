"""Chạy dò lượt 1 (seg-thu-3) MỘT lần trên mọi câu của bộ khó, để gom các dạng lỗi rồi sửa một lần (A59). Không thuộc repo.
Dùng: python -I -X utf8 do_bo_kho.py goi <thư mục ra>   (gọi; câu đã có phản hồi thì bỏ qua, nên chạy lại chỉ bù câu lỗi mạng)
      python -I -X utf8 do_bo_kho.py bao <thư mục ra>   (máy kiểm + cờ để đọc tay, ghi bao_cao.md)"""
import glob, json, os, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

REPO = "C:/Users/TusPC/Documents/kltn"
LO = f"{REPO}/data/sandbox_runs/bo_kho/bo_kho_gflash_m12_lan1/lo/*.json"  # chữ 158 đơn vị bộ khó
MODEL = "dungcsnd113/gemini-flash-3.8"
BASE = "https://api.xah.io"
VERSION = "seg-thu-3"

SYSTEM = """Tách một câu luật tiếng Việt thành các mệnh đề. Mệnh đề là một việc đơn: một hành vi, sự kiện hay trạng thái có thể đúng hoặc sai riêng.

Luật:
1. Mỗi động từ chỉ một việc khác nhau là một mệnh đề riêng. Liệt kê nhiều động từ thì tách từng động từ. Cụm chỉ mục đích ("để ...", "nhằm ...") là mệnh đề riêng.
2. Liệt kê danh từ (đối tượng, thuộc tính, căn cứ, nơi chốn) thì KHÔNG tách, giữ trong cùng mệnh đề hoặc cùng đoạn dùng chung. Một mục của danh sách có chứa động từ ("vì lý do thành lập, gia nhập công đoàn") vẫn là mục của danh sách, không tách.
3. Phần mà nhiều mệnh đề dùng chung ghi MỘT lần thành đoạn dùng chung, kèm các mệnh đề nó áp cho. Gồm cả chủ thể hay cụm mở đầu đứng trước một loạt việc: tách nó ra, không dính vào mệnh đề đầu tiên.
4. Chép nguyên văn, theo thứ tự trong câu. Mọi chữ phải nằm trong một mệnh đề hoặc một đoạn dùng chung, trừ dấu câu và chữ nối: và, hoặc, thì, mà, nếu, khi, hay, nhưng.
5. Không gán vai, không giải thích.

Chỉ trả JSON, các đoạn theo thứ tự xuất hiện:
{"doan":[{"id":"m1","loai":"menh_de","chu":"..."},{"id":"c1","loai":"dung_chung","chu":"...","ap_cho":["m1"]}]}

Ví dụ 1. Câu: "Tuyển dụng, bố trí, quản lý, điều hành, giám sát lao động; khen thưởng và xử lý vi phạm kỷ luật lao động;"
{"doan":[{"id":"m1","loai":"menh_de","chu":"Tuyển dụng"},{"id":"m2","loai":"menh_de","chu":"bố trí"},{"id":"m3","loai":"menh_de","chu":"quản lý"},{"id":"m4","loai":"menh_de","chu":"điều hành"},{"id":"m5","loai":"menh_de","chu":"giám sát"},{"id":"c1","loai":"dung_chung","chu":"lao động","ap_cho":["m1","m2","m3","m4","m5"]},{"id":"m6","loai":"menh_de","chu":"khen thưởng"},{"id":"m7","loai":"menh_de","chu":"xử lý vi phạm kỷ luật lao động"}]}

Ví dụ 2. Câu: "Thiết lập cơ chế và thực hiện đối thoại, trao đổi với người lao động và tổ chức đại diện người lao động; thực hiện quy chế dân chủ ở cơ sở tại nơi làm việc;"
{"doan":[{"id":"m1","loai":"menh_de","chu":"Thiết lập cơ chế"},{"id":"m2","loai":"menh_de","chu":"thực hiện"},{"id":"c1","loai":"dung_chung","chu":"đối thoại, trao đổi với người lao động và tổ chức đại diện người lao động","ap_cho":["m1","m2"]},{"id":"m3","loai":"menh_de","chu":"thực hiện quy chế dân chủ ở cơ sở tại nơi làm việc"}]}

Ví dụ 3. Câu: "Người lao động có quyền thành lập, gia nhập và hoạt động công đoàn theo quy định của Luật Công đoàn."
{"doan":[{"id":"c1","loai":"dung_chung","chu":"Người lao động có quyền","ap_cho":["m1","m2","m3"]},{"id":"m1","loai":"menh_de","chu":"thành lập"},{"id":"m2","loai":"menh_de","chu":"gia nhập"},{"id":"m3","loai":"menh_de","chu":"hoạt động"},{"id":"c2","loai":"dung_chung","chu":"công đoàn theo quy định của Luật Công đoàn","ap_cho":["m1","m2","m3"]}]}"""

NOI = {"và", "hoặc", "thì", "mà", "nếu", "khi", "hay", "nhưng"}
TOK = re.compile(r"\w+|[^\w\s]")
SPLIT = re.compile(r"\n+|(?<=\.)\s+(?=[A-ZĐÀ-Ỹ])")  # câu = dòng, hoặc sau dấu chấm có chữ hoa theo sau


def sentences():
    """Nguồn = mọi đơn vị 1.6A của BLLĐ (propositions.contexts(), 881 đơn vị), cắt câu bằng SPLIT."""
    sys.path.insert(0, f"{REPO}/src")
    import propositions
    out = []
    for uid, ctx in propositions.contexts().items():
        parts = [s.strip() for s in SPLIT.split(ctx["text"]) if s.strip()]
        out += [(f"{uid}#{i}", s) for i, s in enumerate(parts, 1)]
    return out


def toks(s):
    return [t.lower() for t in TOK.findall(s)]


def kiem(cau, out):
    """Máy kiểm: các đoạn khớp nguyên văn theo thứ tự; khe giữa các đoạn chỉ gồm dấu câu và chữ nối; ap_cho trỏ đúng id."""
    loi, src, i = [], toks(cau), 0
    ids = {d.get("id") for d in out.get("doan", []) if d.get("loai") == "menh_de"}
    for d in out.get("doan", []):
        t = toks(d.get("chu", ""))
        j = i
        while j < len(src) and src[j:j + len(t)] != t:
            if src[j].isalnum() and src[j] not in NOI:
                break
            j += 1
        if not t or src[j:j + len(t)] != t:
            loi.append(f"{d.get('id')}: không khớp nguyên văn tại '{' '.join(src[i:i+6])}...'")
            break  # lỗi đầu đủ để biết câu hỏng; các lỗi sau chỉ là hệ quả
        i = j + len(t)
        if d.get("loai") == "dung_chung" and (not d.get("ap_cho") or any(x not in ids for x in d["ap_cho"])):
            loi.append(f"{d.get('id')}: ap_cho sai {d.get('ap_cho')}")
    else:
        du = [t for t in src[i:] if t.isalnum() and t not in NOI]
        if du:
            loi.append(f"chữ bị bỏ ở cuối: {' '.join(du)}")
    return loi


def goi_mot(item, outdir):
    key_id, cau = item
    path = os.path.join(outdir, key_id.replace("#", "_") + ".json")
    if os.path.exists(path):
        return key_id, "co_san"
    body = json.dumps({"model": MODEL, "max_tokens": 16000, "system": SYSTEM,
                       "messages": [{"role": "user", "content": "Câu: \"" + cau + "\""}]}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(BASE + "/v1/messages", data=body, method="POST",
                                 headers={"Authorization": f"Bearer {os.environ['CKEY_API_KEY']}", "Content-Type": "application/json",
                                          "anthropic-version": "2023-06-01"})
    for lan in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                data = json.loads(r.read().decode("utf-8"))
            if data.get("stop_reason") != "end_turn":
                return key_id, f"stop {data.get('stop_reason')}"  # không lưu: lượt cụt không phải kết quả
            json.dump({"cau": cau, "phien_ban": VERSION, "phan_hoi": data}, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            return key_id, "ok"
        except Exception as e:  # lỗi mạng / 429 / 5xx: chờ rồi thử lại, hết 3 lần thì báo, câu đó chạy lại sau
            err = str(e)[:120]
            time.sleep(10 * lan)
    return key_id, f"loi {err}"


def goi(outdir):
    os.makedirs(outdir, exist_ok=True)
    open(os.path.join(outdir, "system.txt"), "w", encoding="utf-8").write(SYSTEM)
    items = sentences()[:int(os.environ.get("GIOI_HAN", "100000"))]  # GIOI_HAN: chạy thử vài câu trước khi chạy cả bộ
    with ThreadPoolExecutor(4) as ex:
        for n, (k, st) in enumerate(ex.map(lambda it: goi_mot(it, outdir), items), 1):
            if st != "co_san":
                print(f"{n}/{len(items)} {k} {st}", flush=True)


CO = {  # cờ để GOM lỗi cho người đọc; không phải phán quyết, mỗi cờ phải đọc tay mẫu
    "de_nham_trong_menh_de": re.compile(r"\s(để|nhằm)\s"),          # cụm mục đích chưa tách (luật 1)
    "cham_phay_trong_menh_de": re.compile(r";"),                       # hai vế câu gộp
    "va_hoac_trong_menh_de": re.compile(r"\s(và|hoặc)\s"),           # gộp hai việc, HOẶC danh sách danh từ (đúng)
    "dan_chieu_trong_menh_de": re.compile(r"\b(Điều|khoản|điểm|Khoản|Điểm)\s+[0-9a-zđ]+\b"),  # lỗi 6: máy sẽ đánh dấu trước ở bản thật
}


def bao(outdir):
    rows, tong = [], {"cau": 0, "qua": 0, "loi": 0, "thieu": 0, "co": 0, "token_ra": 0, "vnd": 0.0}
    dem = {k: 0 for k in list(CO) + ["dai_tu_15_chu", "chung_ap_mot_menh_de", "loi_khong_khop", "loi_bo_chu_cuoi", "loi_ap_cho", "loi_json"]}
    mau = {k: [] for k in dem}
    J = re.compile(r"(,| và | hoặc )")
    for key_id, cau in sentences():
        tong["cau"] += 1
        path = os.path.join(outdir, key_id.replace("#", "_") + ".json")
        if not os.path.exists(path):
            tong["thieu"] += 1
            rows.append(f"### {key_id} — THIẾU PHẢN HỒI\n")
            continue
        data = json.load(open(path, encoding="utf-8"))["phan_hoi"]
        u = data.get("usage") or {}
        tong["token_ra"] += u.get("output_tokens") or 0
        tong["vnd"] += (u.get("x_ckey") or {}).get("cost") or 0
        text = re.sub(r"^```(json)?|```$", "", "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text").strip()).strip()
        try:
            out = json.loads(text)
            loi = kiem(cau, out)
        except ValueError as e:
            out, loi = {"doan": []}, [f"không phải JSON: {e}"]
        tong["qua" if not loi else "loi"] += 1
        hit = set()
        for l in loi:
            hit.add("loi_json" if "JSON" in l else "loi_bo_chu_cuoi" if "bỏ ở cuối" in l else "loi_ap_cho" if "ap_cho" in l else "loi_khong_khop")
        for d in out.get("doan", []):
            chu = d.get("chu", "")
            if d.get("loai") == "menh_de":
                hit.update(k for k, rx in CO.items() if rx.search(chu))
                if len(chu.split()) >= 15:
                    hit.add("dai_tu_15_chu")
            elif len(d.get("ap_cho") or []) == 1:
                hit.add("chung_ap_mot_menh_de")
        for k in hit:  # đếm theo CÂU, không theo mệnh đề
            dem[k] += 1
            if len(mau[k]) < 40:
                mau[k].append(key_id)
        co = [d["id"] for d in out.get("doan", []) if d.get("loai") == "menh_de" and (J.search(d.get("chu", "")) or len(d.get("chu", "").split()) >= 15)]
        tong["co"] += bool(co)
        lines = [f"### {key_id}" + (" — MÁY KIỂM LỖI" if loi else "") + (f" — cờ đọc tay {co}" if co else ""), f"> {cau}", ""]
        for d in out.get("doan", []):
            lines.append(f"- `{d.get('id')}` " + (f"**[chung → {', '.join(d.get('ap_cho', []))}]** " if d.get("loai") == "dung_chung" else "") + d.get("chu", ""))
        lines += [f"- LỖI: {l}" for l in loi]
        rows.append("\n".join(lines) + "\n")
    head = (f"# Chạy dò lượt 1 `{VERSION}` trên BLLĐ (881 đơn vị 1.6A)\n\n{tong['cau']} câu; máy kiểm qua {tong['qua']}, lỗi {tong['loi']}, thiếu {tong['thieu']}; "
            f"câu có mệnh đề cần đọc tay (có dấu phẩy / và / hoặc, hoặc từ 15 chữ) {tong['co']}; token ra {tong['token_ra']}; {tong['vnd']:.1f} VND.\n\n"
            "## Cờ gom lỗi (đếm theo câu; cờ không phải phán quyết)\n\n| cờ | số câu | mẫu (tối đa 40) |\n|---|---|---|\n"
            + "".join(f"| `{k}` | {v} | {', '.join(mau[k])} |\n" for k, v in dem.items()) + "\n## Từng câu\n\n")
    json.dump({"tong": tong, "dem": dem, "mau": mau}, open(os.path.join(outdir, "tong_hop.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(os.path.join(outdir, "bao_cao.md"), "w", encoding="utf-8").write(head + "\n".join(rows))
    print(head)


{"goi": goi, "bao": bao}[sys.argv[1]](sys.argv[2])
