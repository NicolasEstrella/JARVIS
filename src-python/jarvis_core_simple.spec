# -*- mode: python ; coding: utf-8 -*-

# Configuração simples do PyInstaller - SEM VOSK
# Usa apenas SpeechRecognition para evitar problemas de DLL

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('workflows.json', '.'),
    ],
    hiddenimports=[
        'speech_recognition',
        'sounddevice',
        'numpy',
        'pyautogui',
        'keyboard',
        'watchdog',
        'pycaw',
        'comtypes',
        'psutil',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['vosk'],  # Exclui Vosk deliberadamente
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='jarvis_core_simple',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)