#!/usr/bin/env python3
"""
Script para verificar se o Jarvis Python está rodando
Útil para debug e monitoramento
"""

import psutil
import sys
import os

def check_jarvis_process():
    """Verifica se há processo do Jarvis rodando"""
    jarvis_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Verifica se é processo Python executando main.py do Jarvis
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                if proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'main.py' in cmdline and 'src-python' in cmdline:
                        jarvis_processes.append({
                            'pid': proc.info['pid'],
                            'cmdline': cmdline
                        })
            
            # Verifica se é o executável jarvis_core.exe
            elif proc.info['name'] and 'jarvis_core' in proc.info['name'].lower():
                jarvis_processes.append({
                    'pid': proc.info['pid'],
                    'cmdline': proc.info['name']
                })
                
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return jarvis_processes

def main():
    print("[SCAN] Verificando processos do Jarvis...")
    processes = check_jarvis_process()
    
    if processes:
        print(f"[OK] Encontrados {len(processes)} processo(s) do Jarvis:")
        for proc in processes:
            print(f"   PID: {proc['pid']} - {proc['cmdline']}")
    else:
        print("❌ Nenhum processo do Jarvis encontrado")
    
    # Verifica arquivos de log (se existirem)
    log_paths = [
        'src-python/jarvis.log',
        'jarvis.log',
        os.path.expanduser('~/jarvis.log')
    ]
    
    for log_path in log_paths:
        if os.path.exists(log_path):
            print(f"[LOG] Log encontrado: {log_path}")
            # Mostra as últimas 5 linhas
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        print("   Últimas linhas:")
                        for line in lines[-5:]:
                            print(f"   {line.strip()}")
            except:
                pass

if __name__ == "__main__":
    main()