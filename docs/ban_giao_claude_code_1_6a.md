# Quy trình: chạy phần LLM của bước 1.6A bằng phiên Claude Code tách riêng, không gọi API

Dành cho người vận hành (người dùng hoặc agent trong repo). Quyết định gốc: A36 ở `docs/quyet_dinh/pipeline_moi_quyet_dinh.txt`. Viết 13/11/2026, viết lại cùng ngày sau lượt thí điểm đầu.

## 1. Vì sao tách riêng
Bước 1.6A (`src/concepts.py`) cần LLM gạch "cụm" (chủ thể, điều kiện, ngoại lệ, kết luận) trong từng lô (mỗi lô một Điều, 204 lô). API từng chỉ thấy **lời nhắc cộng lô**. Người dùng quyết không gọi API nữa mà dùng một phiên Claude Code, và phiên đó **không được biết gì về dự án** (yêu cầu 13/11).

Lượt thí điểm đầu chạy ngay trong repo và cho thấy lý do: mở phiên trong repo thì `.claude/CLAUDE.md` tự nạp, và chính file hướng dẫn nằm trong repo cũng kể về dự án (phiên đó tự trích "mục 4 của CLAUDE.md", "chưa commit"). Một dòng "đừng biết gì" trong file đó không có tác dụng. Cách làm đúng: phiên chạy trong **thư mục ngoài repo** chỉ có lời nhắc và các lô; mọi việc kiểm và ghi vào cache do người vận hành làm.

Khoá cache của `replay` chỉ cần tên file đúng bằng khoá và trường `output` hợp lệ (đã kiểm trong code; không nơi nào đọc `usage`, `model`, `request_id`), nên không cần sửa code.

## 2. Quy trình
1. **Kiểm cấu hình.** `ds` in `model cấu hình` và số lô thiếu. Model của phiên sẽ chạy phải đúng bằng `trich.model` ở `docs/llm_config.md`. Khoá cache có tên model: model trùng một model đã có cache (Sonnet, Haiku) thì chỉ thiếu ít lô; model chưa từng chạy thì thiếu cả 204. `thiếu: 0` thì không có việc.
2. **Dựng thư mục tách riêng:** `xuat <thư mục>`. Thư mục nằm NGOÀI repo, tên trung tính (không chứa tên dự án), chưa tồn tại hoặc rỗng. Nó chứa `HUONG_DAN.md` (không nhắc dự án), `system.txt` (nguyên văn lời nhắc, đúng thứ bản ghi cache khai), `schema.json` (lược đồ đầu ra, đúng thứ API từng nhận), `lo/001.json` đến `lo/204.json`, `out/` rỗng. Lược đồ phải nằm trong một file mà subagent được đọc: lượt chạy thử đầu thiếu nó, cả 6 lô ra sai tên trường (`ket_qua` thay `units`, `vai`, `cum`, `text` thay `role`, `span`) dù nội dung nguyên văn.
3. **Mở phiên Claude Code MỚI với thư mục làm việc là thư mục đó, không phải repo:** `cd <thư mục>` rồi `claude`. Không dùng `--resume` hay `-c`. Gõ `/model` chọn đúng model của bước 1. Cho phép phiên dùng Agent tool và ghi file trong thư mục đó (đừng bật chế độ bỏ qua hết quyền). Dán đúng một câu, ví dụ đợt thử: "Đọc HUONG_DAN.md và làm theo, chỉ làm lô 001 đến 006."
4. **Mỗi đợt xong:** `nhap <thư mục>`. Nó từ chối (không ghi) lô sai hình, lô thiếu dòng trong `nhat_ky.tsv`, lô mà model tự báo khác `trich.model`; lô đã có bản ghi thì bỏ qua trừ khi thêm `--de`. Cụm không nguyên văn thì vẫn ghi và được đếm (giống API: pipeline loại ở bước sau). Lô bị từ chối: bảo phiên chạy lại đúng các lô đó.
5. **Lặp** đợt tiếp theo cho đến khi `ds` in `thiếu: 0`.
6. **Kiểm cuối:** `python -I src/concepts.py --llm replay` phải ra `lô có kết quả LLM: 204/204  thiếu cache: 0`; rồi `python -I src/run_all.py --llm replay --viewer --tests` phải ra `XONG: 13/13 bước`, mỗi bộ test `tổng test lỗi: 0`. Hai lệnh này ghi đè `data/processed/` và các báo cáo ở `docs/bao_cao_chay/` (sinh tự động).

