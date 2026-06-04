# M2 Cluster Status

**Generated:** 2026-06-04T19:26:37Z
**Host:** jarvis-m2 (192.168.1.26)

---

## Services systemd JARVIS actifs

| Unit | State | Description |
|------|-------|-------------|
| jarvis-cowork-dispatcher.service              | loaded   | JARVIS COWORK Dispatcher — Inbox                           |
| jarvis-cowork-loop.service                    | loaded   | JARVIS COWORK Engine — Continuous                          |
| jarvis-lumen.service                          | loaded   | JARVIS Lumen Token Server —                                |
| jarvis-orchestrator.service                   | loaded   | JARVIS Orchestrator Vocal — Pilotage                       |
| jarvis-scheduler.service                      | loaded   | JARVIS Scheduler - Planificateur horaire                     |
| jarvis-sql-bridge.service                     | loaded   | JARVIS SQL Bridge — REST                                   |
| jarvis-task-executor.service                  | loaded   | JARVIS Task Executor — lit                                 |
| jarvis-task-symbiose.service                  | loaded   | JARVIS Task Symbiose — inter-machine                       |
| jarvis-voice-widget.service                   | loaded   | JARVIS Voice Widget (Alt+X push-to-talk                      |
| jarvis-cluster.target                         | loaded   | JARVIS Core Cluster Target                                   |
| jarvis-full.target                            | loaded   | JARVIS OS Full Cluster Target                                |
| jarvis-backup.timer                           | loaded   | JARVIS database backup timer                                 |
| jarvis-github-push.timer                      | loaded   | JARVIS GitHub State Push Timer                               |
| jarvis-health-check.timer                     | loaded   | JARVIS Health Check Timer —                                |
| jarvis-log-rotate.timer                       | loaded   | JARVIS Log Rotation Timer —                                |
| jarvis-network-map.timer                      | loaded   | JARVIS Network Map — update                                |
| jarvis-notify-check.timer                     | loaded   | JARVIS Schedule Check — toutes                             |
| jarvis-prompt-library.timer                   | loaded   | JARVIS Prompt Library — Timer                              |
| jarvis-sync-config.timer                      | loaded   | JARVIS sync config every 5min                                |
| jarvis-sync-repos.timer                       | loaded   | JARVIS sync repos toutes les                                 |

---

## Modèles LLM actifs

### Port 1234 (LM Studio principal)
- **qwen3.5-9b**

### Port 8082 (LM Studio secondaire)
- **deepseek-r1**

### Port 8083 (LM Studio tertiaire)
- **qwen3.5-9b**

---

## GPU Status (nvidia-smi)

| GPU Index | Température | VRAM Utilisée | VRAM Total |
|-----------|-------------|---------------|------------|
| 0 | 51 | 205 MiB | 8192 MiB |
| 1 | 78 | 5303 MiB | 8192 MiB |
| 2 | 43 | 5671 MiB | 8192 MiB |

---

## Network Map

```json
{
  "generated_at": "2026-06-04T19:25:36Z",
  "nodes": {
    "M1": {
      "ip": "192.168.1.85",
      "hostname": "jarvis-m1",
      "status": "up",
      "services": [
        "lm-studio"
      ],
      "llm_ports": [
        1234
      ],
      "models": [
        "qwen/qwen3.5-9b",
        "openai/gpt-oss-20b",
        "google/gemma-4-e4b",
        "text-embedding-nomic-embed-text-v1.5"
      ],
      "last_seen": "2026-06-04T19:25:36Z"
    },
    "M2": {
      "ip": "192.168.1.26",
      "hostname": "jarvis-m2",
      "status": "up",
      "services": [
        "lm-studio",
        "ollama",
        "redis",
        "vnc",
        "ssh"
      ],
      "llm_ports": [
        1234,
        11434
      ],
      "models": [
        "qwen3.5-9b"
      ],
      "last_seen": "2026-06-04T19:25:36Z"
    },
    "OL1": {
      "ip": "127.0.0.1",
      "hostname": "jarvis-m2",
      "status": "up",
      "services": [
        "ollama"
      ],
      "llm_ports": [
        11434
      ],
      "models": [
        "nomic-embed-text:latest",
        "llama3.2:latest",
        "deepseek-r1:7b",
        "qwen2.5:1.5b",
        "qwen3:1.7b",
        "gemma3:4b",
        "kimi-k2.5:cloud"
      ],
      "last_seen": "2026-06-04T19:25:36Z"
    },
    "M3": {
      "ip": "192.168.1.133",
      "hostname": "jarvis-m3",
      "status": "down",
      "services": [],
      "llm_ports": [
        1234
      ],
      "models": [],
      "last_seen": null
    },
    "M5": {
      "ip": "192.168.1.50",
      "hostname": "jarvis-m5",
      "status": "down",
      "services": [],
      "llm_ports": [
        1234
      ],
      "models": [],
      "last_seen": null
    }
  }
}
```
