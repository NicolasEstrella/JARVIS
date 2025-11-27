"""
Modo Ditado para o Jarvis Assistant
Transcreve fala contínua para texto e escreve no sistema ou arquivo

Funcionalidades:
- Transcrição contínua de fala em tempo real usando Vosk
- Processamento em chunks pequenos para responsividade
- Parada automática por timeout (5 segundos de silêncio)
- Parada manual com comando "parar ditado"
- Saída para terminal, arquivo ou digitação direta
- Digitação em blocos pequenos conforme você fala
"""

import time
import threading
import json
import pyaudio
import vosk
from typing import Optional, IO
from utils.system_utils import system_controller
from utils.logger import log_info, log_error, log_debug

class DictationMode:
    """
    Classe para modo de ditado contínuo e responsivo usando Vosk
    """
    
    def __init__(self):
        self.is_active = False
        self.silence_timeout = 5.0  # Timeout de silêncio aumentado
        self.last_speech_time = time.time()
        self.dictated_text = []
        self.output_file: Optional[IO] = None
        self.output_mode = "type"  # Padrão para digitação
        
        # Configurações de áudio otimizadas para tempo real
        self.chunk_size = 1024  # Menor chunk para mais responsividade
        self.sample_rate = 16000
        self.channels = 1
        
        # Inicializa Vosk
        self.vosk_model = None
        self.vosk_rec = None
        self.audio = None
        self.stream = None
        
        # Buffer para texto parcial
        self.partial_text_buffer = ""
        self.last_partial_text = ""
        
    def _initialize_vosk(self) -> bool:
        """
        Inicializa o modelo Vosk para reconhecimento offline
        
        Returns:
            bool: True se inicializou com sucesso
        """
        try:
            import os
            model_path = "models/vosk-model-small-pt-0.3"
            
            if not os.path.exists(model_path):
                log_error("[ERRO] Modelo Vosk não encontrado. Usando fallback online.")
                return False
            
            log_info("Carregando modelo Vosk para ditado...")
            self.vosk_model = vosk.Model(model_path)
            self.vosk_rec = vosk.KaldiRecognizer(self.vosk_model, self.sample_rate)
            
            # Configura para retornar resultados parciais
            self.vosk_rec.SetWords(True)
            
            log_info("[OK] Modelo Vosk carregado com sucesso")
            return True
            
        except Exception as e:
            log_error(f"[ERRO] Erro ao carregar Vosk: {e}")
            return False
    
    def _initialize_audio_stream(self) -> bool:
        """
        Inicializa stream de áudio para captura em tempo real
        
        Returns:
            bool: True se inicializou com sucesso
        """
        try:
            self.audio = pyaudio.PyAudio()
            
            # Configura stream de áudio
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            log_debug("[AUDIO] Stream de áudio inicializado")
            return True
            
        except Exception as e:
            log_error(f"[ERRO] Erro ao inicializar áudio: {e}")
            return False
    
    def start_dictation(self, 
                       initial_text: str = "", 
                       output_mode: str = "type",
                       output_file_path: str = "dictation_output.txt") -> None:
        """
        Inicia o modo ditado
        
        Args:
            initial_text (str): Texto inicial (primeira frase captada)
            output_mode (str): Modo de saída ("terminal", "file", "type")
            output_file_path (str): Caminho do arquivo se modo for "file"
        """
        if self.is_active:
            log_info("[WARN] Modo ditado já está ativo")
            return
        
        self.is_active = True
        self.output_mode = output_mode
        self.dictated_text = []
        self.last_speech_time = time.time()
        self.partial_text_buffer = ""
        self.last_partial_text = ""
        
        log_info(f"[DICTATION] Iniciando modo ditado em tempo real (saída: {output_mode})")
        log_info("[AUDIO] Fale naturalmente - o texto aparecerá enquanto você fala")
        log_info("Para sair: 'parar ditado' ou 'sair desse modo'")
        log_info("Ou aguarde 5 segundos de silêncio")
        
        # Configura saída
        if output_mode == "file":
            try:
                self.output_file = open(output_file_path, "w", encoding="utf-8")
                log_info(f"[SAVE] Salvando ditado em: {output_file_path}")
            except Exception as e:
                log_error(f"Erro ao abrir arquivo: {e}")
                self.output_mode = "terminal"
        
        # Inicializa Vosk
        if not self._initialize_vosk():
            log_error("[ERRO] Falha ao inicializar Vosk - ditado não disponível")
            self.is_active = False
            return
        
        # Inicializa áudio
        if not self._initialize_audio_stream():
            log_error("[ERRO] Falha ao inicializar áudio - ditado não disponível")
            self.is_active = False
            return
        
        # Inicia ditado em thread separada
        dictation_thread = threading.Thread(target=self._run_realtime_dictation, daemon=True)
        dictation_thread.start()
        
        # Inicia monitor de timeout
        timeout_thread = threading.Thread(target=self._timeout_monitor, daemon=True)
        timeout_thread.start()
        
    def _run_realtime_dictation(self) -> None:
        """
        Executa ditado em tempo real usando Vosk
        """
        log_info("[AUDIO] Modo ditado ativo - comece a falar...")
        
        try:
            while self.is_active and self.stream:
                try:
                    # Lê chunk de áudio
                    data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                    
                    if self.vosk_rec.AcceptWaveform(data):
                        # Resultado final (frase completa)
                        result = json.loads(self.vosk_rec.Result())
                        text = result.get('text', '').strip()
                        
                        if text:
                            self.last_speech_time = time.time()
                            
                            # Verifica comandos de parada
                            if any(cmd in text.lower() for cmd in ["parar ditado", "sair desse modo"]):
                                log_info(f"  Comando de saída detectado: '{text}'")
                                break
                            
                            # Processa texto final
                            self._process_final_text(text)
                            
                            # Limpa buffer parcial
                            self.partial_text_buffer = ""
                            self.last_partial_text = ""
                    else:
                        # Resultado parcial (ainda falando)
                        partial_result = json.loads(self.vosk_rec.PartialResult())
                        partial_text = partial_result.get('partial', '').strip()
                        
                        if partial_text and partial_text != self.last_partial_text:
                            self.last_speech_time = time.time()
                            
                            # Verifica comandos de parada também nos resultados parciais
                            if any(cmd in partial_text.lower() for cmd in ["parar ditado", "sair desse modo"]):
                                log_info(f"  Comando de saída detectado (parcial): '{partial_text}'")
                                break
                            
                            self._process_partial_text(partial_text)
                            self.last_partial_text = partial_text
                    
                except Exception as e:
                    log_error(f"[ERRO] Erro no processamento de áudio: {e}")
                    time.sleep(0.1)
                    
        except Exception as e:
            log_error(f"[ERRO] Erro no ditado em tempo real: {e}")
        finally:
            self._cleanup_audio()
            self._stop_dictation()
    
    def _process_partial_text(self, partial_text: str) -> None:
        """
        Processa texto parcial (ainda sendo falado)
        
        Args:
            partial_text (str): Texto parcial detectado
        """
        if not partial_text:
            return
        
        # Identifica novas palavras
        new_words = self._get_new_words(self.partial_text_buffer, partial_text)
        
        if new_words:
            log_debug(f"Parcial: {new_words}")
            
            # Verifica se contém comando de saída antes de digitar
            if any(cmd in new_words.lower() for cmd in ["parar ditado", "sair desse modo"]):
                log_debug("  Comando de saída detectado - não digitando")
                return
            
            # Digita novas palavras imediatamente
            if self.output_mode == "type":
                try:
                    # Digita palavra por palavra com espaço
                    for word in new_words.split():
                        system_controller.type_text(word + " ", delay=0.03)
                        time.sleep(0.05)  # Pequena pausa entre palavras
                        
                except Exception as e:
                    log_error(f"[ERRO] Erro ao digitar texto parcial: {e}")
            
            # Atualiza buffer
            self.partial_text_buffer = partial_text
    
    def _process_final_text(self, final_text: str) -> None:
        """
        Processa texto final (frase completa)
        
        Args:
            final_text (str): Texto final confirmado
        """
        if not final_text:
            return
        
        # Verifica se é comando de saída - não processa se for
        if any(cmd in final_text.lower() for cmd in ["parar ditado", "sair desse modo"]):
            log_info(f"  Comando de saída ignorado no processamento: {final_text}")
            return
        
        log_info(f"[OK] Frase completa: {final_text}")
        
        # Adiciona ao histórico
        self.dictated_text.append(final_text)
        
        # Processa conforme modo de saída
        if self.output_mode == "terminal":
            print(f"[DITADO] {final_text}")
            
        elif self.output_mode == "file" and self.output_file:
            try:
                self.output_file.write(final_text + ". ")
                self.output_file.flush()
            except Exception as e:
                log_error(f"[ERRO] Erro ao escrever no arquivo: {e}")
        
        # Para modo "type", as palavras já foram digitadas em tempo real
        # Só adiciona pontuação final se necessário
        elif self.output_mode == "type":
            # Se a frase não terminou com pontuação, adiciona ponto
            if final_text and final_text[-1] not in '.!?:;,':
                try:
                    system_controller.type_text(". ", delay=0.1)
                except Exception as e:
                    log_error(f"[ERRO] Erro ao adicionar pontuação: {e}")
    
    def _get_new_words(self, old_text: str, new_text: str) -> str:
        """
        Identifica palavras novas entre dois textos
        
        Args:
            old_text (str): Texto anterior
            new_text (str): Texto novo
            
        Returns:
            str: Apenas as palavras novas
        """
        if not new_text:
            return ""
        
        if not old_text:
            return new_text
        
        # Se o novo texto não contém o antigo, retorna o novo completo
        if old_text not in new_text:
            return new_text
        
        # Retorna apenas a parte nova
        if new_text.startswith(old_text):
            return new_text[len(old_text):].strip()
        
        return new_text
    
    def _timeout_monitor(self) -> None:
        """Monitor de timeout para parar ditado automaticamente"""
        while self.is_active:
            time.sleep(1.0)  # Verifica a cada segundo
            
            if time.time() - self.last_speech_time > self.silence_timeout:
                log_info(f"Timeout de {self.silence_timeout}s atingido - parando ditado")
                self._stop_dictation()
                break
    
    def _cleanup_audio(self) -> None:
        """Limpa recursos de áudio"""
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            
            if self.audio:
                self.audio.terminate()
                self.audio = None
                
            log_debug("Recursos de áudio limpos")
            
        except Exception as e:
            log_error(f"[ERRO] Erro ao limpar áudio: {e}")
    
    def _stop_dictation(self) -> None:
        """Para o modo ditado e limpa recursos"""
        if not self.is_active:
            return
        
        self.is_active = False
        
        # Limpa áudio
        self._cleanup_audio()
        
        # Fecha arquivo se aberto
        if self.output_file:
            try:
                self.output_file.close()
                self.output_file = None
            except Exception as e:
                log_error(f"[ERRO] Erro ao fechar arquivo: {e}")
        
        # Mostra resumo
        total_words = sum(len(text.split()) for text in self.dictated_text)
        total_sentences = len(self.dictated_text)

        log_info(f"[DICTATION] Ditado finalizado:")
        log_info(f"   • {total_sentences} frases completas")
        log_info(f"   • {total_words} palavras")
        log_info(f"   • Modo: {self.output_mode}")
        
        # Limpa dados
        self.dictated_text = []
        self.partial_text_buffer = ""
        self.last_partial_text = ""
    
    def stop(self) -> None:
        """Para o modo ditado externamente"""
        log_info("  Parando modo ditado...")
        self._stop_dictation()
    
    def is_dictation_active(self) -> bool:
        """
        Verifica se o modo ditado está ativo
        
        Returns:
            bool: True se ativo
        """
        return self.is_active
    
    def get_dictated_text(self) -> list:
        """
        Retorna todo o texto ditado
        
        Returns:
            list: Lista de frases ditadas
        """
        return self.dictated_text.copy()
    
    def set_silence_timeout(self, timeout_seconds: float) -> None:
        """
        Define timeout de silêncio
        
        Args:
            timeout_seconds (float): Timeout em segundos
        """
        self.silence_timeout = max(2.0, timeout_seconds)
        log_info(f"Timeout de silêncio definido para {self.silence_timeout}s")

# Instância global do modo ditado
dictation_mode = DictationMode()

def start_dictation_mode(initial_text: str = "", 
                        output_mode: str = "type",
                        output_file: str = "dictation_output.txt") -> None:
    """
    Inicia modo ditado
    
    Args:
        initial_text (str): Texto inicial
        output_mode (str): Modo de saída ("terminal", "file", "type")
        output_file (str): Arquivo de saída se modo for "file"
    """
    dictation_mode.start_dictation(initial_text, output_mode, output_file)

def stop_dictation_mode() -> None:
    """Para o modo ditado"""
    dictation_mode.stop()

def is_dictation_active() -> bool:
    """
    Verifica se ditado está ativo
    
    Returns:
        bool: True se ativo
    """
    return dictation_mode.is_dictation_active()

def get_dictated_text() -> list:
    """
    Obtém texto ditado
    
    Returns:
        list: Lista de frases ditadas
    """
    return dictation_mode.get_dictated_text()

def set_dictation_timeout(timeout: float) -> None:
    """
    Define timeout do ditado
    
    Args:
        timeout (float): Timeout em segundos
    """
    dictation_mode.set_silence_timeout(timeout)