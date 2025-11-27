"""
Reconhecimento de fala usando Vosk
Converte áudio capturado em texto

MIGRAÇÃO RUST: Este módulo pode ser substituído por 'vosk-rs' para
reconhecimento de fala com melhor performance e menor uso de memória.
"""

import json
import os
from typing import Optional
from utils.audio_utils import AudioCapture, SAMPLE_RATE
from utils.logger import log_info, log_error, log_debug
from unidecode import unidecode

# Importação segura do Vosk
try:
    import vosk
    VOSK_AVAILABLE = True
    log_info("[OK] Vosk importado com sucesso")
except Exception as e:
    VOSK_AVAILABLE = False
    log_error(f"[ERRO] Erro ao importar Vosk: {e}")
    log_info("[OK] Usando SpeechRecognition como fallback")

class SpeechRecognizer:
    """
    Classe para reconhecimento de fala usando Vosk
    
    RUST MIGRATION: Esta classe pode ser reimplementada usando 'vosk-rs'
    para melhor integração e performance em sistemas embarcados.
    """
    
    def __init__(self, model_path: str = "models/vosk-model-small-pt-0.3"):
        self.model_path = model_path
        self.model = None
        self.recognizer = None
        self.audio_capture = AudioCapture()
        self.is_listening = False
        
        # Fallback vars
        self.fallback_recognizer = None
        self.fallback_mic = None
        self.using_fallback = False
        
    def initialize(self) -> bool:
        """
        Inicializa o modelo Vosk e o reconhecedor
        
        Returns:
            bool: True se inicializou com sucesso
        """
        if not VOSK_AVAILABLE:
            log_error("[ERRO] Vosk não disponível - usando fallback SpeechRecognition")
            return self._initialize_fallback()
            
        try:
            # Verifica se o modelo existe
            if not os.path.exists(self.model_path):
                log_error(f"Modelo Vosk não encontrado em: {self.model_path}")
                log_info("[OK] Baixe o modelo com:")
                log_info("wget https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip")
                return self._initialize_fallback()
            
            log_info("[LOADING] Carregando modelo Vosk...")
            
            # Carrega o modelo
            self.model = vosk.Model(self.model_path)
            self.recognizer = vosk.KaldiRecognizer(self.model, SAMPLE_RATE)
            
            log_info("[OK] Modelo Vosk carregado com sucesso")
            return True
            
        except Exception as e:
            log_error(f"Erro ao carregar modelo Vosk: {e}")
            return self._initialize_fallback()
    
    def _initialize_fallback(self) -> bool:
        """
        Inicializa fallback usando SpeechRecognition
        """
        try:
            import speech_recognition as sr
            self.fallback_recognizer = sr.Recognizer()
            self.fallback_mic = sr.Microphone()
            self.using_fallback = True
            log_info("[OK] Fallback SpeechRecognition inicializado")
            return True
        except Exception as e:
            log_error(f"[ERRO] Erro no fallback: {e}")
            return False
    
    def process_audio_data(self, audio_data: bytes) -> Optional[str]:
        """
        Processa dados de áudio e retorna texto reconhecido
        
        Args:
            audio_data (bytes): Dados de áudio para processar
            
        Returns:
            Optional[str]: Texto reconhecido ou None se nada foi reconhecido
        """
        if not self.recognizer:
            log_error("Reconhecedor não inicializado")
            return None
        
        try:
            # Processa o áudio
            if self.recognizer.AcceptWaveform(audio_data):
                # Resultado final
                result = json.loads(self.recognizer.Result())
                text = result.get('text', '').strip()
                
                if text:
                    # Remove acentos e converte para minúsculas
                    normalized_text = unidecode(text.lower())
                    log_debug(f"Texto reconhecido: '{normalized_text}'")
                    return normalized_text
            else:
                # Resultado parcial (opcional para feedback em tempo real)
                partial = json.loads(self.recognizer.PartialResult())
                partial_text = partial.get('partial', '').strip()
                if partial_text:
                    log_debug(f"Reconhecimento parcial: '{partial_text}'")
                
        except Exception as e:
            log_error(f"Erro no processamento de áudio: {e}")
        
        return None
    
    def listen_and_transcribe(self, timeout_seconds: int = 30) -> Optional[str]:
        """
        Escuta o microfone e transcreve a fala
        
        Args:
            timeout_seconds (int): Timeout em segundos para parar de escutar
            
        Returns:
            Optional[str]: Texto transcrito ou None se timeout/erro
        """
        if not self.recognizer:
            log_error("Reconhecedor não inicializado")
            return None
        
        log_info("[AUDIO] Escutando... (fale agora)")
        
        # Inicia captura de áudio
        if not self.audio_capture.start_stream():
            return None
        
        self.is_listening = True
        chunks_without_speech = 0
        max_silent_chunks = int(timeout_seconds * SAMPLE_RATE / 1024)  # Aproximadamente
        
        try:
            while self.is_listening and chunks_without_speech < max_silent_chunks:
                # Lê chunk de áudio
                audio_data = self.audio_capture.read_audio_chunk()
                if audio_data is None:
                    break
                
                # Processa o áudio
                recognized_text = self.process_audio_data(audio_data)
                
                if recognized_text:
                    # Reset contador de silêncio quando há fala
                    chunks_without_speech = 0
                    
                    # Verifica se é comando para parar
                    if "parar ditado" in recognized_text:
                        log_info("  Comando 'parar ditado' detectado")
                        break
                    
                    self.stop_listening()
                    return recognized_text
                else:
                    chunks_without_speech += 1
            
            # Timeout atingido
            if chunks_without_speech >= max_silent_chunks:
                log_info(f"Timeout de {timeout_seconds}s atingido")
            
        except Exception as e:
            log_error(f"Erro durante escuta: {e}")
        finally:
            self.stop_listening()
        
        return None
    
    def listen_continuous(self, callback_function) -> None:
        """
        Escuta continuamente e chama callback para cada texto reconhecido
        
        Args:
            callback_function: Função chamada com texto reconhecido
        """
        if not self.recognizer:
            log_error("Reconhecedor não inicializado")
            return
        
        log_info("[AUDIO] Iniciando escuta contínua...")
        
        if not self.audio_capture.start_stream():
            return
        
        self.is_listening = True
        
        try:
            while self.is_listening:
                audio_data = self.audio_capture.read_audio_chunk()
                if audio_data is None:
                    continue
                
                recognized_text = self.process_audio_data(audio_data)
                if recognized_text:
                    callback_function(recognized_text)
                    
        except Exception as e:
            log_error(f"Erro na escuta contínua: {e}")
        finally:
            self.stop_listening()
    
    def stop_listening(self) -> None:
        """Para a escuta de áudio"""
        self.is_listening = False
        self.audio_capture.stop_stream()
        log_debug("[AUDIO] Escuta parada")
    
    def cleanup(self) -> None:
        """Limpa recursos"""
        self.stop_listening()
        self.audio_capture.cleanup()
        log_debug("Recursos do reconhecedor liberados")

# Instância global do reconhecedor
speech_recognizer = SpeechRecognizer()

def initialize_speech_recognition() -> bool:
    """
    Inicializa o reconhecimento de fala
    
    Returns:
        bool: True se inicializou com sucesso
    """
    return speech_recognizer.initialize()

def listen_and_transcribe(timeout: int = 30) -> Optional[str]:
    """
    Função de conveniência para escutar e transcrever
    
    Args:
        timeout (int): Timeout em segundos
        
    Returns:
        Optional[str]: Texto transcrito
    """
    return speech_recognizer.listen_and_transcribe(timeout)

def stop_speech_recognition() -> None:
    """Para o reconhecimento de fala"""
    speech_recognizer.stop_listening()

def cleanup_speech_recognition() -> None:
    """Limpa recursos do reconhecimento de fala"""
    speech_recognizer.cleanup()