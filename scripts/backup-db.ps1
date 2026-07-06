# Backup PostgreSQL to data/dumps/latest.sql.gz
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path $PSScriptRoot -Parent
$DumpsDir = Join-Path $ProjectRoot "data\dumps"
New-Item -ItemType Directory -Force -Path $DumpsDir | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$latest = Join-Path $DumpsDir "latest.sql.gz"
$archive = Join-Path $DumpsDir "svinopass_$timestamp.sql.gz"

Write-Host "Creating backup..."
docker compose -f (Join-Path $ProjectRoot "docker-compose.yml") exec -T postgres `
  pg_dump -U svinopass -d svinopass --no-owner --no-acl | gzip > $latest

Copy-Item $latest $archive -Force
Write-Host "Saved: $latest"
Write-Host "Archive: $archive"