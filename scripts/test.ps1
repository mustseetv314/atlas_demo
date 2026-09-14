param([string]$BaseUrl = "http://localhost:8000")
$failed = $false
@("/", "/health/live", "/health/ready", "/api/info", "/api/assets", "/docs") | ForEach-Object {
  try { Invoke-WebRequest -Uri ($BaseUrl.TrimEnd('/') + $_) -UseBasicParsing -ErrorAction Stop | Out-Null; Write-Host "PASS GET $_" }
  catch { Write-Host "FAIL GET $_ - $($_.Exception.Message)"; $failed = $true }
}
if ($failed) { exit 1 }
exit 0
