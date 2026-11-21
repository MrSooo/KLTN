"""Bộ đơn vị khó của 1.6A (A54): dựng thư mục làm việc và chấm đầu ra theo MỌI loại lỗi A1-A4 cùng lúc.

Luật sửa lỗi A54: mỗi lần sửa đo mọi loại trên cùng bộ lô cố định (`data/eval_dev/proposition_panel.json`), nhận khi loại đích tốt lên
và không loại nào xấu đi quá mức nhiễu; nhiễu đo bằng nhiều lần chạy cùng lời nhắc (`sandbox_api.py --lan K`).
Lô lấy nguyên vẹn từ thư mục làm việc đã chạy (không gom lại) nên chữ gửi đi trùng từng byte với lần gốc: lần 0 đọc từ cache, không tốn tiền.
Đầu ra của bộ khó KHÔNG `nhap` vào cache của pipeline (dưới KLTN_LLM_RUN=ckey sẽ ghi đè BLLD_45-2019.ckey.json); chỉ chấm.

Chạy ở gốc repo:
  python -X utf8 -I utils/llm_runs/proposition_panel.py dung <thư mục mới ngoài repo> [phiên bản lời nhắc]
  python -X utf8 -I utils/llm_runs/proposition_panel.py cham <thư mục> [<thư mục> ...]
Chạy lô (cùng KLTN_LLM_RUN với lần gốc, ở đây ckey):
  KLTN_LLM_RUN=ckey python -X utf8 -I src/sandbox_api.py <thư mục> [--lan K]
"""
import collections
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
import llm_client  # noqa: E402
import propositions  # noqa: E402

PANEL = ROOT / "data" / "eval_dev" / "proposition_panel.json"
LONG = 10  # âm tiết: chữ từ ngần này trở lên ra tên vị từ dài ở 55% số ca (A54)
LEAD = re.compile(r"phải\s+(đáp ứng|có đủ|tuân theo)[^:]{0,60}sau đây\s*:?\s*$", re.I)  # như measure_proposition_errors.py (M1)
LEAK = re.compile(r"(sau đây|như sau|\bgồm)\s*$")  # M2
CATASTROPHIC = 5  # lỗi cổng trong một lô từ ngần này là "lô nổ" (A54: lần 2 có một lô 38 lỗi)
CASES = re.compile(r"^(các )?trường hợp", re.I)  # Điều kết luận nằm ở tiêu đề


def load_panel():
    return json.loads(PANEL.read_text(encoding="utf-8"))


def dung(dest, version=None):
    """version: lời nhắc gửi đi (mặc định lời nhắc của bộ khó); lo/ không phụ thuộc lời nhắc nên dùng chung cho mọi phiên bản."""
    d = Path(dest).resolve()
    if ROOT in d.parents or d == ROOT:
        raise SystemExit(f"{d} nằm trong repo: thư mục làm việc mới phải ở ngoài repo (A36, A53)")
    if d.exists() and any(d.iterdir()):
        raise SystemExit(f"{d} đã có nội dung, không ghi đè")
    panel = load_panel()
    src_system = propositions.PROMPTS[panel["prompt_version"]] + "\n"
    version = version or panel["prompt_version"]
    system = propositions.PROMPTS[version] + "\n"
    cfgs = set()
    (d / "lo").mkdir(parents=True, exist_ok=True)
    (d / "out").mkdir(exist_ok=True)
    for i, lot in enumerate(panel["lots"], 1):
        src = ROOT / lot["source"]
        if (src / "system.txt").read_text(encoding="utf-8") != src_system:
            raise SystemExit(f"{src}/system.txt không phải lời nhắc {panel['prompt_version']}")
        c = json.loads((src / "cau_hinh.json").read_text(encoding="utf-8"))
        cfgs.add((c["model"], c["effort"]))
        shutil.copyfile(src / "lo" / f"{lot['lo']}.json", d / "lo" / f"{i:03d}.json")
    if len(cfgs) != 1:
        raise SystemExit(f"các nguồn khác model hoặc effort: {cfgs}")
    (m, effort), = cfgs
    (d / "system.txt").write_text(system, encoding="utf-8", newline="\n")
    (d / "cau_hinh.json").write_text(json.dumps({"model": m, "effort": effort, "prompt_version": version, "pham_vi": "bo_kho",
                                                "nguon": [[x["source"], x["lo"]] for x in panel["lots"]]}, ensure_ascii=False) + "\n", encoding="utf-8")
    hit = sum((llm_client.CACHE_DIR / "sandbox_api" / f"{llm_client.cache_key(m, 'sandbox_api', 'hop_cat', p.read_text(encoding='utf-8'), system, None)}.json").exists()
              for p in sorted((d / "lo").glob("*.json")))
    print(f"đã dựng {d}: {len(panel['lots'])} lô, lời nhắc {version}, model {m}; lần 0 có sẵn trong cache {hit}/{len(panel['lots'])} lô")


