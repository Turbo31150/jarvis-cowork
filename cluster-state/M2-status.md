# M2 Cluster Status — JARVIS

**Mis à jour :** 2026-06-08 02:19:36 CEST
**Host :** jarvis-m2 · 192.168.1.26
**Nœud :** M2 — Quadro RTX 4000 ×3 (8GB VRAM chacune)

---

## Résumé

| Métrique | Valeur |
|---|---|
| Services actifs | 35 |
| Services en échec | 5 |
| GPU | 3 × Quadro RTX 4000 |
| RAM | 26Gi/46Gi |
| Disque SSD | 126G/228G (58%) |

---

## GPU (Quadro RTX 4000 ×3)

```
GPU0: ✅  65°C |  0% util |  4679/ 8192 MiB
GPU1: ✅  54°C |  0% util |  5295/ 8192 MiB
GPU2: ✅  43°C |  0% util |  5657/ 8192 MiB

```

| GPU Index | Température | VRAM Utilisée | VRAM Total |
|-----------|-------------|---------------|------------|
| 0 |  65 |  4679 MiB |  8192 MiB |
| 1 |  54 |  5295 MiB |  8192 MiB |
| 2 |  43 |  5657 MiB |  8192 MiB |

---

## Modèles LLM actifs

### :1234 — LM Studio principal
- **qwen3.5-9b**

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
| ●                                            | loaded   | failed JARVIS self-heal tick (services, mounts, peers, registry) |
| jarvis-cluster-mount.service                   | active   | JARVIS cluster FS — montage SSHFS homes cross-machine (rw) |
| jarvis-cowork-dispatcher.service               | active   | JARVIS COWORK Dispatcher — Inbox processor + pattern routing daemon |
| jarvis-cowork-loop.service                     | active   | JARVIS COWORK Engine — Continuous 5min Loop                |
| jarvis-dispatch.service                        | active   | JARVIS Universal Dispatch — skills/agents HTTP API :8900   |
| ●                                            | loaded   | failed JARVIS Domino Auto-Trigger Engine (v2.0 with timeout+semaphores) |
| ●                                            | loaded   | failed JARVIS Failure Handler for jarvis-orchestrator.service |
| jarvis-github-push.service                     | activating | start JARVIS GitHub State Push — M2 cluster status         |
| ●                                            | loaded   | failed JARVIS GPU Memory Overclock (Power Limit 100W Quadro RTX 4000 ×3) |
| jarvis-orchestrator.service                    | active   | JARVIS Orchestrator Vocal — Pilotage OS via Telegram       |
| jarvis-scheduler.service                       | active   | JARVIS Scheduler - Planificateur horaire IA                  |
| jarvis-share.service                           | active   | JARVIS cross-machine SSHFS mesh                              |
| jarvis-sql-bridge.service                      | active   | JARVIS SQL Bridge — REST API for SQL + Pinecone semantic search |
| ●                                            | loaded   | failed JARVIS sync config Docker+LLM → SQLite              |
| jarvis-task-executor.service                   | active   | JARVIS Task Executor — lit openclaw_tasks et exécute      |
| jarvis-task-symbiose.service                   | active   | JARVIS Task Symbiose — inter-machine task dispatcher       |
| jarvis-whisper.service                         | active   | JARVIS Whisper STT Server — faster-whisper persistent :8789 |
| jarvis-cluster.target                          | active   | JARVIS Core Cluster Target                                   |
| jarvis-full.target                             | active   | JARVIS OS Full Cluster Target                                |
| jarvis-auto-improver.timer                     | active   | JARVIS Auto-Improver Timer (weekly)                          |
| jarvis-autoheal.timer                          | active   | Run JARVIS self-heal every 10 minutes                        |
| jarvis-backup-sql.timer                        | active   | Backup SQLite + Docker — quotidien 02h00                   |
| jarvis-backup.timer                            | active   | JARVIS database backup timer                                 |
| jarvis-cluster-mount.timer                     | active   | JARVIS cluster FS — remontage périodique                  |
| jarvis-cowork-orchestrator.timer               | active   | JARVIS Cowork Orchestrator — toutes les 2h                 |
| jarvis-github-push.timer                       | active   | JARVIS GitHub State Push Timer — toutes les heures         |
| jarvis-health-check.timer                      | active   | JARVIS Health Check Timer — Every 5 minutes                |
| jarvis-log-rotate.timer                        | active   | JARVIS Log Rotation Timer — Daily at 3am                   |
| jarvis-network-map.timer                       | active   | JARVIS Network Map — update every 5 minutes                |
| jarvis-notify-check.timer                      | active   | JARVIS Schedule Check — toutes les 15 minutes              |
| jarvis-prompt-library.timer                    | active   | JARVIS Prompt Library — Timer 30min                        |
| jarvis-self-improve.timer                      | active   | JARVIS Self-Improve Timer (every 6h)                         |
| jarvis-session-daily-restore-test.timer        | active   | Test restore session JARVIS — quotidien 03h00              |
| jarvis-session-snapshot.timer                  | active   | Snapshot session JARVIS toutes les 5 minutes                 |
| jarvis-sync-config.timer                       | active   | JARVIS sync config every 5min                                |

---

## Carte réseau cluster

```json
{
  "ts": "2026-06-08T02:17:19",
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
_Généré automatiquement par jarvis-github-push.service · 2026-06-08T00:19:36Z_
