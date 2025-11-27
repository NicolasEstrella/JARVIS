import React, { useState } from "react";
import { WorkflowAction, ACTION_TYPES } from "../utils/api";

interface WorkflowEditorProps {
  trigger?: string;
  initialActions?: WorkflowAction[];
  onSave: (trigger: string, actions: WorkflowAction[]) => void;
  onCancel: () => void;
}

export const WorkflowEditor: React.FC<WorkflowEditorProps> = ({
  trigger: initialTrigger,
  initialActions,
  onSave,
  onCancel,
}) => {
  const [trigger, setTrigger] = useState(initialTrigger || "");
  const [actions, setActions] = useState<WorkflowAction[]>(
    initialActions || []
  );

  const addAction = () => {
    setActions([...actions, { action: "open_app", params: {} }]);
  };

  const removeAction = (index: number) => {
    setActions(actions.filter((_, i) => i !== index));
  };

  const updateAction = (
    index: number,
    field: "action" | "params",
    value: any
  ) => {
    const updated = [...actions];
    if (field === "action") {
      updated[index] = { action: value, params: {} };
    } else {
      updated[index] = { ...updated[index], params: value };
    }
    setActions(updated);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!trigger.trim()) {
      alert("Digite uma palavra-chave para o workflow!");
      return;
    }
    if (actions.length === 0) {
      alert("Adicione pelo menos uma ação!");
      return;
    }
    onSave(trigger.toLowerCase().trim(), actions);
  };

  const moveAction = (index: number, direction: "up" | "down") => {
    const newIndex = direction === "up" ? index - 1 : index + 1;
    if (newIndex < 0 || newIndex >= actions.length) return;

    const updated = [...actions];
    [updated[index], updated[newIndex]] = [updated[newIndex], updated[index]];
    setActions(updated);
  };

  return (
    <div className="workflow-editor">
      <h2>{initialTrigger ? "Editar Workflow" : "Novo Workflow"}</h2>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="trigger">
            🎯 Palavra-chave (trigger):
          </label>
          <input
            type="text"
            id="trigger"
            value={trigger}
            onChange={(e) => setTrigger(e.target.value)}
            placeholder="Ex: jogar, trabalhar, estudar..."
            className="form-control"
            disabled={!!initialTrigger}
          />
          <small>
            Diga esta palavra após ativar o Jarvis para executar o workflow
          </small>
        </div>

        <div className="actions-section">
          <div className="section-header">
            <h3>⚙️ Ações do Workflow</h3>
            <button
              type="button"
              onClick={addAction}
              className="btn btn-success"
            >
              + Adicionar Ação
            </button>
          </div>

          {actions.length === 0 ? (
            <p className="empty-actions">
              Nenhuma ação adicionada. Clique em "Adicionar Ação" para começar.
            </p>
          ) : (
            <div className="actions-list">
              {actions.map((action, index) => (
                <ActionEditor
                  key={index}
                  index={index}
                  action={action}
                  totalActions={actions.length}
                  onUpdate={(field, value) =>
                    updateAction(index, field, value)
                  }
                  onRemove={() => removeAction(index)}
                  onMove={(dir) => moveAction(index, dir)}
                />
              ))}
            </div>
          )}
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn-primary">
            💾 Salvar Workflow
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="btn btn-secondary"
          >
            ❌ Cancelar
          </button>
        </div>
      </form>
    </div>
  );
};

interface ActionEditorProps {
  index: number;
  action: WorkflowAction;
  totalActions: number;
  onUpdate: (field: "action" | "params", value: any) => void;
  onRemove: () => void;
  onMove: (direction: "up" | "down") => void;
}

const ActionEditor: React.FC<ActionEditorProps> = ({
  index,
  action,
  totalActions,
  onUpdate,
  onRemove,
  onMove,
}) => {
  const actionType = ACTION_TYPES.find((t) => t.value === action.action);

  const updateParam = (paramName: string, value: any) => {
    onUpdate("params", { ...action.params, [paramName]: value });
  };

  return (
    <div className="action-editor">
      <div className="action-header">
        <span className="action-number">{index + 1}.</span>
        <select
          value={action.action}
          onChange={(e) => onUpdate("action", e.target.value)}
          className="action-select"
        >
          {ACTION_TYPES.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </select>
        <div className="action-controls">
          {index > 0 && (
            <button
              type="button"
              onClick={() => onMove("up")}
              className="btn btn-sm"
              title="Mover para cima"
            >
              ⬆️
            </button>
          )}
          {index < totalActions - 1 && (
            <button
              type="button"
              onClick={() => onMove("down")}
              className="btn btn-sm"
              title="Mover para baixo"
            >
              ⬇️
            </button>
          )}
          <button
            type="button"
            onClick={onRemove}
            className="btn btn-sm btn-danger"
            title="Remover"
          >
            🗑️
          </button>
        </div>
      </div>

      <div className="action-params">
        {actionType?.params.map((param) => (
          <div key={param.name} className="param-field">
            <label>{param.label}:</label>
            {param.type === "text" && (
              <input
                type="text"
                value={action.params[param.name] || ""}
                onChange={(e) => updateParam(param.name, e.target.value)}
                className="form-control"
                placeholder={`Ex: ${getPlaceholderForParam(param.name)}`}
              />
            )}
            {param.type === "number" && (
              <input
                type="number"
                value={action.params[param.name] || ""}
                onChange={(e) =>
                  updateParam(param.name, parseInt(e.target.value))
                }
                className="form-control"
              />
            )}
            {param.type === "array" && (
              <input
                type="text"
                value={
                  Array.isArray(action.params[param.name])
                    ? action.params[param.name].join(", ")
                    : ""
                }
                onChange={(e) =>
                  updateParam(
                    param.name,
                    e.target.value.split(",").map((s) => s.trim())
                  )
                }
                className="form-control"
                placeholder="Ex: ctrl, c"
              />
            )}
            {param.type === "select" && (
              <select
                value={action.params[param.name] || param.options?.[0]}
                onChange={(e) => updateParam(param.name, e.target.value)}
                className="form-control"
              >
                {param.options?.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

function getPlaceholderForParam(paramName: string): string {
  const examples: Record<string, string> = {
    path: "code, chrome, calc, notepad...",
    key: "enter, esc, f5, tab...",
    text: "Hello World!",
    filename: "screenshot.png",
    level: "50",
  };
  return examples[paramName] || "";
}