## 3. Cái người vận hành phải tự xem sau mỗi đợt
`nhap` in số cụm, số cụm không qua cổng nguyên văn và số **đơn vị không có cụm**. Đối chiếu số đơn vị trống với mốc API trên cả 881 đơn vị: Haiku 14, Sonnet 16 (phần lớn là danh sách danh từ và câu dẫn). Một model trả rỗng nhiều hơn hẳn thì phải nhìn cụ thể đơn vị nào: cổng không bắt rỗng.

## 4. Giới hạn (người dùng đã biết, đừng giấu)
- **Cách ly dựa vào lời dặn, không phải kỹ thuật:** thư mục cha vẫn đọc được nếu phiên cố tình mở. Cái ngăn nó biết là không có file nào trong tầm tay nhắc tới dự án, và không có CLAUDE.md của dự án nào được nạp.
- Chữ luật và mã đơn vị (ví dụ `BLLD_45-2019.D1`) lộ ra trong các lô, và model có thể nhận ra bộ luật. API cũng thấy đúng như vậy.
- Bản ghi không có `request_id`, `usage` là `null` (script nào đọc `["usage"]["input_tokens"]` sẽ lỗi với bản ghi này); nguồn gốc dựa vào `produced_by: "claude_code_sandbox"` và model tự báo trong `nhat_ky.tsv`, không kiểm được. Không dựng lại được bằng `--llm live`.
- Điều kiện khác API: harness, có thể có suy nghĩ, lược đồ chỉ được đưa chứ không bị ép (đầu ra sai hình thì `nhap` từ chối và phải chạy lại lô), subagent riêng cho từng lô. Vì thế số đo không so thẳng với Sonnet hay Haiku.
- Cổng nguyên văn chỉ bắt cụm không nguyên văn; không bắt cụm đúng chữ nhưng sai vai, và chấp nhận `spans` rỗng.
- Việc tạo một subagent mỗi lô tốn hạn mức của gói nhiều hơn một phiên làm tuần tự (chưa đo); nếu hạn mức là vấn đề thì đổi cách giao trong `HUONG_DAN` ở script bên dưới (một subagent nhiều lô) và ghi vào quyết định.

## 5. Script vận hành (ghi nguyên văn ra một file ngoài repo, chạy ở thư mục gốc repo)
Dùng `.venv/bin/python -I <file> <lệnh>` (macOS, Linux) hoặc `.venv\Scripts\python.exe -I <file> <lệnh>` (Windows); script chỉ dùng thư viện chuẩn. Chữ trong `HUONG_DAN` chính là thứ phiên Claude Code đọc: không được thêm vào đó tên dự án, bước hay cache.

