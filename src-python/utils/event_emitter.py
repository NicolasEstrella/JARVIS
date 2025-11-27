"""
Sistema de eventos para comunicação com interface Tauri
Emite eventos quando estados do Jarvis mudam
"""

import json
import time
import threading
import queue
from typing import Optional, Dict, Any
from utils.logger import log_info, log_debug, log_error

class JarvisEventEmitter:
    """
    Emite eventos para a interface Tauri sobre mudanças de estado do Jarvis
    """
    
    def __init__(self):
        self.current_state = "idle"
        self.current_command = None
        self.current_action = None
        
        # Implementa sender único para evitar múltiplas threads
        self.event_queue = queue.Queue()
        self.sender_thread = None
        self._start_sender_thread()
        
    def _start_sender_thread(self):
        """Inicia thread única para envio de eventos"""
        if self.sender_thread and self.sender_thread.is_alive():
            return
            
        self.sender_thread = threading.Thread(
            target=self._event_sender_worker,
            daemon=True,
            name="EventSender"
        )
        self.sender_thread.start()
        
    def _event_sender_worker(self):
        """Worker thread que processa fila de eventos"""
        while True:
            try:
                # Pega evento da fila (bloqueia até ter algo)
                event_name, data = self.event_queue.get(timeout=1.0)
                self._send_single_event(event_name, data)
                self.event_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                log_error(f"Erro no worker de eventos: {e}")
                
    def _send_single_event(self, event_name: str, data: Dict[str, Any]):
        """Envia um único evento via socket"""
        try:
            import socket
            
            # Conecta ao servidor Tauri (se estiver rodando)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.0)  # Timeout de 1 segundo
            
            # Tenta conectar no localhost:45678
            sock.connect(('localhost', 45678))
            
            # Prepara mensagem JSON
            message = {
                "event": event_name,
                "data": data,
                "timestamp": data.get("timestamp", int(time.time() * 1000))
            }
            
            # Envia dados
            message_str = json.dumps(message) + "\n"
            sock.send(message_str.encode('utf-8'))
            
            log_debug(f"[IPC] Evento enviado: {event_name}")
            sock.close()
            
        except ConnectionRefusedError:
            # Tauri não está rodando ou servidor IPC não iniciado
            log_debug(f"[IPC] Tauri não conectado - evento ignorado: {event_name}")
        except Exception as e:
            log_debug(f"[IPC] Erro ao enviar evento {event_name}: {e}")
        
    def emit_state_change(self, status: str, command: Optional[str] = None, action: Optional[str] = None) -> None:
        """
        Emite evento de mudança de estado
        
        Args:
            status: Estado atual ('waiting', 'listening', 'executing', 'hidden')
            command: Comando sendo processado (opcional)
            action: Ação sendo executada (opcional)
        """
        try:
            self.current_state = status
            self.current_command = command
            self.current_action = action
            
            event_data = {
                "status": status,
                "timestamp": int(time.time() * 1000)
            }
            
            if command:
                event_data["command"] = command
            if action:
                event_data["action"] = action
            
            # TODO: Implementar comunicação real com Tauri via IPC
            # Por enquanto, apenas log para debug
            log_debug(f"[EVENT] State changed: {json.dumps(event_data)}")
            
            # TODO: Emitir via processo/pipe para Tauri
            self._emit_to_tauri("jarvis-state-changed", event_data)
            
        except Exception as e:
            log_error(f"Erro ao emitir evento de estado: {e}")
    
    def emit_wake_word_detected(self, keyword: str) -> None:
        """
        Emite evento quando wake word é detectada
        
        Args:
            keyword: Palavra-chave detectada
        """
        try:
            event_data = {
                "keyword": keyword,
                "timestamp": int(time.time() * 1000)
            }
            
            log_debug(f"[EVENT] Wake word detected: {keyword}")
            self._emit_to_tauri("jarvis-wake-word", event_data)
            
            # Atualiza estado para listening
            self.emit_state_change("listening")
            
        except Exception as e:
            log_error(f"Erro ao emitir evento de wake word: {e}")
    
    def emit_command_received(self, command: str) -> None:
        """
        Emite evento quando comando é recebido
        
        Args:
            command: Comando de voz recebido
        """
        try:
            event_data = {
                "command": command,
                "timestamp": int(time.time() * 1000)
            }
            
            log_debug(f"[EVENT] Command received: {command}")
            self._emit_to_tauri("jarvis-command", event_data)
            
            # Atualiza estado para executing ao invés de processing
            self.emit_state_change("executing", command=command)
            
        except Exception as e:
            log_error(f"Erro ao emitir evento de comando: {e}")
    
    def emit_action_executing(self, action: str, command: Optional[str] = None) -> None:
        """
        Emite evento quando ação está sendo executada
        
        Args:
            action: Ação sendo executada
            command: Comando original (opcional)
        """
        try:
            event_data = {
                "action": action,
                "timestamp": int(time.time() * 1000)
            }
            
            if command:
                event_data["command"] = command
            
            log_debug(f"[EVENT] Action executing: {action}")
            self._emit_to_tauri("jarvis-action-executing", event_data)
            
            # Atualiza estado para executing
            self.emit_state_change("executing", command=command, action=action)
            
        except Exception as e:
            log_error(f"Erro ao emitir evento de ação: {e}")
    
    def emit_action_completed(self, action: str, success: bool = True) -> None:
        """
        Emite evento quando ação é completada
        
        Args:
            action: Ação completada
            success: Se foi bem-sucedida
        """
        try:
            event_data = {
                "action": action,
                "success": success,
                "timestamp": int(time.time() * 1000)
            }
            
            log_debug(f"[EVENT] Action completed: {action} (success: {success})")
            self._emit_to_tauri("jarvis-action-completed", event_data)
            
            # Volta para waiting após completar
            self.emit_state_change("waiting")
            
        except Exception as e:
            log_error(f"Erro ao emitir evento de conclusão: {e}")
    
    def emit_jarvis_started(self) -> None:
        """Emite evento quando Jarvis é iniciado"""
        try:
            event_data = {
                "status": "started",
                "timestamp": int(time.time() * 1000)
            }
            
            log_info("[EVENT] Jarvis started")
            self._emit_to_tauri("jarvis-started", event_data)
            self.emit_state_change("idle")
            
        except Exception as e:
            log_error(f"Erro ao emitir evento de início: {e}")
    
    def emit_jarvis_stopped(self) -> None:
        """Emite evento quando Jarvis é parado"""
        try:
            event_data = {
                "status": "stopped",
                "timestamp": int(time.time() * 1000)
            }
            
            log_info("[EVENT] Jarvis stopped")
            self._emit_to_tauri("jarvis-stopped", event_data)
            
        except Exception as e:
            log_error(f"Erro ao emitir evento de parada: {e}")
    
    def _emit_to_tauri(self, event_name: str, data: Dict[str, Any]) -> None:
        """
        Emite evento para a interface Tauri via fila de eventos
        
        Args:
            event_name: Nome do evento
            data: Dados do evento
        """
        try:
            # Adiciona evento na fila para ser processado pela thread única
            self.event_queue.put((event_name, data), block=False)
            
        except queue.Full:
            log_error(f"Fila de eventos cheia - evento {event_name} ignorado")
        except Exception as e:
            log_error(f"Erro na comunicação IPC: {e}")
    
    def _emit_via_named_pipe(self, event_name: str, data: Dict[str, Any]) -> None:
        """TODO: Implementar emissão via named pipe"""
        pass
    
    def _emit_via_socket(self, event_name: str, data: Dict[str, Any]) -> None:
        """TODO: Implementar emissão via socket local"""
        pass
    
    def _emit_via_file(self, event_name: str, data: Dict[str, Any]) -> None:
        """TODO: Implementar emissão via arquivo temporário"""
        pass
    
    def get_current_state(self) -> Dict[str, Any]:
        """Retorna estado atual"""
        return {
            "status": self.current_state,
            "command": self.current_command,
            "action": self.current_action,
            "timestamp": int(time.time() * 1000)
        }

# Instância global do emissor de eventos
_event_emitter_instance = None

def get_event_emitter() -> JarvisEventEmitter:
    """Retorna instância singleton do emissor de eventos"""
    global _event_emitter_instance
    if _event_emitter_instance is None:
        _event_emitter_instance = JarvisEventEmitter()
    return _event_emitter_instance

# Para compatibilidade, mantém instância global
event_emitter = get_event_emitter()

def emit_wake_word(keyword: str) -> None:
    """Função conveniente para emitir wake word"""
    event_emitter.emit_wake_word_detected(keyword)

def emit_command(command: str) -> None:
    """Função conveniente para emitir comando"""
    event_emitter.emit_command_received(command)

def emit_action(action: str, command: Optional[str] = None) -> None:
    """Função conveniente para emitir ação"""
    event_emitter.emit_action_executing(action, command)

def emit_completed(action: str, success: bool = True) -> None:
    """Função conveniente para emitir conclusão"""
    event_emitter.emit_action_completed(action, success)

def emit_jarvis_started() -> None:
    """Função conveniente para emitir início"""
    event_emitter.emit_jarvis_started()

def emit_jarvis_stopped() -> None:
    """Função conveniente para emitir parada"""
    event_emitter.emit_jarvis_stopped()