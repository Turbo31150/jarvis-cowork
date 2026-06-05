# M2 Cluster Status — JARVIS

**Mis à jour :** 2026-06-05 04:07:02 CEST
**Host :** jarvis-m2 · 192.168.1.26
**Nœud :** M2 — Quadro RTX 4000 ×3 (8GB VRAM chacune)

---

## Résumé

| Métrique | Valeur |
|---|---|
| Services actifs | 26 |
| Services en échec | 0 |
| GPU | 3 × Quadro RTX 4000 |
| RAM | 34Gi/46Gi |
| Disque SSD | 122G/228G (57%) |

---

## GPU (Quadro RTX 4000 ×3)

```
GPU0: ✅  69°C |  0% util |  2072/ 8192 MiB
GPU1: ✅  65°C |  0% util |  5421/ 8192 MiB
GPU2: ✅  65°C |  0% util |  5765/ 8192 MiB

```

| GPU Index | Température | VRAM Utilisée | VRAM Total |
|-----------|-------------|---------------|------------|
| 0 |  69 |  2072 MiB |  8192 MiB |
| 1 |  65 |  5421 MiB |  8192 MiB |
| 2 |  65 |  5765 MiB |  8192 MiB |

---

## Modèles LLM actifs

### :1234 — LM Studio principal
- **deepseek/deepseek-r1-0528-qwen3-8b**

### :8082 — LM Studio secondaire
- **deepseek-r1**

### :8083 — LM Studio tertiaire
- **qwen3.5-9b**

---

## Services systemd JARVIS

| Unit | State | Description |
|------|-------|-------------|
| jarvis-agent-health.service                    | active   | JARVIS Agent Health Guardian                                 |
| jarvis-agent-monitor.service                   | active   | JARVIS Agent Monitor                                         |
| jarvis-agent-omega.service                     | active   | JARVIS Omega Agent Orchestrator v4                           |
| jarvis-agent-selfimprove.service               | active   | JARVIS Agent Self-Improve                                    |
| jarvis-agent-taskplanner.service               | active   | JARVIS Agent Task Planner                                    |
| jarvis-cowork-dispatcher.service               | activating | JARVIS COWORK Dispatcher — Inbox processor + pattern routing daemon |
| jarvis-cowork-loop.service                     | activating | JARVIS COWORK Engine — Continuous 5min Loop                |
| jarvis-domino.service                          | active   | JARVIS Domino Auto-Trigger Engine (v2.0 with timeout+semaphores) |
| jarvis-github-push.service                     | activating | start JARVIS GitHub State Push — M2 cluster status         |
| jarvis-gpu-oc.service                          | active   | JARVIS GPU Memory Overclock (Power Limit 100W Quadro RTX 4000 ×3) |
| jarvis-orchestrator.service                    | active   | JARVIS Orchestrator Vocal — Pilotage OS via Telegram       |
| jarvis-scheduler.service                       | active   | JARVIS Scheduler - Planificateur horaire IA                  |
| jarvis-sql-bridge.service                      | active   | JARVIS SQL Bridge — REST API for SQL + Pinecone semantic search |
| jarvis-task-executor.service                   | active   | JARVIS Task Executor — lit openclaw_tasks et exécute      |
| jarvis-task-symbiose.service                   | active   | JARVIS Task Symbiose — inter-machine task dispatcher       |
| jarvis-whisper.service                         | active   | JARVIS Whisper STT Server — faster-whisper persistent :8789 |
| jarvis-cluster.target                          | active   | JARVIS Core Cluster Target                                   |
| jarvis-full.target                             | active   | JARVIS OS Full Cluster Target                                |
| jarvis-backup.timer                            | active   | JARVIS database backup timer                                 |
| jarvis-cowork-orchestrator.timer               | active   | JARVIS Cowork Orchestrator — toutes les 2h                 |
| jarvis-github-push.timer                       | active   | JARVIS GitHub State Push Timer — toutes les heures         |
| jarvis-health-check.timer                      | active   | JARVIS Health Check Timer — Every 5 minutes                |
| jarvis-log-rotate.timer                        | active   | JARVIS Log Rotation Timer — Daily at 3am                   |
| jarvis-network-map.timer                       | active   | JARVIS Network Map — update every 5 minutes                |
| jarvis-notify-check.timer                      | active   | JARVIS Schedule Check — toutes les 15 minutes              |
| jarvis-prompt-library.timer                    | active   | JARVIS Prompt Library — Timer 30min                        |
| jarvis-self-improve.timer                      | active   | JARVIS Self-Improve Timer (every 6h)                         |
| jarvis-sync-config.timer                       | active   | JARVIS sync config every 5min                                |
| jarvis-sync-repos.timer                        | active   | JARVIS sync repos toutes les 30min                           |

---

## Carte réseau cluster

```json
{
  "ts": "2026-06-05T04:02:48",
  "nodes": {
    "M1": {
      "ip": "192.168.1.85",
      "status": "up"
    },
    "M2": {
      "ip": "192.168.1.26",
      "status": "up"
    },
    "M5": {
      "ip": "192.168.1.113",
      "status": "up"
    }
  }
}
```

---
_Généré automatiquement par jarvis-github-push.service · 2026-06-05T02:07:02Z_
