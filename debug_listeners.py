"""
Script para debug de listeners duplicados
Testa cenários reais de uso onde threads podem acumular
"""
import threading
import time
import sys
import os

# Adiciona o path do projeto
sys.path.append(os.path.join(os.path.dirname(__file__), 'src-python'))

def monitor_threads():
    """Monitora threads ativas"""
    print("=== THREADS ATIVAS ===")
    for thread in threading.enumerate():
        print(f"Thread: {thread.name} - Alive: {thread.is_alive()} - Daemon: {thread.daemon}")
    
    # Monitora thread manager se disponível
    try:
        from utils.thread_manager import get_thread_manager
        manager = get_thread_manager()
        active_workers = manager.get_active_threads()
        print(f"ThreadManager Workers: {active_workers}")
    except:
        pass
    
    print(f"Total de threads: {threading.active_count()}")
    print()

def simulate_wake_word_detection():
    """Simula detecção de wake word e processamento de comando"""
    from core.listener import initialize_wake_word_detection, start_wake_word_listening, stop_wake_word_listening
    from utils.event_emitter import get_event_emitter
    
    print("=== SIMULANDO DETECÇÃO DE WAKE WORD ===")
    
    # Inicializa
    initialize_wake_word_detection()
    start_wake_word_listening()
    monitor_threads()
    
    # Simula wake word detectada
    print("Simulando wake word detectada...")
    emitter = get_event_emitter()
    emitter.emit_wake_word_detected("testar")
    emitter.emit_state_change("listening")
    time.sleep(0.5)
    
    print("Simulando processamento de comando...")
    emitter.emit_state_change("executing", command="bloco de notas")
    time.sleep(1)
    
    print("Simulando finalização...")
    emitter.emit_action_completed("Bloco de notas aberto")
    time.sleep(0.5)
    
    monitor_threads()
    
    # Para escuta
    stop_wake_word_listening()
    time.sleep(1)
    monitor_threads()

def test_multiple_cycles():
    """Testa múltiplos ciclos de wake word -> comando -> finalização"""
    from core.listener import initialize_wake_word_detection, start_wake_word_listening, stop_wake_word_listening, cleanup_wake_word_detection
    from utils.event_emitter import get_event_emitter
    
    print("\n=== TESTANDO MÚLTIPLOS CICLOS ===")
    
    for cycle in range(3):
        print(f"\n--- CICLO #{cycle+1} ---")
        
        # Inicializa e começa escuta
        initialize_wake_word_detection()
        start_wake_word_listening()
        
        emitter = get_event_emitter()
        
        # Simula detecção e processamento
        emitter.emit_wake_word_detected("testar")
        emitter.emit_state_change("listening")
        time.sleep(0.2)
        
        emitter.emit_state_change("executing", command="calculadora")
        time.sleep(0.3)
        
        emitter.emit_action_completed("Calculadora aberta")
        time.sleep(0.2)
        
        # Para escuta
        stop_wake_word_listening()
        time.sleep(0.5)
        
        print(f"Threads após ciclo {cycle+1}:")
        monitor_threads()
    
    print("\n=== LIMPEZA FINAL ===")
    cleanup_wake_word_detection()
    time.sleep(1)
    monitor_threads()

def test_rapid_commands():
    """Testa comandos em sequência rápida (cenário real)"""
    from core.listener import initialize_wake_word_detection, start_wake_word_listening, stop_wake_word_listening
    from utils.event_emitter import get_event_emitter
    
    print("\n=== TESTANDO COMANDOS RÁPIDOS ===")
    
    initialize_wake_word_detection()
    start_wake_word_listening()
    
    emitter = get_event_emitter()
    
    # Simula vários comandos em sequência
    commands = ["bloco de notas", "calculadora", "navegador", "arquivos"]
    
    for i, cmd in enumerate(commands):
        print(f"\nComando {i+1}: {cmd}")
        
        # Wake word -> comando -> execução -> finalização
        emitter.emit_wake_word_detected("testar")
        emitter.emit_state_change("listening")
        time.sleep(0.1)
        
        emitter.emit_state_change("executing", command=cmd)
        time.sleep(0.2)
        
        emitter.emit_action_completed(f"{cmd} executado")
        time.sleep(0.1)
        
        if i == 1:  # Verifica threads no meio do processo
            print(f"Threads no meio do processo:")
            monitor_threads()
    
    print("\nThreads após todos os comandos:")
    monitor_threads()
    
    stop_wake_word_listening()
    time.sleep(1)
    
    print("Threads após parar:")
    monitor_threads()

def test_background_service_simulation():
    """Simula o comportamento do background service"""
    from core.background_service import BackgroundService
    
    print("\n=== TESTANDO BACKGROUND SERVICE ===")
    
    service = BackgroundService()
    
    print("Antes de inicializar:")
    monitor_threads()
    
    service.initialize()
    
    print("Após inicializar:")
    monitor_threads()
    
    # Simula alguns eventos
    service._on_wake_word_detected("testar")
    time.sleep(1)
    
    print("Após wake word:")
    monitor_threads()
    
    service.stop()
    time.sleep(2)
    
    print("Após parar service:")
    monitor_threads()

if __name__ == "__main__":
    print("=== TESTE COMPLETO DE THREADS ===\n")
    
    print("1. Teste básico de listeners...")
    monitor_threads()
    
    print("\n2. Simulação de wake word...")
    simulate_wake_word_detection()
    
    print("\n3. Múltiplos ciclos...")
    test_multiple_cycles()
    
    print("\n4. Comandos rápidos...")
    test_rapid_commands()
    
    print("\n5. Background service...")
    test_background_service_simulation()
    
    print("\n=== TESTE FINALIZADO ===")
    monitor_threads()