```python
"""Công cụ vận hành cho 1.6A khi phần LLM do một phiên Claude Code làm trong thư mục tách riêng (không gọi API).
Chạy ở thư mục gốc repo:  python -I <file này> <lệnh>
  ds                      liệt kê lô còn thiếu theo model ở docs/llm_config.md (trich.model)
  xuat <thư mục mới>      dựng thư mục tách riêng cho phiên Claude Code (không chứa gì về dự án)
  nhap <thư mục> [--de]   đọc out/ và nhat_ky.tsv của thư mục đó, kiểm rồi ghi bản ghi cache; --de cho ghi đè bản ghi đã có"""
import datetime, json, pathlib, sys

sys.path.insert(0, "src")
import concepts as C, corpus, llm_client as L  # noqa: E402

MODEL = L.load_config()["trich.model"]
CACHE = pathlib.Path("data/llm_cache") / C.TASK

# Chữ cho phiên Claude Code. KHÔNG được nhắc tên dự án, bước, cache, API hay model khác: phiên đó chỉ được biết việc trước mắt.
HUONG_DAN = """# Việc của bạn

Thư mục này là toàn bộ thế giới của bạn. Bạn (và mọi subagent bạn tạo) chỉ đọc và ghi trong thư mục này. Không mở thư mục cha hay thư mục nào khác, không tìm hiểu dữ liệu đến từ đâu hay dùng vào việc gì: bạn không cần biết, và biết sẽ làm lệch kết quả.

Có @N@ lô trong `lo/` (`001.json` đến `@N@.json`). Mỗi lô là một danh sách đơn vị văn bản pháp luật. Với mỗi lô, bạn đóng vai bộ trích xuất: làm đúng theo lời nhắc trong `system.txt`, ghi kết quả vào `out/` với cùng số (`out/001.json` cho `lo/001.json`), là JSON đúng lược đồ trong `schema.json`.

## Model
Việc này phải do model `@MODEL@` làm. ID model chính xác của bạn khác thì dừng lại và báo người dùng, đừng làm.

## Mỗi lô làm độc lập
Các lô không được ảnh hưởng nhau: không mang kết quả hay cách đọc của lô trước sang lô sau. Cách đảm bảo: mỗi lô giao cho MỘT subagent mới (Agent tool), đặt tham số model của subagent tường minh bằng model ở trên, chạy song song tối đa 6 subagent một lúc. Không tạo được subagent, hoặc không đặt được model của subagent, thì dừng và báo người dùng.

Lời giao cho subagent (thay NNN bằng số lô), chỉ gồm đúng thế này:
> Đọc `system.txt`, `schema.json` và `lo/NNN.json` trong thư mục làm việc. Làm đúng theo `system.txt` cho lô đó và ghi kết quả vào `out/NNN.json` là JSON thuần đúng lược đồ trong `schema.json` (đúng tên trường, không đổi tên, không thêm trường). Không đọc hay ghi file nào khác. Cuối cùng chỉ trả lời đúng một dòng: NNN, một ký tự tab, rồi ID model chính xác của bạn.

Bạn (phiên chính) KHÔNG tự làm lô nào. Bạn ghi dòng trả lời của từng subagent vào file `nhat_ky.tsv` (một dòng mỗi lô, dạng `NNN<tab>ID model`).

## Cấm
- Không viết script, regex hay công cụ nào để sinh hoặc sửa cụm. Mọi cụm do model đọc chữ mà chọn.
- Không sửa `out/NNN.json` sau khi subagent đã ghi. Không chạy lại một lô trừ khi người dùng bảo.
- Không đọc nhiều lô cùng nhau để so sánh hay làm cho đều.

## Đầu ra của mỗi lô
JSON thuần, không chữ giải thích, đúng lược đồ trong `schema.json` (đúng tên trường, không đổi tên, không thêm trường); mỗi `unit_id` trong lô có đúng một mục. Hình tóm tắt:

    {"units": [{"unit_id": "...", "spans": [{"span": "...", "role": "chu_the", "params": ["W"]}]}]}

## Làm từng đợt
Người dùng sẽ nói làm những lô nào (ví dụ "001 đến 006"). Chỉ làm đúng các lô đó rồi báo: số file đã ghi, nội dung `nhat_ky.tsv`, lô nào lỗi. Không làm lô khác.
"""


def batches():
    _doc, units, labels, _nodes, _refs = C.load_inputs(corpus.BASE_DOC_ID)
    return C.make_batches(C.unit_contexts(units, labels))


def key_of(batch, model=MODEL):
    return L.cache_key(model, C.TASK, C.PROMPT_VERSION, C.user_message(batch), C.SYSTEM, C.SCHEMA)


def missing(model=MODEL, cache=CACHE):
    return [i for i, b in enumerate(batches(), 1) if not (cache / f"{key_of(b, model)}.json").exists()]


def check(batch, output):
    """-> (lỗi hình hoặc None, cảnh báo, số cụm, số cụm không qua cổng nguyên văn). Cổng là hàm của pipeline (concepts.gate_span)."""
    ctx = {c["id"]: c for c in batch}
    try:
        C.validate_output(output, set(ctx))
    except ValueError as e:
        return str(e), [], 0, 0
    warn = [f"đơn vị không có mục: {u}" for u in ctx if u not in {it["unit_id"] for it in output["units"]}]
    n = bad = 0
    for it in output["units"]:
        for s in it["spans"]:
            n += 1
            ok, why = C.gate_span(s, ctx[it["unit_id"]])
            if not ok:
                bad += 1
                warn.append(f"{it['unit_id']}: {why}: {s['span']!r}")
    return None, warn, n, bad


def xuat(thu_muc):
    d = pathlib.Path(thu_muc)
    if d.exists() and any(d.iterdir()):
        raise SystemExit(f"{d} đã có nội dung, không ghi đè")
    bs = batches()
    (d / "lo").mkdir(parents=True, exist_ok=True)
    (d / "out").mkdir(exist_ok=True)
    (d / "system.txt").write_text(C.SYSTEM + "\n", encoding="utf-8", newline="\n")
    (d / "schema.json").write_text(json.dumps(C.SCHEMA, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")  # lược đồ API từng nhận; tách khỏi system.txt vì bản ghi cache khai system = C.SYSTEM nguyên văn
    for i, b in enumerate(bs, 1):
        (d / "lo" / f"{i:03d}.json").write_text(C.user_message(b), encoding="utf-8", newline="\n")
    (d / "HUONG_DAN.md").write_text(HUONG_DAN.replace("@MODEL@", MODEL).replace("@N@", f"{len(bs):03d}"), encoding="utf-8", newline="\n")
    print(f"đã dựng {d}: {len(bs)} lô, model yêu cầu {MODEL}")


def write(batch, output, reported_model, cache=CACHE):
    rec = {"task": C.TASK, "prompt_version": C.PROMPT_VERSION, "role": "trich", "requested_model": MODEL,
           "created": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "system": C.SYSTEM, "user": C.user_message(batch), "model": MODEL, "request_id": None,
           "produced_by": "claude_code_sandbox", "producer_model_reported": reported_model, "output": output, "usage": None}
    path = cache / f"{key_of(batch)}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rec, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    return path


def nhap(thu_muc, de=False, cache=CACHE):
    d, bs = pathlib.Path(thu_muc), batches()
    log = {}
    if (d / "nhat_ky.tsv").exists():
        for line in (d / "nhat_ky.tsv").read_text(encoding="utf-8").splitlines():
            p = [x.strip() for x in line.split("\t")]
            if len(p) >= 2 and p[0].isdigit():
                log[int(p[0])] = p[1]
    ghi, skip, hinh, thieu_nk, khac = [], [], [], [], []
    tong = bad_t = trong = don_vi = 0
    for f in sorted((d / "out").glob("*.json")):
        if not f.stem.isdigit() or not 1 <= int(f.stem) <= len(bs):
            hinh.append((f.name, "tên file lạ"))
            continue
        n = int(f.stem)
        if n not in log:
            thieu_nk.append(n)
            continue
        if log[n] != MODEL:
            khac.append((n, log[n]))
            continue
        try:
            out = json.loads(f.read_text(encoding="utf-8"))
        except ValueError as e:
            hinh.append((n, f"không phải JSON: {e}"))
            continue
        shape, warn, k, bad = check(bs[n - 1], out)
        if shape:
            hinh.append((n, shape))
            continue
        if (cache / f"{key_of(bs[n - 1])}.json").exists() and not de:
            skip.append(n)
            continue
        write(bs[n - 1], out, log[n], cache)
        ghi.append(n)
        tong, bad_t, don_vi = tong + k, bad_t + bad, don_vi + len(bs[n - 1])
        trong += sum(1 for it in out["units"] if not it["spans"]) + sum(1 for w in warn if w.startswith("đơn vị không có mục"))
        for w in warn:
            print(f"  lô {n}: {w}")
    print(f"đã ghi {len(ghi)} lô: {ghi}")
    print(f"  cụm: {tong}, không qua cổng nguyên văn: {bad_t}, đơn vị không có cụm: {trong}/{don_vi}")
    for nm, v in (("bỏ qua vì đã có bản ghi (cần --de để ghi đè)", skip), ("sai hình, KHÔNG ghi", hinh),
                  ("thiếu dòng trong nhat_ky.tsv, KHÔNG ghi", thieu_nk), (f"model báo cáo khác {MODEL}, KHÔNG ghi", khac)):
        if v:
            print(f"{nm}: {v}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    cmd = sys.argv[1]
    if cmd == "ds":
        m = missing()
        print(f"model cấu hình: {MODEL} | tổng lô: {len(batches())} | thiếu: {len(m)} | số lô thiếu: {m if len(m) <= 30 else str(m[:5]) + ' ... ' + str(m[-3:])}")
    elif cmd == "xuat":
        xuat(sys.argv[2])
    elif cmd == "nhap":
        nhap(sys.argv[2], de="--de" in sys.argv[3:])
```

