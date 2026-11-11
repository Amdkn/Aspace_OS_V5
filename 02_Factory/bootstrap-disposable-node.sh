#!/usr/bin/env bash
# A'Space OS V5 — 02_Factory/bootstrap-disposable-node.sh
# Instancie un nœud d'exécution 100% jetable (VPS Hostinger, WSL CoolEmbrl, Cloud Shell, FreeVPS)
# Source de vérité unique : https://github.com/Amdkn/Aspace_OS_V5

set -euo pipefail

REPO_URL="https://github.com/Amdkn/Aspace_OS_V5.git"
TARGET_DIR="${ASPACE_HOME:-$HOME/Aspace_OS_V5}"
FRACTAL_LAYER="${ASPACE_LAYER:-4L}"
NODE_NAME="$(hostname | tr '[:upper:]' '[:lower:]' | tr ' ' '-')"

echo "=== [ASPACE OS V5] BOOTSTRAP DU NŒUD JETABLE : $NODE_NAME (Couche $FRACTAL_LAYER) ==="

# 1. Clonage Sparse / Shallow ultra-léger depuis GitHub SSOT
if [ ! -d "$TARGET_DIR/.git" ]; then
  git clone --depth 1 "$REPO_URL" "$TARGET_DIR"
fi
cd "$TARGET_DIR"
git fetch origin master
git checkout -B "turns/$NODE_NAME/$(date -u +%Y-%m-%d)" origin/master

# 2. Hydratation uniquement de la couche fractale requise (0L -> 20L)
git submodule update --init --depth 1 -- 01_Forkable/FKB00_Runtime/00_A0_Core/agent-zero || true

# 3. Démarrage en arrière-plan du démon EGM FreeCloud (:31415) si présent
if [ -f "01_Forkable/FKB01_Inference/03_Inference_FreeCloud/aspace_freecloud_gateway.py" ]; then
  nohup python3 01_Forkable/FKB01_Inference/03_Inference_FreeCloud/aspace_freecloud_gateway.py >/tmp/aspace_egm_gateway.log 2>&1 &
fi

# 4. Exécution du premier checkpoint de tour (Git Branch + Sheets Ledger + Drive 5TB CAS Index)
python3 02_Factory/hooks/aspace_turn_persistence_daemon.py "LD01" "B1-BOOK-AMP"

echo "=== [OK] Nœud $NODE_NAME opérationnel et synchronisé sur GitHub SSOT + Drive 5 To ==="
