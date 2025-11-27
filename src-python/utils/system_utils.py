"""
Utilitários do sistema para o Jarvis Assistant
Funções para automação do sistema, abrir aplicações e simular teclas

MIGRAÇÃO RUST: Este módulo pode ser substituído por 'enigo' para automação
cross-platform com melhor performance e menor overhead.
"""

import subprocess
import os
import platform
import keyboard
import pyautogui
from typing import List, Optional, Dict, Any
from utils.logger import log_info, log_error, log_debug

# Configurações do sistema
SYSTEM = platform.system().lower()

class SystemController:
    """
    Controlador principal do sistema
    
    RUST MIGRATION: Esta classe pode ser reimplementada usando 'enigo'
    para automação cross-platform mais eficiente.
    """
    
    def __init__(self):
        # Configurações específicas por OS
        self.os_commands = {
            'windows': {
                'code': ['code'],
                'notepad': ['notepad'],
                'calc': ['calc'],
                'explorer': ['explorer'],
                'cmd': ['cmd'],
                'powershell': ['powershell'],
                'chrome': ['chrome'],
                'firefox': ['firefox'],
                'spotify': ['spotify']
            },
            'linux': {
                'code': ['code'],
                'gedit': ['gedit'],
                'calc': ['gnome-calculator'],
                'files': ['nautilus'],
                'terminal': ['gnome-terminal'],
                'chrome': ['google-chrome'],
                'firefox': ['firefox'],
                'spotify': ['spotify']
            },
            'darwin': {  # macOS
                'code': ['code'],
                'textedit': ['open', '-a', 'TextEdit'],
                'calc': ['open', '-a', 'Calculator'],
                'finder': ['open', '-a', 'Finder'],
                'terminal': ['open', '-a', 'Terminal'],
                'chrome': ['open', '-a', 'Google Chrome'],
                'firefox': ['open', '-a', 'Firefox'],
                'spotify': ['open', '-a', 'Spotify']
            }
        }
    
    def run_command(self, command: List[str]) -> bool:
        """
        Executa um comando do sistema
        
        Args:
            command (List[str]): Comando e argumentos para executar
            
        Returns:
            bool: True se executou com sucesso
        """
        try:
            log_debug(f"[EXECUTE] Executando comando: {' '.join(command)}")
            
            if SYSTEM == 'windows':
                subprocess.Popen(command, shell=True)
            else:
                subprocess.Popen(command)
            
            log_info(f"[OK] Comando executado: {' '.join(command)}")
            return True
            
        except Exception as e:
            log_error(f"Erro ao executar comando {command}: {e}")
            return False
    
    def open_application(self, app_name: str) -> bool:
        """
        Abre uma aplicação específica
        
        Args:
            app_name (str): Nome da aplicação para abrir
            
        Returns:
            bool: True se abriu com sucesso
        """
        app_name = app_name.lower()
        
        if SYSTEM not in self.os_commands:
            log_error(f"Sistema operacional {SYSTEM} não suportado")
            return False
        
        if app_name not in self.os_commands[SYSTEM]:
            log_error(f"Aplicação '{app_name}' não encontrada para {SYSTEM}")
            return False
        
        command = self.os_commands[SYSTEM][app_name]
        return self.run_command(command)
    
    def simulate_key(self, key: str) -> bool:
        """
        Simula o pressionamento de uma tecla
        
        Args:
            key (str): Tecla para simular
            
        Returns:
            bool: True se simulou com sucesso
        """
        try:
            log_debug(f"[KEYBOARD] Simulando tecla: {key}")
            keyboard.press_and_release(key)
            log_info(f"[OK] Tecla simulada: {key}")
            return True
            
        except Exception as e:
            log_error(f"Erro ao simular tecla {key}: {e}")
            return False
    
    def simulate_key_combination(self, keys: List[str]) -> bool:
        """
        Simula combinação de teclas (ex: Ctrl+C)
        
        Args:
            keys (List[str]): Lista de teclas para pressionar em conjunto
            
        Returns:
            bool: True se simulou com sucesso
        """
        try:
            log_debug(f"[KEYBOARD] Simulando combinação: {'+'.join(keys)}")
            keyboard.press_and_release('+'.join(keys))
            log_info(f"[OK] Combinação simulada: {'+'.join(keys)}")
            return True
            
        except Exception as e:
            log_error(f"Erro ao simular combinação {keys}: {e}")
            return False
    
    def type_text(self, text: str, delay: float = 0.02) -> bool:
        """
        Digita texto como se fosse digitado no teclado
        
        Args:
            text (str): Texto para digitar
            delay (float): Delay entre as teclas (padrão 0.02s)
            
        Returns:
            bool: True se digitou com sucesso
        """
        try:
            log_debug(f"[TYPING] Digitando texto: {text[:50]}...")
            pyautogui.write(text, interval=delay)
            log_info(f"[OK] Texto digitado: {len(text)} caracteres")
            return True
            
        except Exception as e:
            log_error(f"Erro ao digitar texto: {e}")
            return False
    
    def get_clipboard(self) -> Optional[str]:
        """
        Obtém conteúdo da área de transferência
        
        Returns:
            Optional[str]: Conteúdo da clipboard ou None se erro
        """
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # Oculta a janela
            clipboard_content = root.clipboard_get()
            root.destroy()
            return clipboard_content
            
        except Exception as e:
            log_error(f"Erro ao ler clipboard: {e}")
            return None
    
    def set_clipboard(self, text: str) -> bool:
        """
        Define conteúdo da área de transferência
        
        Args:
            text (str): Texto para colocar na clipboard
            
        Returns:
            bool: True se definiu com sucesso
        """
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # Oculta a janela
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()  # Mantém o conteúdo após destruir
            root.destroy()
            log_info(f"[OK] Texto copiado para clipboard: {len(text)} caracteres")
            return True
            
        except Exception as e:
            log_error(f"Erro ao definir clipboard: {e}")
            return False

