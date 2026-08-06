#!/bin/bash
# VM1 — PC1 | Pays : FR, DE
cd "$(dirname "$0")/.."

BASE_CMD="python3 runA.py \
  --instruction_path agent/prompts/jsons/multimodale_prompt.json \
  --model gpt-3.5-turbo \
  --consent partial \
  --observation_type html \
  --mode modal \
  --provider openai \
  --connected NotAUTH"

for COUNTRY in PT DE; do
    echo "========================================"
    echo "=== [VM1] Lancement pays : $COUNTRY ==="
    echo "========================================"
    $BASE_CMD --country $COUNTRY
done

echo "=== [VM1] Tous les pays terminés ==="
