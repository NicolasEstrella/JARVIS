"""
Manipulador de comandos para o Jarvis Assistant
Implementa switch-case com palavras-chave e delegação para funções apropriadas
Integrado com workflow_engine para executar workflows customizáveis
"""

import time
from typing import Optional
from utils.system_utils import execute_command, init_app, press_tab, system_controller
from utils.logger import log_info, log_error, log_debug
from core.dictation_mode import start_dictation_mode
from core.workflow_engine import get_engine, execute_workflow

class CommandHandler:
    """
    Classe principal para manipulação de comandos de voz
    """
    
    def __init__(self):
        self.is_active = True
        
        # Mapeamento de comandos para ações
        self.commands = {
            # Comandos de aplicações (simplificados)
            "codigo": lambda: init_app("code"),
            "bloco de notas": lambda: init_app("notepad"),
            "calculadora": lambda: init_app("calc"),
            "arquivos": lambda: init_app("explorer"),
            "navegador": lambda: init_app("chrome"),
            "musica": lambda: init_app("spotify"),
            "terminal": lambda: init_app("cmd"),
            
            # Comandos de teclas
            "tab": lambda: press_tab(),
            "enter": lambda: system_controller.simulate_key("enter"),
            "escape": lambda: system_controller.simulate_key("escape"),
            "espaco": lambda: system_controller.simulate_key("space"),
            
            # Combinações de teclas
            "copiar": lambda: system_controller.simulate_key_combination(["ctrl", "c"]),
            "colar": lambda: system_controller.simulate_key_combination(["ctrl", "v"]),
            "desfazer": lambda: system_controller.simulate_key_combination(["ctrl", "z"]),
            "refazer": lambda: system_controller.simulate_key_combination(["ctrl", "y"]),
            "salvar": lambda: system_controller.simulate_key_combination(["ctrl", "s"]),
            "selecionar": lambda: system_controller.simulate_key_combination(["ctrl", "a"]),
            
            # Comandos de controle
            "parar": self._stop_jarvis,
            "finalizar": self._stop_jarvis,
            "sair": self._stop_jarvis,
            "tchau": self._stop_jarvis,
            "reiniciar": self._restart_jarvis,
            "para a porra toda": self._emergency_stop,
            "quero falar contigo": self._start_dictation,
            
            # Comandos de janela
            "minimizar": lambda: system_controller.simulate_key_combination(["alt", "f9"]),
            "maximizar": lambda: system_controller.simulate_key_combination(["alt", "f10"]),
            "fechar": lambda: system_controller.simulate_key_combination(["alt", "f4"]),
            "trocar": lambda: system_controller.simulate_key_combination(["alt", "tab"]),
            
            # Comandos de navegação
            "voltar": lambda: system_controller.simulate_key_combination(["alt", "left"]),
            "avancar": lambda: system_controller.simulate_key_combination(["alt", "right"]),
            "atualizar": lambda: system_controller.simulate_key("f5"),
            
            # Comandos de texto
            "nova linha": lambda: system_controller.simulate_key("enter"),
            "apagar": lambda: system_controller.simulate_key("backspace"),
            "deletar": lambda: system_controller.simulate_key("delete"),
        }
    
    def handle_command(self, command: str) -> bool:
        """
        Processa um comando de voz e executa a ação correspondente
        Primeiro verifica workflows customizados, depois comandos built-in
        
        Args:
            command (str): Comando em texto (já normalizado e sem acentos)
            
        Returns:
            bool: True se comando foi processado, False se deve entrar em modo ditado
        """
        if not command or not command.strip():
            log_debug("Comando vazio recebido")
            return False
        
        command = command.strip().lower()
        log_info(f"Processando comando: '{command}'")
        
        # PRIORIDADE 1: Verifica workflows customizados
        try:
            workflow_engine = get_engine()
            available_workflows = workflow_engine.list_workflows()
            
            # Verifica match exato de workflow
            if command in available_workflows:
                log_info(f"[WORKFLOW] Executando workflow customizado: '{command}'")
                if execute_workflow(command):
                    return True
            
            # Verifica match parcial de workflow
            for workflow_name in available_workflows:
                if workflow_name in command or command in workflow_name:
                    log_info(f"[WORKFLOW] Executando workflow customizado (match parcial): '{workflow_name}'")
                    if execute_workflow(workflow_name):
                        return True
        except Exception as e:
            log_error(f"[ERRO] Erro ao verificar workflows: {e}")
        
        # PRIORIDADE 2: Verifica comando exato built-in
        if command in self.commands:
            try:
                result = self.commands[command]()
                if result is not False:  # None ou True são considerados sucesso
                    log_info(f"[OK] Comando built-in executado: '{command}'")
                    return True
                else:
                    log_error(f"[ERRO] Falha ao executar comando: '{command}'")
                    return False
            except Exception as e:
                log_error(f"[ERRO] Erro ao executar comando '{command}': {e}")
                return False
        
        # PRIORIDADE 3: Verifica comandos parciais (contém palavra-chave)
        for cmd_key, cmd_func in self.commands.items():
            if cmd_key in command:
                try:
                    log_info(f"Comando parcial detectado: '{cmd_key}' em '{command}'")
                    result = cmd_func()
                    if result is not False:
                        log_info(f"[OK] Comando parcial executado: '{cmd_key}'")
                        return True
                    else:
                        log_error(f"[ERRO] Falha ao executar comando parcial: '{cmd_key}'")
                        return False
                except Exception as e:
                    log_error(f"[ERRO] Erro ao executar comando parcial '{cmd_key}': {e}")
                    return False
        
        # Se chegou aqui, não é um comando reconhecido
        log_info(f"Comando não reconhecido: '{command}'")
        log_info(f"Workflows disponíveis: {', '.join(available_workflows) if available_workflows else 'nenhum'}")
        return False
    
    def _stop_jarvis(self) -> bool:
        """
        Para o Jarvis Assistant
        
        Returns:
            bool: True sempre (comando executado com sucesso)
        """
        log_info("  Comando de parada recebido")
        self.is_active = False
        return True
    
    def _restart_jarvis(self) -> bool:
        """
        Reinicia o Jarvis Assistant
        
        Returns:
            bool: True sempre (comando executado com sucesso)
        """
        log_info("[RESTART] Comando de reinicialização recebido")
        self.is_active = False
        
        # Sinaliza para reiniciar em vez de apenas parar (usando thread manager)
        from utils.thread_manager import submit_delayed_task
        submit_delayed_task(2.0, self._delayed_restart)
        return True
    
    def _delayed_restart(self) -> None:
        """Reinicia o serviço após pequeno delay"""
        try:
            from core.background_service import restart_service
            restart_service()
        except Exception as e:
            log_error(f"Erro ao reiniciar: {e}")
    
    def _emergency_stop(self) -> bool:
        """
        Parada de emergência - para tudo imediatamente
        
        Returns:
            bool: True sempre (comando executado com sucesso)
        """
        log_info("[EMERGENCY STOP] PARADA DE EMERGÊNCIA - 'para a porra toda' detectado!")
        self.is_active = False
        
        # Força parada do serviço em background
        try:
            import sys
            sys.exit(0)
        except:
            pass
        
        return True
    
    def _start_dictation(self) -> bool:
        """
        Inicia o modo ditado
        
        Returns:
            bool: True sempre (comando executado com sucesso)
        """
        log_info("[DICTATION] Iniciando modo ditado...")
        try:
            from core.dictation_mode import start_dictation_mode
            start_dictation_mode()
            return True
        except Exception as e:
            log_error(f"Erro ao iniciar modo ditado: {e}")
            return False
    
    def is_jarvis_active(self) -> bool:
        """
        Verifica se o Jarvis está ativo
        
        Returns:
            bool: True se ativo, False se deve parar
        """
        return self.is_active
    
    def add_custom_command(self, command: str, action_func) -> None:
        """
        Adiciona um comando customizado
        
        Args:
            command (str): Comando em texto
            action_func: Função a ser executada
        """
        self.commands[command.lower()] = action_func
        log_info(f"[ADD] Comando customizado adicionado: '{command}'")
    
    def remove_command(self, command: str) -> bool:
        """
        Remove um comando
        
        Args:
            command (str): Comando a ser removido
            
        Returns:
            bool: True se removido, False se não existia
        """
        command = command.lower()
        if command in self.commands:
            del self.commands[command]
            log_info(f"[REMOVE] Comando removido: '{command}'")
            return True
        return False
    
    def list_commands(self) -> list:
        """
        Lista todos os comandos disponíveis
        
        Returns:
            list: Lista de comandos disponíveis
        """
        return list(self.commands.keys())
    
    def process_voice_input(self, text: str) -> None:
        """
        Processa entrada de voz e decide se é comando ou ditado
        
        Args:
            text (str): Texto reconhecido da fala
        """
        if not text:
            return
        
        # Tenta processar como comando
        is_command = self.handle_command(text)
        
        # Se não for comando, simplesmente ignora
        if not is_command:
            log_info(f"[INFO] Comando não reconhecido, aguardando próximo comando...")
            return

# Instância global do manipulador de comandos
command_handler = CommandHandler()

def handle_command(command: str) -> bool:
    """
    Função de conveniência para processar comandos
    
    Args:
        command (str): Comando a ser processado
        
    Returns:
        bool: True se comando foi processado
    """
    return command_handler.handle_command(command)

def process_voice_input(text: str) -> None:
    """
    Função de conveniência para processar entrada de voz
    
    Args:
        text (str): Texto da fala para processar
    """
    command_handler.process_voice_input(text)

def stop_jarvis() -> None:
    """Para o Jarvis Assistant"""
    command_handler._stop_jarvis()

def is_jarvis_active() -> bool:
    """
    Verifica se Jarvis está ativo
    
    Returns:
        bool: True se ativo
    """
    return command_handler.is_jarvis_active()

def add_custom_command(command: str, action_func) -> None:
    """
    Adiciona comando customizado
    
    Args:
        command (str): Nome do comando
        action_func: Função a executar
    """
    command_handler.add_custom_command(command, action_func)

def list_available_commands() -> list:
    """
    Lista comandos disponíveis
    
    Returns:
        list: Lista de comandos
    """
    return command_handler.list_commands()