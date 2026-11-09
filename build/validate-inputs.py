#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import sys

if len(sys.argv) != 3:
    sys.exit('usage: validate-inputs.py TU_DIRECTORY DLC_XEX')
evidence = Path(__file__).resolve().parent / 'evidence/build-evidence.json'
expected = json.loads(evidence.read_text())['game_input_hashes']
tu, dlc = Path(sys.argv[1]), Path(sys.argv[2])
for name, digest in expected.items():
    path = dlc if name.startswith('dlc/') else tu / name
    if not path.is_file():
        sys.exit(f'Missing input: {path}')
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != digest:
        sys.exit(f'Unsupported input hash: {name}; expected {digest}, got {actual}')
    print(f'OK {name}')
