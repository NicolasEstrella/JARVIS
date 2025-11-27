"""
Listener para wake word detection offline
Detecta palavras-chave usando Vosk (offline) e SpeechRecognition (fallback)

SOLUÇÃO OFFLINE PRIORITÁRIA - Usa Vosk quando disponível
"""

import speech_recognition as sr
import threading
import time
import json
import pyaudio
from typing import Optional, Callable
from utils.audio_utils import AudioCapture, calculate_volume
from utils.logger import log_info, log_error, log_debug, log_warning
from unidecode import unidecode

# Importação condicional do Vosk
try:
    import vosk
    log_info("[OK] Vosk importado com sucesso")
    VOSK_AVAILABLE = True
except ImportError as e:
    log_error(f"[ERRO] Erro ao importar Vosk: {e}")
    log_error("[ERRO] Vosk não disponível - usando fallback SpeechRecognition")
    VOSK_AVAILABLE = False

class VoskWakeWordListener:
    """
    Classe para detecção de wake word usando Vosk (offline)
    Processa áudio localmente sem necessidade de internet
    """
    
    def __init__(self):
        self.model = None
        self.recognizer = None
        self.is_listening = False
        self.callback_function: Optional[Callable] = None
        self.keywords = ["testar", "jarvis"]  # Palavras aceitas
        self.audio_stream = None
        self.sample_rate = 16000
        self.listen_thread = None  # Armazena referência da thread
        
    def initialize(self) -> bool:
        """
        Inicializa o detector de wake word Vosk
        
        Returns:
            bool: True se inicializou com sucesso
        """
        try:
            if not VOSK_AVAILABLE:
                return False
                
            log_info("Inicializando detector de wake word Vosk...")
            
            # Define caminho do modelo
            import os
            model_path = os.path.join(os.path.dirname(__file__), "..", "models", "vosk-model-small-pt-0.3")
            
            if not os.path.exists(model_path):
                log_error(f"Modelo Vosk não encontrado em: {model_path}")
                return False
            
            # Carrega modelo Vosk
            self.model = vosk.Model(model_path)
            self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
            
            # Configura PyAudio
            self.audio = pyaudio.PyAudio()
            
            log_info("[OK] Detector de wake word Vosk inicializado")
            log_info(f"[SCAN] Detectando palavras: {', '.join(self.keywords)}")
            return True
            
        except Exception as e:
            log_error(f"Erro ao inicializar detector Vosk: {e}")
            return False
    
    def set_callback(self, callback: Callable) -> None:
        """
        Define função callback para quando wake word for detectada
        
        Args:
            callback (Callable): Função a ser chamada quando wake word detectada
        """
        self.callback_function = callback
        log_debug("Callback definido para wake word")
    
    def _listen_for_wake_word(self) -> None:
        """Thread de escuta contínua por wake word usando Vosk"""
        log_info("Escutando continuamente por wake word (Vosk)...")
        
        try:
            # Configura stream de áudio
            self.audio_stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=4000
            )
            
            while self.is_listening:
                try:
                    # Lê dados do áudio
                    data = self.audio_stream.read(4000, exception_on_overflow=False)
                    
                    # Processa com Vosk
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get('text', '').strip()
                        
                        if text:
                            self._process_text_for_wake_word(text)
                    
                except Exception as e:
                        if self.is_listening:
                            log_error(f"Erro na escuta Vosk: {e}")
                            time.sleep(1)
                            
        except Exception as e:
            log_error(f"Erro ao configurar stream Vosk: {e}")
        finally:
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
    
    def _process_text_for_wake_word(self, text: str) -> None:
        """
        Processa texto em busca de wake word
        
        Args:
            text: Texto reconhecido para processamento
        """
        try:
            text_normalized = unidecode(text.lower().strip())
            log_debug(f"[VOSK] Áudio reconhecido: '{text_normalized}'")
            
            # Verifica se contém wake word
            for keyword in self.keywords:
                if keyword in text_normalized:
                    log_info(f"[OK] Wake word detectada: '{keyword}' em '{text_normalized}'")
                    
                    # INTEGRAÇÃO FASE 2: Emite evento para Tauri
                    from utils.event_emitter import emit_wake_word
                    emit_wake_word(keyword)
                    
                    if self.callback_function:
                        self.callback_function(keyword)
                    break
                    
        except Exception as e:
            log_debug(f"Erro no processamento de texto: {e}")
    
    def start_listening(self) -> bool:
        """
        Inicia a escuta por wake word
        
        Returns:
            bool: True se iniciou com sucesso
        """
        if self.is_listening:
            log_warning("Wake word listener já está ativo")
            return True
        
        # Se existe uma thread anterior ainda rodando, para ela primeiro
        if self.listen_thread and self.listen_thread.is_alive():
            log_debug("Thread anterior ainda ativa, interrompendo...")
            self.is_listening = False
            self.listen_thread.join(timeout=1.0)  # Aguarda até 1 segundo
        
        self.is_listening = True
        
        # INTEGRAÇÃO FASE 2: Emite estado "waiting" quando começa a escutar
        from utils.event_emitter import get_event_emitter
        emitter = get_event_emitter()
        emitter.emit_state_change("waiting")
        
        # Inicia thread de escuta
        self.listen_thread = threading.Thread(
            target=self._listen_for_wake_word,
            daemon=True,
            name="VoskWakeWordListener"
        )
        self.listen_thread.start()
        
        log_info("Escuta de wake word Vosk iniciada - Estado: waiting")
        return True
    
    def stop_listening(self) -> None:
        """Para a escuta de wake word"""
        self.is_listening = False
        
        # Aguarda a thread finalizar
        if self.listen_thread and self.listen_thread.is_alive():
            log_debug("Aguardando thread VoskWakeWordListener finalizar...")
            self.listen_thread.join(timeout=2.0)
            if self.listen_thread.is_alive():
                log_warning("Thread VoskWakeWordListener não finalizou no tempo esperado")
        
        # INTEGRAÇÃO FASE 2: Emite estado "hidden" quando para de escutar
        from utils.event_emitter import get_event_emitter
        emitter = get_event_emitter()
        emitter.emit_state_change("hidden")
        
        log_debug("Escuta de wake word Vosk parada - Estado: hidden")
    
    def cleanup(self) -> None:
        """Limpa recursos"""
        self.stop_listening()
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=1.0)
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        if hasattr(self, 'audio'):
            self.audio.terminate()
        log_debug("Recursos do detector Vosk liberados")

