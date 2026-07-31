# daily-backup.ps1 — auto-commit + push lovely/ to GitHub (PorNitcha/PorNitcha)
# Scheduled via Windows Task Scheduler at 08:00 daily.

$repoPath = "C:\Users\NitchaSuwongtham\OneDrive - THAIWAH\Desktop\lovely"
$logPath  = Join-Path $repoPath ".claude\backup-log.txt"
$gitExe   = "C:\Users\NitchaSuwongtham\AppData\Local\Programs\Git\cmd\git.exe"

function Write-Log($msg) {
    $msg | Out-File -FilePath $logPath -Append -Encoding utf8
}

try {
    Set-Location -Path $repoPath -ErrorAction Stop

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Log "[$timestamp] Starting backup..."

    if (-not (Test-Path $gitExe)) {
        $gitCmd = Get-Command git -ErrorAction SilentlyContinue
        if ($gitCmd) { $gitExe = $gitCmd.Source }
    }
    Write-Log "[$timestamp] Using git: $gitExe"

    & $gitExe -C $repoPath add -A 2>&1 | ForEach-Object { Write-Log $_ }

    $status = & $gitExe -C $repoPath status --porcelain
    if ([string]::IsNullOrWhiteSpace($status)) {
        Write-Log "[$timestamp] No changes to back up."
    } else {
        & $gitExe -C $repoPath commit -m "Auto backup $timestamp" 2>&1 | ForEach-Object { Write-Log $_ }
        & $gitExe -C $repoPath push origin main 2>&1 | ForEach-Object { Write-Log $_ }
        Write-Log "[$timestamp] Backup pushed to GitHub."
    }
} catch {
    Write-Log "[$timestamp] ERROR: $($_.Exception.Message)"
}
