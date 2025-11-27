"""
System Actions - Ações do sistema (mouse, screenshot, volume, etc)
"""

import pyautogui
import time
import os
from typing import Optional, Tuple
from utils.logger import log_info, log_error, log_debug, log_warning

# Configurações do PyAutoGUI
pyautogui.PAUSE = 0.1  # Pausa entre ações
pyautogui.FAILSAFE = True  # Move mouse para canto superior esquerdo para parar


def click_mouse(x: Optional[int] = None, y: Optional[int] = None, 
                button: str = 'left', clicks: int = 1, interval: float = 0.0) -> bool:
    """
    Clica o mouse em uma posição
    
    Args:
        x: Coordenada X (None = posição atual)
        y: Coordenada Y (None = posição atual)
        button: Botão do mouse ('left', 'right', 'middle')
        clicks: Número de cliques
        interval: Intervalo entre cliques
        
    Returns:
        True se executou com sucesso
        
    Examples:
        >>> click_mouse()  # Clique esquerdo na posição atual
        >>> click_mouse(100, 200)  # Clique na posição (100, 200)
        >>> click_mouse(100, 200, 'right')  # Clique direito
        >>> click_mouse(100, 200, clicks=2)  # Duplo clique
    """
    try:
        if x is not None and y is not None:
            log_info(f"[MOUSE] Clicando mouse em ({x}, {y}) - botão: {button}")
            pyautogui.click(x, y, clicks=clicks, interval=interval, button=button)
        else:
            log_info(f"[MOUSE] Clicando mouse - botão: {button}")
            pyautogui.click(clicks=clicks, interval=interval, button=button)
        
        log_debug(f"[OK] Mouse clicado")
        return True
    except Exception as e:
        log_error(f"[ERRO] Erro ao clicar mouse: {e}")
        return False


def move_mouse(x: int, y: int, duration: float = 0.5) -> bool:
    """
    Move o mouse para uma posição
    
    Args:
        x: Coordenada X
        y: Coordenada Y
        duration: Duração do movimento em segundos
        
    Returns:
        True se executou com sucesso
    """
    try:
        log_info(f"[MOUSE] Movendo mouse para ({x}, {y})")
        pyautogui.moveTo(x, y, duration=duration)
        log_debug(f"[OK] Mouse movido")
        return True
    except Exception as e:
        log_error(f"[ERRO] Erro ao mover mouse: {e}")
        return False


def get_mouse_position() -> Tuple[int, int]:
    """
    Obtém posição atual do mouse
    
    Returns:
        Tupla (x, y) com coordenadas
    """
    pos = pyautogui.position()
    log_debug(f"[MOUSE] Posição do mouse: {pos}")
    return pos.x, pos.y


def scroll(amount: int, direction: str = 'down') -> bool:
    """
    Rola a tela (scroll)
    
    Args:
        amount: Quantidade de scroll
        direction: Direção ('up', 'down', 'left', 'right')
        
    Returns:
        True se executou com sucesso
    """
    try:
        log_info(f"[MOUSE] Scroll: {direction} ({amount})")
        
        if direction in ['down', 'up']:
            scroll_amount = -amount if direction == 'down' else amount
            pyautogui.scroll(scroll_amount)
        elif direction == 'left':
            pyautogui.hscroll(-amount)
        elif direction == 'right':
            pyautogui.hscroll(amount)
        else:
            log_error(f"[ERRO] Direção inválida: {direction}")
            return False
        
        log_debug(f"[OK] Scroll executado")
        return True
    except Exception as e:
        log_error(f"[ERRO] Erro ao fazer scroll: {e}")
        return False


