"""
Actions package - Módulos de ações automatizadas
"""

from .open_app import run
from .keyboard_actions import press_key, type_text, press_hotkey
from .system_actions import click_mouse, screenshot, set_volume

__all__ = [
    'run',
    'press_key',
    'type_text',
    'press_hotkey',
    'click_mouse',
    'screenshot',
    'set_volume'
]
