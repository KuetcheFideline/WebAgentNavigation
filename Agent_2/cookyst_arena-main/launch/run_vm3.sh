#!/bin/bash
# VM3 — PC1 | Pays : PT, PL, NL
cd "$(dirname "$0")/.."

BASE_CMD="python3 runA.py \
  --instruction_path agent/prompts/jsons/multimodale_prompt.json \
  --model gpt-3.5-turbo \
  --consent partial \
  --observation_type html \
  --mode modal \
  --provider openai \
  --connected NotAUTH"

for COUNTRY in PL NL; do
    echo "========================================"
    echo "=== [VM3] Lancement pays : $COUNTRY ==="
    echo "========================================"
    $BASE_CMD --country $COUNTRY
done

echo "=== [VM3] Tous les pays terminés ==="
