#!/usr/bin/env python3
"""
Script de teste para verificar a comunicação IPC Python → Tauri
"""

import sys
import os

# Adiciona o diretório src-python ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src-python'))

from utils.event_emitter import emit_wake_word, emit_command, emit_action, emit_completed

def test_ipc_events():
    """Testa todos os tipos de eventos IPC"""
    print("🧪 Iniciando teste de eventos IPC...")
    
    # Teste 1: Wake Word
    print("\n1. Testando wake word...")
    emit_wake_word("jarvis")
    
    import time
    time.sleep(2)
    
    # Teste 2: Command 
    print("2. Testando comando...")
    emit_command("abrir navegador")
    
    time.sleep(2)
    
    # Teste 3: Action Execution
    print("3. Testando execução de ação...")
    emit_action("open_app", "abrir navegador")
    
    time.sleep(2)
    
    # Teste 4: Completion
    print("4. Testando conclusão...")
    emit_completed("open_app", True)
    
    time.sleep(1)
    
    print("\n✅ Teste de eventos IPC concluído!")
    print("Verifique se o overlay apareceu na interface do Jarvis")

if __name__ == "__main__":
    test_ipc_events()