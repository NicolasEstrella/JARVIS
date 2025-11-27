// IPC Server para comunicação Python → Tauri
use std::net::{TcpListener, TcpStream};
use std::io::{BufRead, BufReader};
use std::sync::Arc;
use std::thread;
use tauri::{AppHandle, Emitter, Manager};
use serde_json::Value;

pub struct IpcServer {
    port: u16,
    app_handle: Arc<AppHandle>,
}

impl IpcServer {
    pub fn new(app_handle: AppHandle) -> Self {
        Self {
            port: 45678,
            app_handle: Arc::new(app_handle),
        }
    }

    /// Inicia servidor IPC em background
    pub fn start(&self) -> Result<(), Box<dyn std::error::Error>> {
        let listener = TcpListener::bind(format!("127.0.0.1:{}", self.port))?;
        let app_handle = Arc::clone(&self.app_handle);
        
        println!("[IPC] Servidor iniciado na porta {}", self.port);
        
        // Thread para aceitar conexões
        thread::spawn(move || {
            for stream in listener.incoming() {
                match stream {
                    Ok(stream) => {
                        let app_handle = Arc::clone(&app_handle);
                        thread::spawn(move || {
                            if let Err(e) = Self::handle_client(stream, app_handle) {
                                eprintln!("[IPC] Erro ao processar cliente: {}", e);
                            }
                        });
                    }
                    Err(e) => {
                        eprintln!("[IPC] Erro na conexão: {}", e);
                    }
                }
            }
        });

        Ok(())
    }

    /// Processa mensagem de cliente Python
    fn handle_client(
        stream: TcpStream, 
        app_handle: Arc<AppHandle>
    ) -> Result<(), Box<dyn std::error::Error>> {
        let mut reader = BufReader::new(stream);
        let mut line = String::new();
        
        // Lê linha JSON do Python
        reader.read_line(&mut line)?;
        
        if line.trim().is_empty() {
            return Ok(());
        }

        // Parse da mensagem JSON
        let message: Value = serde_json::from_str(line.trim())?;
        
        if let (Some(event_name), Some(data)) = (
            message["event"].as_str(),
            message.get("data")
        ) {
            println!("[IPC] Evento recebido: {} -> {:?}", event_name, data);
            
            // Emite evento para frontend React
            if let Err(e) = app_handle.emit(event_name, data) {
                eprintln!("[IPC] Erro ao emitir evento: {}", e);
            }
        }

        Ok(())
    }
}

// Comando Tauri para iniciar servidor IPC
#[tauri::command]
pub async fn start_ipc_server(app_handle: tauri::AppHandle) -> Result<String, String> {
    let server = IpcServer::new(app_handle);
    
    match server.start() {
        Ok(_) => {
            println!("[IPC] Servidor IPC iniciado com sucesso");
            Ok("IPC Server started successfully".to_string())
        }
        Err(e) => {
            let error_msg = format!("Failed to start IPC server: {}", e);
            eprintln!("[IPC] {}", error_msg);
            Err(error_msg)
        }
    }
}

#[tauri::command]
pub async fn test_ipc_event(app_handle: tauri::AppHandle) -> Result<String, String> {
    // Comando para testar eventos IPC manualmente
    let test_data = serde_json::json!({
        "status": "listening",
        "timestamp": chrono::Utc::now().timestamp_millis()
    });
    
    if let Err(e) = app_handle.emit("jarvis-state-changed", &test_data) {
        return Err(format!("Failed to emit test event: {}", e));
    }
    
    Ok("Test event emitted successfully".to_string())
}