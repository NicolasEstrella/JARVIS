"""
Workflow Engine - Executor de workflows configuráveis
Lê workflows.json e executa sequências de ações automatizadas
"""

import json
import os
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from utils.logger import log_info, log_error, log_debug, log_warning

class WorkflowFileHandler(FileSystemEventHandler):
    """Handler para monitorar mudanças em workflows.json"""
    
    def __init__(self, engine):
        self.engine = engine
        self.last_modified = time.time()
        
    def on_modified(self, event):
        """Callback quando arquivo é modificado"""
        if event.src_path.endswith('workflows.json'):
            # Debounce para evitar múltiplos reloads
            current_time = time.time()
            if current_time - self.last_modified > 1:
                self.last_modified = current_time
                log_info("workflows.json modificado - recarregando workflows...")
                self.engine.reload_workflows()

class WorkflowEngine:
    """
    Engine principal para execução de workflows
    """
    
    def __init__(self, workflows_file: str = None):
        """
        Inicializa o workflow engine
        
        Args:
            workflows_file: Caminho para arquivo workflows.json
        """
        if workflows_file is None:
            # Usa caminho padrão relativo ao diretório src-python
            base_dir = Path(__file__).parent.parent
            workflows_file = base_dir / "workflows.json"
        
        self.workflows_file = Path(workflows_file)
        self.workflows: Dict[str, List[Dict[str, Any]]] = {}
        self.observer: Optional["Observer"] = None
        self.action_modules = {}
        
        # Cria arquivo se não existir
        self._ensure_workflows_file()
        
        # Carrega workflows
        self.reload_workflows()
        
        # Importa módulos de ações dinamicamente
        self._load_action_modules()
        
    def _ensure_workflows_file(self):
        """Garante que o arquivo workflows.json existe"""
        if not self.workflows_file.exists():
            log_info(f"Criando workflows.json em {self.workflows_file}")
            self.workflows_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Cria arquivo com workflows de exemplo
            default_workflows = {
                "jogar": [
                    {
                        "action": "open_app",
                        "params": {"path": "spotify.exe"}
                    },
                    {
                        "action": "press_key",
                        "params": {"key": "p"}
                    }
                ],
                "trabalhar": [
                    {
                        "action": "open_app",
                        "params": {"path": "code"}
                    },
                    {
                        "action": "open_app",
                        "params": {"path": "chrome"}
                    }
                ],
                "codigo": [
                    {
                        "action": "open_app",
                        "params": {"path": "code"}
                    }
                ],
                "calculadora": [
                    {
                        "action": "open_app",
                        "params": {"path": "calc"}
                    }
                ]
            }
            
            with open(self.workflows_file, 'w', encoding='utf-8') as f:
                json.dump(default_workflows, f, indent=2, ensure_ascii=False)
    
    def _load_action_modules(self):
        """Carrega módulos de ações dinamicamente"""
        try:
            from actions import open_app, keyboard_actions, system_actions
            
            self.action_modules = {
                'open_app': open_app,
                'press_key': keyboard_actions,
                'type_text': keyboard_actions,
                'press_hotkey': keyboard_actions,
                'click_mouse': system_actions,
                'screenshot': system_actions,
                'volume': system_actions
            }
            
            log_debug("[OK] Módulos de ações carregados")
            
        except ImportError as e:
            log_warning(f"[WARN] Alguns módulos de ações não puderam ser carregados: {e}")
    
    def reload_workflows(self):
        """Recarrega workflows do arquivo JSON"""
        try:
            if self.workflows_file.exists():
                with open(self.workflows_file, 'r', encoding='utf-8') as f:
                    self.workflows = json.load(f)
                
                log_info(f"[OK] {len(self.workflows)} workflow(s) carregado(s)")
                log_debug(f"Triggers disponíveis: {', '.join(self.workflows.keys())}")
            else:
                log_warning(f"[WARN] Arquivo {self.workflows_file} não encontrado")
                self.workflows = {}
                
        except json.JSONDecodeError as e:
            log_error(f"[ERRO] Erro ao parsear workflows.json: {e}")
            self.workflows = {}
        except Exception as e:
            log_error(f"[ERRO] Erro ao carregar workflows: {e}")
            self.workflows = {}
    
    def start_watching(self):
        """Inicia monitoramento de mudanças no arquivo workflows.json"""
        if self.observer is not None:
            log_warning("[WARN] Já existe um observer ativo")
            return
        
        try:
            event_handler = WorkflowFileHandler(self)
            self.observer = Observer()
            self.observer.schedule(
                event_handler,
                str(self.workflows_file.parent),
                recursive=False
            )
            self.observer.start()
            
            log_info(f"Monitorando mudanças em {self.workflows_file}")
            
        except Exception as e:
            log_error(f"[ERRO] Erro ao iniciar monitoramento: {e}")

    def stop_watching(self):
        """Para monitoramento de mudanças"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            log_debug("Monitoramento parado")
    
    def get_workflow(self, trigger: str) -> Optional[List[Dict[str, Any]]]:
        """
        Obtém workflow pelo trigger
        
        Args:
            trigger: Nome do trigger (ex: "jogar", "trabalhar")
            
        Returns:
            Lista de ações ou None se não encontrado
        """
        return self.workflows.get(trigger.lower())
    
    def list_workflows(self) -> List[str]:
        """
        Lista todos os triggers disponíveis
        
        Returns:
            Lista de nomes de triggers
        """
        return list(self.workflows.keys())
    
    def execute_workflow(self, trigger: str) -> bool:
        """
        Executa um workflow pelo trigger
        
        Args:
            trigger: Nome do trigger
            
        Returns:
            True se executou com sucesso, False caso contrário
        """
        workflow = self.get_workflow(trigger)
        
        if not workflow:
            log_warning(f"[WARN] Workflow '{trigger}' não encontrado")
            return False

        log_info(f"Executando workflow '{trigger}' com {len(workflow)} ação(ões)")

        try:
            for idx, action_config in enumerate(workflow, 1):
                action_name = action_config.get('action')
                params = action_config.get('params', {})
                
                log_debug(f"  [{idx}/{len(workflow)}] {action_name}: {params}")
                
                # Executa a ação
                if not self._execute_action(action_name, params):
                    log_error(f"[ERRO] Falha ao executar ação {idx}: {action_name}")
                    return False
                
                # Pequena pausa entre ações para evitar problemas
                time.sleep(0.3)
            
            log_info(f"[OK] Workflow '{trigger}' executado com sucesso!")
            return True
            
        except Exception as e:
            log_error(f"[ERRO] Erro ao executar workflow '{trigger}': {e}")
            return False
    
    def _execute_action(self, action_name: str, params: Dict[str, Any]) -> bool:
        """
        Executa uma ação individual
        
        Args:
            action_name: Nome da ação (ex: 'open_app', 'press_key')
            params: Parâmetros da ação
            
        Returns:
            True se executou com sucesso
        """
        try:
            # Mapeia ação para módulo
            if action_name == 'open_app':
                from actions.open_app import run
                return run(params.get('path', ''))
                
            elif action_name == 'press_key':
                from actions.keyboard_actions import press_key
                return press_key(params.get('key', ''))
                
            elif action_name == 'type_text':
                from actions.keyboard_actions import type_text
                return type_text(params.get('text', ''))
                
            elif action_name == 'press_hotkey':
                from actions.keyboard_actions import press_hotkey
                keys = params.get('keys', [])
                return press_hotkey(*keys)
                
            elif action_name == 'click_mouse':
                from actions.system_actions import click_mouse
                return click_mouse(
                    params.get('x'),
                    params.get('y'),
                    params.get('button', 'left')
                )
                
            elif action_name == 'screenshot':
                from actions.system_actions import screenshot
                return screenshot(params.get('filename'))
                
            elif action_name == 'volume':
                from actions.system_actions import set_volume
                return set_volume(params.get('level', 50))
                
            else:
                log_warning(f"[WARN] Ação desconhecida: {action_name}")
                return False
                
        except ImportError as e:
            log_error(f"[ERRO] Módulo de ação não encontrado para '{action_name}': {e}")
            return False
        except Exception as e:
            log_error(f"[ERRO] Erro ao executar ação '{action_name}': {e}")
            return False
    
    def save_workflow(self, trigger: str, actions: List[Dict[str, Any]]) -> bool:
        """
        Salva ou atualiza um workflow
        
        Args:
            trigger: Nome do trigger
            actions: Lista de ações
            
        Returns:
            True se salvou com sucesso
        """
        try:
            self.workflows[trigger.lower()] = actions
            
            with open(self.workflows_file, 'w', encoding='utf-8') as f:
                json.dump(self.workflows, f, indent=2, ensure_ascii=False)
            
            log_info(f"[SAVE] Workflow '{trigger}' salvo com sucesso")
            return True
            
        except Exception as e:
            log_error(f"[ERRO] Erro ao salvar workflow '{trigger}': {e}")
            return False
    
    def delete_workflow(self, trigger: str) -> bool:
        """
        Remove um workflow
        
        Args:
            trigger: Nome do trigger
            
        Returns:
            True se removeu com sucesso
        """
        try:
            if trigger.lower() in self.workflows:
                del self.workflows[trigger.lower()]
                
                with open(self.workflows_file, 'w', encoding='utf-8') as f:
                    json.dump(self.workflows, f, indent=2, ensure_ascii=False)

                log_info(f"[DELETE] Workflow '{trigger}' removido")
                return True
            else:
                log_warning(f"[WARN] Workflow '{trigger}' não encontrado para remoção")
                return False
                
        except Exception as e:
            log_error(f"[ERRO] Erro ao remover workflow '{trigger}': {e}")
            return False


# Instância global do engine
_engine: Optional[WorkflowEngine] = None


def get_engine() -> WorkflowEngine:
    """Obtém instância global do workflow engine"""
    global _engine
    if _engine is None:
        _engine = WorkflowEngine()
    return _engine


def initialize_workflow_engine() -> bool:
    """Inicializa e retorna engine de workflows"""
    try:
        engine = get_engine()
        engine.start_watching()
        log_info("[OK] Workflow engine inicializado")
        return True
    except Exception as e:
        log_error(f"[ERRO] Erro ao inicializar workflow engine: {e}")
        return False


def execute_workflow(trigger: str) -> bool:
    """Executa workflow pelo trigger"""
    return get_engine().execute_workflow(trigger)


def list_workflows() -> List[str]:
    """Lista workflows disponíveis"""
    return get_engine().list_workflows()


def cleanup_workflow_engine():
    """Limpa recursos do engine"""
    global _engine
    if _engine:
        _engine.stop_watching()
        _engine = None
        log_debug("Workflow engine limpo")
