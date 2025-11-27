"""
Serviço em background para o Jarvis Assistant
Executa o Jarvis como daemon/thread em segundo plano

Funcionalidades:
- Execução contínua como thread daemon
- Auto-restart em caso de falhas
- Controle de inicialização/parada
- Logging de estado do serviço
"""

import threading
import time
import signal
import sys
from typing import Optional
from core.listener import (
    initialize_wake_word_detection, 
    set_wake_word_callback, 
    start_wake_word_listening,
    stop_wake_word_listening,
    cleanup_wake_word_detection
)
from core.speech_to_text import (
    initialize_speech_recognition,
    listen_and_transcribe,
    cleanup_speech_recognition
)
from core.command_handler import process_voice_input, is_jarvis_active
from core.workflow_engine import initialize_workflow_engine, cleanup_workflow_engine
from utils.logger import log_info, log_error, log_debug
from utils.audio_utils import test_microphone

class BackgroundService:
    """
    Serviço principal do Jarvis em background
    """
    
    def __init__(self):
        self.is_running = False
        self.service_thread: Optional[threading.Thread] = None
        self.restart_count = 0
        self.max_restarts = 5
        self.restart_delay = 10  # segundos
        self.continuous_mode = False  # Modo de escuta contínua
        self.continuous_timeout = 10  # Timeout para modo contínuo
        
    def initialize(self) -> bool:
        """
        Inicializa todos os componentes necessários
        
        Returns:
            bool: True se inicializou com sucesso
        """
        log_info("[INFO] Inicializando componentes do Jarvis...")
        
        # Testa microfone
        if not test_microphone():
            log_error("[ERRO] Microfone não está funcionando")
            return False
        
        # Inicializa workflow engine
        if not initialize_workflow_engine():
            log_error("[ERRO] Falha ao inicializar workflow engine")
            return False
        
        # Inicializa reconhecimento de fala
        if not initialize_speech_recognition():
            log_error("[ERRO] Falha ao inicializar reconhecimento de fala")
            return False
        
        # Inicializa detecção de wake word (100% gratuita)
        if not initialize_wake_word_detection():
            log_error("[ERRO] Falha ao inicializar detecção de wake word")
            return False
        
        # Define callback para wake word
        set_wake_word_callback(self._on_wake_word_detected)
        
        log_info("[OK] Todos os componentes inicializados com sucesso")
        return True
    
    def _on_wake_word_detected(self, keyword: str) -> None:
        """
        Callback chamado quando wake word é detectada
        
        Args:
            keyword (str): Palavra-chave detectada
        """
        log_info(f"[OK] Wake word detectada: '{keyword}' - Ativando Jarvis!")
        
        # Para temporariamente a escuta de wake word
        stop_wake_word_listening()
        
        # Entra em modo de escuta contínua
        self.continuous_mode = True
        self._continuous_listening_mode()
    
    def _continuous_listening_mode(self) -> None:
        """
        Modo de escuta contínua - escuta comandos sem precisar repetir wake word
        """
        log_info("[AUDIO] Modo escuta contínua ativado - fale seus comandos!")
        log_info("[INFO] Comandos: 'codigo', 'calculadora', 'copiar', 'colar', etc.")
        log_info("[INFO] Para parar: 'parar', 'sair', 'tchau' ou 'para a porra toda'")
        log_info("[INFO] Para reiniciar: 'reiniciar'")
        
        while self.continuous_mode and self.is_running:
            try:
                # Escuta comando com timeout
                text = listen_and_transcribe(timeout=self.continuous_timeout)
                
                if text:
                    log_info(f"[INFO] Comando recebido: '{text}'")
                    
                    # Verifica comandos de finalização
                    text_lower = text.lower()
                    
                    # Comando especial para parar tudo
                    if "para a porra toda" in text_lower:
                        log_info("[INFO] Comando 'para a porra toda' detectado - PARANDO TUDO!")
                        self.continuous_mode = False
                        self.stop()
                        return
                    
                    # Comandos normais de parada
                    if any(cmd in text_lower for cmd in ["parar", "finalizar", "sair", "tchau", "obrigado"]):
                        log_info("[INFO] Comando de finalização detectado - saindo do modo contínuo")
                        self.continuous_mode = False
                        break
                    
                    # Comando de reiniciar
                    if "reiniciar" in text_lower:
                        log_info("[INFO] Comando de reinicialização detectado")
                        self.continuous_mode = False
                        # Processa o comando de reiniciar
                        process_voice_input(text)
                        return
                    
                    # Processa comando normalmente
                    process_voice_input(text)
                    
                    # Pequena pausa para evitar sobreposição
                    time.sleep(0.5)
                    
                else:
                    # Timeout - sai do modo contínuo
                    log_info(f"[INFO] Timeout de {self.continuous_timeout}s - saindo do modo contínuo")
                    self.continuous_mode = False
                    break
                    
            except Exception as e:
                log_error(f"Erro no modo contínuo: {e}")
                self.continuous_mode = False
                break
        
        # Verifica se Jarvis ainda deve estar ativo
        if is_jarvis_active() and self.is_running:
            # Reinicia escuta de wake word após modo contínuo (usando thread manager)
            log_debug("[INFO] Saindo do modo contínuo - reiniciando escuta de wake word...")
            from utils.thread_manager import submit_delayed_task
            submit_delayed_task(1.0, self._restart_wake_word_listening)
        else:
            log_info("  Jarvis foi desativado")
            self.stop()
    
    def _restart_wake_word_listening(self) -> None:
        """Reinicia escuta de wake word após pequeno delay"""
        try:
            if self.is_running:
                log_debug("[INFO] Reiniciando escuta de wake word...")
                start_wake_word_listening()
        except Exception as e:
            log_error(f"Erro ao reiniciar escuta: {e}")
    
    def _service_loop(self) -> None:
        """Loop principal do serviço em background"""
        log_info("Jarvis Assistant iniciado em background")
        log_info("Aguardando wake word 'jarvis'...")
        
        try:
            # Inicia escuta de wake word
            start_wake_word_listening()
            
        except Exception as e:
            log_error(f"[ERRO] Erro no loop principal: {e}")
            
            # Tenta reiniciar se não atingiu limite
            if self.restart_count < self.max_restarts:
                self.restart_count += 1
                log_info(f"[INFO] Tentando reiniciar ({self.restart_count}/{self.max_restarts}) em {self.restart_delay}s...")
                time.sleep(self.restart_delay)
                
                if self.is_running:
                    self._service_loop()
            else:
                log_error(f"[ERRO] Limite de reinicializações atingido ({self.max_restarts})")
                self.stop()
    
    def start(self) -> bool:
        """
        Inicia o serviço em background
        
        Returns:
            bool: True se iniciou com sucesso
        """
        if self.is_running:
            log_info("[WARN] Serviço já está rodando")
            return True
        
        if not self.initialize():
            return False
        
        self.is_running = True
        self.restart_count = 0
        
        # Cria thread daemon para o serviço
        self.service_thread = threading.Thread(
            target=self._service_loop,
            daemon=True,
            name="JarvisBackgroundService"
        )
        
        self.service_thread.start()
        log_info("  Serviço Jarvis iniciado como thread daemon")
        
        # Configura handlers para sinais de sistema
        self._setup_signal_handlers()
        
        return True
    
    def stop(self) -> None:
        """Para o serviço"""
        if not self.is_running:
            return
        
        log_info("  Parando serviço Jarvis...")
        self.is_running = False
        self.continuous_mode = False  # Para modo contínuo também
        
        # Para escuta de wake word
        stop_wake_word_listening()
        
        # Limpa recursos
        cleanup_wake_word_detection()
        cleanup_speech_recognition()
        cleanup_workflow_engine()
        
        log_info("[OK] Serviço Jarvis parado")
    
    def set_continuous_timeout(self, timeout_seconds: int) -> None:
        """
        Ajusta o timeout do modo contínuo
        
        Args:
            timeout_seconds (int): Timeout em segundos (padrão: 10)
        """
        self.continuous_timeout = max(5, timeout_seconds)
        log_info(f"[INFO] Timeout do modo contínuo ajustado para {self.continuous_timeout}s")
    
    def is_service_running(self) -> bool:
        """
        Verifica se o serviço está rodando
        
        Returns:
            bool: True se rodando
        """
        return self.is_running
    
    def wait_for_completion(self) -> None:
        """Aguarda o serviço terminar (para execução não-daemon)"""
        if self.service_thread and self.service_thread.is_alive():
            try:
                while self.is_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                log_info("[INFO] Interrupção do usuário detectada")
                self.stop()
    
    def _setup_signal_handlers(self) -> None:
        """Configura handlers para sinais do sistema"""
        def signal_handler(signum, frame):
            log_info(f"[INFO] Sinal {signum} recebido - parando Jarvis...")
            self.stop()
            sys.exit(0)
        
        # Configura handlers para sinais comuns
        try:
            signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
            signal.signal(signal.SIGTERM, signal_handler)  # Terminação
            
            # Windows específico
            if hasattr(signal, 'SIGBREAK'):
                signal.signal(signal.SIGBREAK, signal_handler)
                
        except Exception as e:
            log_debug(f"Não foi possível configurar alguns signal handlers: {e}")

# Instância global do serviço
background_service = BackgroundService()

def start_background_service() -> bool:
    """
    Inicia o serviço Jarvis em background
    
    Returns:
        bool: True se iniciou com sucesso
    """
    if background_service.start():
        # Mantém o programa rodando
        try:
            background_service.wait_for_completion()
        except KeyboardInterrupt:
            log_info("[INFO] Finalizando Jarvis Assistant...")
        finally:
            background_service.stop()
        return True
    return False

def stop_background_service() -> None:
    """Para o serviço em background"""
    background_service.stop()

def is_service_running() -> bool:
    """
    Verifica se o serviço está rodando
    
    Returns:
        bool: True se rodando
    """
    return background_service.is_service_running()

def restart_service() -> bool:
    """
    Reinicia o serviço
    
    Returns:
        bool: True se reiniciou com sucesso
    """
    log_info("[INFO] Reiniciando serviço Jarvis...")
    stop_background_service()
    time.sleep(2)
    return start_background_service()