# Instância global do controlador
system_controller = SystemController()

def execute_command(command_list: List[str]) -> bool:
    """
    Função de conveniência para executar comandos
    
    Args:
        command_list (List[str]): Lista de comandos/argumentos
        
    Returns:
        bool: True se executou com sucesso
    """
    return system_controller.run_command(command_list)

def init_app(app_name: str) -> bool:
    """
    Função de conveniência para abrir aplicações
    
    Args:
        app_name (str): Nome da aplicação
        
    Returns:
        bool: True se abriu com sucesso
    """
    return system_controller.open_application(app_name)

def press_tab() -> bool:
    """
    Função específica para pressionar Tab
    
    Returns:
        bool: True se pressionou com sucesso
    """
    return system_controller.simulate_key('tab')

def press_enter() -> bool:
    """
    Função específica para pressionar Enter
    
    Returns:
        bool: True se pressionou com sucesso
    """
    return system_controller.simulate_key('enter')

def press_escape() -> bool:
    """
    Função específica para pressionar Escape
    
    Returns:
        bool: True se pressionou com sucesso
    """
    return system_controller.simulate_key('escape')

def copy_to_clipboard() -> bool:
    """
    Simula Ctrl+C para copiar
    
    Returns:
        bool: True se copiou com sucesso
    """
    if SYSTEM == 'darwin':  # macOS
        return system_controller.simulate_key_combination(['cmd', 'c'])
    else:
        return system_controller.simulate_key_combination(['ctrl', 'c'])

def paste_from_clipboard() -> bool:
    """
    Simula Ctrl+V para colar
    
    Returns:
        bool: True se colou com sucesso
    """
    if SYSTEM == 'darwin':  # macOS
        return system_controller.simulate_key_combination(['cmd', 'v'])
    else:
        return system_controller.simulate_key_combination(['ctrl', 'v'])

def get_system_info() -> Dict[str, Any]:
    """
    Obtém informações do sistema
    
    Returns:
        Dict[str, Any]: Informações do sistema
    """
    return {
        'platform': platform.platform(),
        'system': platform.system(),
        'version': platform.version(),
        'architecture': platform.architecture(),
        'processor': platform.processor(),
        'python_version': platform.python_version()
    }