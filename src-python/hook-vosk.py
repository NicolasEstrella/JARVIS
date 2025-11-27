"""
Hook customizado para o Vosk no PyInstaller
Garante que as DLLs necessárias sejam incluídas
"""
import os
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

# Coleta DLLs do Vosk
binaries = collect_dynamic_libs('vosk')

# Adiciona DLLs manualmente se não encontradas
vosk_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'site-packages', 'vosk')
if os.path.exists(vosk_path):
    dll_files = [
        'libgcc_s_seh-1.dll',
        'libstdc++-6.dll', 
        'libvosk.dll',
        'libwinpthread-1.dll'
    ]
    
    for dll in dll_files:
        dll_path = os.path.join(vosk_path, dll)
        if os.path.exists(dll_path):
            binaries.append((dll_path, 'vosk'))

print(f"Hook Vosk: {len(binaries)} DLLs encontradas")