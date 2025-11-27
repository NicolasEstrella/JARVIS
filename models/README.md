# Diretório para modelo Vosk

Este diretório deve conter o modelo Vosk em português para reconhecimento de fala.

## Download do Modelo

Execute um dos comandos abaixo para baixar o modelo:

### Windows (PowerShell):
```powershell
Invoke-WebRequest -Uri "https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip" -OutFile "vosk-model-small-pt-0.3.zip"
Expand-Archive -Path "vosk-model-small-pt-0.3.zip" -DestinationPath "."
```

### Linux/Mac:
```bash
wget https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip
unzip vosk-model-small-pt-0.3.zip
```

### Alternativa - Script Python:
```bash
python setup.py
```

## Estrutura Esperada

Após o download, você deve ter:
```
models/
└── vosk-model-small-pt-0.3/
    ├── am/
    ├── graph/
    ├── ivector/
    └── conf/
```

## Modelos Alternativos

Para melhor precisão, você pode usar modelos maiores:
- `vosk-model-pt-0.3` (1.2GB) - Melhor precisão
- `vosk-model-small-pt-0.3` (39MB) - Mais rápido, menor precisão

Modelos disponíveis em: https://alphacephei.com/vosk/models