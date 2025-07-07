#!/bin/bash
# ==========================================
# Script: generate_keys.sh
# Description: Run generate_keys.py and generate 'generated_keys.json'
# ==========================================

set -euo pipefail

KEYS_JSON="output/generated_keys.json"


echo "[INFO] Generating keys..."
mkdir -p output
python3 src/keys_gen/generate_keys.py output/generated_keys.json

echo "[INFO] Output saved to generated_keys.json"