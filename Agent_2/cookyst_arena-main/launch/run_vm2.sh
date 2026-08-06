#!/bin/bash
# VM2 — PC1 | Pays : IT, ES
cd "$(dirname "$0")/.."

BASE_CMD="python3 runA.py \
  --instruction_path agent/prompts/jsons/multimodale_prompt.json \
  --model gpt-3.5-turbo \
  --consent partial \
  --observation_type html \
  --mode modal \
  --provider openai \
  --connected NotAUTH"

for COUNTRY in IT ES; do
    echo "========================================"
    echo "=== [VM2] Lancement pays : $COUNTRY ==="
    echo "========================================"
    $BASE_CMD --country $COUNTRY
done

echo "=== [VM2] Tous les pays terminés ==="
