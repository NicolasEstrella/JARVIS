#   Jarvis Assistant - Assistente de Voz Local

Um assistente de voz **100% gratuito** em Python que responde ao wake word "Jarvis" e executa comandos ou entra em modo ditado.

## 🎯 Características Principais

- ✅ **100% Gratuito** - Sem APIs pagas ou access keys
- 🎤 **Wake Word Detection** - Detecta "Jarvis" usando SpeechRecognition + Google API
- �️ **Reconhecimento de Fala** - Vosk (offline) + Google Speech (online)
- ⚙️ **Comandos por Voz** - Sistema extensível de comandos
- 📝 **Modo Ditado** - Transcreve fala para texto automaticamente
- 🔄 **Executável Standalone** - Gera .exe com PyInstaller
- 🖥️ **Cross-Platform** - Windows, Linux, macOS

## �📁 Estrutura do Projeto

```
JARVIS/
├── main.py                    # Ponto de entrada
├── build_exe.py               # Script para gerar executável
├── requirements.txt           # Dependências
├── README.md                  # Esta documentação
├── core/                      # Módulos principais
│   ├── listener.py            # Wake word detection (gratuito)
│   ├── speech_to_text.py      # Reconhecimento de fala (Vosk)
│   ├── command_handler.py     # Processamento de comandos
│   ├── dictation_mode.py      # Modo ditado
│   └── background_service.py  # Serviço em background
├── utils/                     # Utilitários
│   ├── logger.py              # Sistema de logs
│   ├── audio_utils.py         # Funções de áudio
│   └── system_utils.py        # Automação do sistema
└── models/                    # Modelos de IA
    └── README.md              # Instruções para Vosk
```

## 🎙️ Funcionalidades

1. **Wake Word "Jarvis"** - Detecta a palavra-chave usando Porcupine
2. **Reconhecimento de Fala** - Transcreve áudio usando Vosk
3. **Comandos por Palavra-chave** - Executa ações baseadas em comandos específicos
4. **Modo Ditado** - Transcreve fala para texto quando não há comandos específicos
5. **Serviço em Background** - Roda continuamente como daemon
6. **Logging Estruturado** - Sistema de logs com timestamps

##   Instalação e Configuração

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Baixar Modelo Vosk

Baixe o modelo Vosk em português:
```bash
# Linux/Mac
wget https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip
unzip vosk-model-small-pt-0.3.zip -d models/

# Windows (PowerShell)
Invoke-WebRequest -Uri "https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip" -OutFile "vosk-model-small-pt-0.3.zip"
Expand-Archive -Path "vosk-model-small-pt-0.3.zip" -DestinationPath "models/"
```

### 3. Configurar Microfone

Certifique-se de que seu microfone está configurado corretamente no sistema.

## 🏃‍♂️ Como Usar

### Execução Simples
```bash
python main.py
```

### Comandos Disponíveis

Após dizer "Teste", você pode usar:

### 📋 Tabela de Comandos

#### 🎤 Modo Escuta Contínua
Após ativar com **"teste"**, o Jarvis entra em modo contínuo onde você pode dar vários comandos seguidos:

| Comando | Ação | Categoria |
|---------|------|-----------|
| **"codigo"** | Abre VS Code | 🖥️ Aplicações |
| **"bloco"** | Abre Bloco de Notas | 🖥️ Aplicações |
| **"calculadora"** | Abre Calculadora | 🖥️ Aplicações |
| **"arquivos"** | Abre Explorador de Arquivos | 🖥️ Aplicações |
| **"navegador"** | Abre Chrome | 🖥️ Aplicações |
| **"musica"** | Abre Spotify | 🖥️ Aplicações |
| **"terminal"** | Abre Terminal/CMD | 🖥️ Aplicações |
| **"tab"** | Pressiona Tab | ⌨️ Teclas |
| **"enter"** | Pressiona Enter | ⌨️ Teclas |
| **"escape"** | Pressiona Escape | ⌨️ Teclas |
| **"espaco"** | Pressiona Espaço | ⌨️ Teclas |
| **"copiar"** | Ctrl+C | 📋 Clipboard |
| **"colar"** | Ctrl+V | 📋 Clipboard |
| **"desfazer"** | Ctrl+Z | 📋 Edição |
| **"salvar"** | Ctrl+S | � Edição |
| **"selecionar"** | Ctrl+A (selecionar tudo) | 📋 Edição |
| **"minimizar"** | Minimiza janela | 🪟 Janela |
| **"maximizar"** | Maximiza janela | 🪟 Janela |
| **"fechar"** | Fecha janela atual | 🪟 Janela |
| **"trocar"** | Alt+Tab (trocar janela) | 🪟 Janela |
| **"voltar"** | Volta página/pasta | 🧭 Navegação |
| **"avancar"** | Avança página/pasta | 🧭 Navegação |
| **"atualizar"** | F5 (recarregar) | 🧭 Navegação |
| **"nova linha"** | Enter (quebra linha) | ✏️ Texto |
| **"apagar"** | Backspace | ✏️ Texto |
| **"deletar"** | Delete | ✏️ Texto |

####   Comandos de Controle

