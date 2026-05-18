# 打包部署目录（在项目根执行）
#   .\deploy\pack-for-server.ps1
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Out = Join-Path $Root "dist-quatangshi-deploy.zip"

if (-not (Test-Path (Join-Path $Root "index\quatangshi_phase1.jsonl"))) {
    Write-Host "请先运行: python tools/build_phase1_index.py"
    exit 1
}

$staging = Join-Path $env:TEMP "qts-deploy-$(Get-Random)"
New-Item -ItemType Directory -Force -Path $staging | Out-Null

$items = @(
    "deploy",
    "apps/api",
    "apps/web/package.json",
    "apps/web/package-lock.json",
    "apps/web/index.html",
    "apps/web/vite.config.ts",
    "apps/web/tsconfig.json",
    "apps/web/src",
    "tools/corpus_paths.py",
    "tools/sync_postgres.py",
    "tools/build_meilisearch_index.py",
    "index/quatangshi_phase1.jsonl",
    "db/schema.sql",
    "requirements-search.txt"
)

foreach ($rel in $items) {
    $src = Join-Path $Root $rel
    $dst = Join-Path $staging $rel
    if (-not (Test-Path $src)) {
        Write-Host "缺少: $rel"
        exit 1
    }
    $parent = Split-Path $dst -Parent
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    Copy-Item -Recurse -Force $src $dst
}

Compress-Archive -Force -Path (Join-Path $staging "*") -DestinationPath $Out
Remove-Item -Recurse -Force $staging
Write-Host "已生成: $Out"
