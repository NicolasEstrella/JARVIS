import React from "react";
import { WorkflowAction, ACTION_TYPES } from "../utils/api";

interface WorkflowListProps {
  workflows: Record<string, WorkflowAction[]>;
  onEdit: (trigger: string) => void;
  onDelete: (trigger: string) => void;
  onRefresh: () => void;
}

export const WorkflowList: React.FC<WorkflowListProps> = ({
  workflows,
  onEdit,
  onDelete,
  onRefresh,
}) => {
  const workflowEntries = Object.entries(workflows);

  return (
    <div className="workflow-list">
      <div className="list-header">
        <h2>Workflows Configurados</h2>
        <button onClick={onRefresh} className="btn btn-secondary">
          🔄 Atualizar
        </button>
      </div>

      {workflowEntries.length === 0 ? (
        <div className="empty-state">
          <p>Nenhum workflow configurado ainda.</p>
          <p>Crie seu primeiro workflow abaixo!</p>
        </div>
      ) : (
        <div className="workflow-grid">
          {workflowEntries.map(([trigger, actions]) => (
            <div key={trigger} className="workflow-card">
              <div className="workflow-header">
                <h3>🎯 {trigger}</h3>
                <div className="workflow-actions">
                  <button
                    onClick={() => onEdit(trigger)}
                    className="btn btn-sm btn-primary"
                    title="Editar"
                  >
                    ✏️
                  </button>
                  <button
                    onClick={() => {
                      if (
                        confirm(
                          `Tem certeza que deseja remover o workflow "${trigger}"?`
                        )
                      ) {
                        onDelete(trigger);
                      }
                    }}
                    className="btn btn-sm btn-danger"
                    title="Deletar"
                  >
                    🗑️
                  </button>
                </div>
              </div>
              <div className="workflow-body">
                <p className="action-count">
                  {actions.length} ação(ões):
                </p>
                <ul className="action-list">
                  {actions.map((action, idx) => {
                    const actionType = ACTION_TYPES.find(
                      (t) => t.value === action.action
                    );
                    return (
                      <li key={idx}>
                        <span className="action-number">{idx + 1}.</span>
                        <span className="action-name">
                          {actionType?.label || action.action}
                        </span>
                        <span className="action-params">
                          {JSON.stringify(action.params)}
                        </span>
                      </li>
                    );
                  })}
                </ul>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
