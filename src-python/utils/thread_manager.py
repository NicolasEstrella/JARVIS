"""
Sistema de gerenciamento de threads para evitar proliferação
Pool de threads controlado para operações de background
"""

import threading
import queue
import time
from typing import Callable, Any, Optional
from utils.logger import log_debug, log_error, log_warning

class ThreadManager:
    """
    Gerenciador centralizado de threads para evitar proliferação
    Usa um pool de workers para executar tarefas em background
    """
    
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.task_queue = queue.Queue()
        self.workers = []
        self.running = True
        self._start_workers()
    
    def _start_workers(self):
        """Inicia workers do pool de threads"""
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker,
                daemon=True,
                name=f"ThreadManager-Worker-{i+1}"
            )
            worker.start()
            self.workers.append(worker)
        
        log_debug(f"ThreadManager iniciado com {self.max_workers} workers")
    
    def _worker(self):
        """Worker que processa tarefas da fila"""
        while self.running:
            try:
                # Pega uma tarefa da fila (timeout de 1 segundo)
                task, args, kwargs = self.task_queue.get(timeout=1.0)
                
                if task is None:  # Sinal de parada
                    break
                
                # Executa a tarefa
                try:
                    task(*args, **kwargs)
                except Exception as e:
                    log_error(f"Erro ao executar tarefa: {e}")
                finally:
                    self.task_queue.task_done()
                    
            except queue.Empty:
                continue  # Timeout normal, continua
            except Exception as e:
                log_error(f"Erro no worker: {e}")
    
    def submit_task(self, task: Callable, *args, **kwargs):
        """
        Submete uma tarefa para execução em background
        
        Args:
            task: Função a ser executada
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
        """
        if not self.running:
            log_warning("ThreadManager parado, ignorando tarefa")
            return
        
        try:
            self.task_queue.put((task, args, kwargs), timeout=1.0)
            log_debug(f"Tarefa submetida: {task.__name__}")
        except queue.Full:
            log_warning("Fila de tarefas cheia, ignorando tarefa")
    
    def submit_delayed_task(self, delay: float, task: Callable, *args, **kwargs):
        """
        Submete uma tarefa para execução após um delay
        
        Args:
            delay: Tempo em segundos para aguardar
            task: Função a ser executada
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
        """
        def delayed_task():
            time.sleep(delay)
            task(*args, **kwargs)
        
        self.submit_task(delayed_task)
    
    def stop(self):
        """Para o pool de threads"""
        self.running = False
        
        # Envia sinais de parada para todos os workers
        for _ in self.workers:
            self.task_queue.put((None, (), {}))
        
        # Aguarda workers finalizarem
        for worker in self.workers:
            worker.join(timeout=2.0)
            if worker.is_alive():
                log_warning(f"Worker {worker.name} não finalizou no tempo esperado")
        
        log_debug("ThreadManager parado")
    
    def get_active_threads(self) -> int:
        """Retorna número de threads ativas do manager"""
        return len([w for w in self.workers if w.is_alive()])

# Instância global do gerenciador
_thread_manager: Optional[ThreadManager] = None

def get_thread_manager() -> ThreadManager:
    """Obtém instância global do gerenciador de threads"""
    global _thread_manager
    if _thread_manager is None:
        _thread_manager = ThreadManager()
    return _thread_manager

def submit_background_task(task: Callable, *args, **kwargs):
    """
    Função de conveniência para submeter tarefa em background
    
    Args:
        task: Função a ser executada
        *args: Argumentos posicionais
        **kwargs: Argumentos nomeados
    """
    manager = get_thread_manager()
    manager.submit_task(task, *args, **kwargs)

def submit_delayed_task(delay: float, task: Callable, *args, **kwargs):
    """
    Função de conveniência para submeter tarefa com delay
    
    Args:
        delay: Tempo em segundos para aguardar
        task: Função a ser executada
        *args: Argumentos posicionais
        **kwargs: Argumentos nomeados
    """
    manager = get_thread_manager()
    manager.submit_delayed_task(delay, task, *args, **kwargs)

def cleanup_thread_manager():
    """Limpa o gerenciador de threads"""
    global _thread_manager
    if _thread_manager:
        _thread_manager.stop()
        _thread_manager = None