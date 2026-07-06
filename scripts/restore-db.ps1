# Restore from data/dumps/latest.sql.gz (wipes data/postgres first)
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path $PSScriptRoot -Parent
$Dump = Join-Path $ProjectRoot "data\dumps\latest.sql.gz"
$PgData = Join-Path $ProjectRoot "data\postgres"

if (-not (Test-Path $Dump)) {
  Write-Error "Dump not found: $Dump"
}

Write-Host "Stopping postgres..."
docker compose -f (Join-Path $ProjectRoot "docker-compose.yml") stop postgres

Write-Host "Removing PG data directory..."
if (Test-Path $PgData) { Remove-Item -Recurse -Force $PgData }
New-Item -ItemType Directory -Force -Path $PgData | Out-Null
Copy-Item (Join-Path $ProjectRoot "data\postgres\.gitkeep") (Join-Path $PgData ".gitkeep") -ErrorAction SilentlyContinue

Write-Host "Starting postgres (init will restore from dump)..."
docker compose -f (Join-Path $ProjectRoot "docker-compose.yml") up postgres -d

Write-Host "Done. Database will restore on first init."