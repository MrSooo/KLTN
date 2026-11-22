"""Thử khả thi lượt 1 (seg-thu-2) trên 5 câu khó + chạy lại D217.K3. Không thuộc repo.
Dùng: python -I -X utf8 thu_nam_cau.py goi|kiem   (goi: mỗi câu gọi ckey một lần rồi kiểm; kiem: chỉ kiểm lại phản hồi đã lưu)."""
import json, os, re, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = "dungcsnd113/gemini-flash-3.8"
BASE = "https://api.xah.io"  # api.base_url ở docs/llm_config.md

CAU = {
    "D3.K8": ("Phân biệt đối xử trong lao động là hành vi phân biệt, loại trừ hoặc ưu tiên dựa trên chủng tộc, màu da, nguồn gốc quốc gia hoặc "
              "nguồn gốc xã hội, dân tộc, giới tính, độ tuổi, tình trạng thai sản, tình trạng hôn nhân, tôn giáo, tín ngưỡng, chính kiến, khuyết tật, "
              "trách nhiệm gia đình hoặc trên cơ sở tình trạng nhiễm HIV hoặc vì lý do thành lập, gia nhập và hoạt động công đoàn, tổ chức của người "
              "lao động tại doanh nghiệp có tác động làm ảnh hưởng đến bình đẳng về cơ hội việc làm hoặc nghề nghiệp."),
    "D151.K1.b": "Có trình độ chuyên môn, kỹ thuật, tay nghề, kinh nghiệm làm việc; có đủ sức khỏe theo quy định của Bộ trưởng Bộ Y tế;",
    "D154.K5": ("Vào Việt Nam với thời hạn dưới 03 tháng để xử lý sự cố, tình huống kỹ thuật, công nghệ phức tạp nảy sinh làm ảnh hưởng hoặc có nguy "
                "cơ ảnh hưởng tới sản xuất, kinh doanh mà các chuyên gia Việt Nam và các chuyên gia nước ngoài hiện đang ở Việt Nam không xử lý được."),
    "D36.K1.c": ("Do thiên tai, hỏa hoạn, dịch bệnh nguy hiểm, địch họa hoặc di dời, thu hẹp sản xuất, kinh doanh theo yêu cầu của cơ quan nhà nước "
                 "có thẩm quyền mà người sử dụng lao động đã tìm mọi biện pháp khắc phục nhưng vẫn buộc phải giảm chỗ làm việc;"),
    "D8.K4": ("Lợi dụng danh nghĩa dạy nghề, tập nghề để trục lợi, bóc lột sức lao động hoặc lôi kéo, dụ dỗ, ép buộc người học nghề, người tập nghề "
              "vào hoạt động trái pháp luật."),
    "D217.K3": ("Người lợi dụng đình công gây mất trật tự, an toàn công cộng, làm tổn hại máy, thiết bị, tài sản của người sử dụng lao động; "
                "người có hành vi cản trở thực hiện quyền đình công, kích động, lôi kéo, ép buộc người lao động đình công; người có hành vi trù dập, "
                "trả thù người tham gia đình công, người lãnh đạo cuộc đình công thì tùy theo mức độ vi phạm mà bị xử phạt vi phạm hành chính hoặc "
                "truy cứu trách nhiệm hình sự, nếu gây thiệt hại thì phải bồi thường theo quy định của pháp luật."),
}

SYSTEM = """Tách một câu luật tiếng Việt thành các mệnh đề. Mệnh đề là một việc đơn: một hành vi, sự kiện hay trạng thái có thể đúng hoặc sai riêng.

Luật:
1. Mỗi động từ chỉ một việc khác nhau là một mệnh đề riêng. Liệt kê nhiều động từ thì tách từng động từ.
2. Liệt kê danh từ (đối tượng, thuộc tính, nơi chốn) thì KHÔNG tách, giữ trong cùng mệnh đề.
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


def toks(s):
    return [t.lower() for t in TOK.findall(s)]


def kiem(cau, out):
    """Máy kiểm: các đoạn khớp nguyên văn, theo thứ tự; khe giữa các đoạn chỉ gồm dấu câu và chữ nối; ap_cho trỏ đúng id."""
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


def goi(uid, cau):
    key = os.environ["CKEY_API_KEY"]
    body = json.dumps({"model": MODEL, "max_tokens": 16000, "system": SYSTEM,
                       "messages": [{"role": "user", "content": "Câu: \"" + cau + "\""}]}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(BASE + "/v1/messages", data=body, method="POST",
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.loads(r.read().decode("utf-8"))
    with open(os.path.join(HERE, f"phan_hoi_{uid}.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    return data


def main():
    for uid, cau in CAU.items():
        path = os.path.join(HERE, f"phan_hoi_{uid}.json")
        data = goi(uid, cau) if sys.argv[1] == "goi" else json.load(open(path, encoding="utf-8"))
        u = data.get("usage") or {}
        print(f"\n=== {uid} | stop {data.get('stop_reason')} | token vào {u.get('input_tokens')} ra {u.get('output_tokens')} | "
              f"{(u.get('x_ckey') or {}).get('cost')} VND")
        text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text").strip()
        text = re.sub(r"^```(json)?|```$", "", text).strip()
        try:
            out = json.loads(text)
        except ValueError as e:
            print("  KHÔNG PHẢI JSON:", e)
            continue
        for d in out.get("doan", []):
            extra = f"  -> {d.get('ap_cho')}" if d.get("loai") == "dung_chung" else ""
            print(f"{d.get('id'):>4} {'[chung]' if d.get('loai') == 'dung_chung' else '       '} {d.get('chu')}{extra}")
        loi = kiem(cau, out)
        print("MÁY KIỂM:", "qua" if not loi else "LỖI")
        for l in loi:
            print("  -", l)


main()
