# M2 Cluster Status — JARVIS

**Mis à jour :** 2026-06-14 03:22:19 CEST
**Host :** jarvis-m2 · 192.168.1.26
**Nœud :** M2 — Quadro RTX 4000 ×3 (8GB VRAM chacune)

---

## Résumé

| Métrique | Valeur |
|---|---|
| Services actifs | 35 |
| Services en échec | 0 |
| GPU | 3 × Quadro RTX 4000 |
| RAM | 28Gi/46Gi |
| Disque SSD | 134G/228G (62%) |

---

## GPU (Quadro RTX 4000 ×3)

```
GPU0: ✅  57°C |  34% util |  3508/ 8192 MiB
GPU1: ✅  55°C |  25% util |  6593/ 8192 MiB
GPU2: ✅  61°C |  0% util |  2075/ 8192 MiB

```

| GPU Index | Température | VRAM Utilisée | VRAM Total |
|-----------|-------------|---------------|------------|
| 0 |  57 |  3499 MiB |  8192 MiB |
| 1 |  55 |  6593 MiB |  8192 MiB |
| 2 |  61 |  2075 MiB |  8192 MiB |

---

## Modèles LLM actifs

### :1234 — LM Studio principal
- **qwen/qwen3.5-9b**

### :8082 — LM Studio secondaire
- **deepseek-r1**

### :8083 — LM Studio tertiaire
_(aucun modèle chargé)_

---

## Services systemd JARVIS

| Unit | State | Description |
|------|-------|-------------|
| jarvis-agent-health.service                    | active   | JARVIS Agent Health Guardian                                 |
| jarvis-agent-monitor.service                   | active   | JARVIS Agent Monitor                                         |
| jarvis-agent-omega.service                     | active   | JARVIS Omega Agent Orchestrator v4                           |
| jarvis-agent-selfimprove.service               | active   | JARVIS Agent Self-Improve                                    |
| jarvis-agent-taskplanner.service               | active   | JARVIS Agent Task Planner                                    |
| jarvis-cluster-mount.service                   | active   | JARVIS cluster FS — montage SSHFS homes cross-machine (rw) |
| jarvis-cowork-dispatcher.service               | active   | JARVIS COWORK Dispatcher — Inbox processor + pattern routing daemon |
| jarvis-cowork-loop.service                     | active   | JARVIS COWORK Engine — Continuous 5min Loop                |
| jarvis-dispatch.service                        | active   | JARVIS Universal Dispatch — skills/agents HTTP API :8900   |
| jarvis-github-push.service                     | activating | start JARVIS GitHub State Push — M2 cluster status         |
| jarvis-gpu-oc.service                          | active   | JARVIS GPU Memory Overclock (Power Limit 100W Quadro RTX 4000 ×3) |
| jarvis-orchestrator.service                    | active   | JARVIS Orchestrator Vocal — Pilotage OS via Telegram       |
| jarvis-scheduler.service                       | active   | JARVIS Scheduler - Planificateur horaire IA                  |
| jarvis-session-restore.service                 | active   | JARVIS Session Restore au boot                               |
| jarvis-share.service                           | active   | JARVIS cross-machine SSHFS mesh                              |
| jarvis-sql-bridge.service                      | active   | JARVIS SQL Bridge — REST API for SQL + Pinecone semantic search |
| jarvis-task-executor.service                   | active   | JARVIS Task Executor — lit openclaw_tasks et exécute      |
| jarvis-task-symbiose.service                   | active   | JARVIS Task Symbiose — inter-machine task dispatcher       |
| jarvis-voice-widget.service                    | activating | JARVIS Voice Widget (Alt+X push-to-talk → Whisper → paste) |
| jarvis-whisper.service                         | active   | JARVIS Whisper STT Server — faster-whisper persistent :8789 |
| jarvis-cluster.target                          | active   | JARVIS Core Cluster Target                                   |
| jarvis-full.target                             | active   | JARVIS OS Full Cluster Target                                |
| jarvis-auto-improver.timer                     | active   | JARVIS Auto-Improver Timer (weekly)                          |
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
| jarvis-sync-repos.timer                        | active   | JARVIS sync repos toutes les 30min                           |

---

## Carte réseau cluster

```json
{
  "ts": "2026-06-14T03:21:48",
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
      "status": "down"
    }
  }
}
```

---
_Généré automatiquement par jarvis-github-push.service · 2026-06-14T01:22:19Z_
