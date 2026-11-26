"""Đo độ nối giữa các Điều theo dẫn chiếu của chính Bộ luật (A62). Không gọi API.

Vì sao có: các vòng sửa 1.6 trước đây chỉ đo bằng thước của từng bước (qua cổng, gold ranh giới), nên lỗi "quy tắc không nối được sang
Điều khác" lọt qua. Thước ở đây không chọn theo lỗi đã biết: mỗi dẫn chiếu khác Điều do 1.2 bắt bằng regex là một chỗ luật tự nói hai
đơn vị liên quan.

Hai số:
  1. nối (lỏng): quy tắc của nguồn và của đích dùng chung ít nhất một vị từ (đầu, thân, hay đầu chặn). Lỏng vì không xét phương thức,
     cực; và khi 1.8 biên dịch con trỏ thì cạnh nối có sẵn, nên số này KHÔNG dùng để chấm bản sửa con trỏ.
  2. phép thử cặp (có thể trượt): với mỗi quy tắc dùng đúng một con trỏ applies_<T>, ca CÓ (sự kiện = điều kiện dương khác của quy tắc
     + một thân định nghĩa applies_<T>) phải suy ra đầu bằng s(CASP); ca ĐỐI CHỨNG (bỏ phần của T) không được suy ra. Mỗi truy vấn một
     tiến trình swipl (s(CASP) bản 10.0.2 lỗi ở truy vấn thứ hai trong cùng phiên).

Chạy ở gốc repo:  python -X utf8 -I utils/llm_runs/measure_reference_links.py data/processed_tach [--cap] [--mau N]
"""
import argparse
import collections
import concurrent.futures
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
import rules  # noqa: E402

DOC = "BLLD_45-2019"


def read_jsonl(p):
    return [json.loads(x) for x in Path(p).read_text(encoding="utf-8").splitlines() if x.strip()]


def link_rate(base):
    """-> Counter trạng thái của các dẫn chiếu khác Điều: noi_duoc | khong_noi | dich_khong_co_quy_tac | nguon_khong_co_quy_tac."""
    refs = [m for m in read_jsonl(ROOT / "data/processed_tach/refs" / f"refs_mentions_{DOC}.jsonl")
            if m["o"].startswith("BLLD") and m["s"].split(".")[1] != m["o"].split(".")[1]]
    rs = read_jsonl(Path(base) / "rules" / f"rules_{DOC}.jsonl")
    a2p = {r["head"]["atom"]: r["head"]["pred"] for r in rs}
    heads, bodies = collections.defaultdict(set), collections.defaultdict(set)
    for r in rs:
        for u in r["source_units"]:
            heads[u].add(r["head"]["pred"])
            for b in r["body"]:
                if b.get("role") == "chu_the":
                    continue
                if "blocked_by" in b:
                    bodies[u].update(a2p.get(x, x) for x in b["blocked_by"])
                else:
                    bodies[u].add(b.get("pred") or b["atom"])
    units = set(heads) | set(bodies)

    def under(d, o):
        return set().union(*([d[u] for u in units if rules.under(u, o)] or [set()]))
    st = collections.Counter()
    for m in refs:
        src, dst = under(heads, m["s"]) | under(bodies, m["s"]), under(heads, m["o"]) | under(bodies, m["o"])
        st["dich_khong_co_quy_tac" if not dst else "nguon_khong_co_quy_tac" if not src else "noi_duoc" if src & dst else "khong_noi"] += 1
    return len(refs), st


def chain_test(base, sample=None):
    rs = read_jsonl(Path(base) / "rules" / f"rules_{DOC}.jsonl")
    prog = (Path(base) / "rules" / f"rules_{DOC}.pl").read_text(encoding="utf-8")
    iso = {r["id"] for r in rs if r["isolated"]}
    defs = collections.defaultdict(list)
    for r in rs:
        if r["how"] == "pointer_def" and r["id"] not in iso:
            defs[r["head"]["atom"]].append(r)

    def facts(lits, c):
        return [f"{'-' if x.get('neg') else ''}{x['atom']}({c})." for x in lits
                if not x.get("naf") and x["atom"] != "blocked" and not x["atom"].startswith(rules.POINTER_PREFIX)]
    cases, seen = [], set()
    for r in rs:
        if r["how"] == "pointer_def" or r["id"] in iso:
            continue
        ptr = [x for x in r["body"] if x["atom"].startswith(rules.POINTER_PREFIX)]
        if len(ptr) != 1 or (r["unit"], ptr[0]["atom"]) in seen or not defs.get(ptr[0]["atom"]):
            continue
        seen.add((r["unit"], ptr[0]["atom"]))
        cases.append((r, ptr[0]["atom"], [x for x in r["body"] if x is not ptr[0]], defs[ptr[0]["atom"]][0]))
    if sample:
        random.Random(0).shuffle(cases)
        cases = cases[:sample]
    lines, qs = [], []
    for k, (r, _a, others, d) in enumerate(cases):
        lines += facts(others, f"cp{k}") + facts(d["body"], f"cp{k}") + facts(others, f"cn{k}")
        qs.append((k, f"{'-' if r['head']['neg'] else ''}{r['head']['atom']}"))
    f = Path(tempfile.mkdtemp()) / "p.pl"
    f.write_text(prog + "\n" + "\n".join(sorted(set(lines))) + "\n", encoding="utf-8")

    def one(job):
        k, h, c = job
        goal = f"consult('{f.as_posix()}'), catch((scasp({h}({c}),[model(_)])->write(yes);write(no)),_,write(err)),nl,halt"
        try:
            o = subprocess.run([rules.SWIPL, "-q", "-g", goal, "-t", "halt(1)"], capture_output=True, text=True, encoding="utf-8",
                               timeout=120).stdout.strip().splitlines()
        except subprocess.TimeoutExpired:
            return (k, c[:2]), "het_gio"
        return (k, c[:2]), (o[-1] if o else "err")
    jobs = [(k, h, f"{p}{k}") for k, h in qs for p in ("cp", "cn")]
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        raw = dict(ex.map(one, jobs))
    st, bad = collections.Counter(), []
    for k, _h in qs:
        y, n = raw[(k, "cp")], raw[(k, "cn")]
        ok = y == "yes" and n == "no"
        st["dat" if ok else f"truot (co:{y}, doi chung:{n})"] += 1
        if not ok:
            bad.append((cases[k][0]["unit"], cases[k][1], y, n))
    return len(qs), st, bad


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("base", help="thư mục đầu ra của lần chạy, ví dụ data/processed_tach")
    ap.add_argument("--cap", action="store_true", help="chạy thêm phép thử cặp bằng s(CASP)")
    ap.add_argument("--mau", type=int, help="chỉ thử N ca chọn ngẫu nhiên (hạt giống 0)")
    a = ap.parse_args()
    n, st = link_rate(a.base)
    print(f"dẫn chiếu khác Điều: {n}; {dict(st)}")
    if a.cap:
        n, st, bad = chain_test(a.base, a.mau)
        print(f"phép thử cặp: {n} ca; {dict(st)}")
        for b in bad:
            print("  ", b)
