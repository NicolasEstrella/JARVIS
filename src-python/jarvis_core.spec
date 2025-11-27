# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[
        ('C:/Users/nicol/AppData/Local/Programs/Python/Python312/Lib/site-packages/vosk/*.dll', 'vosk'),
    ],
    datas=[
        ('models/vosk-model-small-pt-0.3', 'models/vosk-model-small-pt-0.3'),
        ('workflows.json', '.'),
    ],
    hiddenimports=[
        'vosk',
        'sounddevice',
        'numpy',
        'scipy',
        'speech_recognition',
        'pydub',
        'pyautogui',
        'keyboard',
        'watchdog',
        'pycaw',
        'comtypes',
        'psutil',
        'pyaudio',
        'json',
        'threading',
        'unidecode',
    ],
    hookspath=['.'],  # Hook customizado na pasta atual
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='jarvis_core',
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