def ctx_of(item):
    return {"heading": item["tieu_de_dieu"], "chapeau": item["khoan_cha"], "text": item["chu_don_vi"], "refs": item.get("dan_chieu") or []}


def cham_mot(d):
    """-> (số đo, ghi chú) của một thư mục làm việc."""
    d = Path(d)
    version = json.loads((d / "cau_hinh.json").read_text(encoding="utf-8"))["prompt_version"]
    m = collections.Counter()
    gate = collections.Counter()
    units = {}
    per_lot = []
    for lo in sorted((d / "lo").glob("*.json")):
        items = {it["unit_id"]: it for it in json.loads(lo.read_text(encoding="utf-8"))["don_vi"]}
        out = d / "out" / lo.name
        m["don_vi"] += len(items)
        if not out.exists():
            m["lo_thieu"] += 1
            continue
        try:
            got = {it["unit_id"]: it["dong"] for it in json.loads(out.read_text(encoding="utf-8"))["units"]}
        except (ValueError, KeyError, TypeError):
            m["lo_sai_hinh"] += 1
            continue
        m["don_vi_thieu"] += len(set(items) - set(got))
        lot_err = 0
        for uid, rows in got.items():
            if uid not in items:
                continue
            rows = propositions.normalize(rows)
            err, _flag = propositions.gate_unit(ctx_of(items[uid]), rows, version=version)
            units[uid] = (items[uid], rows)
            m["dong"] += len(rows)
            m["A1_loi_cong"] += len(err)
            lot_err += len(err)
            m["A1_dong_loi"] += len({i for i, _ in err})
            for _i, s in err:
                gate[re.split(r"[:'\"{(\d]", s, maxsplit=1)[0].strip()[:40]] += 1
            for r in rows:
                if not isinstance(r, dict) or r.get("loai") != "menh_de":
                    continue
                m["menh_de"] += 1
                m["A2_bo_ngu_con"] += bool(r.get("bo_ngu"))
                m["A2_dieu_kien"] += r.get("vai") == "dieu_kien"
                syl = len(propositions.syllables(r.get("menh_de") or ""))
                m["A2_am_tiet"] += syl
                m["A2_dai"] += syl >= LONG
                ct = r.get("chu_the")
                if isinstance(ct, dict) and re.search(r"\b(và|hoặc)\b|,", ct.get("chu") or ""):
                    m["A2_chu_the_gop"] += 1
                if LEAK.search(r.get("menh_de") or ""):
                    m["A3_cau_dan_lot"] += 1
                if r.get("cuc") == "phu_dinh" and re.match(r"(không|chưa)\b", (r.get("menh_de") or "").strip().lower()):
                    m["A4_phu_dinh_kep"] += 1
                    m["A4_con_sau_may"] += propositions.effective_cuc(r) == "phu_dinh"
        per_lot.append(lot_err)
    m["per_lot"] = per_lot
    # A3: mục con của câu dẫn yêu cầu có kết luận; Điều "Các trường hợp ..." có kết luận ở mỗi đơn vị con
    for uid, (it, rows) in units.items():
        if LEAD.search(it["chu_don_vi"] or ""):  # nhận câu dẫn từ chữ luật, không từ trich của model (trich đổi giữa các lần chạy)
            for k, (_it, krows) in units.items():
                if k.startswith(uid + ".") and k.count(".") == uid.count(".") + 1:
                    m["A3_muc_con_yeu_cau"] += 1
                    m["A3_muc_con_co_ket_luan"] += any(isinstance(r, dict) and r.get("vai") == "ket_luan" for r in krows)
        if CASES.match(it["tieu_de_dieu"] or "") and uid.count(".") >= 2:
            m["A3_don_vi_truong_hop"] += 1
            m["A3_truong_hop_co_ket_luan"] += any(isinstance(r, dict) and r.get("loai") == "menh_de" and r.get("vai") == "ket_luan" for r in rows)
    return m, gate


