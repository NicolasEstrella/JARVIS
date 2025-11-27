"""
Keyboard Actions - Automação de teclado
"""

import keyboard
import time
from typing import List, Union
from utils.logger import log_info, log_error, log_debug


def press_key(key: str, delay: float = 0.1) -> bool:
    """
    Pressiona uma tecla
    
    Args:
        key: Nome da tecla (ex: 'enter', 'esc', 'a', 'f1')
        delay: Delay após pressionar (segundos)
        
    Returns:
        True se executou com sucesso
        
    Examples:
        >>> press_key('enter')
        >>> press_key('esc')
        >>> press_key('f5')
    """
    try:
        log_info(f"[KEY] Pressionando tecla: {key}")
        keyboard.press_and_release(key)
        time.sleep(delay)
        log_debug(f"[OK] Tecla '{key}' pressionada")
        return True
    except Exception as e:
        log_error(f"[ERRO] Erro ao pressionar tecla '{key}': {e}")
        return False


def press_hotkey(*keys: str, delay: float = 0.1) -> bool:
    """
    Pressiona combinação de teclas (hotkey)
    
    Args:
        *keys: Teclas para pressionar juntas
        delay: Delay após pressionar
        
    Returns:
        True se executou com sucesso
        
    Examples:
        >>> press_hotkey('ctrl', 'c')  # Copiar
        >>> press_hotkey('ctrl', 'v')  # Colar
        >>> press_hotkey('ctrl', 'shift', 'esc')  # Task Manager
        >>> press_hotkey('win', 'd')  # Mostrar Desktop
    """
    try:
        keys_str = '+'.join(keys)
        log_info(f"[KEY] Pressionando hotkey: {keys_str}")
        keyboard.press_and_release(keys_str)
        time.sleep(delay)
        log_debug(f"[OK] Hotkey '{keys_str}' pressionada")
        return True
    except Exception as e:
        log_error(f"[ERRO] Erro ao pressionar hotkey {keys}: {e}")
        return False


def type_text(text: str, interval: float = 0.05) -> bool:
    """
    Digita texto (simula digitação)
    
    Args:
        text: Texto para digitar
        interval: Intervalo entre teclas (segundos)
        
    Returns:
        True se executou com sucesso
        
    Examples:
        >>> type_text('Hello World!')
        >>> type_text('teste@email.com')
    """
    try:
        log_info(f"[KEY] Digitando texto: '{text[:50]}...'")
        keyboard.write(text, delay=interval)
        log_debug(f"[OK] Texto digitado ({len(text)} caracteres)")
        return True
    except Exception as e:
        log_error(f"[ERRO] Erro ao digitar texto: {e}")
        return False


def hold_key(key: str, duration: float = 1.0) -> bool:
    """
    Mantém uma tecla pressionada por um tempo
    
    Args:
        key: Nome da tecla
        duration: Duração em segundos
        
    Returns:
        True se executou com sucesso
    """
    try:
        log_info(f"[KEY] Mantendo tecla '{key}' pressionada por {duration}s")
        keyboard.press(key)
        time.sleep(duration)
        keyboard.release(key)
        log_debug(f"[OK] Tecla '{key}' liberada")
        return True
    except Exception as e:
        log_error(f"[ERRO] Erro ao manter tecla '{key}': {e}")
        return False


# Atalhos comuns pré-configurados
def copy() -> bool:
    """Ctrl+C - Copiar"""
    log_info("[EXECUTE] Executando: Copiar (Ctrl+C)")
    return press_hotkey('ctrl', 'c')


def paste() -> bool:
    """Ctrl+V - Colar"""
    log_info("[EXECUTE] Executando: Colar (Ctrl+V)")
    return press_hotkey('ctrl', 'v')


def cut() -> bool:
    """Ctrl+X - Recortar"""
    log_info("[EXECUTE] Executando: Recortar (Ctrl+X)")
    return press_hotkey('ctrl', 'x')


def undo() -> bool:
    """Ctrl+Z - Desfazer"""
    log_info("[EXECUTE] Executando: Desfazer (Ctrl+Z)")
    return press_hotkey('ctrl', 'z')


def redo() -> bool:
    """Ctrl+Y - Refazer"""
    log_info("[EXECUTE] Executando: Refazer (Ctrl+Y)")
    return press_hotkey('ctrl', 'y')


def select_all() -> bool:
    """Ctrl+A - Selecionar Tudo"""
    log_info("[EXECUTE] Executando: Selecionar Tudo (Ctrl+A)")
    return press_hotkey('ctrl', 'a')


def save() -> bool:
    """Ctrl+S - Salvar"""
    log_info("[EXECUTE] Executando: Salvar (Ctrl+S)")
    return press_hotkey('ctrl', 's')


def find() -> bool:
    """Ctrl+F - Localizar"""
    log_info("[EXECUTE] Executando: Localizar (Ctrl+F)")
    return press_hotkey('ctrl', 'f')


def new_tab() -> bool:
    """Ctrl+T - Nova aba (navegador)"""
    log_info("[EXECUTE] Executando: Nova aba (Ctrl+T)")
    return press_hotkey('ctrl', 't')


def close_tab() -> bool:
    """Ctrl+W - Fechar aba"""
    log_info("[EXECUTE] Executando: Fechar aba (Ctrl+W)")
    return press_hotkey('ctrl', 'w')


def alt_tab() -> bool:
    """Alt+Tab - Trocar janela"""
    log_info("[EXECUTE] Executando: Trocar janela (Alt+Tab)")
    return press_hotkey('alt', 'tab')


def show_desktop() -> bool:
    """Win+D - Mostrar Desktop"""
    log_info("[EXECUTE] Executando: Mostrar Desktop (Win+D)")
    return press_hotkey('win', 'd')


def task_manager() -> bool:
    """Ctrl+Shift+Esc - Gerenciador de Tarefas"""
    log_info("[EXECUTE] Executando: Gerenciador de Tarefas")
    return press_hotkey('ctrl', 'shift', 'esc')


def screenshot_key() -> bool:
    """Print Screen - Screenshot"""
    log_info("[EXECUTE] Executando: Print Screen")
    return press_key('print screen')


def lock_screen() -> bool:
    """Win+L - Bloquear tela"""
    log_info("[EXECUTE] Executando: Bloquear tela (Win+L)")
    return press_hotkey('win', 'l')


# Mapeamento de comandos de voz para ações
VOICE_COMMAND_MAP = {
    'copiar': copy,
    'colar': paste,
    'recortar': cut,
    'desfazer': undo,
    'refazer': redo,
    'selecionar tudo': select_all,
    'salvar': save,
    'localizar': find,
    'buscar': find,
    'nova aba': new_tab,
    'fechar aba': close_tab,
    'trocar janela': alt_tab,
    'mostrar desktop': show_desktop,
    'gerenciador de tarefas': task_manager,
    'print screen': screenshot_key,
    'bloquear': lock_screen,
    'bloquear tela': lock_screen,
}


def execute_voice_command(command: str) -> bool:
    """
    Executa comando de teclado baseado em voz
    
    Args:
        command: Comando falado
        
    Returns:
        True se executou com sucesso
    """
    command_lower = command.lower().strip()
    
    if command_lower in VOICE_COMMAND_MAP:
        return VOICE_COMMAND_MAP[command_lower]()
    else:
        log_debug(f"[WARN] Comando de teclado não mapeado: '{command}'")
        return False
