"""Đo offline hướng 2 của A62 (mục 8 của bao_cao_a62.md): nếu máy lọc từ vựng 1.9 theo chữ Việt trùng với câu hỏi, tên ĐÚNG có còn trong
danh sách ngắn không. Không gọi LLM, không đổi lời nhắc. Đây chỉ là điều kiện CẦN: lọc giữ được tên đúng thì LLM vẫn phải chọn đúng trong
danh sách ngắn.

Dùng: KLTN_LLM_RUN=tach python -X utf8 -I utils/llm_runs/measure_vocab_filter.py [cache 1.9]
(cache mặc định: data/llm_cache/answering/blld_questions.<LLM_RUN>.json, để lấy tên LLM đã chọn sai).

Cách lọc (chốt TRƯỚC khi xem kết quả, không chỉnh theo 34 câu): chữ NFC, casefold, thống nhất dấu thanh (textutil.TONE), tách âm tiết theo
chữ cái; thuật ngữ = âm tiết đơn + cặp âm tiết liền nhau; trọng số idf tính trên toàn bộ "nghia" của từ vựng (kết luận và vị từ tính riêng);
điểm ứng viên = tổng idf các thuật ngữ khác nhau có cả trong câu hỏi và trong "nghia". Với kết luận, "nghia" bỏ tiền tố chế độ ("phải:",
"được:"...). Hạng = thứ tự điểm giảm dần, hoà thì theo tên. K = 20, 50, 100.

Gold (do máy suy từ `can_cu` của bộ câu, chỉ câu có đáp án ket_luan_duoc hoặc bi_bac):
- quy tắc gold: quy tắc sống (không cô lập) có source_units nằm dưới một đơn vị can_cu (rules.under, như answering.run);
- với mỗi quy tắc gold: đầu (phải có trong danh sách kết luận) và các literal thân phải cấp làm dữ kiện = không naf, atom không là đầu
  của quy tắc nào (atom là đầu thì máy suy ra, không cần dữ kiện). Literal neg vẫn tính (dữ kiện phu_dinh).
- câu "lọt @K" khi có ÍT NHẤT MỘT quy tắc gold có đầu trong top-K kết luận VÀ mọi dữ kiện cần trong top-K vị từ.
Biến thể B (chốt trước khi xem kết quả B, sau khi đã thấy kết quả A): danh sách vị từ @K = top-K vị từ theo chữ HỢP mọi atom thân (trừ đầu)
của các quy tắc sống có đầu nằm trong top-K kết luận. In thêm cỡ danh sách vị từ B (trung bình trên các câu) để thấy giá phải trả.
Giới hạn: không xét chuỗi quy tắc (thân là đầu của quy tắc khác thì bỏ qua dữ kiện của quy tắc đó); quy tắc gold có thể có điều kiện mà câu
hỏi không cần nêu (bi_bac); nên đây là cận dưới của "lọt" theo nghĩa chặt."""
import collections
import json
import math
import os
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
import answering  # noqa: E402
import corpus  # noqa: E402
import rules  # noqa: E402
import textutil  # noqa: E402

KS = (20, 50, 100)
MODE_PREFIX = re.compile(r"^(phải không|phải|được|cấm|không thuộc diện): ")
WORD = re.compile(r"[^\W\d_]+")


def terms(s):
    s = unicodedata.normalize("NFC", s or "").casefold()
    for a, b in textutil.TONE:
        s = s.replace(a, b)
    sy = WORD.findall(s)
    return set(sy) | {f"{a} {b}" for a, b in zip(sy, sy[1:])}


def ranker(entries):
    """entries: [(ten, nghia)] -> hàm(câu hỏi) -> {ten: hạng (1 = cao nhất)}."""
    docs = [(t, terms(MODE_PREFIX.sub("", n))) for t, n in entries]
    df = collections.Counter(x for _t, ts in docs for x in ts)
    idf = {x: math.log(len(docs) / c) for x, c in df.items()}

    def rank(q):
        qt = terms(q)
        scored = sorted(((-sum(idf[x] for x in ts & qt), t) for t, ts in docs))
        return {t: i + 1 for i, (_s, t) in enumerate(scored)}, {t: -s for s, t in scored}
    return rank


