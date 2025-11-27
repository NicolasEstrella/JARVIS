Place the packaged Python backend here as jarvis_core.exe.

How to build:
1) In the repo root, run: PowerShell build.ps1
   - This script will install Python deps, run PyInstaller, and copy dist/jarvis_core.exe here.
2) Or run manually in ./src-python:
   pyinstaller --onefile --noconsole main.py --name jarvis_core
   Then copy .\src-python\dist\jarvis_core.exe to this folder.

At bundle time, files in this folder are included via bundle.resources (tauri.conf.json).