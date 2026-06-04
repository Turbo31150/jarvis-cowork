# M2 Cluster Status

**Generated:** 2026-06-04T20:04:45Z
**Host:** jarvis-m2 (192.168.1.26)

---

## Services systemd JARVIS actifs

| Unit | State | Description |
|------|-------|-------------|
| jarvis-agent-health.service                   | loaded   | JARVIS Agent Health Guardian                                 |
| jarvis-agent-monitor.service                  | loaded   | JARVIS Agent Monitor                                         |
| jarvis-agent-omega.service                    | loaded   | JARVIS Omega Agent Orchestrator v4                           |
| jarvis-agent-selfimprove.service              | loaded   | JARVIS Agent Self-Improve                                    |
| jarvis-agent-taskplanner.service              | loaded   | JARVIS Agent Task Planner                                    |
| jarvis-domino.service                         | loaded   | JARVIS Domino Auto-Trigger Engine (v2.0                      |
| jarvis-gpu-oc.service                         | loaded   | JARVIS GPU Memory Overclock (+500MHz                         |
| jarvis-scheduler.service                      | loaded   | JARVIS Scheduler - Planificateur horaire                     |
| jarvis-task-executor.service                  | loaded   | JARVIS Task Executor — lit                                 |
| jarvis-task-symbiose.service                  | loaded   | JARVIS Task Symbiose — inter-machine                       |
| jarvis-voice-widget.service                   | loaded   | JARVIS Voice Widget (Alt+X push-to-talk                      |
| jarvis-cluster.target                         | loaded   | JARVIS Core Cluster Target                                   |
| jarvis-full.target                            | loaded   | JARVIS OS Full Cluster Target                                |
| jarvis-backup.timer                           | loaded   | JARVIS database backup timer                                 |
| jarvis-cowork-orchestrator.timer              | loaded   | JARVIS Cowork Orchestrator — toutes                        |
| jarvis-github-push.timer                      | loaded   | JARVIS GitHub State Push Timer                               |
| jarvis-health-check.timer                     | loaded   | JARVIS Health Check Timer —                                |
| jarvis-log-rotate.timer                       | loaded   | JARVIS Log Rotation Timer —                                |
| jarvis-network-map.timer                      | loaded   | JARVIS Network Map — update                                |
| jarvis-notify-check.timer                     | loaded   | JARVIS Schedule Check — toutes                             |
| jarvis-prompt-library.timer                   | loaded   | JARVIS Prompt Library — Timer                              |
| jarvis-self-improve.timer                     | loaded   | JARVIS Self-Improve Timer (every 6h)                         |
| jarvis-sync-config.timer                      | loaded   | JARVIS sync config every 5min                                |
| jarvis-sync-repos.timer                       | loaded   | JARVIS sync repos toutes les                                 |

---

## Modèles LLM actifs

### Port 1234 (LM Studio principal)


### Port 8082 (LM Studio secondaire)
- **deepseek-r1**

### Port 8083 (LM Studio tertiaire)


---

## GPU Status (nvidia-smi)

| GPU Index | Température | VRAM Utilisée | VRAM Total |
|-----------|-------------|---------------|------------|
| 0 | 63 | 272 MiB | 8192 MiB |
| 1 | 59 | 5351 MiB | 8192 MiB |
| 2 | 60 | 108 MiB | 8192 MiB |

---

## Network Map

```json
{
  "generated_at": "2026-06-04T20:00:15Z",
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
      "last_seen": "2026-06-04T20:00:15Z"
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
      "models": [],
      "last_seen": "2026-06-04T20:00:15Z"
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
      "models": [],
      "last_seen": "2026-06-04T20:00:15Z"
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
