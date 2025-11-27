// lib.rs - Biblioteca principal do Jarvis Tauri
// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/

use tauri::{Emitter, Listener, Manager};
use std::sync::Arc;
use parking_lot::Mutex;

// Módulos
mod commands;
mod ipc_server;
mod tray;
mod tray_manager;

// Re-exportações
pub use commands::*;
pub use ipc_server::*;
pub use tray::*;

use commands::*;
use tray::create_tray;
use ipc_server::{start_ipc_server, test_ipc_event};
use tray_manager::TrayManager; // Reabilitado para tray com ícones de status

// Estado global da aplicação
#[derive(Default)]
pub struct AppState {
    pub jarvis_running: Arc<Mutex<bool>>,
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // Inicializa estado global
    let app_state = AppState::default();

    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .manage(app_state)
        .setup(|app| {
            // Inicializa estado do Jarvis
            app.manage(JarvisState::new());
            
            // Inicializa TrayManager para ícones de status
            let tray_manager = TrayManager::new();
            if let Err(e) = tray_manager.initialize(app.handle()) {
                eprintln!("[ERRO] Erro ao inicializar TrayManager: {}", e);
            }
            app.manage(tray_manager);
            
            // Cria system tray (legacy - TODO: migrar para TrayManager)
            create_tray(app.handle())?;
            
            // INICIA servidor IPC para comunicação Python → Tauri
            let app_handle = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                if let Err(e) = start_ipc_server(app_handle).await {
                    eprintln!("[IPC] Erro ao iniciar servidor: {}", e);
                }
            });
            
            // AUTO-INICIA o Jarvis Python em background
            let state = app.state::<JarvisState>();
            match start_jarvis(state) {
                Ok(msg) => {
                    println!("  {}", msg);
                    // TODO: Atualizar tray para estado ativo quando TrayManager estiver funcional
                },
                Err(e) => eprintln!("[ERRO] Erro ao auto-iniciar Jarvis: {}", e),
            }
            
            // Listener para eventos do tray
            let app_handle = app.handle().clone();
            app.listen("jarvis-start", move |_event| {
                let state = app_handle.state::<JarvisState>();
                match start_jarvis(state) {
                    Ok(msg) => println!("{}", msg),
                    Err(e) => eprintln!("Erro: {}", e),
                }
            });
            
            let app_handle = app.handle().clone();
            app.listen("jarvis-stop", move |_event| {
                let state = app_handle.state::<JarvisState>();
                match stop_jarvis(state) {
                    Ok(msg) => println!("{}", msg),
                    Err(e) => eprintln!("Erro: {}", e),
                }
            });
            
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            // Comandos de workflow
            save_workflow,
            load_workflows,
            delete_workflow,
            // Comandos de controle do Jarvis
            start_jarvis,
            stop_jarvis,
            restart_jarvis,
            is_jarvis_running,
            get_jarvis_status,
            // Comandos IPC
            start_ipc_server,
            test_ipc_event,
            // TODO: Comandos do TrayManager (temporariamente desabilitados)
            // update_tray_state,
            // get_tray_state,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
