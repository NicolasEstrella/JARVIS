"""
Sistema de Logging para o Jarvis Assistant
Fornece logging padronizado com timestamps e cores
"""

import logging
import os
import sys
from datetime import datetime
from colorama import init, Fore, Style

# Inicializa colorama para Windows
init(autoreset=True)

# Fix para encoding no Windows
def safe_print(message: str) -> None:
    """
    Print seguro que funciona com emojis no Windows
    """
    try:
        print(message)
    except UnicodeEncodeError:
        # Remove emojis e caracteres especiais se houver erro
        safe_message = message.encode('ascii', 'ignore').decode('ascii')
        print(safe_message)

# Configuração do logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jarvis.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('jarvis')

def log_info(message: str) -> None:
    """
    Loga uma mensagem de informação com timestamp
    
    Args:
        message (str): Mensagem a ser logada
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    colored_message = f"{Fore.GREEN}[{timestamp}] {message}{Style.RESET_ALL}"
    safe_print(colored_message)
    # Log apenas texto limpo para arquivo
    clean_message = message.encode('ascii', 'ignore').decode('ascii')
    logger.info(clean_message)

def log_error(message: str) -> None:
    """
    Loga uma mensagem de erro com timestamp
    
    Args:
        message (str): Mensagem de erro a ser logada
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    colored_message = f"{Fore.RED}[{timestamp}] ERRO: {message}{Style.RESET_ALL}"
    safe_print(colored_message)
    # Log apenas texto limpo para arquivo
    clean_message = message.encode('ascii', 'ignore').decode('ascii')
    logger.error(clean_message)

def log_warning(message: str) -> None:
    """
    Loga uma mensagem de aviso com timestamp
    
    Args:
        message (str): Mensagem de aviso a ser logada
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    colored_message = f"{Fore.YELLOW}[{timestamp}] [WARN] {message}{Style.RESET_ALL}"
    print(colored_message)
    logger.warning(message)

def log_debug(message: str) -> None:
    """
    Loga uma mensagem de debug com timestamp
    
    Args:
        message (str): Mensagem de debug a ser logada
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    colored_message = f"{Fore.BLUE}[{timestamp}] [SCAN] {message}{Style.RESET_ALL}"
    print(colored_message)
    logger.debug(message)