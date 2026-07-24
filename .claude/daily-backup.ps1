# daily-backup.ps1 — auto-commit + push lovely/ to GitHub (PorNitcha/PorNitcha)
# Scheduled via Windows Task Scheduler at 08:00 daily.

$repoPath = "C:\Users\NitchaSuwongtham\OneDrive - THAIWAH\Desktop\lovely"
$logPath  = Join-Path $repoPath ".claude\backup-log.txt"

Set-Location $repoPath

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"[$timestamp] Starting backup..." | Out-File -FilePath $logPath -Append -Encoding utf8

git add -A 2>&1 | Out-File -FilePath $logPath -Append -Encoding utf8

$status = git status --porcelain
if ([string]::IsNullOrWhiteSpace($status)) {
    "[$timestamp] No changes to back up." | Out-File -FilePath $logPath -Append -Encoding utf8
} else {
    git commit -m "Auto backup $timestamp" 2>&1 | Out-File -FilePath $logPath -Append -Encoding utf8
    git push origin main 2>&1 | Out-File -FilePath $logPath -Append -Encoding utf8
    "[$timestamp] Backup pushed to GitHub." | Out-File -FilePath $logPath -Append -Encoding utf8
}
