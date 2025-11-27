// TrayManager - Gerencia ícones e estados do system tray
use std::sync::Mutex;
use tauri::{
    image::Image,
    tray::{TrayIcon, TrayIconBuilder},
    AppHandle, Runtime, Emitter,
};

pub struct TrayManager<R: Runtime> {
    tray_icon: Mutex<Option<TrayIcon<R>>>,
    current_state: Mutex<JarvisState>,
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub enum JarvisState {
    Hidden,    // Jarvis desligado
    Waiting,   // Esperando wake word
    Listening, // Wake word detectada, ouvindo comando
    Executing, // Executando comando
}

impl<R: Runtime> TrayManager<R> {
    pub fn new() -> Self {
        Self {
            tray_icon: Mutex::new(None),
            current_state: Mutex::new(JarvisState::Hidden),
        }
    }

    /// Inicializa o tray icon
    pub fn initialize(&self, app: &AppHandle<R>) -> tauri::Result<()> {
        // TODO: Carregar ícones SVG e converter para Image
        let inactive_icon = self.load_icon("jarvis-inactive.svg")?;
        
        let tray = TrayIconBuilder::new()
            .icon(inactive_icon)
            .tooltip("Jarvis Assistant - Inativo")
            .on_tray_icon_event(|_tray, event| {
                // Implementa eventos de clique no tray
                match event {
                    tauri::tray::TrayIconEvent::Click { button, .. } => {
                        match button {
                            tauri::tray::MouseButton::Left => {
                                // Clique esquerdo: emite evento para mostrar painel principal
                                println!("Left click on tray - opening main panel");
                                // TODO: Emitir evento para mostrar janela principal
                            }
                            tauri::tray::MouseButton::Right => {
                                // Clique direito: mostra menu de contexto
                                println!("Right click on tray - showing context menu");
                                // TODO: Implementar menu de contexto
                            }
                            _ => {}
                        }
                    }
                    _ => {}
                }
            })
            .build(app)?;

        *self.tray_icon.lock().unwrap() = Some(tray);
        Ok(())
    }

    /// Atualiza o estado visual do tray
    pub fn update_state(&self, new_state: JarvisState) -> tauri::Result<()> {
        let mut current_state = self.current_state.lock().unwrap();
        *current_state = new_state.clone();

        if let Some(tray) = self.tray_icon.lock().unwrap().as_ref() {
            // Atualiza ícone baseado no estado
            let (icon_path, tooltip) = match new_state {
                JarvisState::Hidden => ("jarvis-inactive.svg", "Jarvis Assistant - Desligado"),
                JarvisState::Waiting => ("jarvis-active.svg", "Jarvis Assistant - Esperando"),
                JarvisState::Listening => ("jarvis-active.svg", "Jarvis Assistant - Escutando"),
                JarvisState::Executing => ("jarvis-active.svg", "Jarvis Assistant - Executando"),
            };

            let icon = self.load_icon(icon_path)?;
            tray.set_icon(Some(icon))?;
            tray.set_tooltip(Some(tooltip))?;
        }

        Ok(())
    }

    /// Carrega ícone do sistema de arquivos
    fn load_icon(&self, _icon_name: &str) -> tauri::Result<Image<'static>> {
        // TODO: Implementar carregamento de ícones SVG
        // Por enquanto, usar ícone padrão
        let icon_data = include_bytes!("../icons/32x32.png");
        Ok(Image::from_bytes(icon_data)?)
    }

    /// Obtém o estado atual
    pub fn get_current_state(&self) -> JarvisState {
        self.current_state.lock().unwrap().clone()
    }
}

// Comandos Tauri para controle do tray
#[tauri::command]
pub async fn update_tray_state(
    app_handle: tauri::AppHandle,
    state: JarvisState,
) -> Result<(), String> {
    // TODO: Acessar TrayManager do state global
    println!("Updating tray state to: {:?}", state);
    
    // TODO: Emitir evento para o frontend sobre mudança de estado
    app_handle
        .emit("jarvis-state-changed", &state)
        .map_err(|e| format!("Failed to emit event: {}", e))?;
    
    Ok(())
}

#[tauri::command]
pub async fn get_tray_state() -> Result<JarvisState, String> {
    // Retorna estado padrão para quando Jarvis está desligado
    Ok(JarvisState::Hidden)
}

// Implementa menu de contexto do tray (TODO: Implementar corretamente para Tauri v2)
pub fn create_tray_menu() -> tauri::menu::Menu<tauri::Wry> {
    // TODO: Implementar menu com API correta do Tauri v2
    // A API de Menu mudou no Tauri v2, necessário revisar documentação
    todo!("Implementar menu de contexto do tray com API do Tauri v2")
}

// Implementa handlers de eventos do tray
pub fn handle_tray_event(event: tauri::tray::TrayIconEvent) {
    match event {
        tauri::tray::TrayIconEvent::Click { button, .. } => {
            match button {
                tauri::tray::MouseButton::Left => {
                    println!("Tray left click - show main window");
                }
                tauri::tray::MouseButton::Right => {
                    println!("Tray right click - show context menu");
                }
                _ => {}
            }
        }
        tauri::tray::TrayIconEvent::DoubleClick { .. } => {
            println!("Tray double click - toggle Jarvis");
        }
        _ => {}
    }
}