## 6. Đợt thử lời nhắc concepts-3 (14/11, A36): lô nào và lời giao
**KẾT QUẢ: concepts-3 bị RÚT** (cứu được D205.K1-3 nhưng làm hỏng (d) ở D67, xem A36); lời nhắc cuối là concepts-2, xem mục 8. Mục này và mục 7 giữ lại làm hồ sơ.
Lời nhắc đổi lần cuối (concepts-3: một vế ở quy tắc 2) nên thư mục tách riêng phải dựng mới: `xuat /Users/admin/Documents/bo_trich_xuat_3`. Thư mục `bo_trich_xuat_2` (concepts-2) GIỮ NGUYÊN, không sửa, không chạy lại: nó là phương án lùi ở A36 (đầu ra 19 lô, CHƯA nhập cache). Thư mục `bo_trich_xuat` (concepts-1) không dùng nữa. Đợt thử là 21 lô; nếu đạt tiêu chí ở A36 thì 21 lô này GIỮ làm kết quả cuối:
- lô 1 đến 6; lô định nghĩa ngoài Điều 3: 9, 13, 51, 62, 64, 86, 103; lô đối chứng "là" không phải định nghĩa: 34, 52, 70, 88; lô đối chứng danh sách: 66, 192; hai lô thêm cho vế mới của quy tắc 2: 18 (mục chỉ nêu tên bên) và 21 (mục chỉ nêu nội dung). (Số lô theo thứ tự `make_batches`, không trùng số Điều.)
- Lời giao cho phiên Claude Code (mở ở thư mục tách riêng như mục 2, bước 3): "Đọc HUONG_DAN.md và làm theo, chỉ làm lô 001 đến 006, 009, 013, 018, 021, 034, 051, 052, 062, 064, 066, 070, 086, 088, 103 và 192."
- Xong thì: chạy script ở mục 7 để chấm tiêu chí (chỉ đọc `out/`, chưa ghi gì vào cache); các khoản "đọc tay" mà script in ra thì người vận hành đọc và ghi kết luận vào `docs/quyet_dinh/pipeline_moi_quyet_dinh.txt` (A36). CHỈ SAU ĐÓ mới `nhap` (mục 2, bước 4). Đạt thì không sửa lời nhắc nữa; không đạt thì làm theo "PHƯƠNG ÁN LÙI" ở A36. Lưu ý nếu lùi về concepts-2: `nhap` khoá bản ghi theo lời nhắc đang nằm trong `src/concepts.py`, nên phải trả `src/concepts.py` về chữ concepts-2 (bỏ vế thêm ở quy tắc 2, `PROMPT_VERSION = "concepts-2"`) TRƯỚC khi `nhap` thư mục `bo_trich_xuat_2`, và hỏi user trước.

