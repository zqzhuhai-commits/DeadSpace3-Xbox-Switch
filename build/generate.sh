#!/usr/bin/env bash
set -euo pipefail
TOP="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE="$(cd "${1:?source checkout required}" && pwd)"
TU="$(cd "${2:?TU directory required}" && pwd)"
DLC="${3:?Awakened deadspace_game_f.xex required}"
python3 "$TOP/build/validate-inputs.py" "$TU" "$DLC"
(cd "$SOURCE/sdk" && python3 tools/switch_setup.py)
python3 - "$SOURCE" <<'PY'
from pathlib import Path
import hashlib, shutil, subprocess, sys
root = Path(sys.argv[1])
record = root / 'ds3/out/sdk-patches.applied'
record.parent.mkdir(parents=True, exist_ok=True)
known = set(record.read_text().splitlines()) if record.exists() else set()
for patch in sorted((root / 'ds3/sdk-patches').glob('*.patch')):
    entry = patch.name + ' ' + hashlib.sha256(patch.read_bytes()).hexdigest()
    if entry in known:
        continue
    cmd = ['git', '-C', str(root / 'sdk'), 'apply']
    if subprocess.run(cmd + ['--check', str(patch)], capture_output=True).returncode == 0:
        subprocess.run(cmd + [str(patch)], check=True)
    else:
        subprocess.run(cmd + ['--reverse', '--check', str(patch)], check=True)
    with record.open('a') as f:
        f.write(entry + '\n')
shutil.copytree(root / 'sdk/switch/overlay', root / 'sdk/thirdparty', dirs_exist_ok=True)
PY
export DLC_XEX="$(python3 -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).resolve())' "$DLC")"
export JOBS="${JOBS:-4}"
"$SOURCE/ds3/tools/codegen.sh" "$TU"