| Comando | Ação | Tipo |
|---------|------|------|
| **"parar"** | Sai do modo contínuo | 🔄 Controle |
| **"finalizar"** | Sai do modo contínuo | 🔄 Controle |
| **"sair"** | Sai do modo contínuo | 🔄 Controle |
| **"tchau"** | Sai do modo contínuo | 🔄 Controle |
| **"reiniciar"** | Reinicia o Jarvis | 🔄 Sistema |
| **"quero falar contigo"** | Inicia modo ditado | � Ditado |
| **"para a porra toda"** | Para aplicação completamente | 🚫 Emergência |

#### ⏰ Comportamentos Automáticos
- **Timeout**: Se ficar **10 segundos** sem falar, sai do modo contínuo
- **Modo Ditado**: Ativado apenas com comando **"quero falar contigo"**
- **Ditado Responsivo**: Texto aparece conforme você fala

### 📝 Modo Ditado Avançado

O Jarvis possui um modo de ditado responsivo que digita o texto conforme você fala:

#### Como Usar:
1. **Ativar**: Diga "**teste**" para acordar o Jarvis
2. **Iniciar Ditado**: Diga "**quero falar contigo**"
3. **Falar**: Comece a falar naturalmente - o texto aparece em tempo real
4. **Parar**: Diga "**parar ditado**" ou aguarde 3 segundos de silêncio

#### Características:
- [ENERGY] **Responsivo**: Texto aparece conforme você fala
- 🎯 **Micro Delays**: Velocidade de digitação natural (25ms entre teclas)
- ⏰ **Timeout Inteligente**: Para automaticamente após 3s de silêncio
- 🎤 **Escuta Contínua**: Processa fala em blocos pequenos para maior fluidez
- 📝 **Digitação Imediata**: Não acumula texto - digita instantaneamente

#### Exemplo de Uso:
```
Você: "teste"
Jarvis: [Ativa modo contínuo]

Você: "quero falar contigo" 
Jarvis: [Inicia modo ditado]

Você: "Olá, este é um exemplo de ditado responsivo..."
[Texto aparece instantaneamente enquanto você fala]

Você: "parar ditado"
Jarvis: [Para ditado e volta ao modo comando]
```

##   Gerar Executável (.exe)

Para criar um executável standalone que pode ser distribuído sem Python:

### 1. Instalar PyInstaller
```bash
pip install pyinstaller
```

### 2. Gerar Executável
```bash
python build_exe.py
```

Este script irá:
- ✅ Verificar e instalar dependências necessárias
- 🎨 Criar ícone para o executável
- 📄 Gerar arquivo de especificação otimizado
- 🔨 Compilar executável com PyInstaller
- 📦 Criar pacote portátil completo
- 🧹 Limpar arquivos temporários

### 3. Resultado
Após a execução, você terá:
- `dist/JarvisAssistant.exe` - Executável principal
- `JarvisAssistant_Portable/` - Pacote completo para distribuição

### 4. Distribuição
- Copie toda a pasta `JarvisAssistant_Portable` 
- O executável funcionará em qualquer PC Windows sem Python instalado
- **Requer internet** para reconhecimento de voz (Google API gratuita)

## �🔧 Executar como Serviço

### Windows (Serviço do Sistema)

1. Crie um arquivo `jarvis_service.py`:
```python
import win32serviceutil
import win32service
import win32event
import subprocess
import os

class JarvisService(win32serviceutil.ServiceFramework):
    _svc_name_ = "JarvisAssistant"
    _svc_display_name_ = "Jarvis Voice Assistant"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        
    def SvcDoRun(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        subprocess.run([
            "python", 
            os.path.join(script_dir, "main.py")
        ])

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(JarvisService)
```

2. Instalar o serviço:
```bash
python jarvis_service.py install
python jarvis_service.py start
```

### Linux (systemd)

1. Crie o arquivo `/etc/systemd/system/jarvis.service`:
```ini
[Unit]
Description=Jarvis Voice Assistant
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/jarvis_assistant
ExecStart=/usr/bin/python3 /path/to/jarvis_assistant/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

2. Ativar o serviço:
```bash
sudo systemctl enable jarvis.service
sudo systemctl start jarvis.service
```

## 🔮 Migração Futura para Rust

Este projeto foi estruturado pensando numa futura migração para Rust. As seguintes bibliotecas podem ser utilizadas:

- **Audio**: `cpal` para captura de áudio
- **Wake Word**: `porcupine-rs` para detecção de wake word  
- **Speech Recognition**: `vosk-rs` para reconhecimento de fala
- **System Integration**: `enigo` para automação do sistema

### Pontos de Migração:

1. **`audio_utils.py`** → Rust com `cpal`
2. **`listener.py`** → Rust com `porcupine-rs`  
3. **`speech_to_text.py`** → Rust com `vosk-rs`
4. **`system_utils.py`** → Rust com `enigo`

## 🐛 Troubleshooting

### Problemas de Áudio
- Verifique se o microfone está conectado
- Teste a captura de áudio com outras aplicações
- Ajuste os níveis de volume do microfone

### Problemas de Dependências
- Certifique-se de que está usando Python 3.8+
- No Windows, pode ser necessário instalar Visual C++ Build Tools
- No Linux, instale `python3-dev` e `portaudio19-dev`

### Performance
- O modelo Vosk pode ser trocado por versões maiores para melhor precisão
- Ajuste os timeouts no código conforme necessário

## 📝 License

MIT License - veja LICENSE para detalhes.

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request