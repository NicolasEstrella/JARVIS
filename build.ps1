# Script de Build Automatizado para Jarvis Desktop
# Este script compila todo o projeto e gera o instalador final

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   Jarvis Desktop - Build Automatizado     " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Python
Write-Host "[1/6] Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Python encontrado: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  ❌ Python não encontrado! Instale Python 3.8+" -ForegroundColor Red
    exit 1
}

# 2. Instalar dependências Python
Write-Host ""
Write-Host "[2/6] Instalando dependências Python..." -ForegroundColor Yellow
Push-Location src-python
python -m pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Dependências Python instaladas" -ForegroundColor Green
} else {
    Write-Host "  ❌ Erro ao instalar dependências Python" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

# 3. Gerar executável Python com PyInstaller
Write-Host ""
Write-Host "[3/6] Gerando jarvis_core.exe com PyInstaller..." -ForegroundColor Yellow
Push-Location src-python

# Limpa builds anteriores
if (Test-Path "dist") {
    Remove-Item -Recurse -Force dist
}
if (Test-Path "build") {
    Remove-Item -Recurse -Force build
}

# Executa PyInstaller
pyinstaller --onefile --noconsole main.py --name jarvis_core

if ($LASTEXITCODE -eq 0 -and (Test-Path "dist/jarvis_core.exe")) {
    Write-Host "  [OK] jarvis_core.exe gerado com sucesso" -ForegroundColor Green
    
    # Copia para diretório bin do Tauri
    Pop-Location
    if (!(Test-Path "src-tauri/bin")) {
        New-Item -ItemType Directory -Force -Path "src-tauri/bin" | Out-Null
    }
    Copy-Item "src-python/dist/jarvis_core.exe" -Destination "src-tauri/bin/" -Force
    Write-Host "  [OK] jarvis_core.exe copiado para src-tauri/bin/" -ForegroundColor Green
} else {
    Write-Host "  ❌ Erro ao gerar jarvis_core.exe" -ForegroundColor Red
    Pop-Location
    exit 1
}

# 4. Instalar dependências Node
Write-Host ""
Write-Host "[4/6] Instalando dependências Node..." -ForegroundColor Yellow
npm install --silent
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Dependências Node instaladas" -ForegroundColor Green
} else {
    Write-Host "  ❌ Erro ao instalar dependências Node" -ForegroundColor Red
    exit 1
}

# 5. Build React
Write-Host ""
Write-Host "[5/6] Building frontend React..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Frontend React compilado" -ForegroundColor Green
} else {
    Write-Host "  ❌ Erro ao compilar React" -ForegroundColor Red
    exit 1
}

# 6. Build Tauri
Write-Host ""
Write-Host "[6/6] Building aplicação Tauri..." -ForegroundColor Yellow
Write-Host "  (Isso pode levar alguns minutos...)" -ForegroundColor Gray
npm run tauri build

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "   [OK] Build concluído com sucesso!         " -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Instalador gerado em:" -ForegroundColor Cyan
    Write-Host "  src-tauri/target/release/bundle/nsis/" -ForegroundColor White
    Write-Host ""
    
    # Tenta abrir pasta do instalador
    $bundlePath = "src-tauri\target\release\bundle\nsis"
    if (Test-Path $bundlePath) {
        Write-Host "Abrindo pasta do instalador..." -ForegroundColor Yellow
        explorer.exe $bundlePath
    }
} else {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Red
    Write-Host "   ❌ Erro durante o build do Tauri        " -ForegroundColor Red
    Write-Host "============================================" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Cyan
Write-Host "  1. Teste o instalador gerado" -ForegroundColor White
Write-Host "  2. Execute o Jarvis e verifique funcionalidades" -ForegroundColor White
Write-Host "  3. Distribua o instalador .exe" -ForegroundColor White
Write-Host ""
