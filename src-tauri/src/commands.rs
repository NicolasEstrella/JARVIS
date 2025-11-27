// Comandos Tauri para gerenciar workflows e processo Python

use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::fs;
use std::path::PathBuf;
use std::process::{Child, Command, Stdio};
use std::sync::Arc;
use parking_lot::Mutex;
use tauri::State;

// Estado global para gerenciar processo Python
pub struct JarvisState {
    pub python_process: Arc<Mutex<Option<Child>>>,
    pub is_running: Arc<Mutex<bool>>,
}

impl JarvisState {
    pub fn new() -> Self {
        Self {
            python_process: Arc::new(Mutex::new(None)),
            is_running: Arc::new(Mutex::new(false)),
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct WorkflowAction {
    pub action: String,
    pub params: Value,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Workflow {
    pub trigger: String,
    pub actions: Vec<WorkflowAction>,
}

/// Obtém caminho para o arquivo workflows.json
fn get_workflows_path() -> PathBuf {
    // Em desenvolvimento, usa src-python/workflows.json
    // Em produção, usaria o diretório da aplicação
    let mut path = std::env::current_dir().unwrap();
    path.push("src-python");
    path.push("workflows.json");
    path
}

/// Salva um workflow
#[tauri::command]
pub fn save_workflow(trigger: String, actions: Value) -> Result<(), String> {
    let path = get_workflows_path();
    
    // Lê workflows existentes ou cria novo objeto
    let mut workflows: Value = if path.exists() {
        let content = fs::read_to_string(&path)
            .map_err(|e| format!("Erro ao ler workflows.json: {}", e))?;
        serde_json::from_str(&content)
            .unwrap_or_else(|_| serde_json::json!({}))
    } else {
        serde_json::json!({})
    };
    
    // Atualiza ou adiciona workflow
    if let Some(obj) = workflows.as_object_mut() {
        obj.insert(trigger.to_lowercase(), actions);
    }
    
    // Salva de volta
    let json_str = serde_json::to_string_pretty(&workflows)
        .map_err(|e| format!("Erro ao serializar workflows: {}", e))?;
    
    fs::write(&path, json_str)
        .map_err(|e| format!("Erro ao salvar workflows.json: {}", e))?;
    
    println!("[OK] Workflow '{}' salvo com sucesso", trigger);
    Ok(())
}

/// Carrega todos os workflows
#[tauri::command]
pub fn load_workflows() -> Result<Value, String> {
    let path = get_workflows_path();
    
    if !path.exists() {
        return Ok(serde_json::json!({}));
    }
    
    let content = fs::read_to_string(&path)
        .map_err(|e| format!("Erro ao ler workflows.json: {}", e))?;
    
    let workflows: Value = serde_json::from_str(&content)
        .map_err(|e| format!("Erro ao parsear workflows.json: {}", e))?;
    
    Ok(workflows)
}

/// Remove um workflow
#[tauri::command]
pub fn delete_workflow(trigger: String) -> Result<(), String> {
    let path = get_workflows_path();
    
    if !path.exists() {
        return Err("Arquivo workflows.json não existe".to_string());
    }
    
    let content = fs::read_to_string(&path)
        .map_err(|e| format!("Erro ao ler workflows.json: {}", e))?;
    
    let mut workflows: Value = serde_json::from_str(&content)
        .map_err(|e| format!("Erro ao parsear workflows.json: {}", e))?;
    
    if let Some(obj) = workflows.as_object_mut() {
        obj.remove(&trigger.to_lowercase());
    }
    
    let json_str = serde_json::to_string_pretty(&workflows)
        .map_err(|e| format!("Erro ao serializar workflows: {}", e))?;
    
    fs::write(&path, json_str)
        .map_err(|e| format!("Erro ao salvar workflows.json: {}", e))?;
    
    println!("🗑️ Workflow '{}' removido", trigger);
    Ok(())
}

/// Inicia o processo Python do Jarvis
#[tauri::command]
pub fn start_jarvis(state: State<JarvisState>) -> Result<String, String> {
    let mut is_running = state.is_running.lock();
    
    if *is_running {
        return Ok("Jarvis já está rodando".to_string());
    }
    
    // Caminho para o executável Python
    // Em desenvolvimento: python src-python/main.py
    // Em produção: bin/jarvis_core.exe
    // Caminho para o executável Python
    // Prioridade: 1) bin/jarvis_core.exe (se existe) 2) python src-python/main.py
    let current_dir = std::env::current_dir().unwrap();
    let project_root = if current_dir.file_name().unwrap() == "src-tauri" {
        current_dir.parent().unwrap()
    } else {
        &current_dir
    };
    
    let jarvis_exe = project_root.join("src-tauri").join("bin").join("jarvis_core.exe");
    
    let mut cmd = if jarvis_exe.exists() {
        // Usa o executável empacotado (preferível)
        println!("[SCAN] DEBUG: Usando jarvis_core.exe empacotado");
        println!("[SCAN] DEBUG: Caminho: {:?}", jarvis_exe);
        
        let mut c = Command::new(&jarvis_exe);
        c.current_dir(project_root);
        
        println!("[SCAN] DEBUG: Comando: {:?} no diretório {:?}", jarvis_exe, project_root);
        c
    } else {
        // Fallback para código fonte Python (desenvolvimento)
        println!("[SCAN] DEBUG: jarvis_core.exe não encontrado, usando Python");
        println!("[SCAN] DEBUG: Diretório do projeto: {:?}", project_root);
        
        let mut c = Command::new("cmd");
        c.args(&["/c", "start", "/b", "python", "src-python/main.py"]);
        c.current_dir(project_root);
        
        println!("[SCAN] DEBUG: Comando: cmd /c start /b python src-python/main.py no diretório {:?}", project_root);
        c
    };
    
    // Configura processo
    cmd.stdout(Stdio::null())  // Não captura stdout (deixa o Python livre)
       .stderr(Stdio::null())  // Não captura stderr
       .stdin(Stdio::null());
    
    println!("[SCAN] DEBUG: Configurado para rodar independente (stdout/stderr=null)");
    
    // Inicia processo
    println!("[SCAN] DEBUG: Tentando spawnar processo...");
    let child = cmd.spawn()
        .map_err(|e| {
            println!("❌ DEBUG: Erro ao spawnar: {}", e);
            format!("Erro ao iniciar Jarvis: {}", e)
        })?;
    
    let pid = child.id();
    println!("[SCAN] DEBUG: Comando start executado com PID: {}", pid);
    
    // O processo "start" vai terminar imediatamente, mas vai deixar o Python rodando
    
    // Não armazenamos o processo do 'start', pois ele termina rapidamente
    *is_running = true;
    
    println!("  Jarvis iniciado via start command");
    Ok("Jarvis iniciado com sucesso em background".to_string())
}

/// Para o processo Python do Jarvis
#[tauri::command]
pub fn stop_jarvis(state: State<JarvisState>) -> Result<String, String> {
    let mut is_running = state.is_running.lock();
    
    if !*is_running {
        return Ok("Jarvis não está rodando".to_string());
    }
    
    let mut process = state.python_process.lock();
    
    if let Some(mut child) = process.take() {
        // Tenta matar o processo
        match child.kill() {
            Ok(_) => {
                let _ = child.wait(); // Aguarda processo terminar
                *is_running = false;
                println!("  Jarvis parado");
                Ok("Jarvis parado com sucesso".to_string())
            }
            Err(e) => Err(format!("Erro ao parar Jarvis: {}", e)),
        }
    } else {
        *is_running = false;
        Ok("Processo não encontrado".to_string())
    }
}

/// Verifica se Jarvis está rodando
#[tauri::command]
pub fn is_jarvis_running(state: State<JarvisState>) -> Result<bool, String> {
    let is_running = state.is_running.lock();
    Ok(*is_running)
}

/// Reinicia o Jarvis
#[tauri::command]
pub fn restart_jarvis(state: State<JarvisState>) -> Result<String, String> {
    println!("🔄 Reiniciando Jarvis...");
    
    // Para se estiver rodando
    let _ = stop_jarvis(state.clone());
    
    // Aguarda um pouco
    std::thread::sleep(std::time::Duration::from_secs(1));
    
    // Inicia novamente
    start_jarvis(state)
}

/// Obtém status do Jarvis
#[tauri::command]
pub fn get_jarvis_status(state: State<JarvisState>) -> Result<Value, String> {
    let is_running = state.is_running.lock();
    let process = state.python_process.lock();
    
    let status = serde_json::json!({
        "running": *is_running,
        "has_process": process.is_some(),
    });
    
    Ok(status)
}
