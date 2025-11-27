import React, { useState, useEffect } from 'react';
import { listen } from '@tauri-apps/api/event';
import { invoke } from '@tauri-apps/api/core';
import ListeningOverlay, { JarvisState } from './ListeningOverlay';

/**
 * Componente standalone para o overlay de voz
 * Separado do painel de controle principal
 * Aparece apenas quando Jarvis está ativo e há interação por voz
 */
const VoiceOverlay: React.FC = () => {
  const [overlayVisible, setOverlayVisible] = useState(false);
  const [jarvisState, setJarvisState] = useState<JarvisState>({
    status: 'hidden'
  });
  const [jarvisRunning, setJarvisRunning] = useState(false);

  // Função para verificar status do Jarvis
  const checkJarvisStatus = async () => {
    try {
      const status = await invoke('get_jarvis_status') as { running: boolean };
      const wasRunning = jarvisRunning;
      const isRunning = status.running;
      
      setJarvisRunning(isRunning);
      
      // Se Jarvis mudou de estado, atualiza overlay
      if (wasRunning !== isRunning) {
        console.log('[OVERLAY] Jarvis status changed:', isRunning ? 'STARTED' : 'STOPPED');
        
        if (!isRunning) {
          // Se parou, esconde overlay imediatamente
          setOverlayVisible(false);
          setJarvisState({ status: 'hidden' });
        }
      }
    } catch (error) {
      console.error('[OVERLAY] Error checking Jarvis status:', error);
      setJarvisRunning(false);
    }
  };

  useEffect(() => {
    // Verifica status inicial do Jarvis
    checkJarvisStatus();
    
    // Verifica status periodicamente
    const statusInterval = setInterval(checkJarvisStatus, 3000);

    // Listener para eventos de estado do Jarvis vindos do backend Python
    const unlistenStateChanged = listen('jarvis-state-changed', (event: any) => {
      const newState = event.payload as JarvisState;
      console.log('[OVERLAY] State changed:', newState);
      
      setJarvisState(newState);
      
      // Overlay só aparece se Jarvis estiver rodando
      if (jarvisRunning && newState.status !== 'hidden') {
        setOverlayVisible(true);
        
        // Auto-hide após tempo em waiting
        if (newState.status === 'waiting') {
          setTimeout(() => {
            setOverlayVisible(false);
          }, 3000);
        }
      } else {
        setOverlayVisible(false);
      }
    });

    // Listener para mudanças no status de execução do Jarvis
    const unlistenJarvisStatus = listen('jarvis-running-changed', (event: any) => {
      const running = event.payload as boolean;
      console.log('[OVERLAY] Jarvis running changed:', running);
      
      setJarvisRunning(running);
      
      // Se Jarvis parou, esconde overlay imediatamente
      if (!running) {
        setOverlayVisible(false);
        setJarvisState({ status: 'hidden' });
      }
    });

    // Listener para wake words - força exibição
    const unlistenWakeWord = listen('jarvis-wake-word', (event: any) => {
      console.log('[OVERLAY] Wake word detected:', event.payload);
      
      if (jarvisRunning) {
        setJarvisState({ status: 'listening', timestamp: Date.now() });
        setOverlayVisible(true);
      }
    });

    // Listener para comandos sendo executados
    const unlistenCommand = listen('jarvis-command', (event: any) => {
      console.log('[OVERLAY] Command executing:', event.payload);
      
      if (jarvisRunning) {
        setJarvisState({ 
          status: 'executing', 
          command: event.payload.command,
          timestamp: Date.now() 
        });
        setOverlayVisible(true);
      }
    });

    return () => {
      clearInterval(statusInterval);
      unlistenStateChanged.then(f => f());
      unlistenJarvisStatus.then(f => f());
      unlistenWakeWord.then(f => f());
      unlistenCommand.then(f => f());
    };
  }, [jarvisRunning]);

  // Callback quando settings é clicado (não deve abrir painel aqui)
  const handleSettingsClick = () => {
    console.log('[OVERLAY] Settings clicked - overlay should stay minimal');
    // TODO: Emitir evento para abrir painel via tray se necessário
  };

  // Não renderiza nada se Jarvis está desligado
  if (!jarvisRunning) {
    return null;
  }

  return (
    <ListeningOverlay
      visible={overlayVisible}
      state={jarvisState}
      onSettingsClick={handleSettingsClick}
    />
  );
};

export default VoiceOverlay;