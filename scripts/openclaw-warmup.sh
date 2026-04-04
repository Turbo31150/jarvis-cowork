#!/usr/bin/env bash
# OpenClaw Agent Warmup — lance tous les agents enregistrés au boot
# Chaque agent reçoit un ping pour créer son conteneur sandbox

set -euo pipefail

LOG="/tmp/openclaw-warmup.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] OpenClaw warmup starting..." > "$LOG"

# Attendre que le gateway soit prêt
MAX_WAIT=60
WAITED=0
while ! curl -sf http://127.0.0.1:18789/ >/dev/null 2>&1; do
    sleep 2
    WAITED=$((WAITED + 2))
    if [ "$WAITED" -ge "$MAX_WAIT" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] TIMEOUT: gateway not ready after ${MAX_WAIT}s" >> "$LOG"
        exit 1
    fi
done
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Gateway ready (waited ${WAITED}s)" >> "$LOG"

# Liste des agents à warm-up
AGENTS=(
    main master sys-ops linux-admin ai-engine cluster-mgr
    trading-engine automation monitoring ops-sre voice-engine comms
    browser-ops linkedin-agent codeur-agent mail-agent
    cowork-codegen cowork-testing cowork-deploy cowork-docs
    cowork-monitor cowork-git cowork-refactor
)

OK=0
FAIL=0

for agent in "${AGENTS[@]}"; do
    if openclaw agent --agent "$agent" -m "/nothink status ping" --timeout 30 --json >/dev/null 2>&1; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ $agent" >> "$LOG"
        OK=$((OK + 1))
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✗ $agent" >> "$LOG"
        FAIL=$((FAIL + 1))
    fi
done

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Warmup done: ${OK} ok, ${FAIL} failed / ${#AGENTS[@]} total" >> "$LOG"
