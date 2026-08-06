#!/bin/bash
# VM6 — PC2 | Pays : SE, LU, SV
cd "$(dirname "$0")/.."

BASE_CMD="python3 runA.py \
  --instruction_path agent/prompts/jsons/multimodale_prompt.json \
  --model gpt-3.5-turbo \
  --consent partial \
  --observation_type html \
  --mode modal \
  --provider openai \
  --connected NotAUTH"

for COUNTRY in SE LU SV; do
    echo "========================================"
    echo "=== [VM6] Lancement pays : $COUNTRY ==="
    echo "========================================"
    $BASE_CMD --country $COUNTRY
done

echo "=== [VM6] Tous les pays terminés ==="
