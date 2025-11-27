# Script de Teste - Jarvis Background
# Testa se o Jarvis está funcionando em background

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   Teste Jarvis Background Operation       " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar se o processo está rodando
Write-Host "[1/4] Verificando processos..." -ForegroundColor Yellow
python check_jarvis.py

Write-Host ""
Write-Host "[2/4] Testando hotword..." -ForegroundColor Yellow
Write-Host "  💡 Fale 'testar' próximo ao microfone" -ForegroundColor Green
Write-Host "  💡 Se funcionar, deve abrir o Notepad" -ForegroundColor Green
Write-Host "  ⏰ Aguardando 15 segundos..." -ForegroundColor Gray

Start-Sleep -Seconds 15

Write-Host ""
Write-Host "[3/4] Verificando se Notepad foi aberto..." -ForegroundColor Yellow
$notepadProcess = Get-Process -Name "notepad" -ErrorAction SilentlyContinue
if ($notepadProcess) {
    Write-Host "  [OK] Notepad está rodando! Hotword funcionou!" -ForegroundColor Green
    Write-Host "  📋 PIDs: $($notepadProcess.Id -join ', ')" -ForegroundColor Gray
} else {
    Write-Host "  ❌ Notepad não encontrado" -ForegroundColor Red
    Write-Host "  💡 Verifique se o microfone está funcionando" -ForegroundColor Yellow
    Write-Host "  💡 Tente falar 'testar' mais alto e claro" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[4/4] Verificando System Tray..." -ForegroundColor Yellow
Write-Host "  💡 Verifique se há ícone do Jarvis no system tray" -ForegroundColor Green
Write-Host "  💡 Clique com botão direito para ver menu:" -ForegroundColor Green
Write-Host "     - Iniciar Jarvis" -ForegroundColor White
Write-Host "     - Parar Jarvis" -ForegroundColor White
Write-Host "     - Abrir Painel" -ForegroundColor White
Write-Host "     - Sair" -ForegroundColor White

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   Comandos úteis:                          " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  python check_jarvis.py  # Verifica status" -ForegroundColor White
Write-Host "  npm run tauri dev       # Roda em dev" -ForegroundColor White
Write-Host "  PowerShell build.ps1    # Build completo" -ForegroundColor White
Write-Host ""
Write-Host "💡 Se algo não funcionou:" -ForegroundColor Yellow
Write-Host "  1. Verifique se Python está no PATH" -ForegroundColor White
Write-Host "  2. Instale dependências: pip install -r src-python/requirements.txt" -ForegroundColor White
Write-Host "  3. Teste o microfone no Windows" -ForegroundColor White
Write-Host "  4. Verifique o arquivo jarvis.log" -ForegroundColor White