## 7. Script kiểm tiêu chí đạt của concepts-3 (ghi nguyên văn ra một file ngoài repo, chạy ở thư mục gốc repo)
`python -I <file> /Users/admin/Documents/bo_trich_xuat_3` (Windows: dùng `.venv\Scripts\python.exe`). Chỉ đọc. Đã thử trên đầu ra concepts-2 thật (báo hỏng (h) và phần D205 của (d), thiếu lô 18, 21) và trên đầu ra tổng hợp (chỉ còn lô 52 hỏng (e), đúng dự đoán ở A36). Mốc đối chiếu chỉ lấy bản ghi Sonnet/Haiku có lời gửi khớp lời gửi hiện tại; lô 66 và 192 không có bản ghi Sonnet đúng nên dùng Haiku.

```python
"""Kiểm tiêu chí đạt của lời nhắc concepts-3 (A36, đoạn đăng ký 14/11) trên đầu ra thô của thư mục tách riêng. Chỉ đọc, không ghi gì.
So với bản concepts-2: thêm lô 18, 21; thêm (h); (d) phần D205 đổi thành "mỗi khoản 1 đến 2 chu_the". (e) giữ nguyên 0,7-1,6.
Chạy ở thư mục gốc repo:  python -I <file này> <thư mục tách riêng có out/>
Đối chiếu Sonnet và Haiku bằng bản ghi trong data/llm_cache/concepts_spans/, chỉ lấy bản ghi có lời gửi (user) KHỚP lời gửi hiện tại."""
import glob, json, pathlib, sys

sys.path.insert(0, "src")
import concepts as C, corpus  # noqa: E402

P = "BLLD_45-2019."
TRANCHE = [1, 2, 3, 4, 5, 6, 9, 13, 18, 21, 34, 51, 52, 62, 64, 66, 70, 86, 88, 103, 192]
DEF = [f"D3.K{i}" for i in range(1, 10)] + ["D9.K1", "D13.K1", "D52.K1", "D63.K1", "D65", "D90.K1", "D107.K1"]
DEF_LO = {3, 9, 13, 51, 62, 64, 86, 103}                      # lô chứa khoản định nghĩa: (e) chỉ in, không chấm
CONTROL_LA = ["D34.K5", "D34.K7", "D34.K12", "D53.K1", "D72.K3", "D92.K2"]   # "là" không phải định nghĩa: đọc tay
LIST_CONTROL = [f"D67.K{i}" for i in range(1, 9)] + [f"D205.K{i}" for i in range(1, 4)]
PARTIES = ["người lao động", "người sử dụng lao động", "tổ chức đại diện người lao động", "tổ chức đại diện người sử dụng lao động"]


def fold(s):
    return " ".join(s.split()).casefold()


def x_of(text):
    """Thuật ngữ X của khoản 'X là Y': chữ trước chữ ' là ' đầu tiên."""
    return fold(text.split(" là ", 1)[0])


def nonempty(d, u):
    return bool(d.get(P + u))


def crit_a(out):
    """Điều 1: có chu_the cho đủ bốn bên."""
    got = [fold(s["span"]) for s in out.get(P + "D1", []) if s["role"] == "chu_the"]
    miss = [t for t in PARTIES if not any(g == t or g.startswith(t + " ") for g in got)]
    return not miss, f"thiếu chu_the cho: {miss}" if miss else "đủ bốn bên"


def crit_g(out):
    """Điều 2: mỗi khoản K1-K4 vẫn có chu_the."""
    bad = [f"D2.K{k}" for k in range(1, 5) if not any(s["role"] == "chu_the" for s in out.get(f"{P}D2.K{k}", []))]
    return not bad, f"khoản mất chu_the: {bad}" if bad else "K1-K4 đều có chu_the"


def crit_b(out, text):
    """Điều 3: K3-K9 có cụm, câu dẫn trống; X làm ket_luan ở >= 80% khoản định nghĩa có mặt."""
    probs = [f"D3.K{k} trống" for k in range(3, 10) if not nonempty(out, f"D3.K{k}")]
    if P + "D3" in out and out[P + "D3"]:
        probs.append("câu dẫn D3 không trống")
    have = [u for u in DEF if P + u in out]
    xk = [u for u in have if any(s["role"] == "ket_luan" and fold(s["span"]) == x_of(text[P + u]) for s in out[P + u])]
    xc = [u for u in have if any(s["role"] == "chu_the" and fold(s["span"]) == x_of(text[P + u]) for s in out[P + u])]
    ratio = len(xk) / len(have) if have else 0
    ok = not probs and ratio >= 0.8
    return ok, f"{'; '.join(probs) or 'K3-K9 có cụm, câu dẫn trống'} | X là ket_luan: {len(xk)}/{len(have)} ({ratio:.0%}); X còn là chu_the ở: {[u for u in xc]}"


def crit_c(out, S, H):
    """Định nghĩa ngoài D3 mà Sonnet (bản đúng ngữ cảnh) VÀ Haiku đều gạch được: Opus gạch được >= 90%. c2: D63.K1, D107.K1 không trống."""
    cand = [u for u in DEF if not u.startswith("D3.") and P + u in out and S.get(P + u) and H.get(P + u)]
    hit = [u for u in cand if out[P + u]]
    r = len(hit) / len(cand) if cand else 0
    c2 = [u for u in ("D63.K1", "D107.K1") if P + u in out and not out[P + u]]
    return (r >= 0.9 and not c2), f"{len(hit)}/{len(cand)} ({r:.0%}); trống: {[u for u in cand if u not in hit]}; D63.K1/D107.K1 trống: {c2}"


def crit_d(out, H, text):
    lines = []
    for u in CONTROL_LA:   # đọc tay: không được gạch theo khuôn định nghĩa
        if P + u in out:
            lines.append(f"  {u} {text[P + u][:80]!r}\n     " + " | ".join(f"{s['role'][:4]}:{s['span'][:50]!r}" for s in out[P + u]))
    us = [u for u in LIST_CONTROL if u.startswith("D67.") and P + u in out]
    o67 = sum(1 for u in us for s in out[P + u] if s["role"] == "chu_the")
    h67 = sum(1 for u in us for s in H.get(P + u, []) if s["role"] == "chu_the")
    per205 = {u: sum(1 for s in out.get(P + u, []) if s["role"] == "chu_the") for u in ("D205.K1", "D205.K2", "D205.K3")}
    ok = o67 <= h67 and all(1 <= x <= 2 for x in per205.values())   # D205: cận Haiku cũ bỏ vì (h) đòi >= 1 chu_the mỗi khoản (A36 đăng ký 14/11)
    return ok, f"chu_the D67 Opus/Haiku: {o67}/{h67}; D205 mỗi khoản (đăng ký 1 đến 2): {per205}", lines


def crit_h(out):
    """(h) D205.K1-K3 mỗi khoản có ít nhất một chu_the; D18.K3.d, K4.a, K4.c (mục chỉ nêu tên bên) không rỗng."""
    a = [u for u in ("D205.K1", "D205.K2", "D205.K3") if not any(s["role"] == "chu_the" for s in out.get(P + u, []))]
    b = [u for u in ("D18.K3.d", "D18.K4.a", "D18.K4.c") if not out.get(P + u)]
    return not a and not b, f"khoản D205 thiếu chu_the: {a or 'không'}; mục D18 rỗng: {b or 'không'}"


def crit_e(out, batches, S_cur, H):
    rows, bad = [], []
    for n in TRANCHE:
        b = batches[n - 1]
        ids = [c["id"] for c in b]
        if not all(i in out for i in ids):
            continue
        base_src = "Sonnet" if n in S_cur else "Haiku"
        base = sum(len(S_cur[n].get(i, [])) for i in ids) if n in S_cur else sum(len(H.get(i, [])) for i in ids)
        o = sum(len(out[i]) for i in ids)
        r = o / base if base else float("inf")
        scored = len(b) >= 4 and n not in DEF_LO
        rows.append(f"lô {n:3} ({len(b):2} đơn vị) Opus {o:3} / {base_src} {base:3} = {r:.2f}{'' if scored else '  [chỉ xem]'}")
        if scored and not 0.7 <= r <= 1.6:   # cận trên 1.6: Opus vốn ra 1.12-1.44 lần Sonnet ở lô thường (đo trên đầu ra concepts-1, A36), cận này chỉ bắt thêm phình do quy tắc mới
            bad.append(n)
    return not bad, f"lô ngoài 0.7-1.6: {bad}", rows


def load_refs(batches):
    recs = {"claude-sonnet-5-5": {}, "claude-haiku-5-5": {}}
    for f in glob.glob("data/llm_cache/concepts_spans/*.json"):
        d = json.load(open(f, encoding="utf-8"))
        if d.get("model") in recs:
            recs[d["model"]][d["user"]] = d
    S_cur, H = {}, {}
    for n, b in enumerate(batches, 1):
        u = C.user_message(b)
        if u in recs["claude-sonnet-5-5"]:
            S_cur[n] = {it["unit_id"]: it["spans"] for it in recs["claude-sonnet-5-5"][u]["output"]["units"]}
        if u in recs["claude-haiku-5-5"]:
            H.update({it["unit_id"]: it["spans"] for it in recs["claude-haiku-5-5"][u]["output"]["units"]})
    return S_cur, H


def main(d):
    _doc, units, labels, _nodes, _refs = C.load_inputs(corpus.BASE_DOC_ID)
    ctxs = C.unit_contexts(units, labels)
    batches = C.make_batches(ctxs)
    text = {c["id"]: c["text"] for c in ctxs}
    out, gate_bad, missing = {}, [], []
    for n in TRANCHE:
        f = pathlib.Path(d) / "out" / f"{n:03d}.json"
        if not f.exists():
            missing.append(n)
            continue
        o = json.loads(f.read_text(encoding="utf-8"))
        ctx = {c["id"]: c for c in batches[n - 1]}
        try:
            C.validate_output(o, set(ctx))
        except ValueError as e:
            print(f"lô {n}: SAI HÌNH ({e}), bỏ qua")
            continue
        for it in o["units"]:
            out[it["unit_id"]] = it["spans"]
            for s in it["spans"]:
                ok, why = C.gate_span(s, ctx[it["unit_id"]])
                if not ok:
                    gate_bad.append((it["unit_id"], s["span"][:40], why))
    S_cur, H = load_refs(batches)
    S_flat = {u: sp for m in S_cur.values() for u, sp in m.items()}
    print(f"lô thiếu trong out/: {missing or 'không'}\n")
    res = [("(a) Điều 1 đủ bốn bên chu_the",) + crit_a(out), ("(b) Điều 3 và X làm ket_luan",) + crit_b(out, text),
           ("(c) định nghĩa ngoài D3",) + crit_c(out, S_flat, H), ("(f) cụm không qua cổng nguyên văn = 0", not gate_bad, f"{len(gate_bad)} cụm hỏng {gate_bad[:3]}"),
           ("(g) Điều 2 vẫn có chu_the",) + crit_g(out), ("(h) D205.K1-3 có chu_the; D18 không rỗng",) + crit_h(out)]
    d_ok, d_msg, d_lines = crit_d(out, H, text)
    e_ok, e_msg, e_rows = crit_e(out, batches, S_cur, H)
    res += [("(d) đối chứng danh sách (số chu_the) + đọc tay các khoản bên dưới", d_ok, d_msg), ("(e) số cụm 0.7-1.6 lần mốc (lô không định nghĩa)", e_ok, e_msg)]
    for name, ok, msg in res:
        print(f"{'ĐẠT ' if ok else 'HỎNG'} {name}: {msg}")
    print("\n(d) đọc tay, các khoản 'là' không phải định nghĩa (không được gạch theo khuôn X=ket_luan, Y=dieu_kien):")
    print("\n".join(d_lines) or "  (chưa có)")
    print("\n(e) từng lô:\n  " + "\n  ".join(e_rows or ["(chưa có)"]))
    if missing:
        print("\nLƯU Ý: còn lô thiếu nên kết luận chưa đầy đủ; tiêu chí không có dữ liệu có thể báo HỎNG vì thiếu.")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main(sys.argv[1])
```

