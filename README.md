<div align="center">
  <img src="assets/logo.svg" alt="JARVIS·COWORK" width="520"/>
  <br/><br/>

  [![License: MIT](https://img.shields.io/badge/License-MIT-34D399?style=flat-square)](LICENSE)
  [![Python](https://img.shields.io/badge/Python-3.11+-34D399?style=flat-square&logo=python&logoColor=black)](#)
  [![Scripts](https://img.shields.io/badge/249_scripts-autonomous-10B981?style=flat-square)](#scripts)
  [![Platform](https://img.shields.io/badge/Windows_%2B_Linux-cross--platform-34D399?style=flat-square)](#)
  [![JARVIS](https://img.shields.io/badge/JARVIS-integrated-10B981?style=flat-square)](#intégration)

  <br/>
  <p><strong>249 scripts de co-développement autonome · Windows + Linux · Claude Code · JARVIS intégré</strong></p>
  <p><em>Espace de travail IA collaboratif — sessions de développement continu orchestrées par JARVIS</em></p>
</div>

---

## Présentation

**JARVIS·COWORK** est l'espace de travail de co-développement autonome de l'écosystème JARVIS. Il regroupe **249 scripts** couvrant l'intégralité du cycle de développement : génération de code, tests, déploiement, documentation, monitoring — exécutés de manière autonome ou semi-autonome par les agents JARVIS.

---

## Structure du projet

```
jarvis-cowork/
├── README.md               ← Ce fichier
├── AGENTS.md               ← Définition des agents Cowork
├── IDENTITY.md             ← Identité et rôle du système
├── INSTRUCTIONS.md         ← Instructions d'utilisation
├── SOUL.md                 ← Philosophie et valeurs
├── TOOLS.md                ← Outils disponibles
├── USER.md                 ← Profil utilisateur (Franc)
├── WINDOWS.md              ← Spécificités Windows
├── WORKFLOW_AUTO.md        ← Workflows automatisés
├── COWORK_QUEUE.md         ← File d'attente des tâches
├── COWORK_TASKS.md         ← Tâches en cours / terminées
├── HEARTBEAT.md            ← État du système en temps réel
├── cowork_dispatcher.py    ← Dispatche les tâches aux agents
├── cowork_engine.py        ← Moteur d'exécution principale
├── cowork_mcp_bridge.py    ← Bridge MCP pour Claude Code
├── deploy_cowork_agents.py ← Déploiement des agents
└── dev/                    ← Scripts de développement
    └── [249 scripts]
```

---

## Scripts — catégories

| Catégorie | Nombre | Exemples |
|-----------|--------|---------|
| **Génération code** | 48 | scaffolding, templates, boilerplate |
| **Tests & QA** | 42 | pytest auto, coverage, lint |
| **Déploiement** | 38 | Docker build, push, systemd deploy |
| **Documentation** | 35 | README gen, changelog, docstrings |
| **Monitoring** | 32 | health checks, alertes, logs |
| **Git / CI** | 28 | commits auto, PR, branches |
| **Refactoring** | 26 | code cleanup, migration, format |

---

## Workflow d'une session Cowork

```
Franc → Claude Code (COWORK mode)
         │
         ▼
  Task Dispatcher       ← COWORK_QUEUE.md
         │
    ┌────┴────┐
    │  Agent  │         ← cowork_engine.py
    │  Pool   │         ← 249 scripts disponibles
    └────┬────┘
         │
    ┌────▼────┐
    │  MCP    │         ← cowork_mcp_bridge.py
    │  Bridge │         ← Claude SDK + JARVIS WS:9742
    └────┬────┘
         │
    Résultat → HEARTBEAT.md
              → COWORK_TASKS.md
              → Telegram notification
```

---

## Utilisation

```bash
# Lancer une session Cowork
python cowork_engine.py

# Dispatcher une tâche spécifique
python cowork_dispatcher.py --task "generate_tests" --target "src/trading/"

# Déployer les agents
python deploy_cowork_agents.py --all

# Voir l'état en temps réel
cat HEARTBEAT.md
```

---

## Intégration

```python
# Via MCP Bridge
from cowork_mcp_bridge import CoworkBridge

bridge = CoworkBridge(jarvis_ws="ws://127.0.0.1:9742")
await bridge.dispatch("refactor_module", path="core/agent_manager.py")
await bridge.dispatch("generate_docs", path="modules/trading/")
```

---

<div align="center">

**Franc Delmas (Turbo31150)** · [github.com/Turbo31150](https://github.com/Turbo31150) · Toulouse

*JARVIS·COWORK — Autonomous AI Co-Development Workspace — MIT License*

</div>
