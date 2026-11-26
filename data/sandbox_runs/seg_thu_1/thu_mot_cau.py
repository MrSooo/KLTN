"""Thử khả thi lượt 1 (chỉ gạch ranh giới mệnh đề) trên MỘT câu. Không thuộc repo.
Dùng: python -I -X utf8 thu_mot_cau.py goi|kiem   (goi: gọi ckey một lần rồi kiểm; kiem: chỉ kiểm lại file đã lưu)."""
import json, os, re, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = "dungcsnd113/gemini-flash-3.8"
BASE = "https://api.xah.io"  # api.base_url ở docs/llm_config.md
CAU = ("Người lợi dụng đình công gây mất trật tự, an toàn công cộng, làm tổn hại máy, thiết bị, tài sản của người sử dụng lao động; "
       "người có hành vi cản trở thực hiện quyền đình công, kích động, lôi kéo, ép buộc người lao động đình công; người có hành vi trù dập, "
       "trả thù người tham gia đình công, người lãnh đạo cuộc đình công thì tùy theo mức độ vi phạm mà bị xử phạt vi phạm hành chính hoặc "
       "truy cứu trách nhiệm hình sự, nếu gây thiệt hại thì phải bồi thường theo quy định của pháp luật.")

SYSTEM = """Tách một câu luật tiếng Việt thành các mệnh đề. Mệnh đề là một việc đơn: một hành vi, sự kiện hay trạng thái có thể đúng hoặc sai riêng.

Luật:
1. Mỗi động từ chỉ một việc khác nhau là một mệnh đề riêng. Liệt kê nhiều động từ thì tách từng động từ.
2. Liệt kê danh từ (đối tượng, thuộc tính, nơi chốn) thì KHÔNG tách, giữ trong cùng mệnh đề.
3. Phần mà nhiều mệnh đề dùng chung (chủ thể, tân ngữ, bổ ngữ) ghi MỘT lần thành đoạn dùng chung, kèm các mệnh đề nó áp cho.
4. Chép nguyên văn, theo thứ tự trong câu. Mọi chữ phải nằm trong một mệnh đề hoặc một đoạn dùng chung, trừ dấu câu và chữ nối: và, hoặc, thì, mà, nếu, khi, hay.
5. Không gán vai, không giải thích.

Chỉ trả JSON, các đoạn theo thứ tự xuất hiện:
{"doan":[{"id":"m1","loai":"menh_de","chu":"..."},{"id":"c1","loai":"dung_chung","chu":"...","ap_cho":["m1"]}]}

Ví dụ 1. Câu: "Tuyển dụng, bố trí, quản lý, điều hành, giám sát lao động; khen thưởng và xử lý vi phạm kỷ luật lao động;"
{"doan":[{"id":"m1","loai":"menh_de","chu":"Tuyển dụng"},{"id":"m2","loai":"menh_de","chu":"bố trí"},{"id":"m3","loai":"menh_de","chu":"quản lý"},{"id":"m4","loai":"menh_de","chu":"điều hành"},{"id":"m5","loai":"menh_de","chu":"giám sát"},{"id":"c1","loai":"dung_chung","chu":"lao động","ap_cho":["m1","m2","m3","m4","m5"]},{"id":"m6","loai":"menh_de","chu":"khen thưởng"},{"id":"m7","loai":"menh_de","chu":"xử lý vi phạm kỷ luật lao động"}]}

Ví dụ 2. Câu: "Thiết lập cơ chế và thực hiện đối thoại, trao đổi với người lao động và tổ chức đại diện người lao động; thực hiện quy chế dân chủ ở cơ sở tại nơi làm việc;"
{"doan":[{"id":"m1","loai":"menh_de","chu":"Thiết lập cơ chế"},{"id":"m2","loai":"menh_de","chu":"thực hiện"},{"id":"c1","loai":"dung_chung","chu":"đối thoại, trao đổi với người lao động và tổ chức đại diện người lao động","ap_cho":["m1","m2"]},{"id":"m3","loai":"menh_de","chu":"thực hiện quy chế dân chủ ở cơ sở tại nơi làm việc"}]}"""

NOI = {"và", "hoặc", "thì", "mà", "nếu", "khi", "hay"}
TOK = re.compile(r"\w+|[^\w\s]")


def toks(s):
    return [t.lower() for t in TOK.findall(s)]


def kiem(out):
    """Máy kiểm: các đoạn khớp nguyên văn, theo thứ tự; khe giữa các đoạn chỉ gồm dấu câu và chữ nối; ap_cho trỏ đúng id."""
    loi, src, i = [], toks(CAU), 0
    ids = {d.get("id") for d in out.get("doan", []) if d.get("loai") == "menh_de"}
    for d in out.get("doan", []):
        t = toks(d.get("chu", ""))
        j = i
        while j < len(src) and src[j:j + len(t)] != t:
            if src[j].isalnum() and src[j] not in NOI:
                break
            j += 1
        if src[j:j + len(t)] != t:
            loi.append(f"{d.get('id')}: không khớp nguyên văn tại vị trí {i} ('{' '.join(src[i:i+6])}...')")
            continue
        i = j + len(t)
        if d.get("loai") == "dung_chung":
            bad = [x for x in d.get("ap_cho", []) if x not in ids]
            if bad or not d.get("ap_cho"):
                loi.append(f"{d.get('id')}: ap_cho sai {d.get('ap_cho')}")
    du = [t for t in src[i:] if t.isalnum() and t not in NOI]
    if du:
        loi.append(f"chữ bị bỏ ở cuối: {' '.join(du)}")
    return loi


def goi():
    key = os.environ["CKEY_API_KEY"]
    body = json.dumps({"model": MODEL, "max_tokens": 16000, "system": SYSTEM,
                       "messages": [{"role": "user", "content": "Câu: \"" + CAU + "\""}]}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(BASE + "/v1/messages", data=body, method="POST",
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.loads(r.read().decode("utf-8"))
    with open(os.path.join(HERE, "phan_hoi.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    return data


def main():
    data = goi() if sys.argv[1] == "goi" else json.load(open(os.path.join(HERE, "phan_hoi.json"), encoding="utf-8"))
    print("stop_reason:", data.get("stop_reason"), "| usage:", json.dumps(data.get("usage"), ensure_ascii=False))
    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text").strip()
    text = re.sub(r"^```(json)?|```$", "", text).strip()
    out = json.loads(text)
    for d in out["doan"]:
        extra = f"  -> {d.get('ap_cho')}" if d.get("loai") == "dung_chung" else ""
        print(f"{d['id']:>4} {'[chung]' if d['loai'] == 'dung_chung' else '       '} {d['chu']}{extra}")
    loi = kiem(out)
    print("MÁY KIỂM:", "qua" if not loi else "LỖI")
    for l in loi:
        print("  -", l)


main()
