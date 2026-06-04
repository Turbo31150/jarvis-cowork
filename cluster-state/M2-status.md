# M2 Cluster Status

**Generated:** 2026-06-04T21:13:29Z
**Host:** jarvis-m2 (192.168.1.26)

---

## Services systemd JARVIS actifs

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
| jarvis-gpu-oc.service                          | active   | JARVIS GPU Memory Overclock (+500MHz RTX 3080 + RTX 2060)    |
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

## Modèles LLM actifs

### Port 1234 (LM Studio principal)


### Port 8082 (LM Studio secondaire)
- **deepseek-r1**

### Port 8083 (LM Studio tertiaire)
- **qwen3.5-9b**

---

## GPU Status (nvidia-smi)

| GPU Index | Température | VRAM Utilisée | VRAM Total |
|-----------|-------------|---------------|------------|
| 0 |  73 |  1944 MiB |  8192 MiB |
| 1 |  60 |  5351 MiB |  8192 MiB |
| 2 |  59 |  5668 MiB |  8192 MiB |

---

## Network Map

```json

```
