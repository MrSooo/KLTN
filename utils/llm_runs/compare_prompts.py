"""So chữ mọi lời nhắc 1.6A của bản propositions.py đã commit với bản đang sửa: lời nhắc đã dùng để chạy
mà đổi một chữ là vỡ cache (CONTRIBUTING mục 4), nên sau khi thêm phiên bản mới phải thấy các bản cũ "giống".
Chạy ở gốc repo: git show HEAD:src/propositions.py > <tệp tạm>; python -X utf8 -I utils/llm_runs/compare_prompts.py <tệp tạm>"""
import importlib.util, sys
sys.path.insert(0, "src")
def load(path, name):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
new = load("src/propositions.py", "pn")
old = load(sys.argv[1], "po")
for k in old.PROMPTS:
    print(k, "giống" if old.PROMPTS[k] == new.PROMPTS[k] else "KHÁC")
for k in new.PROMPTS.keys() - old.PROMPTS.keys():
    print(k, "mới")
