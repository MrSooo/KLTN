#!/bin/zsh
# Dùng: utils/llm_runs/run_sandbox_retry.sh <thư mục hộp cát ngoài repo>   (KLTN_LLM_RUN mặc định tach2; log ở <thư mục>_run.log)
# Chạy sandbox_api cho một hộp cát (A63, 27/11). Lỗi TUYẾN (5xx, 429, mạng, quá trần SSE) -> nghỉ 60 giây, gọi thử tuyến bằng lời nhắn
# ngắn (utils/llm_runs/probe_route.py) mỗi 60 giây đến khi sống rồi chạy tiếp. 10 lần lỗi liền thì dừng hẳn; lỗi khác dừng ngay.
# Cần CKEY_API_KEY trong môi trường (Mac: ~/.zshenv).
R=$(cd "$(dirname "$0")/../.." && pwd)
D=${1:?thiếu thư mục hộp cát}
L="${D%/}_run.log"
cd "$R"
export KLTN_LLM_RUN=${KLTN_LLM_RUN:-tach2}
while pgrep -f "Python -X utf8 -I src/sandbox_api.py" >/dev/null; do sleep 5; done
fails=0
while true; do
  before=$(ls "$D/out" | wc -l)
  .venv/bin/python -X utf8 -I src/sandbox_api.py "$D" >> "$L" 2>&1
  [ $? -eq 0 ] && { echo "$(date +%T) XONG (mã 0)" >> "$L"; exit 0; }
  last=$(grep 'DỪNG' "$L" | tail -1)
  if ! echo "$last" | grep -q -E 'lỗi API: (API (lỗi (5[0-9][0-9]|429)|lỗi kết nối)|luồng SSE)'; then
    echo "$(date +%T) DỪNG HẲN (không phải lỗi tuyến): $last" >> "$L"; exit 1
  fi
  after=$(ls "$D/out" | wc -l)
  [ $after -gt $before ] && fails=0
  while true; do
    fails=$((fails+1))
    [ $fails -ge 10 ] && { echo "$(date +%T) DỪNG HẲN: lỗi tuyến $fails lần liền" >> "$L"; exit 1; }
    echo "$(date +%T) lỗi tuyến (lần liền $fails/10), nghỉ 60 giây rồi gọi thử tuyến" >> "$L"
    sleep 60
    r=$(.venv/bin/python -I utils/llm_runs/probe_route.py "$R" 2>&1); rc=$?
    echo "$(date +%T) $r" >> "$L"
    [ $rc -eq 0 ] && break
  done
done
