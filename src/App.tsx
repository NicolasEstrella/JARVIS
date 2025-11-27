import { useState, useEffect } from "react";
import "./App.css";
import { WorkflowList } from "./components/WorkflowList";
import { WorkflowEditor } from "./components/WorkflowEditor";
import VoiceOverlay from "./components/VoiceOverlay";
import {
  loadWorkflows,
  saveWorkflow,
  deleteWorkflow,
  startJarvis,
  stopJarvis,
  restartJarvis,
  getJarvisStatus,
  type WorkflowAction,
} from "./utils/api";

function App() {
  const [workflows, setWorkflows] = useState<Record<string, WorkflowAction[]>>(
    {}
  );
  const [editingTrigger, setEditingTrigger] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [jarvisRunning, setJarvisRunning] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{ message: string; type: "success" | "error" } | null>(null);

  // Carrega workflows ao iniciar
  useEffect(() => {
    refreshWorkflows();
    checkJarvisStatus();
    
    // Atualiza status a cada 3 segundos
    const interval = setInterval(checkJarvisStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  const refreshWorkflows = async () => {
    try {
      const data = await loadWorkflows();
      setWorkflows(data);
    } catch (error) {
      console.error("Erro ao carregar workflows:", error);
      showStatus("Erro ao carregar workflows", "error");
    }
  };

  const checkJarvisStatus = async () => {
    try {
      const status = await getJarvisStatus();
      setJarvisRunning(status.running);
    } catch (error) {
      console.error("Erro ao verificar status:", error);
    }
  };

  const showStatus = (message: string, type: "success" | "error" = "success") => {
    setStatusMessage({ message, type });

    setTimeout(() => setStatusMessage(null), 3000);

    // Apply different styling based on type
    const statusElement = document.querySelector('.status-message');
    if (statusElement) {
      statusElement.className = `status-message status-${type}`;
    }
  };

  const handleSaveWorkflow = async (
    trigger: string,
    actions: WorkflowAction[]
  ) => {
    try {
      await saveWorkflow(trigger, actions);
      showStatus(`Workflow "${trigger}" salvo com sucesso!`);
      await refreshWorkflows();
      setIsCreating(false);
      setEditingTrigger(null);
    } catch (error) {
      console.error("Erro ao salvar workflow:", error);
      showStatus("Erro ao salvar workflow", "error");
    }
  };

  const handleDeleteWorkflow = async (trigger: string) => {
    try {
      await deleteWorkflow(trigger);
      showStatus(`Workflow "${trigger}" removido`);
      await refreshWorkflows();
    } catch (error) {
      console.error("Erro ao deletar workflow:", error);
      showStatus("Erro ao deletar workflow", "error");
    }
  };

  const handleStartJarvis = async () => {
    try {
      const msg = await startJarvis();
      showStatus(msg);
      await checkJarvisStatus();
    } catch (error) {
      console.error("Erro ao iniciar Jarvis:", error);
      showStatus("Erro ao iniciar Jarvis", "error");
    }
  };

  const handleStopJarvis = async () => {
    try {
      const msg = await stopJarvis();
      showStatus(msg);
      await checkJarvisStatus();
    } catch (error) {
      console.error("Erro ao parar Jarvis:", error);
      showStatus("Erro ao parar Jarvis", "error");
    }
  };

  const handleRestartJarvis = async () => {
    try {
      const msg = await restartJarvis();
      showStatus(msg);
      await checkJarvisStatus();
    } catch (error) {
      console.error("Erro ao reiniciar Jarvis:", error);
      showStatus("Erro ao reiniciar Jarvis", "error");
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🤖 Jarvis Assistant - Painel de Controle</h1>
        <div className="header-controls">
          <div className={`status-badge ${jarvisRunning ? "running" : "stopped"}`}>
            {jarvisRunning ? "🟢 Rodando" : "🔴 Parado"}
          </div>
          <div className="control-buttons">
            {!jarvisRunning ? (
              <button onClick={handleStartJarvis} className="btn btn-success">
                ▶️ Iniciar Jarvis
              </button>
            ) : (
              <>
                <button onClick={handleStopJarvis} className="btn btn-danger">
                  ⏹️ Parar
                </button>
                <button onClick={handleRestartJarvis} className="btn btn-warning">
                  🔄 Reiniciar
                </button>
              </>
            )}
          </div>
        </div>
      </header>

      {statusMessage && (
        <div className={`status-message status-${statusMessage.type}`}>
          {statusMessage.message}
        </div>
      )}

      <main className="app-main">
        {isCreating || editingTrigger ? (
          <WorkflowEditor
            trigger={editingTrigger || undefined}
            initialActions={
              editingTrigger ? workflows[editingTrigger] : undefined
            }
            onSave={handleSaveWorkflow}
            onCancel={() => {
              setIsCreating(false);
              setEditingTrigger(null);
            }}
          />
        ) : (
          <>
            <div className="create-section">
              <button
                onClick={() => setIsCreating(true)}
                className="btn btn-lg btn-primary"
              >
                ➕ Criar Novo Workflow
              </button>
            </div>

            <WorkflowList
              workflows={workflows}
              onEdit={(trigger) => setEditingTrigger(trigger)}
              onDelete={handleDeleteWorkflow}
              onRefresh={refreshWorkflows}
            />
          </>
        )}
      </main>

      <footer className="app-footer">
        <p>
          💡 <strong>Como usar:</strong> Diga "Jarvis" (ou sua wake word) e em
          seguida diga o nome de um workflow para executá-lo
        </p>
        <p>
          📚 Workflows são executados automaticamente quando você diz a
          palavra-chave configurada
        </p>
      </footer>

      {/* Voice Overlay - independente do painel de controle */}
      <VoiceOverlay />
    </div>
  );
}

export default App;
