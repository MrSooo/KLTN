import sys
sys.path.insert(0, "src")
import llm
print("llm.enabled() =", llm.enabled())
print("LLM_MODEL =", (__import__("os").environ.get("LLM_MODEL", "") or "(unset)"))