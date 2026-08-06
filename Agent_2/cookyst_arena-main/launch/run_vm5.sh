#!/bin/bash
# VM5 — PC2 | Pays : EN, IE
cd "$(dirname "$0")/.."

BASE_CMD="python3 runA.py \
  --instruction_path agent/prompts/jsons/multimodale_prompt.json \
  --model gpt-3.5-turbo \
  --consent partial \
  --observation_type html \
  --mode modal \
  --provider openai \
  --connected NotAUTH"

for COUNTRY in EN IE; do
    echo "========================================"
    echo "=== [VM5] Lancement pays : $COUNTRY ==="
    echo "========================================"
    $BASE_CMD --country $COUNTRY
done

echo "=== [VM5] Tous les pays terminés ==="
