// API para comunicação com backend Tauri
import { invoke } from "@tauri-apps/api/core";

export interface WorkflowAction {
  action: string;
  params: Record<string, any>;
}

export interface Workflow {
  trigger: string;
  actions: WorkflowAction[];
}

export interface JarvisStatus {
  running: boolean;
  has_process: boolean;
}

// ========== Workflow Management ==========

/**
 * Salva um workflow
 */
export async function saveWorkflow(
  trigger: string,
  actions: WorkflowAction[]
): Promise<void> {
  await invoke("save_workflow", { trigger, actions });
}

/**
 * Carrega todos os workflows
 */
export async function loadWorkflows(): Promise<Record<string, WorkflowAction[]>> {
  return await invoke("load_workflows");
}

/**
 * Remove um workflow
 */
export async function deleteWorkflow(trigger: string): Promise<void> {
  await invoke("delete_workflow", { trigger });
}

// ========== Jarvis Control ==========

/**
 * Inicia o Jarvis
 */
export async function startJarvis(): Promise<string> {
  return await invoke("start_jarvis");
}

/**
 * Para o Jarvis
 */
export async function stopJarvis(): Promise<string> {
  return await invoke("stop_jarvis");
}

/**
 * Reinicia o Jarvis
 */
export async function restartJarvis(): Promise<string> {
  return await invoke("restart_jarvis");
}

/**
 * Verifica se Jarvis está rodando
 */
export async function isJarvisRunning(): Promise<boolean> {
  return await invoke("is_jarvis_running");
}

/**
 * Obtém status do Jarvis
 */
export async function getJarvisStatus(): Promise<JarvisStatus> {
  return await invoke("get_jarvis_status");
}

// ========== Action Types ==========

export const ACTION_TYPES = [
  {
    value: "open_app",
    label: "Abrir Aplicação",
    params: [{ name: "path", type: "text", label: "Caminho ou Nome do App" }],
  },
  {
    value: "press_key",
    label: "Pressionar Tecla",
    params: [{ name: "key", type: "text", label: "Tecla (ex: enter, esc)" }],
  },
  {
    value: "type_text",
    label: "Digitar Texto",
    params: [{ name: "text", type: "text", label: "Texto para Digitar" }],
  },
  {
    value: "press_hotkey",
    label: "Atalho de Teclado",
    params: [
      {
        name: "keys",
        type: "array",
        label: "Teclas (separadas por vírgula)",
      },
    ],
  },
  {
    value: "click_mouse",
    label: "Clicar Mouse",
    params: [
      { name: "x", type: "number", label: "Posição X (opcional)" },
      { name: "y", type: "number", label: "Posição Y (opcional)" },
      {
        name: "button",
        type: "select",
        label: "Botão",
        options: ["left", "right", "middle"],
      },
    ],
  },
  {
    value: "screenshot",
    label: "Tirar Screenshot",
    params: [{ name: "filename", type: "text", label: "Nome do Arquivo (opcional)" }],
  },
  {
    value: "volume",
    label: "Ajustar Volume",
    params: [{ name: "level", type: "number", label: "Nível (0-100)" }],
  },
] as const;

export type ActionType = (typeof ACTION_TYPES)[number]["value"];
