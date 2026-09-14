$ErrorActionPreference = "Stop"
$python = Get-Command python -ErrorAction Stop
$versionText = & $python.Source -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$parts = $versionText.Split('.')
if ([int]$parts[0] -lt 3 -or ([int]$parts[0] -eq 3 -and [int]$parts[1] -lt 12)) { throw "Python 3.12 or later is required." }
if (-not (Test-Path ".venv")) { & $python.Source -m venv .venv }
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if (-not (Test-Path ".env")) { Copy-Item .env.example .env; Write-Host "Created .env; update its SQL Server credentials." }
Write-Host "Setup complete. Run .\scripts\run.ps1 after configuring .env."