def main():
    run = corpus.LLM_RUN or ""
    cache_p = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data/llm_cache/answering" / f"blld_questions.{run}.json"
    picks = json.loads(cache_p.read_text(encoding="utf-8"))["answers"] if cache_p.exists() else {}
    qs = json.loads((ROOT / "data/eval_dev/blld_questions.json").read_text(encoding="utf-8"))["cau_hoi"]
    all_rules = answering.load_rules()
    vocab, preds, heads = answering.vocabulary(all_rules)
    all_heads = {r["head"]["atom"] for r in all_rules}
    rank_h = ranker([(e["ten"], e["nghia"]) for e in vocab["ket_luan"]])
    rank_p = ranker([(e["ten"], e["nghia"]) for e in vocab["vi_tu"]])
    print(f"KB {run or 'mặc định'}: {len(vocab['ket_luan'])} kết luận, {len(vocab['vi_tu'])} vị từ; K = {KS}")
    print("cột: id đáp_án | hạng đầu gold tốt nhất | quy tắc gold tốt nhất: hạng đầu / hạng dữ kiện tệ nhất (số dữ kiện) | lọt@20/50/100"
          " | φ LLM chọn (hạng) | dữ kiện LLM chọn không thuộc quy tắc gold (hạng) và dữ kiện gold LLM bỏ (hạng)")
    tally = collections.Counter()
    tally_b = collections.Counter()
    sizes = collections.defaultdict(list)
    n_scored = 0
    for q in qs:
        if q.get("dap_an") not in ("ket_luan_duoc", "bi_bac"):
            print(f"{q['id']} {q.get('dap_an')}: không xét (không có quy tắc gold)")
            continue
        rh, _ = rank_h(q["cau_hoi"])
        rp, _ = rank_p(q["cau_hoi"])
        gold = [r for r in all_rules if not r.get("isolated") and r["head"]["atom"] in heads
                and any(rules.under(s, u) for s in r["source_units"] for u in q.get("can_cu", []))]
        if not gold:
            print(f"{q['id']} {q['dap_an']}: KHÔNG có quy tắc sống nào dưới can_cu {q.get('can_cu')} (lọc không cứu được)")
            tally["khong_quy_tac"] += 1
            n_scored += 1
            continue
        n_scored += 1
        best = None
        for r in gold:
            need = sorted({l["atom"] for l in r["body"] if not l.get("naf") and l["atom"] not in all_heads})
            hr = rh[r["head"]["atom"]]
            fr = max((rp.get(a, 10**6) for a in need), default=0)
            key = max(hr, fr)
            if best is None or key < best[0]:
                best = (key, r, hr, fr, need)
        key, r, hr, fr, need = best
        ok = [key <= k for k in KS]
        for k in KS:
            top_h = {h for h, i in rh.items() if i <= k}
            pool = {h for h, i in rp.items() if i <= k} | {l["atom"] for x in all_rules if not x.get("isolated") and x["head"]["atom"] in top_h
                                                          for l in x["body"] if l["atom"] not in all_heads}
            sizes[k].append(len(pool))
            tally_b[k] += any(rh[x["head"]["atom"]] <= k and all(a in pool for a in nd) for x, nd in
                              ((x, {l["atom"] for l in x["body"] if not l.get("naf") and l["atom"] not in all_heads}) for x in gold))
        for k, o in zip(KS, ok):
            tally[k] += o
        best_head = min(rh[x["head"]["atom"]] for x in gold)
        line = (f"{q['id']} {q['dap_an']} | đầu gold {best_head} | {r['unit']} {r['head']['atom']}: {hr} / {fr} ({len(need)}) | "
                + "/".join("có" if o else "không" for o in ok))
        a = picks.get(q["id"])
        if a and a.get("cau_hoi") == q["cau_hoi"]:
            phi = a.get("phi")
            line += f" | φ={phi} ({rh.get(phi, '-') if phi else '-'})"
            gold_atoms = {l["atom"] for x in gold for l in x["body"]}
            extra = [f"{f['vi_tu']}({rp.get(f['vi_tu'], '-')})" for f in a.get("su_kien", []) if f["vi_tu"] not in gold_atoms]
            chosen = {f["vi_tu"] for f in a.get("su_kien", [])}
            miss = [f"{x}({rp.get(x, '-')})" for x in need if x not in chosen]
            line += f" | thừa: {', '.join(extra) or '-'}; bỏ: {', '.join(miss) or '-'}"
        print(line)
    print(f"TỔNG: {n_scored} câu xét; lọt " + ", ".join(f"@{k}: {tally[k]}/{n_scored}" for k in KS)
          + f"; không có quy tắc gold: {tally['khong_quy_tac']}")
    print("BIẾN THỂ B (vị từ = top-K chữ ∪ thân quy tắc của top-K kết luận): lọt " + ", ".join(f"@{k}: {tally_b[k]}/{n_scored}" for k in KS)
          + "; cỡ danh sách vị từ trung bình " + ", ".join(f"@{k}: {sum(v) / len(v):.0f}" for k, v in sizes.items()))


if __name__ == "__main__":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    main()
