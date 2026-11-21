"""Bộ chạy hộp cát qua API (A46): làm thay phiên Claude Code trong thư mục làm việc mà `xuat` của 1.6A, 1.6B, 1.7, 1.9 và 2.6 dựng.

Vì sao có: khi phần LLM chạy bằng một model qua API (máy chủ ckey, vai `api` của docs/llm_config.md) thay cho phiên Claude Code (A36),
bộ chạy chỉ cần làm đúng việc của phiên chính và subagent theo HUONG_DAN.md, còn toàn bộ kiểm tra giữ nguyên ở lệnh `nhap` của từng bước.
Không bước nào phải viết lại đường gọi API riêng, và không có LLM nào kiểm LLM khác.

Chạy ở gốc repo, với CÙNG biến KLTN_TAP_CON và KLTN_LLM_RUN như lúc dựng hộp cát (cần CKEY_API_KEY trong môi trường):
  python -X utf8 -I src/sandbox_api.py <thư mục> [--toi-da N] [--song-song K]
    --toi-da N     chỉ làm N lô (hay N lượt) chưa có đầu ra, rồi dừng (luật dừng A39: soát sau 60 lô đầu)
    --song-song K  số lô gọi cùng lúc, chỉ cho hộp cát lô độc lập (mặc định 4, như HUONG_DAN); hộp cát tuần tự luôn một lượt một lần
    --lan K        lần chạy lặp thứ K (A54, đo nhiễu): khoá cache riêng ("hop_cat#lanK"), chữ gửi đi giữ nguyên; mặc định là lần gốc
    --lam-lai 015,117  hộp cát lô độc lập: làm lại các lô mà `nhap` từ chối (ví dụ model bỏ sót unit_id). out cũ cất sang out_sai/,
                   bản ghi cache sang _rejected/ (đọc lại cache sẽ ra đúng đầu ra hỏng), rồi gọi lại như lô chưa làm

Hai kiểu thư mục, nhận theo file có trong thư mục:
  - lô độc lập (không có tiep.py: 1.6A, 1.7, 1.9): mỗi `lo/NNN.json` chưa có `out/NNN.json` được gửi một lượt; đầu ra ghi vào
    `out/NNN.json`, thêm dòng `NNN<tab>model<tab>effort` vào `nhat_ky.tsv`. Lô lỗi API thì bỏ qua và báo; chạy lại lệnh là làm tiếp lô còn thiếu.
  - tuần tự (có tiep.py: 1.6B, sổ vị từ 2.6): vòng `tiep.py moi` -> gọi -> ghi out và nhật ký -> `tiep.py ghi NNN`, đúng vòng lặp mà
    HUONG_DAN.md giao cho phiên chính. Dòng `DỪNG ...` hay dòng lạ thì dừng và in nguyên văn (người vận hành xử lý, như với phiên Claude Code).

Chữ gửi đi là NGUYÊN VĂN `system.txt` (vai system; thư mục có `schema.json` thì nối thêm lược đồ, như subagent được đọc file đó)
và `lo/NNN.json` (lời user), không thêm lời giao của HUONG_DAN: thêm chữ là đổi lời
nhắc (phải nâng PROMPT_VERSION). Model ghi vào nhật ký là `api.model` (ID gửi lên máy chủ); ID đó không chứng minh model thật phía sau
(A46). Bộ chạy không kiểm nội dung đầu ra ngoài "là một đối tượng JSON": hình và nghĩa do `nhap` kiểm.
"""
import argparse
import concurrent.futures
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import llm_client  # noqa: E402

TASK = "sandbox_api"  # thư mục cache data/llm_cache/sandbox_api/: phản hồi thô của mọi lượt, để chạy lại sau lỗi không tốn tiền
PROMPT_TAG = "hop_cat"  # khoá cache đã chứa nguyên chữ system và lời user, nên một nhãn chung cho mọi bước là đủ phân biệt
# Lược đồ gửi kèm ngay sau chữ system.txt (A46): thiếu nó thì model không biết khuôn ngoài (lượt 1.6B đầu tiên ra danh sách trần, 19/11).
SCHEMA_NOTE = "\n\nLược đồ đầu ra (JSON Schema, nội dung file schema.json):\n"
STOP_AFTER_FAILS = 3  # lô độc lập: lỗi API liền nhau ngần này lần thì coi như máy chủ đang hỏng, dừng thay vì đốt cả danh sách