class FreeWakeWordListener:
    """
    Classe para detecção de wake word usando SpeechRecognition (fallback)
    Usa Google Speech API (gratuita) quando Vosk não está disponível
    """
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.callback_function: Optional[Callable] = None
        self.keywords = ["testar"]  # Palavras aceitas
        self.energy_threshold = 4000
        self.dynamic_energy_threshold = True
        self.listen_thread = None  # Armazena referência da thread
        
    def initialize(self) -> bool:
        """
        Inicializa o detector de wake word SpeechRecognition (fallback)
        
        Returns:
            bool: True se inicializou com sucesso
        """
        try:
            log_info("Inicializando detector de wake word SpeechRecognition (fallback)...")
            
            # Ajusta para ruído ambiente
            log_info("[AUDIO] Calibrando microfone para ruído ambiente...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            
            # Configura reconhecedor
            self.recognizer.energy_threshold = self.energy_threshold
            self.recognizer.dynamic_energy_threshold = self.dynamic_energy_threshold
            self.recognizer.pause_threshold = 0.5  # Pausa menor para responsividade
            self.recognizer.phrase_threshold = 0.3
            
            log_info("[OK] Detector de wake word SpeechRecognition inicializado")
            log_info(f"[SCAN] Detectando palavras: {', '.join(self.keywords)}")
            log_info(f"[ENERGY] Limite de energia: {self.recognizer.energy_threshold}")
            return True
            
        except Exception as e:
            log_error(f"Erro ao inicializar detector SpeechRecognition: {e}")
            return False
    
    def set_callback(self, callback: Callable) -> None:
        """
        Define função callback para quando wake word for detectada
        
        Args:
            callback (Callable): Função a ser chamada quando wake word detectada
        """
        self.callback_function = callback
        log_debug("Callback definido para wake word")
    
    def _listen_for_wake_word(self) -> None:
        """Thread de escuta contínua por wake word"""
        log_info("Escutando continuamente por wake word...")
        
        while self.is_listening:
            try:
                # Escuta por áudio
                with self.microphone as source:
                    # Timeout curto para permitir parada do loop
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                
                # Reconhece fala em background thread
                threading.Thread(
                    target=self._process_audio_for_wake_word,
                    args=(audio,),
                    daemon=True
                ).start()
                
            except sr.WaitTimeoutError:
                # Timeout é normal, continua o loop
                continue
            except Exception as e:
                if self.is_listening:  # Só loga se ainda deveria estar escutando
                    log_error(f"Erro na escuta de wake word: {e}")
                    time.sleep(1)  # Pausa antes de tentar novamente
    
    def _process_audio_for_wake_word(self, audio) -> None:
        """
        Processa áudio em busca de wake word
        
        Args:
            audio: Áudio capturado para processamento
        """
        try:
            # Usa Google Speech API (gratuita) para reconhecimento
            text = self.recognizer.recognize_google(audio, language="pt-BR")
            text_normalized = unidecode(text.lower().strip())
            
            log_debug(f"[AUDIO] Áudio reconhecido: '{text_normalized}'")
            
            # Verifica se contém wake word
            for keyword in self.keywords:
                if keyword in text_normalized:
                    log_info(f"[OK] Wake word detectada: '{keyword}' em '{text_normalized}'")
                    
                    # INTEGRAÇÃO FASE 2: Emite evento para Tauri
                    from utils.event_emitter import emit_wake_word
                    emit_wake_word(keyword)
                    
                    if self.callback_function:
                        self.callback_function(keyword)
                    break
                    
        except sr.UnknownValueError:
            # Não conseguiu reconhecer - normal, não loga
            pass
        except sr.RequestError as e:
            log_warning(f"Erro no serviço de reconhecimento: {e}")
        except Exception as e:
            log_debug(f"Erro no processamento de áudio: {e}")
    
    def start_listening(self) -> bool:
        """
        Inicia a escuta por wake word
        
        Returns:
            bool: True se iniciou com sucesso
        """
        if self.is_listening:
            log_warning("Wake word listener já está ativo")
            return True
        
        self.is_listening = True
        
        # INTEGRAÇÃO FASE 2: Emite estado "waiting" quando começa a escutar
        from utils.event_emitter import get_event_emitter
        emitter = get_event_emitter()
        emitter.emit_state_change("waiting")
        
        # Inicia thread de escuta
        listen_thread = threading.Thread(
            target=self._listen_for_wake_word,
            daemon=True,
            name="WakeWordListener"
        )
        listen_thread.start()
        
        log_info("Escuta de wake word iniciada")
        return True
    
    def stop_listening(self) -> None:
        """Para a escuta de wake word"""
        self.is_listening = False
        
        # INTEGRAÇÃO FASE 2: Emite estado "hidden" quando para de escutar
        from utils.event_emitter import get_event_emitter
        emitter = get_event_emitter()
        emitter.emit_state_change("hidden")
        
        log_debug("Escuta de wake word parada - Estado: hidden")
    
    def cleanup(self) -> None:
        """Limpa recursos"""
        self.stop_listening()
        log_debug("Recursos do detector liberados")

class VolumeBasedWakeWordListener:
    """
    Listener de fallback baseado em volume de áudio
    Para uso quando não há internet ou falha no reconhecimento online
    """
    
    def __init__(self):
        self.audio_capture = AudioCapture()
        self.is_listening = False
        self.callback_function: Optional[Callable] = None
        self.volume_threshold = 0.05
        self.consecutive_speech_chunks = 0
        self.required_speech_chunks = 8  # ~0.5 segundos de fala
        
    def initialize(self) -> bool:
        """Inicializa listener baseado em volume"""
        log_warning("Usando detector de wake word baseado em volume (fallback)")
        log_info("Para melhor detecção, verifique conexão com internet")
        return True
    
    def set_callback(self, callback: Callable) -> None:
        """Define callback para detecção"""
        self.callback_function = callback
    
    def start_listening(self) -> bool:
        """Inicia escuta baseada em volume"""
        if not self.audio_capture.start_stream():
            return False
        
        self.is_listening = True
        
        # INTEGRAÇÃO FASE 2: Emite estado "waiting" quando começa a escutar
        from utils.event_emitter import get_event_emitter
        emitter = get_event_emitter()
        emitter.emit_state_change("waiting")
        
        # Thread de escuta
        listen_thread = threading.Thread(
            target=self._volume_listen_loop,
            daemon=True,
            name="VolumeWakeWordListener"
        )
        listen_thread.start()
        
        log_info("Escuta baseada em volume iniciada")
        log_info("Fale alto para ativar (detecta qualquer fala)")
        return True
    
    def _volume_listen_loop(self) -> None:
        """Loop de escuta baseado em volume"""
        silent_chunks = 0
        
        while self.is_listening:
            try:
                audio_data = self.audio_capture.read_audio_chunk()
                if audio_data is None:
                    continue
                
                volume = calculate_volume(audio_data)
                
                if volume > self.volume_threshold:
                    self.consecutive_speech_chunks += 1
                    silent_chunks = 0
                    
                    # Se detectou fala suficiente, considera como wake word
                    if self.consecutive_speech_chunks >= self.required_speech_chunks:
                        log_info("[OK] Atividade de voz detectada (fallback)")
                        self.consecutive_speech_chunks = 0
                        
                        if self.callback_function:
                            self.callback_function("voice_detected")
                        
                        # Pausa para evitar múltiplas detecções
                        time.sleep(2)
                else:
                    silent_chunks += 1
                    if silent_chunks > 20:  # Reset após silêncio
                        self.consecutive_speech_chunks = 0
                        
            except Exception as e:
                if self.is_listening:
                    log_error(f"Erro no listener de volume: {e}")
                    time.sleep(1)
    
    def stop_listening(self) -> None:
        """Para escuta baseada em volume"""
        self.is_listening = False
        self.audio_capture.stop_stream()
        
        # INTEGRAÇÃO FASE 2: Emite estado "hidden" quando para de escutar
        from utils.event_emitter import get_event_emitter
        emitter = get_event_emitter()
        emitter.emit_state_change("hidden")
    
    def cleanup(self) -> None:
        """Limpa recursos"""
        self.stop_listening()
        self.audio_capture.cleanup()

# Instância global do listener
vosk_listener: Optional[VoskWakeWordListener] = None
speech_listener: Optional[FreeWakeWordListener] = None
volume_listener: Optional[VolumeBasedWakeWordListener] = None

def initialize_wake_word_detection() -> bool:
    """
    Inicializa detecção de wake word (prioriza Vosk offline)
    
    Returns:
        bool: True se inicializou com sucesso
    """
    global vosk_listener, speech_listener, volume_listener
    
    # Se já existe uma instância ativa, não cria outra
    if vosk_listener is not None:
        log_debug("Detector Vosk já inicializado, reutilizando instância")
        return True
    if speech_listener is not None:
        log_debug("Detector SpeechRecognition já inicializado, reutilizando instância") 
        return True
    if volume_listener is not None:
        log_debug("Detector de volume já inicializado, reutilizando instância")
        return True
    
    # Tenta inicializar Vosk primeiro (offline)
    if VOSK_AVAILABLE:
        vosk_listener = VoskWakeWordListener()
        if vosk_listener.initialize():
            log_info("Usando detector Vosk (offline)")
            return True
        else:
            log_warning("Vosk falhou, tentando SpeechRecognition...")
    
    # Se Vosk falhar, usa SpeechRecognition (online)
    speech_listener = FreeWakeWordListener()
    if speech_listener.initialize():
        log_info("Usando detector SpeechRecognition (online)")
        return True
    
    # Se ambos falharem, usa fallback baseado em volume
    log_warning("Detectores de fala falharam, usando fallback baseado em volume")
    volume_listener = VolumeBasedWakeWordListener()
    return volume_listener.initialize()

def set_wake_word_callback(callback: Callable) -> None:
    """
    Define callback para wake word detectada
    
    Args:
        callback (Callable): Função a ser chamada
    """
    global vosk_listener, speech_listener, volume_listener
    
    if vosk_listener:
        vosk_listener.set_callback(callback)
    elif speech_listener:
        speech_listener.set_callback(callback)
    elif volume_listener:
        volume_listener.set_callback(callback)

def start_wake_word_listening() -> bool:
    """
    Inicia escuta por wake word
    
    Returns:
        bool: True se iniciou com sucesso
    """
    global vosk_listener, speech_listener, volume_listener
    
    if vosk_listener:
        return vosk_listener.start_listening()
    elif speech_listener:
        return speech_listener.start_listening()
    elif volume_listener:
        return volume_listener.start_listening()
    
    log_error("Nenhum listener de wake word inicializado")
    return False

def stop_wake_word_listening() -> None:
    """Para escuta de wake word"""
    global vosk_listener, speech_listener, volume_listener
    
    if vosk_listener:
        vosk_listener.stop_listening()
    elif speech_listener:
        speech_listener.stop_listening()
    elif volume_listener:
        volume_listener.stop_listening()

def cleanup_wake_word_detection() -> None:
    """Limpa recursos de detecção de wake word"""
    global vosk_listener, speech_listener, volume_listener
    
    if vosk_listener:
        vosk_listener.cleanup()
        vosk_listener = None
    
    if speech_listener:
        speech_listener.cleanup()
        speech_listener = None
    
    if volume_listener:
        volume_listener.cleanup()
        volume_listener = None
