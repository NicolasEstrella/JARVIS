# 🎯 JARVIS Visual Status System - TODOs

## 📋 **Implementação Fase a Fase**

### **✅ FASE 1: Estrutura Base (CONCLUÍDA)**
- [x] Ícones SVG para tray (ativo/inativo)
- [x] Componente ListeningOverlay.tsx 
- [x] CSS com animações modernas
- [x] TrayManager em Rust
- [x] EventEmitter em Python
- [x] Integração básica no App.tsx

---

### **🔧 FASE 2: Funcionalidade Core (EM PROGRESSO)**

#### **Frontend (React/Tauri)**
- [ ] **ListeningOverlay.tsx**
  - [ ] Remover import desnecessário de `invoke`
  - [ ] Implementar transições suaves entre estados
  - [ ] Adicionar lógica de auto-hide após timeout
  - [ ] Melhorar responsividade do overlay

#### **Backend (Rust)**
- [ ] **TrayManager**
  - [ ] Implementar carregamento real de ícones SVG
  - [ ] Converter SVG para formato Image do Tauri
  - [ ] Criar menu de contexto (Start/Stop/Settings/Exit)
  - [ ] Implementar handlers de eventos de clique
  - [ ] Gerenciar estado global do tray

- [ ] **lib.rs**
  - [ ] Integrar TrayManager com estado global
  - [ ] Remover tray legacy quando TrayManager estiver completo
  - [ ] Adicionar tratamento de erros para inicialização

#### **Python Backend**
- [ ] **EventEmitter**
  - [ ] Escolher método de comunicação IPC (Named Pipe/Socket/File)
  - [ ] Implementar `_emit_via_named_pipe()` ou `_emit_via_socket()`
  - [ ] Testar comunicação Python → Tauri
  - [ ] Adicionar retry logic para falhas de comunicação

---

### **🎨 FASE 3: Animações e UX (PRÓXIMA)**

#### **CSS Animations**
- [ ] **Audio Bars (Listening)**
  - [ ] Implementar barras reativas ao volume real do microfone
  - [ ] Adicionar efeito de glow baseado na intensidade
  - [ ] Sincronizar animação com detecção de voz

- [ ] **Processing Spinner**
  - [ ] Adicionar múltiplas camadas de rotação
  - [ ] Implementar efeito de "breathing" 
  - [ ] Usar gradientes dinâmicos

- [ ] **Execution Pulse**
  - [ ] Pulso sincronizado com tipo de ação
  - [ ] Cores diferentes por categoria de ação
  - [ ] Animação de conclusão (checkmark)

- [ ] **Wake-up Effect**
  - [ ] Efeito de "olho abrindo" 
  - [ ] Onda de ativação radiante
  - [ ] Transição suave para estado de escuta

#### **Glassmorphism Enhancement**
- [ ] Ajustar blur e transparência por estado
- [ ] Adicionar particle effects sutis
- [ ] Implementar shadow dinâmica baseada em hora do dia

---

### **🔗 FASE 4: Integração Completa (FUTURA)**

#### **Event System**
- [ ] **Integrar com background_service.py**
  - [ ] Chamar `emit_wake_word()` quando wake word detectada
  - [ ] Chamar `emit_command()` quando comando reconhecido
  - [ ] Chamar `emit_action()` durante execução de workflows

- [ ] **Integrar com workflow_engine.py**
  - [ ] Emitir eventos durante execução de ações
  - [ ] Mostrar progresso de workflows multi-step
  - [ ] Indicar sucesso/falha de cada ação

- [ ] **Integrar com command_handler.py**
  - [ ] Mostrar comando sendo processado
  - [ ] Indicar busca por workflows matching
  - [ ] Exibir ação específica sendo executada

#### **Window Management**
- [ ] **Settings Button Integration**
  - [ ] Implementar comando Tauri para mostrar janela principal
  - [ ] Gerenciar foco de janelas (overlay → settings → overlay)
  - [ ] Adicionar animação de transição

- [ ] **Multi-window Support**
  - [ ] Overlay sempre visível em todas as telas
  - [ ] Detecção de mudança de monitor ativo
  - [ ] Posicionamento inteligente do overlay

---

### **⚡ FASE 5: Performance e Polish (FINAL)**

#### **Performance**
- [ ] Otimizar renderização do overlay (apenas quando necessário)
- [ ] Implementar debounce para mudanças rápidas de estado
- [ ] Cache de ícones e assets
- [ ] Reduzir overhead de comunicação IPC

#### **Accessibility**
- [ ] Suporte a high contrast themes
- [ ] Keyboard navigation para settings button
- [ ] Screen reader compatibility
- [ ] Customização de tamanho do overlay

#### **Configuration**
- [ ] Settings para personalizar overlay
  - [ ] Posição (bottom/top/custom)
  - [ ] Transparência ajustável
  - [ ] Tamanho do overlay
  - [ ] Timeout de auto-hide
  - [ ] Cores e temas personalizados

---

## 🚀 **Próximos Passos Imediatos**

### **1. Testar Build Atual**
```bash
npm run tauri dev
```
- Verificar se overlay aparece (mesmo que não funcional)
- Confirmar que ícones do tray são carregados
- Testar integração básica

### **2. Implementar Comunicação IPC**
- Escolher entre Named Pipe (Windows) ou Socket local
- Implementar método escolhido no `event_emitter.py`
- Testar evento simples Python → Tauri

### **3. Conectar com Eventos Reais**
- Integrar `emit_wake_word()` no `listener.py`
- Adicionar `emit_command()` no `speech_to_text.py`
- Testar fluxo completo: wake word → overlay → comando → ação

### **4. Polish Visual**
- Ajustar CSS para Windows 11 styling
- Testar em diferentes resoluções
- Otimizar animações para 60fps

---

## 📝 **Notas de Implementação**

### **Comunicação IPC Recomendada**
```python
# Opção 1: Named Pipe (Windows nativo)
pipe_name = r'\\.\pipe\jarvis_events'

# Opção 2: Socket local (cross-platform)
socket_port = 45678
```

### **Estados do Overlay**
```typescript
type JarvisState = {
  status: 'idle' | 'listening' | 'processing' | 'executing';
  command?: string;
  action?: string;
  timestamp?: number;
}
```

### **Estrutura de Eventos**
```json
{
  "jarvis-wake-word": { "keyword": "jarvis", "timestamp": 1234567890 },
  "jarvis-command": { "command": "abrir navegador", "timestamp": 1234567890 },
  "jarvis-action-executing": { "action": "open_app", "command": "abrir navegador" },
  "jarvis-action-completed": { "action": "open_app", "success": true }
}
```

---

## 🎯 **Critérios de Sucesso**

- [ ] Ícone do tray muda dinamicamente (verde/vermelho)
- [ ] Overlay aparece automaticamente com wake word
- [ ] Animações são suaves e responsivas
- [ ] Botão de settings abre painel principal
- [ ] Sistema funciona de forma consistente
- [ ] Performance não impacta uso do sistema

**META: Sistema visual completo e funcional em produção! 🚀**