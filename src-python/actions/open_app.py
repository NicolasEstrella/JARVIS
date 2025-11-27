"""
Open App Action - Abre aplicações do sistema
"""

import subprocess
import os
import sys
from pathlib import Path
from typing import Union
from utils.logger import log_info, log_error, log_debug

# Mapeamento de nomes comuns para executáveis do Windows
COMMON_APPS = {
    'chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    'firefox': r'C:\Program Files\Mozilla Firefox\firefox.exe',
    'edge': r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    'code': r'C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\Code.exe',
    'vscode': r'C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\Code.exe',
    'notepad': 'notepad.exe',
    'calc': 'calc.exe',
    'calculadora': 'calc.exe',
    'explorer': 'explorer.exe',
    'cmd': 'cmd.exe',
    'powershell': 'powershell.exe',
    'paint': 'mspaint.exe',
    'spotify': r'C:\Users\{}\AppData\Roaming\Spotify\Spotify.exe',
    'discord': r'C:\Users\{}\AppData\Local\Discord\app-1.0.9005\Discord.exe',
    'steam': r'C:\Program Files (x86)\Steam\steam.exe',
    'excel': r'C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE',
    'word': r'C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE',
    'outlook': r'C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE',
    'teams': r'C:\Users\{}\AppData\Local\Microsoft\Teams\current\Teams.exe',
}


def _resolve_app_path(app_name: str) -> str:
    """
    Resolve o caminho completo do aplicativo
    
    Args:
        app_name: Nome ou caminho do app
        
    Returns:
        Caminho completo do executável
    """
    # Se já é um caminho completo, retorna
    if os.path.isabs(app_name) and os.path.exists(app_name):
        return app_name
    
    # Verifica se é um nome comum
    app_lower = app_name.lower()
    if app_lower in COMMON_APPS:
        path_template = COMMON_APPS[app_lower]
        
        # Substitui {} pelo nome de usuário se necessário
        if '{}' in path_template:
            username = os.getenv('USERNAME', 'User')
            path = path_template.format(username)
        else:
            path = path_template
        
        if os.path.exists(path):
            return path
        else:
            log_debug(f"Caminho padrão não encontrado: {path}, tentando nome direto")
            return app_name
    
    # Se tem extensão .exe, tenta executar diretamente
    if app_name.endswith('.exe'):
        return app_name
    
    # Caso contrário, retorna como está (pode ser comando do sistema)
    return app_name


def run(path: Union[str, Path], args: list = None, wait: bool = False) -> bool:
    """
    Abre uma aplicação
    
    Args:
        path: Nome ou caminho completo do aplicativo
        args: Argumentos adicionais para passar ao app
        wait: Se deve esperar o app fechar
        
    Returns:
        True se executou com sucesso, False caso contrário
        
    Examples:
        >>> run('code')  # Abre VS Code
        >>> run('chrome')  # Abre Google Chrome
        >>> run('calc')  # Abre Calculadora
        >>> run(r'C:\Program Files\App\app.exe')  # Caminho completo
        >>> run('notepad', ['arquivo.txt'])  # Com argumentos
    """
    try:
        app_path = str(path) if isinstance(path, Path) else path
        resolved_path = _resolve_app_path(app_path)
        
        log_info(f"  Abrindo aplicação: {resolved_path}")
        
        # Monta comando
        cmd = [resolved_path]
        if args:
            cmd.extend(args)
        
        # Executa aplicação
        if sys.platform == 'win32':
            # No Windows, usa shell para apps do sistema
            if not os.path.isabs(resolved_path):
                subprocess.Popen(
                    ' '.join(cmd),
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.DETACHED_PROCESS
                )
            else:
                # Para caminhos absolutos, executa diretamente
                subprocess.Popen(
                    cmd,
                    creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.DETACHED_PROCESS
                )
        else:
            # Linux/Mac
            subprocess.Popen(cmd)
        
        log_info(f"[OK] Aplicação '{app_path}' aberta com sucesso")
        return True
        
    except FileNotFoundError:
        log_error(f"[ERRO] Aplicação não encontrada: {path}")
        return False
    except PermissionError:
        log_error(f"[ERRO] Sem permissão para executar: {path}")
        return False
    except Exception as e:
        log_error(f"[ERRO] Erro ao abrir aplicação '{path}': {e}")
        return False


def open_url(url: str) -> bool:
    """
    Abre uma URL no navegador padrão
    
    Args:
        url: URL para abrir
        
    Returns:
        True se executou com sucesso
    """
    try:
        import webbrowser
        log_info(f"[WEB] Abrindo URL: {url}")
        webbrowser.open(url)
        return True
    except Exception as e:
        log_error(f"[ERRO] Erro ao abrir URL '{url}': {e}")
        return False


def open_file(filepath: Union[str, Path]) -> bool:
    """
    Abre um arquivo com o aplicativo padrão
    
    Args:
        filepath: Caminho do arquivo
        
    Returns:
        True se executou com sucesso
    """
    try:
        filepath = str(filepath) if isinstance(filepath, Path) else filepath
        
        if not os.path.exists(filepath):
            log_error(f"[ERRO] Arquivo não encontrado: {filepath}")
            return False
        
        log_info(f"Abrindo arquivo: {filepath}")
        
        if sys.platform == 'win32':
            os.startfile(filepath)
        elif sys.platform == 'darwin':  # macOS
            subprocess.Popen(['open', filepath])
        else:  # Linux
            subprocess.Popen(['xdg-open', filepath])
        
        return True
        
    except Exception as e:
        log_error(f"[ERRO] Erro ao abrir arquivo '{filepath}': {e}")
        return False


def open_folder(folderpath: Union[str, Path]) -> bool:
    """
    Abre uma pasta no explorador de arquivos
    
    Args:
        folderpath: Caminho da pasta
        
    Returns:
        True se executou com sucesso
    """
    try:
        folderpath = str(folderpath) if isinstance(folderpath, Path) else folderpath
        
        if not os.path.exists(folderpath):
            log_error(f"[ERRO] Pasta não encontrada: {folderpath}")
            return False
        
        log_info(f"[ARQUIVO] Abrindo pasta: {folderpath}")
        
        if sys.platform == 'win32':
            subprocess.Popen(['explorer', folderpath])
        elif sys.platform == 'darwin':  # macOS
            subprocess.Popen(['open', folderpath])
        else:  # Linux
            subprocess.Popen(['xdg-open', folderpath])
        
        return True
        
    except Exception as e:
        log_error(f"[ERRO] Erro ao abrir pasta '{folderpath}': {e}")
        return False
