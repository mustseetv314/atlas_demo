$ErrorActionPreference = "Stop"
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) { throw "Run .\scripts\setup.ps1 first." }
& .\.venv\Scripts\Activate.ps1
if (Test-Path ".env") {
  Get-Content .env | Where-Object { $_ -match '^\s*[^#][^=]*=' } | ForEach-Object {
    $name, $value = $_ -split '=', 2
    [Environment]::SetEnvironmentVariable($name.Trim(), $value.Trim(), "Process")
  }
}
$hostAddress = if ($env:APP_HOST) { $env:APP_HOST } else { "0.0.0.0" }
$port = if ($env:APP_PORT) { $env:APP_PORT } else { "8000" }
Write-Host @"
Atlas is running.

Application: http://localhost:$port
Liveness:   http://localhost:$port/health/live
Readiness:  http://localhost:$port/health/ready
Assets API: http://localhost:$port/api/assets
Swagger:    http://localhost:$port/docs
"@
python -m uvicorn app.main:app --host $hostAddress --port $port
