# 🤖 Jarvis Desktop - Assistente de Voz Completo

Aplicação desktop completa integrada usando **Tauri (Rust + React) + Python**, funcionando como assistente de voz local capaz de:

- [OK] Rodar no tray do Windows em segundo plano
- [OK] Ouvir microfone esperando palavra de ativação
- [OK] Executar ações automatizadas (abrir apps, teclas, digitar)
- [OK] Criar workflows personalizados via interface React
- [OK] Empacotável em um único `.exe`

## 🏗️ Arquitetura do Projeto

```
jarvis-desktop/
├── src-tauri/          # Backend Rust (Tauri)
│   ├── src/
│   │   ├── main.rs           # Entry point
│   │   ├── lib.rs            # Lógica principal + tray
│   │   ├── commands.rs       # Comandos Tauri
│   │   └── tray.rs           # System tray menu
│   └── bin/                  # jarvis_core.exe (gerado)
│
├── src/                # Frontend React
│   ├── App.tsx              # App principal
│   ├── components/
│   │   ├── WorkflowEditor.tsx
│   │   └── WorkflowList.tsx
│   └── utils/api.ts         # Comunicação Tauri
│
└── src-python/        # Backend Python (Jarvis Core)
    ├── main.py                # Loop principal
    ├── workflows.json         # Workflows configuráveis
    ├── core/
    │   ├── workflow_engine.py      # Executor de workflows
    │   ├── background_service.py   # Serviço daemon
    │   ├── listener.py             # Wake word detection
    │   ├── speech_to_text.py       # STT
    │   └── command_handler.py      # Processador de comandos
    └── actions/
        ├── open_app.py             # Abrir aplicações
        ├── keyboard_actions.py     # Ações de teclado
        └── system_actions.py       # Ações de sistema
```

##   Como Usar (Desenvolvimento)

### 1. Instalar Dependências

#### Python:
```powershell
cd src-python
python -m pip install -r requirements.txt
```

#### Node.js:
```powershell
npm install
```

### 2. Executar em Modo Desenvolvimento

```powershell
npm run tauri dev
```

Isso irá:
- Iniciar o servidor Vite (React)
- Compilar e executar a aplicação Tauri
- A janela principal abrirá automaticamente

### 3. Usar o Jarvis

#### Via System Tray:
1. Procure o ícone do Jarvis na bandeja do sistema (tray)
2. Clique com botão direito
3. Escolha "Iniciar Jarvis"
4. O assistente começará a ouvir

#### Via Painel:
1. No tray, clique em "Abrir Painel"
2. Use a interface para:
   - Criar novos workflows
   - Editar workflows existentes
   - Iniciar/Parar o Jarvis
   - Ver status

### 4. Ativar o Jarvis

1. Diga **"testar"** (wake word configurada)
2. O Jarvis ativará e aguardará comandos
3. Diga um comando configurado (ex: "codigo", "calculadora", "jogar")
4. O workflow será executado automaticamente

## 📝 Criar Workflows Personalizados

### Via Interface (Recomendado):

1. Abra o Painel do Jarvis
2. Clique em "➕ Criar Novo Workflow"
3. Digite a palavra-chave (trigger)
4. Adicione ações:
   - **Abrir Aplicação**: `open_app`
   - **Pressionar Tecla**: `press_key`
   - **Digitar Texto**: `type_text`
   - **Atalho de Teclado**: `press_hotkey`
   - **Clicar Mouse**: `click_mouse`
   - **Screenshot**: `screenshot`
   - **Ajustar Volume**: `volume`
5. Salve o workflow

### Exemplo de Workflow:

**Trigger**: "estudar"

**Ações**:
1. Abrir VS Code (`open_app` → `code`)
2. Abrir Spotify (`open_app` → `spotify`)
3. Pressionar Play (`press_key` → `p`)
4. Abrir Chrome (`open_app` → `chrome`)

Agora ao dizer "Jarvis" → "estudar", todas essas ações serão executadas automaticamente!

## 🔧 Build para Produção

### 1. Gerar Executável Python (PyInstaller)

```powershell
cd src-python
pyinstaller --onefile --noconsole main.py --name jarvis_core
```

Isso gerará `dist/jarvis_core.exe`

### 2. Copiar para Tauri

```powershell
# Criar diretório bin no Tauri
New-Item -ItemType Directory -Force -Path "src-tauri/bin"

# Copiar executável
Copy-Item "src-python/dist/jarvis_core.exe" -Destination "src-tauri/bin/"
```

### 3. Build do Tauri

```powershell
npm run tauri build
```

O instalador final estará em:
```
src-tauri/target/release/bundle/nsis/jarvis_X.X.X_x64-setup.exe
```

## 📦 Distribuição

O instalador `.exe` final contém:
- Frontend React (embutido)
- Backend Rust (embutido)
- Jarvis Python Core (embutido em `bin/jarvis_core.exe`)
- Todos os recursos necessários

**Tamanho aproximado**: 30-50 MB (dependendo das dependências Python)

## ⚙️ Configuração Avançada

### Mudar Wake Word

Edite `src-python/core/listener.py`:

```python
self.keywords = ["jarvis", "assistente", "hey"]  # Adicione suas palavras
```

### Ajustar Timeout de Escuta Contínua

No `App.tsx` ou via código Python:

```python
service.set_continuous_timeout(15)  # 15 segundos
```

### Adicionar Novos Tipos de Ação

1. Crie módulo em `src-python/actions/`
2. Implemente a função de ação
3. Adicione em `workflow_engine.py` no método `_execute_action`
4. Adicione em `src/utils/api.ts` em `ACTION_TYPES`

## 🐛 Troubleshooting

### Jarvis não inicia:
- Verifique se Python está instalado: `python --version`
- Certifique-se de que as dependências estão instaladas
- Veja logs no console do Tauri

### Microfone não funciona:
- Verifique permissões de microfone no Windows
- Teste com `python src-python/utils/audio_utils.py`

### Wake word não detecta:
- Fale mais alto e claramente
- Reduza ruído ambiente
- Ajuste `energy_threshold` em `listener.py`

### Workflow não executa:
- Verifique se o caminho do app está correto
- Teste ações individualmente via Python
- Veja logs em tempo real no console

## 📚 Comandos Disponíveis

### NPM:
```powershell
npm run dev          # Vite dev server
npm run build        # Build React
npm run tauri dev    # Desenvolvimento Tauri
npm run tauri build  # Build produção
```

### Python:
```powershell
python src-python/main.py                    # Rodar Jarvis standalone
python -m pytest src-python/tests/           # Testes (se tiver)
```

## 🎯 Roadmap

- [ ] Suporte para Linux e macOS
- [ ] Modo de ditado melhorado
- [ ] Integração com GPT para comandos de linguagem natural
- [ ] Suporte para plugins/extensões
- [ ] Auto-update
- [ ] Sincronização de workflows na nuvem
- [ ] App mobile companion

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto é de código aberto sob licença MIT.

## 🙏 Créditos

- **Tauri**: Framework para apps desktop
- **React**: Framework UI
- **Python**: Backend de processamento
- **SpeechRecognition**: Reconhecimento de voz
- **Vosk**: Modelo de STT offline
- **PyAutoGUI**: Automação de interface
- **Keyboard**: Automação de teclado

---

**Desenvolvido com ❤️ para produtividade e automação**
