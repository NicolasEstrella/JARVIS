"""
Jarvis Assistant - Main Entry Point
Ponto de entrada principal da aplicação Jarvis
"""

import sys
import os

# Adiciona o diretório do projeto ao path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.background_service import start_background_service
from utils.logger import log_info, log_error

def main():
    """
    Função principal - inicia o serviço Jarvis em background
    """
    try:
        log_info("  Iniciando Jarvis Assistant...")
        log_info(f"[ARQUIVO] Diretório de trabalho: {os.getcwd()}")
        log_info(f"Python: {sys.version}")
        log_info("[AUDIO] Iniciando escuta em background...")
        
        start_background_service()
    except KeyboardInterrupt:
        log_info("[INFO] Jarvis Assistant finalizado pelo usuário")
    except Exception as e:
        log_error(f"[ERRO] Erro fatal no Jarvis Assistant: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()