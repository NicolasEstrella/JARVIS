# 🤖 Jarvis Desktop - Assistente de Voz com Workflows Customizáveis

Aplicação desktop completa e integrada usando **Tauri (Rust + React) + Python Backend**, funcionando como um assistente de voz local capaz de executar workflows automatizados através de comandos de voz.

![Tauri](https://img.shields.io/badge/Tauri-2.0-blue)
![React](https://img.shields.io/badge/React-19.1-61dafb)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Rust](https://img.shields.io/badge/Rust-1.70+-orange)

## ✨ Funcionalidades

- [AUDIO] **Reconhecimento de Voz Local** - 100% offline, sem APIs pagas
- 🔊 **Wake Word Detection** - Ativa com "Jarvis" ou palavra customizada
- 🎯 **Workflows Customizáveis** - Crie sequências de ações via interface gráfica
- 🪟 **System Tray** - Roda em segundo plano no Windows
- [ENERGY] **Ações Automatizadas**:
  - Abrir aplicações
  - Pressionar teclas e atalhos
  - Digitar texto
  - Controlar mouse
  - Screenshots
  - Controle de volume
- 📦 **Single EXE** - Empacotável em único executável
- 🎨 **Interface Moderna** - React + Design System personalizado

##   Quick Start

### Desenvolvimento:

```powershell
# Instalar dependências
npm install
cd src-python
pip install -r requirements.txt
cd ..

# Executar em modo dev
.\dev.ps1
# ou
npm run tauri dev
```

### Build para Produção:

```powershell
# Build automatizado completo
.\build.ps1
```

O instalador estará em: `src-tauri/target/release/bundle/nsis/`

## 📖 Como Usar

1. **Inicie o Jarvis** via system tray ou painel
2. **Diga "testar"** (wake word padrão)
3. **Diga um comando** configurado:
   - "codigo" → Abre VS Code
   - "calculadora" → Abre calculadora
   - "jogar" → Abre Spotify e pressiona Play
   - "copiar" / "colar" → Atalhos de teclado

## 🎯 Criar Workflows Personalizados

1. Abra o **Painel do Jarvis**
2. Clique em **"➕ Criar Novo Workflow"**
3. Digite a **palavra-chave** (trigger)
4. **Adicione ações** sequencialmente:
   - Abrir apps
   - Teclas/atalhos
   - Digitar texto
   - E muito mais!
5. **Salve** e pronto!

Agora ao dizer "Jarvis" → sua palavra-chave, o workflow executa automaticamente!

## 📁 Estrutura do Projeto

```
jarvis-desktop/
├── src/                    # Frontend React
├── src-tauri/             # Backend Rust (Tauri)
├── src-python/            # Backend Python (Jarvis Core)
│   ├── core/              # Lógica principal
│   ├── actions/           # Módulos de ação
│   └── workflows.json     # Workflows configuráveis
├── build.ps1              # Script de build
└── dev.ps1                # Script de dev
```

## 🔧 Tecnologias

- **Frontend**: React 19 + TypeScript + Vite
- **Desktop Framework**: Tauri 2.0 (Rust)
- **Backend**: Python 3.8+
- **Speech Recognition**: SpeechRecognition + Vosk (offline)
- **Automação**: PyAutoGUI + Keyboard
- **Build**: PyInstaller + Tauri bundler

## 📚 Documentação Completa

Veja [BUILD_GUIDE.md](BUILD_GUIDE.md) para:
- Arquitetura detalhada
- Guia de build completo
- Configurações avançadas
- Troubleshooting
- Contribuição

## 🐛 Problemas Comuns

**Jarvis não inicia?**
- Verifique Python instalado
- Instale dependências: `pip install -r src-python/requirements.txt`

**Wake word não detecta?**
- Fale claramente
- Reduza ruído ambiente
- Ajuste sensibilidade em `src-python/core/listener.py`

**Workflow não executa?**
- Verifique caminhos dos apps
- Teste ações individualmente
- Veja logs no console

## 🎯 Roadmap

- [ ] Suporte Linux/macOS
- [ ] Integração com GPT/LLMs
- [ ] Plugin system
- [ ] Auto-update
- [ ] Cloud sync de workflows
- [ ] App mobile companion

## 🤝 Contribuindo

Contribuições são bem-vindas! Abra issues e PRs.

## 📄 Licença

MIT License - Veja [LICENSE](LICENSE)

## 🙏 Créditos

Desenvolvido com ❤️ para produtividade e automação.

---

**⭐ Se gostou, deixe uma estrela!**

