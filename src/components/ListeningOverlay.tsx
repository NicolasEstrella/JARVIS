import React, { useState, useEffect } from 'react';
import './ListeningOverlay.css';

export interface JarvisState {
  status: 'waiting' | 'listening' | 'executing' | 'hidden';
  command?: string;
  action?: string;
  timestamp?: number;
}

interface ListeningOverlayProps {
  visible: boolean;
  state: JarvisState;
  onSettingsClick: () => void;
}

const ListeningOverlay: React.FC<ListeningOverlayProps> = ({ 
  visible, 
  state, 
  onSettingsClick 
}) => {
  const [animationClass, setAnimationClass] = useState('');

  useEffect(() => {
    if (visible) {
      setAnimationClass('slide-up');
      
      // Auto-hide quando voltar para waiting ou hidden
      const hideTimer = setTimeout(() => {
        if (state.status === 'waiting' || state.status === 'hidden') {
          setAnimationClass('slide-down');
          // TODO: Callback para parent component esconder overlay
        }
      }, 5000); // 5 segundos timeout
      
      return () => clearTimeout(hideTimer);
    } else {
      setAnimationClass('slide-down');
    }
  }, [visible, state.status]);

  // Implementar animações específicas para cada estado
  const getStatusText = () => {
    switch (state.status) {
      case 'waiting':
        return 'Esperando comando...';
      case 'listening':
        return 'Te ouvindo...';
      case 'executing':
        return `Executando: ${state.command || 'comando'}`;
      case 'hidden':
        return '';
      default:
        return 'Jarvis ativo';
    }
  };

  // Implementar ícones específicos para cada estado
  const getStatusIcon = () => {
    switch (state.status) {
      case 'waiting':
        return '👁️';
      case 'listening':
        return '🎤';
      case 'executing':
        return '⚙️';
      case 'hidden':
        return '';
      default:
        return '👁️';
    }
  };

  // Implementar indicador visual baseado no status
  const getIndicatorComponent = () => {
    switch (state.status) {
      case 'waiting':
        return <WakeUpPulse />;
      case 'listening':
        return <AudioBars />;
      case 'executing':
        return <ExecutingPulse />;
      case 'hidden':
        return null;
      default:
        return <WakeUpPulse />;
    }
  };

  if (!visible) return null;

  return (
    <div className={`listening-overlay ${animationClass}`}>
      <div className="overlay-content">
        {/* Status Indicator */}
        <div className="status-indicator">
          {getIndicatorComponent()}
        </div>

        {/* Status Text */}
        <div className="status-text">
          <span className="status-icon">{getStatusIcon()}</span>
          <span className="status-message">{getStatusText()}</span>
        </div>

        {/* Command Display */}
        {state.command && (
          <div className="command-display">
            "{state.command}"
          </div>
        )}

        {/* Settings Button */}
        <button 
          className="settings-button"
          onClick={onSettingsClick}
          title="Abrir painel do Jarvis"
        >
          ⚙️
        </button>
      </div>
    </div>
  );
};

// TODO: Implementar componentes de animação
const AudioBars: React.FC = () => (
  <div className="audio-bars">
    {[...Array(5)].map((_, i) => (
      <div key={i} className={`bar bar-${i}`} />
    ))}
  </div>
);

const ProcessingSpinner: React.FC = () => (
  <div className="processing-spinner">
    <div className="spinner" />
  </div>
);

const ExecutingPulse: React.FC = () => (
  <div className="executing-pulse">
    <div className="pulse-ring" />
    <div className="pulse-core" />
  </div>
);

const WakeUpPulse: React.FC = () => (
  <div className="wakeup-pulse">
    <div className="wake-ring" />
    <div className="wake-core" />
  </div>
);

export default ListeningOverlay;