def screenshot(filename: Optional[str] = None, region: Optional[Tuple[int, int, int, int]] = None) -> bool:
    """
    Tira screenshot da tela
    
    Args:
        filename: Nome do arquivo (None = auto-gera com timestamp)
        region: Região para capturar (x, y, width, height)
        
    Returns:
        True se executou com sucesso
        
    Examples:
        >>> screenshot()  # Tela inteira, nome auto
        >>> screenshot('captura.png')  # Tela inteira
        >>> screenshot('area.png', (0, 0, 800, 600))  # Região específica
    """
    try:
        # Gera nome automático se não fornecido
        if filename is None:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'screenshot_{timestamp}.png'
        
        # Garante extensão .png
        if not filename.endswith('.png'):
            filename += '.png'
        
        # Define caminho completo (pasta Screenshots no home)
        screenshots_dir = os.path.join(os.path.expanduser('~'), 'Screenshots')
        os.makedirs(screenshots_dir, exist_ok=True)
        filepath = os.path.join(screenshots_dir, filename)
        
        log_info(f"[PRINT] Tirando screenshot: {filepath}")
        
        # Captura screenshot
        if region:
            screenshot_img = pyautogui.screenshot(region=region)
        else:
            screenshot_img = pyautogui.screenshot()
        
        # Salva imagem
        screenshot_img.save(filepath)
        
        log_info(f"[OK] Screenshot salvo: {filepath}")
        return True
        
    except Exception as e:
        log_error(f"[ERRO] Erro ao tirar screenshot: {e}")
        return False


def set_volume(level: int) -> bool:
    """
    Define volume do sistema (Windows)
    
    Args:
        level: Nível de volume (0-100)
        
    Returns:
        True se executou com sucesso
    """
    try:
        import sys
        
        # Garante valor válido
        level = max(0, min(100, level))
        
        log_info(f"[AUDIO] Ajustando volume para: {level}%")
        
        if sys.platform == 'win32':
            # No Windows, usa NirCmd ou pycaw
            try:
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                
                # Converte porcentagem para escala (0.0 - 1.0)
                volume.SetMasterVolumeLevelScalar(level / 100, None)
                
                log_info(f"[OK] Volume ajustado para {level}%")
                return True
                
            except ImportError:
                log_warning("[WARN] pycaw não instalado, usando comando alternativo")
                # Fallback usando NirCmd (precisa estar instalado)
                import subprocess
                subprocess.run(['nircmd', 'setsysvolume', str(int(655.35 * level))], 
                             check=True, capture_output=True)
                return True
        else:
            log_warning("[WARN] Controle de volume só suportado no Windows")
            return False
            
    except Exception as e:
        log_error(f"[ERRO] Erro ao ajustar volume: {e}")
        return False


def mute_volume() -> bool:
    """Silencia o volume"""
    log_info("[AUDIO] Silenciando volume")
    return set_volume(0)


def max_volume() -> bool:
    """Volume máximo"""
    log_info("[AUDIO] Volume máximo")
    return set_volume(100)


def get_screen_size() -> Tuple[int, int]:
    """
    Obtém tamanho da tela
    
    Returns:
        Tupla (width, height)
    """
    size = pyautogui.size()
    log_debug(f"[SCREEN] Tamanho da tela: {size}")
    return size.width, size.height


def alert(text: str, title: str = 'Jarvis', button: str = 'OK') -> bool:
    """
    Mostra caixa de diálogo de alerta
    
    Args:
        text: Texto da mensagem
        title: Título da janela
        button: Texto do botão
        
    Returns:
        True sempre
    """
    try:
        log_info(f"[WARN] Mostrando alerta: {text}")
        pyautogui.alert(text=text, title=title, button=button)
        return True
    except Exception as e:
        log_error(f"[ERRO] Erro ao mostrar alerta: {e}")
        return False


def confirm(text: str, title: str = 'Jarvis') -> bool:
    """
    Mostra caixa de confirmação (OK/Cancel)
    
    Args:
        text: Texto da mensagem
        title: Título da janela
        
    Returns:
        True se clicou OK, False se cancelou
    """
    try:
        log_info(f"Mostrando confirmação: {text}")
        result = pyautogui.confirm(text=text, title=title, buttons=['OK', 'Cancelar'])
        return result == 'OK'
    except Exception as e:
        log_error(f"[ERRO] Erro ao mostrar confirmação: {e}")
        return False


# Ações específicas do Windows
def minimize_all_windows() -> bool:
    """Minimiza todas as janelas (Win+D)"""
    try:
        import keyboard
        log_info("[WINDOW] Minimizando todas as janelas")
        keyboard.press_and_release('win+d')
        return True
    except Exception as e:
        log_error(f"[ERRO] Erro ao minimizar janelas: {e}")
        return False


def switch_window() -> bool:
    """Troca de janela (Alt+Tab)"""
    try:
        import keyboard
        log_info("[WINDOW] Trocando de janela")
        keyboard.press_and_release('alt+tab')
        return True
    except Exception as e:
        log_error(f"[ERRO] Erro ao trocar janela: {e}")
        return False
