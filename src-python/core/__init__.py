"""
Jarvis Assistant - Core Package
Módulos principais do assistente de voz
"""

from .listener import initialize_wake_word_detection, start_wake_word_listening
from .speech_to_text import initialize_speech_recognition, listen_and_transcribe
from .command_handler import handle_command, process_voice_input
from .dictation_mode import start_dictation_mode, is_dictation_active
from .background_service import start_background_service, stop_background_service

__all__ = [
    'initialize_wake_word_detection',
    'start_wake_word_listening', 
    'initialize_speech_recognition',
    'listen_and_transcribe',
    'handle_command',
    'process_voice_input',
    'start_dictation_mode',
    'is_dictation_active',
    'start_background_service',
    'stop_background_service'
]