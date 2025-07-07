#!/bin/bash
set -euo pipefail

KEYS_JSON="output/generated_keys.json"
DUT_PATH="src/keys_validator/dut.py"

echo "[INFO] Writing keys from $KEYS_JSON ..."
python3 src/keys_writer/write_keys.py "$DUT_PATH" "$KEYS_JSON"
