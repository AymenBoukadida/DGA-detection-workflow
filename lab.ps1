param(
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".env")) {
    throw "Missing .env. Copy .env.example to .env and fill the values first."
}

$envText = Get-Content ".env" -Raw
if ($envText -match "CHANGEME") {
    throw ".env still contains CHANGEME placeholders. Fill every value first."
}
New-Item -ItemType Directory -Force -Path "bootstrap/out" | Out-Null

Write-Host "[1/5] Starting the lab stack"
if ($SkipBuild) {
    docker compose up -d --wait
} else {
    docker compose up -d --build --wait
}

Write-Host "[2/5] Bootstrapping Cortex, TheHive and n8n"
docker compose --profile tools run --rm bootstrap
if ($LASTEXITCODE -ne 0) { throw "bootstrap failed" }

Write-Host "[3/5] Importing n8n credentials and workflow"
docker compose stop n8n | Out-Null
docker compose --profile tools run --rm n8n-cli import:credentials --input=/out/credentials.json
if ($LASTEXITCODE -ne 0) { throw "credential import failed" }
docker compose --profile tools run --rm n8n-cli import:workflow --input=/import/dga-workflow.json
if ($LASTEXITCODE -ne 0) { throw "workflow import failed" }
docker compose start n8n | Out-Null

Write-Host "[4/5] Waiting for n8n"
for ($i = 0; $i -lt 40; $i++) {
    try {
        Invoke-WebRequest -UseBasicParsing "http://localhost:5678/healthz" -TimeoutSec 3 | Out-Null
        break
    } catch {
        Start-Sleep -Seconds 3
    }
}

Write-Host "[5/5] Lab ready"
Write-Host "  n8n        http://localhost:5678"
Write-Host "  TheHive    http://localhost:9000/thehive"
Write-Host "  Cortex     http://localhost:9001/cortex"
Write-Host "  ML API     http://localhost:8000/docs"
Write-Host "  MailHog    http://localhost:8025"
