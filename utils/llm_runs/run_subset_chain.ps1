# Chạy cả chuỗi 7 hộp cát của tập con lldnn cho một lần chạy (A50-A52). Dùng: powershell -File utils/llm_runs/run_subset_chain.ps1 <run> <thư mục làm việc ngoài repo> [mode]
# Thư mục làm việc phải nằm ngoài repo (A36, docs/operations/llm_sandbox.md); log và cache vẫn ghi theo đường của repo.
# Mỗi hộp cát: xuat -> sandbox_api (lô lỗi thì chạy lại, tối đa 3 lần) -> nhap; giữa các bước replay tập con. nhap lỗi thì dừng cả chuỗi.
# tu_so_vi_tu: bỏ mọi bước 1.6A, 1.6B, 1.7 (đã nhập), chạy từ sổ vị từ 2.6 đến hết.
# tu_1_6b: bỏ 1.6A gốc (đã có cache), chạy tiếp từ 1.6B gốc đến hết.
# chi_1_6a: chỉ chạy hai hộp cát 1.6A (gốc và cập nhật). Chế độ này hỏng: xuat-1-6a của cập nhật cần sổ vị từ 1.6B của lần chạy (A51, status nợ 18).
param([string]$run, [string]$root, [string]$mode = "du")
$ErrorActionPreference = "Continue"
Set-Location "C:\Users\TusPC\Documents\kltn"
$env:KLTN_LLM_RUN = $run; $env:KLTN_TAP_CON = "lldnn"
$env:CKEY_API_KEY = [Environment]::GetEnvironmentVariable("CKEY_API_KEY", "User")
New-Item -ItemType Directory -Force $root | Out-Null
$log = Join-Path $root "chuoi.log"
function Write-Log($m) { $line = "$(Get-Date -Format 'HH:mm:ss') $m"; $line | Out-File -Append -Encoding utf8 $log; $line }
function Invoke-Replay($tag) {
    python -X utf8 -I src/run_all.py --tap-con lldnn --llm-run $run --llm replay *> (Join-Path $root "replay_$tag.log")
    Write-Log "replay ${tag}: ma thoat $LASTEXITCODE"
}
function Invoke-Api($name) {
    $d = Join-Path $root $name
    foreach ($i in 1, 2, 3) {
        $t0 = Get-Date
        python -X utf8 -I src/sandbox_api.py $d *> (Join-Path $root "api_${name}_$i.log")
        $code = $LASTEXITCODE
        Write-Log "$name sandbox_api lan ${i}: ma thoat $code, $([int]((Get-Date) - $t0).TotalSeconds)s"
        if ($code -eq 0) { break }
    }
}
function Test-Nhap($name, $out) {
    Write-Log "$name nhap (ma $LASTEXITCODE): $((($out | Out-String).Trim() -split "`n" | Select-Object -Last 3) -join ' | ')"
    if ($LASTEXITCODE -ne 0) { Write-Log "DUNG o $name"; exit 1 }
}
Write-Log "bat dau chuoi $run ($mode)"
Invoke-Replay "0"

if ($mode -ne "tu_so_vi_tu") {
if ($mode -ne "tu_1_6b") {
$d = Join-Path $root "b1_6a"
Write-Log ("b1_6a xuat: " + (python -X utf8 -I src/propositions.py xuat $d deepseek-v4.1-flash khong_co --tat-ca 2>&1 | Out-String).Trim())
Invoke-Api "b1_6a"
$o = python -X utf8 -I src/propositions.py nhap $d 2>&1; Test-Nhap "b1_6a" $o
Invoke-Replay "1"
}

if ($mode -ne "chi_1_6a") {
    $d = Join-Path $root "b1_6b"
    Write-Log ("b1_6b xuat: " + (python -X utf8 -I src/predicates.py --xuat $d 2>&1 | Out-String).Trim())
    Invoke-Api "b1_6b"
    $o = python -X utf8 -I src/predicates.py --nhap $d 2>&1; Test-Nhap "b1_6b" $o
    Invoke-Replay "2"

    $d = Join-Path $root "b1_7"
    Write-Log ("b1_7 xuat: " + (python -X utf8 -I src/implicit_exceptions.py xuat $d 2>&1 | Out-String).Trim())
    Invoke-Api "b1_7"
    $o = python -X utf8 -I src/implicit_exceptions.py nhap $d 2>&1; Test-Nhap "b1_7" $o
    Invoke-Replay "3"
}

$d = Join-Path $root "u1_6a"
Write-Log ("u1_6a xuat: " + (python -X utf8 -I src/update.py xuat-1-6a $d 2>&1 | Out-String).Trim())
Invoke-Api "u1_6a"
$o = python -X utf8 -I src/update.py nhap-1-6a $d 2>&1; Test-Nhap "u1_6a" $o
Invoke-Replay "4"
}
if ($mode -eq "chi_1_6a") { Write-Log "XONG ($mode)"; exit 0 }

$d = Join-Path $root "so_vi_tu"
Write-Log ("so_vi_tu xuat: " + (python -X utf8 -I src/predicate_registry.py --xuat $d 2>&1 | Out-String).Trim())
Invoke-Api "so_vi_tu"
$o = python -X utf8 -I src/predicate_registry.py --nhap $d 2>&1; Test-Nhap "so_vi_tu" $o
Invoke-Replay "5"

$d = Join-Path $root "u1_7"
Write-Log ("u1_7 xuat: " + (python -X utf8 -I src/update.py xuat-1-7 $d 2>&1 | Out-String).Trim())
Invoke-Api "u1_7"
$o = python -X utf8 -I src/update.py nhap-1-7 $d 2>&1; Test-Nhap "u1_7" $o
Invoke-Replay "6"

$d = Join-Path $root "u1_9"
Write-Log ("u1_9 xuat: " + (python -X utf8 -I src/answering.py xuat $d 2>&1 | Out-String).Trim())
Invoke-Api "u1_9"
$o = python -X utf8 -I src/answering.py nhap $d 2>&1; Test-Nhap "u1_9" $o
python -X utf8 -I src/run_all.py --tap-con lldnn --llm-run $run --llm replay --viewer *> (Join-Path $root "replay_7.log")
Write-Log "replay 7 (viewer): ma thoat $LASTEXITCODE"
Write-Log "XONG ($mode)"