def cham(dirs):
    keys = ["don_vi", "lo_thieu", "lo_sai_hinh", "don_vi_thieu", "dong", "menh_de", "A1_loi_cong", "A1_dong_loi", "A1_ti_le_dong_loi", "A1_lo_tham_hoa",
            "A1_bo_lo_xau_nhat", "A1_trung_vi_lo", "A2_dai", "A2_ti_le_dai", "A2_tb_am_tiet",
            "A2_chu_the_gop", "A2_bo_ngu_con", "A2_dieu_kien", "A3_muc_con_co_ket_luan", "A3_truong_hop_co_ket_luan", "A3_cau_dan_lot", "A4_phu_dinh_kep", "A4_con_sau_may"]
    res = []
    for d in dirs:
        m, gate = cham_mot(d)
        m["A2_tb_am_tiet"] = round(m["A2_am_tiet"] / m["menh_de"], 1) if m["menh_de"] else 0
        pl = m.pop("per_lot", [])
        m["A1_lo_tham_hoa"] = sum(x >= CATASTROPHIC for x in pl)  # lô nổ (một lô một cách hỏng) tách khỏi lỗi rải rác
        m["A1_bo_lo_xau_nhat"] = sum(pl) - max(pl) if pl else 0
        m["A1_trung_vi_lo"] = sorted(pl)[len(pl) // 2] if pl else 0
        m["A1_ti_le_dong_loi"] = f"{m['A1_dong_loi'] / m['dong']:.1%}" if m["dong"] else "-"
        m["A2_ti_le_dai"] = f"{m['A2_dai'] / m['menh_de']:.1%}" if m["menh_de"] else "-"
        m["_per_lot"] = pl
        res.append((d, m, gate))
    for k in keys:
        vals = []
        for _d, m, _g in res:
            if k == "A3_muc_con_co_ket_luan":
                vals.append(f"{m[k]}/{m['A3_muc_con_yeu_cau']}")
            elif k == "A3_truong_hop_co_ket_luan":
                vals.append(f"{m[k]}/{m['A3_don_vi_truong_hop']}")
            else:
                vals.append(str(m[k]))
        print(f"{k:28} " + "  ".join(f"{v:>8}" for v in vals))
    for d, m, _g in res:
        print(f"lỗi cổng theo lô ({Path(d).name}): {m['_per_lot']}")
    for d, _m, gate in res:
        print(f"lỗi cổng theo loại ({Path(d).name}): " + "; ".join(f"{k} {v}" for k, v in gate.most_common(8)))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "dung" and len(sys.argv) in (3, 4):
        dung(sys.argv[2], sys.argv[3] if len(sys.argv) == 4 else None)
    elif cmd == "cham" and len(sys.argv) >= 3:
        cham(sys.argv[2:])
    else:
        raise SystemExit(__doc__)