## 8. Chạy 185 lô còn lại với lời nhắc concepts-2 (đã đóng băng, 14/11, A36)
Concepts-3 đã thử và rút; lời nhắc cuối của 1.6A là concepts-2 (`src/concepts.py` đã trả về, `PROMPT_VERSION = "concepts-2"`, trùng từng chữ với `system.txt` của `bo_trich_xuat_2`). 19 lô đầu đã nhập cache ngày 14/11. Dùng LẠI thư mục `bo_trich_xuat_2`, không dựng mới và không xoá `out/` (đã có 19 file; `bo_trich_xuat_3` không dùng nữa):
- Mở phiên Claude Code mới ở `/Users/admin/Documents/bo_trich_xuat_2`, dùng `/model` chọn Opus 5.5.
- Lời giao: "Đọc HUONG_DAN.md và làm theo, chỉ làm các lô từ 001 đến 204 mà thư mục out/ chưa có file. 19 lô đã có file thì bỏ qua, không làm lại." Nếu muốn chia đợt cho phiên đỡ dài, đổi khoảng số: 001 đến 070, rồi 071 đến 140, rồi 141 đến 204 (mỗi đợt vẫn chỉ làm lô chưa có file).
- 185 lô thiếu lúc 14/11: 007-008, 010-012, 014-033, 035-050, 053-061, 063, 065, 067-069, 071-085, 087, 089-102, 104-191, 193-204.
- Xong thì: chạy `nhap` trên thư mục đó (19 lô đã có bản ghi sẽ bị bỏ qua, không cần `--de`); `ds` phải báo thiếu 0; `python -I src/concepts.py --llm replay` phải đọc 204/204; rồi `python -I src/run_all.py --llm replay --viewer --tests` phải ra 13/13 và 8 bộ test `tổng test lỗi: 0`.
- Sau đó người vận hành đo danh sách sót trên cả 204 lô và ghi vào A36 (đơn vị rỗng, lô ngoài 0,7-1,6 so mốc). Không chạy lại lô nào.
