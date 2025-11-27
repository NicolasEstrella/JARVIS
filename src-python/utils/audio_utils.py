"""
Utilitários de áudio para o Jarvis Assistant
Funções auxiliares para captura e processamento de áudio

MIGRAÇÃO RUST: Este módulo pode ser substituído por 'cpal' para captura de áudio
e processamento de dados em tempo real com melhor performance.
"""

import pyaudio
import wave
import numpy as np
from typing import Optional, Tuple
from utils.logger import log_info, log_error, log_debug

# Configurações de áudio
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
CHANNELS = 1
AUDIO_FORMAT = pyaudio.paInt16

class AudioCapture:
    """
    Classe para captura de áudio do microfone
    
    RUST MIGRATION: Esta classe pode ser reimplementada usando 'cpal'
    para melhor controle de latência e performance cross-platform.
    """
    
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream: Optional[pyaudio.Stream] = None
        
    def start_stream(self) -> bool:
        """
        Inicia o stream de captura de áudio
        
        Returns:
            bool: True se iniciou com sucesso, False caso contrário
        """
        try:
            self.stream = self.audio.open(
                format=AUDIO_FORMAT,
                channels=CHANNELS,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE
            )
            log_debug("[AUDIO] Stream de áudio iniciado")
            return True
        except Exception as e:
            log_error(f"Erro ao iniciar stream de áudio: {e}")
            return False
    
    def read_audio_chunk(self) -> Optional[bytes]:
        """
        Lê um chunk de áudio do microfone
        
        Returns:
            Optional[bytes]: Dados de áudio ou None se erro
        """
        if not self.stream:
            return None
            
        try:
            return self.stream.read(CHUNK_SIZE, exception_on_overflow=False)
        except Exception as e:
            log_error(f"Erro ao ler áudio: {e}")
            return None
    
    def stop_stream(self) -> None:
        """Para o stream de captura de áudio"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            log_debug("[AUDIO] Stream de áudio parado")
    
    def cleanup(self) -> None:
        """Limpa recursos de áudio"""
        self.stop_stream()
        if self.audio:
            self.audio.terminate()
            log_debug("[AUDIO] Recursos de áudio liberados")

def get_audio_devices() -> list:
    """
    Lista dispositivos de áudio disponíveis
    
    Returns:
        list: Lista de dispositivos de entrada de áudio
    """
    audio = pyaudio.PyAudio()
    devices = []
    
    try:
        for i in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': device_info['name'],
                    'channels': device_info['maxInputChannels'],
                    'sample_rate': device_info['defaultSampleRate']
                })
    except Exception as e:
        log_error(f"Erro ao listar dispositivos de áudio: {e}")
    finally:
        audio.terminate()
    
    return devices

def test_microphone() -> bool:
    """
    Testa se o microfone está funcionando
    
    Returns:
        bool: True se microfone está OK, False caso contrário
    """
    log_info("[AUDIO] Testando microfone...")
    
    capture = AudioCapture()
    if not capture.start_stream():
        capture.cleanup()
        return False
    
    try:
        # Tenta capturar alguns chunks de áudio
        for _ in range(10):
            chunk = capture.read_audio_chunk()
            if chunk is None:
                log_error("Falha ao capturar áudio do microfone")
                return False
        
        log_info("[OK] Microfone funcionando corretamente")
        return True
        
    except Exception as e:
        log_error(f"Erro no teste do microfone: {e}")
        return False
    finally:
        capture.cleanup()

def calculate_volume(audio_data: bytes) -> float:
    """
    Calcula o volume (RMS) dos dados de áudio
    
    Args:
        audio_data (bytes): Dados de áudio em formato bytes
        
    Returns:
        float: Nível de volume (0.0 a 1.0)
    """
    try:
        # Converte bytes para array numpy
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # Calcula RMS (Root Mean Square)
        rms = np.sqrt(np.mean(audio_array**2))
        
        # Normaliza para 0-1 (assumindo int16 max = 32767)
        normalized_volume = min(rms / 32767.0, 1.0)
        
        return normalized_volume
        
    except Exception as e:
        log_error(f"Erro ao calcular volume: {e}")
        return 0.0

def is_speech_detected(audio_data: bytes, threshold: float = 0.01) -> bool:
    """
    Detecta se há fala nos dados de áudio baseado no volume
    
    Args:
        audio_data (bytes): Dados de áudio
        threshold (float): Limite mínimo de volume para considerar fala
        
    Returns:
        bool: True se fala foi detectada
    """
    volume = calculate_volume(audio_data)
    return volume > threshold

def save_audio_to_file(audio_data: list, filename: str) -> bool:
    """
    Salva dados de áudio em arquivo WAV
    
    Args:
        audio_data (list): Lista de chunks de áudio
        filename (str): Nome do arquivo para salvar
        
    Returns:
        bool: True se salvou com sucesso
    """
    try:
        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(CHANNELS)
            wav_file.setsampwidth(pyaudio.PyAudio().get_sample_size(AUDIO_FORMAT))
            wav_file.setframerate(SAMPLE_RATE)
            wav_file.writeframes(b''.join(audio_data))
        
        log_debug(f"[ARQUIVO] Áudio salvo em: {filename}")
        return True
        
    except Exception as e:
        log_error(f"Erro ao salvar áudio: {e}")
        return False