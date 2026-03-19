# JARVIS COWORK — Autonomous Development Factory

> **EN** | [FR](#version-française)
>
> ![Python](https://img.shields.io/badge/python-3.11+-green)
> ![Scripts](https://img.shields.io/badge/scripts-249_autonomous-blue)
> ![Cycle](https://img.shields.io/badge/cycle-every_6h-orange)
> ![Platform](https://img.shields.io/badge/platform-Windows_+_Linux-lightgrey)
>
> Autonomous continuous development engine — 249 Python scripts that run every 6 hours to test, detect gaps, anticipate needs, and improve the JARVIS AI cluster automatically.
>
> **Part of the [JARVIS ecosystem](https://github.com/Turbo31150/jarvis-linux)** | Compatible: Windows + Linux
>
> ---
>
> ## Table of Contents
>
> 1. [What is COWORK?](#what-is-cowork)
> 2. 2. [Architecture](#architecture)
>    3. 3. [4-Phase Autonomous Cycle](#4-phase-autonomous-cycle)
>       4. 4. [Script Categories](#script-categories)
>          5. 5. [MCP Interface (8 tools)](#mcp-interface)
>             6. 6. [Constraints & Rules](#constraints--rules)
>                7. 7. [Installation](#installation)
>                   8. 8. [Usage](#usage)
>                      9. 9. [Integration with JARVIS](#integration-with-jarvis)
>                         10. 10. [Related Repos](#related-repos)
>                             11. 11. [Version Française](#version-française)
>                                
>                                 12. ---
>                                
>                                 13. ## What is COWORK?
>                                
>                                 14. COWORK is a **self-developing autonomous factory** — a collection of 249 Python scripts that:
> - Run every 6 hours via systemd timer (`jarvis-cowork@1.timer`)
> - - Test themselves and all other JARVIS components
>   - - Detect missing functionality (gaps analysis)
>     - - Anticipate future needs using AI prediction
>       - - Generate and improve scripts automatically
>        
>         - No external dependencies — all scripts use Python stdlib only.
>        
>         - ---
>
> ## Architecture
>
> ```
> jarvis-cowork/
> ├── cowork_engine.py        # Main engine (4 modes)
> ├── cowork_dispatcher.py    # Pattern router
> ├── cowork_mcp_bridge.py    # MCP interface (8 tools)
> ├── deploy_cowork_agents.py # Deployment manager
> ├── path_resolver.py        # Dynamic path resolution
> └── dev/                    # 249 autonomous scripts
>     ├── linux_*.py          # Linux system automation
>     ├── jarvis_*.py         # JARVIS intelligence
>     ├── ia_*.py             # AI & ML autonomous
>     ├── auto_*.py           # Cross-domain automation
>     ├── cluster_*.py        # Cluster management
>     ├── voice_*.py          # Voice pipeline
>     ├── dispatch_*.py       # Routing engine
>     └── trading_*.py        # Trading automation
> ```
>
> ---
>
> ## 4-Phase Autonomous Cycle
>
> Every 6 hours, COWORK runs through 4 sequential phases:
>
> ### Phase 1 — TEST-ALL
> ```bash
> cowork_engine.py --mode test-all
> ```
> For each of the 249 scripts:
> - Import the module
> - - Execute `main()` or `run()`
>   - - Verify exit code (0 = OK, 1 = fail)
>     - - Capture stdout/stderr
>       - - Log result in `etoile.db`
>        
>         - ### Phase 2 — GAPS (gap detection)
>         - ```bash
>           cowork_engine.py --mode gaps
>           ```
>           Analyzes JARVIS code to find:
>           - Functions without tests
>           - - Modules without monitoring
>             - - Endpoints without validation
>               - - Dispatch patterns without benchmarks
>                 - - Generates list of scripts to create
>                  
>                   - ### Phase 3 — ANTICIPATE
>                   - ```bash
>                     cowork_engine.py --mode anticipate
>                     ```
>                     Uses AI (M1/OL1) to predict:
>                     - Which components will need updates
>                     - - Which bugs are likely (drift detection)
>                       - - Which optimizations are possible
>                         - - Prioritizes actions by impact
>                          
>                           - ### Phase 4 — IMPROVE
>                           - ```bash
>                             cowork_engine.py --mode improve
>                             ```
>                             Executes identified improvements:
>                             - Generates new COWORK scripts
>                             - - Improves existing scripts
>                               - - Updates benchmarks
>                                 - - Optimizes dispatch routes
>                                   - - Commits changes (if `auto_commit=true`)
>                                    
>                                     - ---
>
> ## Script Categories
>
> | Category | Prefix | Count | Description |
> |----------|--------|-------|-------------|
> | Linux automation | `linux_*.py` | ~40 | System, files, processes, services |
> | JARVIS intelligence | `jarvis_*.py` | ~50 | Core logic, memory, agents |
> | AI & ML | `ia_*.py` | ~30 | Model testing, benchmarks |
> | Cross-domain | `auto_*.py` | ~35 | Transverse automation |
> | Cluster | `cluster_*.py` | ~25 | Node management, health |
> | Voice pipeline | `voice_*.py` | ~20 | STT, TTS, wake word |
> | Dispatch routing | `dispatch_*.py` | ~25 | Routing engine, quality gates |
> | Trading | `trading_*.py` | ~24 | Signals, strategies, backtest |
>
> ---
>
> ## MCP Interface
>
> 8 tools exposed via MCP for external integration:
>
> | Tool | Description |
> |------|-------------|
> | `cowork_execute` | Execute a specific COWORK script |
> | `cowork_list` | List available scripts |
> | `cowork_search` | Search by pattern/keyword |
> | `cowork_stats` | Execution statistics |
> | `cowork_proactive_discover` | Proactive needs discovery |
> | `cowork_proactive_execute` | Proactive execution |
> | `cowork_proactive_status` | Proactive task status |
> | `cowork_proactive_queue` | Queue management |
>
> ---
>
> ## Constraints & Rules
>
> Every COWORK script MUST follow these rules:
>
> - **stdlib-only** — No pip dependencies allowed
> - - **Self-test required** — Each script must have its own test
>   - - **30s timeout** — Per script execution limit
>     - - **Max 600 active scripts** — Auto-prune if > 600
>       - - **Exit codes**: 0 = success, 1 = failure
>         - - **Logging**: All results logged to `etoile.db`
>          
>           - ---
>
> ## Installation
>
> ```bash
> git clone https://github.com/Turbo31150/jarvis-cowork.git
> cd jarvis-cowork
>
> # No pip install needed — stdlib only
> python cowork_engine.py --mode test-all
> ```
>
> ### With JARVIS (recommended)
> The scripts are designed to run within the JARVIS ecosystem:
> ```bash
> # From jarvis-linux root
> python main.py
> # Then via MCP: cowork_execute, cowork_list, cowork_stats
> ```
>
> ---
>
> ## Usage
>
> ```bash
> # Run all tests
> python cowork_engine.py --mode test-all
>
> # Detect gaps
> python cowork_engine.py --mode gaps
>
> # Anticipate improvements
> python cowork_engine.py --mode anticipate
>
> # Auto-improve
> python cowork_engine.py --mode improve
>
> # Search scripts
> python cowork_engine.py --search "trading"
>
> # Execute specific script
> python cowork_engine.py --run trading_signal_validator.py
> ```
>
> ---
>
> ## Integration with JARVIS
>
> COWORK integrates with the JARVIS ecosystem via:
>
> - **Systemd timer**: `jarvis-cowork@1.timer` — runs every 6 hours automatically
> - - **Docker container**: `cowork-engine` + `cowork-dispatcher` in `docker-compose.modular.yml`
>   - - **MCP bridge**: `cowork_mcp_bridge.py` — exposes 8 tools to Claude SDK
>     - - **Database**: Results logged to `etoile.db` (42 tables, shared with all JARVIS components)
>       - - **WebSocket**: Events broadcast on `jarvis-ws :9742`
>        
>         - ---
>
> ## Related Repos
>
> | Repo | Description |
> |------|-------------|
> | [jarvis-linux](https://github.com/Turbo31150/jarvis-linux) | Main JARVIS repo — full deployment |
> | [JARVIS-CLUSTER](https://github.com/Turbo31150/JARVIS-CLUSTER) | Multi-node cluster infrastructure |
> | [jarvis-whisper-flow](https://github.com/Turbo31150/jarvis-whisper-flow) | Voice assistant (Whisper-based) |
>
> ---
>
> *Author: Turbo31150 | Platform: Windows + Linux | Cycle: Every 6h autonomous | March 2026*
>
> ---
> ---
>
> # Version Française
>
> > [EN](#jarvis-cowork--autonomous-development-factory) | **FR**
> >
> > ![Python](https://img.shields.io/badge/python-3.11+-green)
> > ![Scripts](https://img.shields.io/badge/scripts-249_autonomes-blue)
> > ![Cycle](https://img.shields.io/badge/cycle-toutes_6h-orange)
> > ![Plateforme](https://img.shields.io/badge/plateforme-Windows_+_Linux-lightgrey)
> >
> > Moteur de développement continu autonome — 249 scripts Python qui s'exécutent toutes les 6 heures pour tester, détecter les manques, anticiper les besoins et améliorer le cluster IA JARVIS automatiquement.
> >
> > **Fait partie de l'[écosystème JARVIS](https://github.com/Turbo31150/jarvis-linux)** | Compatible : Windows + Linux
> >
> > ---
> >
> > ## Table des matières FR
> >
> > 1. [Qu'est-ce que COWORK ?](#quest-ce-que-cowork)
> > 2. 2. [Architecture](#architecture-fr)
> >    3. 3. [Cycle autonome 4 phases](#cycle-autonome-4-phases)
> >       4. 4. [Catégories de scripts](#catégories-de-scripts)
> >          5. 5. [Interface MCP (8 outils)](#interface-mcp)
> >             6. 6. [Contraintes & Règles](#contraintes--règles)
> >                7. 7. [Installation](#installation-fr)
> >                   8. 8. [Utilisation](#utilisation)
> >                      9. 9. [Intégration avec JARVIS](#intégration-avec-jarvis)
> >                         10. 10. [Repos liés](#repos-liés)
> >                            
> >                             11. ---
> >                            
> >                             12. ## Qu'est-ce que COWORK ?
> >                            
> >                             13. COWORK est une **usine de développement autonome** — une collection de 249 scripts Python qui :
> > - S'exécutent toutes les 6 heures via timer systemd (`jarvis-cowork@1.timer`)
> > - - Se testent eux-mêmes et testent tous les composants JARVIS
> >   - - Détectent les fonctionnalités manquantes (analyse des gaps)
> >     - - Anticipent les besoins futurs via prédiction IA
> >       - - Génèrent et améliorent des scripts automatiquement
> >        
> >         - Aucune dépendance externe — tous les scripts utilisent uniquement la stdlib Python.
> >        
> >         - ---
> >
> > ## Architecture FR
> >
> > ```
> > jarvis-cowork/
> > ├── cowork_engine.py        # Moteur principal (4 modes)
> > ├── cowork_dispatcher.py    # Routeur de patterns
> > ├── cowork_mcp_bridge.py    # Interface MCP (8 outils)
> > ├── deploy_cowork_agents.py # Gestionnaire de déploiement
> > ├── path_resolver.py        # Résolution dynamique des chemins
> > └── dev/                    # 249 scripts autonomes
> >     ├── linux_*.py          # Automatisation système Linux
> >     ├── jarvis_*.py         # Intelligence JARVIS
> >     ├── ia_*.py             # IA & ML autonome
> >     ├── auto_*.py           # Automatisation transverse
> >     ├── cluster_*.py        # Gestion du cluster
> >     ├── voice_*.py          # Pipeline vocal
> >     ├── dispatch_*.py       # Moteur de routage
> >     └── trading_*.py        # Automatisation trading
> > ```
> >
> > ---
> >
> > ## Cycle autonome 4 phases
> >
> > Toutes les 6 heures, COWORK s'exécute en 4 phases séquentielles :
> >
> > ### Phase 1 — TEST-ALL
> > Pour chaque script parmi les 249 :
> > - Importer le module
> > - - Exécuter `main()` ou `run()`
> >   - - Vérifier le code de sortie (0 = OK, 1 = échec)
> >     - - Capturer stdout/stderr
> >       - - Logger le résultat dans `etoile.db`
> >        
> >         - ### Phase 2 — GAPS (détection de manques)
> >         - Analyse le code JARVIS pour trouver :
> >         - - Fonctions sans tests
> >           - - Modules sans monitoring
> >             - - Endpoints sans validation
> >               - - Patterns de dispatch sans benchmark
> >                 - - Génère une liste de scripts à créer
> >                  
> >                   - ### Phase 3 — ANTICIPATE
> >                   - Utilise l'IA (M1/OL1) pour prédire :
> >                   - - Quels composants auront besoin de mises à jour
> >                     - - Quels bugs sont probables (détection de drift)
> >                       - - Quelles optimisations sont possibles
> >                         - - Priorise les actions par impact
> >                          
> >                           - ### Phase 4 — IMPROVE
> >                           - Exécute les améliorations identifiées :
> >                           - - Génère de nouveaux scripts COWORK
> >                             - - Améliore les scripts existants
> >                               - - Met à jour les benchmarks
> >                                 - - Optimise les routes de dispatch
> >                                   - - Commit les changements (si `auto_commit=true`)
> >                                    
> >                                     - ---
> >
> > ## Catégories de scripts
> >
> > | Catégorie | Préfixe | Nb | Description |
> > |-----------|---------|-----|-------------|
> > | Automatisation Linux | `linux_*.py` | ~40 | Système, fichiers, processus |
> > | Intelligence JARVIS | `jarvis_*.py` | ~50 | Logique core, mémoire, agents |
> > | IA & ML | `ia_*.py` | ~30 | Tests de modèles, benchmarks |
> > | Transverse | `auto_*.py` | ~35 | Automatisation générale |
> > | Cluster | `cluster_*.py` | ~25 | Gestion des nœuds, santé |
> > | Pipeline vocal | `voice_*.py` | ~20 | STT, TTS, wake word |
> > | Routage dispatch | `dispatch_*.py` | ~25 | Moteur routing, quality gates |
> > | Trading | `trading_*.py` | ~24 | Signaux, stratégies, backtest |
> >
> > ---
> >
> > ## Interface MCP
> >
> > 8 outils exposés via MCP pour intégration externe :
> >
> > | Outil | Description |
> > |-------|-------------|
> > | `cowork_execute` | Exécuter un script COWORK spécifique |
> > | `cowork_list` | Lister les scripts disponibles |
> > | `cowork_search` | Rechercher par pattern/mot-clé |
> > | `cowork_stats` | Statistiques d'exécution |
> > | `cowork_proactive_discover` | Découverte proactive de besoins |
> > | `cowork_proactive_execute` | Exécution proactive |
> > | `cowork_proactive_status` | Statut des tâches proactives |
> > | `cowork_proactive_queue` | Gestion de la file d'attente |
> >
> > ---
> >
> > ## Contraintes & Règles
> >
> > Chaque script COWORK DOIT respecter ces règles :
> >
> > - **stdlib uniquement** — Aucune dépendance pip autorisée
> > - - **Self-test obligatoire** — Chaque script doit avoir son propre test
> >   - - **Timeout 30s** — Limite par exécution de script
> >     - - **Max 600 scripts actifs** — Auto-pruning si > 600
> >       - - **Codes de sortie** : 0 = succès, 1 = échec
> >         - - **Logging** : Tous les résultats loggés dans `etoile.db`
> >          
> >           - ---
> >
> > ## Installation FR
> >
> > ```bash
> > git clone https://github.com/Turbo31150/jarvis-cowork.git
> > cd jarvis-cowork
> >
> > # Aucun pip install nécessaire — stdlib uniquement
> > python cowork_engine.py --mode test-all
> > ```
> >
> > ### Avec JARVIS (recommandé)
> > Les scripts sont conçus pour s'exécuter dans l'écosystème JARVIS :
> > ```bash
> > # Depuis la racine jarvis-linux
> > python main.py
> > # Puis via MCP : cowork_execute, cowork_list, cowork_stats
> > ```
> >
> > ---
> >
> > ## Utilisation
> >
> > ```bash
> > # Exécuter tous les tests
> > python cowork_engine.py --mode test-all
> >
> > # Détecter les gaps
> > python cowork_engine.py --mode gaps
> >
> > # Anticiper les améliorations
> > python cowork_engine.py --mode anticipate
> >
> > # Auto-amélioration
> > python cowork_engine.py --mode improve
> >
> > # Rechercher des scripts
> > python cowork_engine.py --search "trading"
> >
> > # Exécuter un script spécifique
> > python cowork_engine.py --run trading_signal_validator.py
> > ```
> >
> > ---
> >
> > ## Intégration avec JARVIS
> >
> > COWORK s'intègre à l'écosystème JARVIS via :
> >
> > - **Timer systemd** : `jarvis-cowork@1.timer` — s'exécute automatiquement toutes les 6h
> > - - **Conteneur Docker** : `cowork-engine` + `cowork-dispatcher` dans `docker-compose.modular.yml`
> >   - - **Bridge MCP** : `cowork_mcp_bridge.py` — expose 8 outils au Claude SDK
> >     - - **Base de données** : Résultats loggés dans `etoile.db` (42 tables, partagée avec tous les composants JARVIS)
> >       - - **WebSocket** : Événements diffusés sur `jarvis-ws :9742`
> >        
> >         - ---
> >
> > ## Repos liés
> >
> > | Repo | Description |
> > |------|-------------|
> > | [jarvis-linux](https://github.com/Turbo31150/jarvis-linux) | Repo principal JARVIS — déploiement complet |
> > | [JARVIS-CLUSTER](https://github.com/Turbo31150/JARVIS-CLUSTER) | Infrastructure cluster multi-nœuds |
> > | [jarvis-whisper-flow](https://github.com/Turbo31150/jarvis-whisper-flow) | Assistant vocal (basé sur Whisper) |
> >
> > ---
> >
> > *Auteur : Turbo31150 | Plateforme : Windows + Linux | Cycle : Toutes les 6h autonome | Mars 2026*