def is_object(output):
    """Kiểm tối thiểu của bộ chạy: đầu ra phải là một đối tượng JSON (mọi khuôn đầu ra của các bước đều là đối tượng)."""
    if not isinstance(output, dict):
        raise ValueError(f"đầu ra là {type(output).__name__}, không phải đối tượng JSON")


def expected_model(d, cfg):
    """(model, effort) mà hộp cát đòi trong nhật ký: lô độc lập ghi ở cau_hinh.json; hộp cát tuần tự (1.6B) đòi ten.model và hop_cat.effort."""
    f = d / "cau_hinh.json"
    if f.exists():
        c = json.loads(f.read_text(encoding="utf-8"))
        return c["model"], c.get("effort")
    return cfg["ten.model"], cfg["hop_cat.effort"]


class Runner:
    def __init__(self, d, client, lan=None):
        self.d, self.client = Path(d), client
        # [THÊM, A54] lần chạy lặp: nhãn chỉ vào khoá cache (llm_client.cache_key), không vào chữ gửi đi, nên lời nhắc không đổi;
        # mỗi lần lặp là một bản ghi riêng, bản ghi của lần chạy trước không bị cất hay ghi đè (đo nhiễu, luật sửa lỗi A54).
        self.tag = PROMPT_TAG if lan is None else f"{PROMPT_TAG}#lan{lan}"
        self.system = (self.d / "system.txt").read_text(encoding="utf-8")
        schema = self.d / "schema.json"
        if schema.exists():  # hộp cát 1.6B, sổ vị từ: HUONG_DAN cho subagent đọc cả schema.json, mà system.txt chỉ nói "đúng lược đồ đã cho"
            self.system += SCHEMA_NOTE + schema.read_text(encoding="utf-8")
        self.model = client.cfg[f"{llm_client.API_ROLE}.model"]
        want, self.effort = expected_model(self.d, client.cfg)
        if want != self.model:  # gọi model này mà hộp cát đòi model khác thì `nhap` sẽ từ chối mọi lô: dừng trước khi tốn tiền
            raise SystemExit(f"hộp cát đòi model {want!r}, vai {llm_client.API_ROLE} gọi {self.model!r}: dựng lại hộp cát với KLTN_LLM_RUN "
                             f"đúng lần chạy (khoá <lần chạy>.hop_cat.model, <lần chạy>.ten.model trong docs/llm_config.md)")

    def user(self, n):
        return (self.d / "lo" / f"{n:03d}.json").read_text(encoding="utf-8")

    def ask(self, n):
        """Một lượt cho lô n. -> bản ghi của llm_client (đầu ra ở 'output'). Ném LLMError / InvalidOutput như llm_client."""
        return self.client.ask(TASK, self.tag, self.system, self.user(n), None, role=llm_client.API_ROLE, validate=is_object, label=f"lô {n:03d}")

    def write(self, n, output):
        """Ghi out/NNN.json rồi dòng nhật ký (đúng thứ tự đó: nhật ký có dòng thì out đã có)."""
        (self.d / "out").mkdir(exist_ok=True)
        (self.d / "out" / f"{n:03d}.json").write_text(json.dumps(output, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        with (self.d / "nhat_ky.tsv").open("a", encoding="utf-8", newline="\n") as f:
            f.write(f"{n:03d}\t{self.model}\t{self.effort}\n")

    def redo(self, n):
        """Chuẩn bị làm lại lô n: cất out/NNN.json sang out_sai/NNN_<k>.json (không xoá, để còn xem) và quên bản ghi cache. Dòng nhật ký cũ
        để nguyên: các bước đọc nhật ký lấy dòng SAU CÙNG của mỗi lô."""
        out = self.d / "out" / f"{n:03d}.json"
        if out.exists():
            (self.d / "out_sai").mkdir(exist_ok=True)
            k = 1 + sum(1 for _ in (self.d / "out_sai").glob(f"{n:03d}_*.json"))
            out.replace(self.d / "out_sai" / f"{n:03d}_{k}.json")
        self.forget(n)

    def forget(self, n):
        """Cất bản ghi cache của lô n sang _rejected/ để lần gọi sau hỏi lại model (dùng khi tiep.py báo SAI HÌNH: đọc lại cache sẽ sai y hệt)."""
        key = llm_client.cache_key(self.model, TASK, self.tag, self.user(n), self.system, None)
        path = self.client.cache_dir / TASK / f"{key}.json"
        if path.exists():
            self.client._quarantine(path, json.loads(path.read_text(encoding="utf-8")), "tiep.py báo sai hình")

    # ---- lô độc lập ----
    def run_lots(self, limit=None, workers=4):
        todo = sorted(int(p.stem) for p in (self.d / "lo").glob("*.json") if not (self.d / "out" / p.name).exists())[:limit]
        print(f"{self.d}: {len(todo)} lô cần làm, model {self.model}, song song {workers}")
        done, failed, streak = 0, [], 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(self.ask, n): n for n in todo}
            for fut in concurrent.futures.as_completed(futures):
                n = futures[fut]
                try:
                    rec = fut.result()
                except llm_client.QuotaReached as e:
                    failed.append((n, str(e)))
                    for f in futures:
                        f.cancel()
                    break
                except (llm_client.LLMError, llm_client.InvalidOutput) as e:
                    failed.append((n, str(e)[:200]))
                    streak += 1
                    if streak >= STOP_AFTER_FAILS:
                        print(f"DỪNG: {streak} lô lỗi liền nhau, máy chủ có thể đang hỏng; các lô đang chờ bị huỷ, chạy lại lệnh để làm tiếp")
                        for f in futures:
                            f.cancel()
                        break
                    continue
                streak = 0
                self.write(n, rec["output"])
                done += 1
                if rec.get("boc_rao"):
                    print(f"  lô {n:03d}: đã bóc rào ``` quanh JSON (A46)")
        print(f"xong {done}/{len(todo)} lô; lỗi {len(failed)}")
        for n, why in sorted(failed):
            print(f"  lô {n:03d} LỖI: {why}")
        return 0 if not failed else 1

    # ---- tuần tự ----
    def tiep(self, *args):
        """Chạy tiep.py trong thư mục làm việc (như phiên chính làm). -> dòng cuối nó in."""
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", "tiep.py", *args], cwd=self.d, capture_output=True, text=True, encoding="utf-8")
        lines = (r.stdout or "").strip().splitlines()
        return lines[-1] if lines else f"DỪNG: tiep.py không in gì (mã {r.returncode}): {(r.stderr or '').strip()[-300:]}"

    def run_rounds(self, limit=None):
        made = 0
        while limit is None or made < limit:
            line = self.tiep("moi")
            print(line)
            if line.startswith("HẾT"):
                return 0
            m = re.match(r"(LƯỢT|CHỜ) (\d+)", line)
            if not m:  # DỪNG, THIẾU NHẬT KÝ (bộ chạy luôn ghi nhật ký cùng out nên không nên gặp) hay dòng lạ: người vận hành xử lý
                return 1
            n = int(m[2])
            try:
                rec = self.ask(n)
            except (llm_client.LLMError, llm_client.InvalidOutput) as e:
                print(f"DỪNG: lượt {n:03d} lỗi API: {str(e)[:300]}; chạy lại lệnh để làm tiếp từ lượt này")
                return 1
            self.write(n, rec["output"])
            made += 1
            line = self.tiep("ghi", f"{n:03d}")
            print(line)
            if line.startswith("SAI HÌNH"):
                self.forget(n)  # tiep.py đã cất out sang out_sai/; vòng sau gặp CHỜ n và hỏi lại model (lần hai sai thì tiep.py tự DỪNG)
                continue
            if not line.startswith("ĐÃ NHẬN") or "DỪNG" in line:
                return 1
            if "HẾT" in line:
                return 0
        print(f"dừng theo --toi-da sau {made} lượt")
        return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("thu_muc")
    ap.add_argument("--toi-da", type=int, default=None)
    ap.add_argument("--song-song", type=int, default=4)
    ap.add_argument("--lam-lai", default="", help="các số lô cách nhau bằng dấu phẩy")
    ap.add_argument("--lan", type=int, default=None, help="lần chạy lặp K (A54): bản ghi cache riêng, không đổi chữ gửi đi")
    args = ap.parse_args(argv)
    d = Path(args.thu_muc)
    if not (d / "system.txt").exists():
        raise SystemExit(f"{d} không phải thư mục làm việc (thiếu system.txt)")
    runner = Runner(d, llm_client.Client("live", log=llm_client.stderr_log), lan=args.lan)
    if args.lam_lai:
        if (d / "tiep.py").exists():
            raise SystemExit("--lam-lai chỉ cho hộp cát lô độc lập; hộp cát tuần tự làm lại qua tiep.py (SAI HÌNH)")
        for n in (int(x) for x in args.lam_lai.split(",")):
            runner.redo(n)
    code = runner.run_rounds(args.toi_da) if (d / "tiep.py").exists() else runner.run_lots(args.toi_da, args.song_song)
    raise SystemExit(code)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
