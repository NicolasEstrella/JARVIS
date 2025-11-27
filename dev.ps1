# Script de Development - Inicia Jarvis em modo desenvolvimento

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   Jarvis Desktop - Modo Desenvolvimento   " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verifica Node
Write-Host "Verificando Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Node.js: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "  ❌ Node.js não encontrado!" -ForegroundColor Red
    exit 1
}

# Verifica Python
Write-Host "Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Python: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  ❌ Python não encontrado!" -ForegroundColor Red
    exit 1
}

# Instala dependências se necessário
if (!(Test-Path "node_modules")) {
    Write-Host ""
    Write-Host "Instalando dependências Node..." -ForegroundColor Yellow
    npm install
}

Write-Host ""
Write-Host "Iniciando Jarvis em modo desenvolvimento..." -ForegroundColor Green
Write-Host "(Pressione Ctrl+C para parar)" -ForegroundColor Gray
Write-Host ""

# Inicia Tauri dev
npm run tauri dev
