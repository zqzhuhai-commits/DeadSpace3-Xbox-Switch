#!/usr/bin/env bash
set -euo pipefail
TOP="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${1:?usage: prepare-source.sh NEW_CHECKOUT_DIRECTORY}"
if [ -e "$DEST" ]; then
  echo "Refusing to overwrite existing path: $DEST" >&2
  exit 1
fi
mkdir -p "$(dirname "$DEST")"
git clone --depth 1 --branch v1.0.1 https://github.com/VasilkovND/ds3-nx.git "$DEST"
test "$(git -C "$DEST" rev-parse HEAD)" = 717ae41deaf9c22059d6f27a0376d18cb443ca43
cp -a "$TOP/source/." "$DEST/"
git -C "$DEST" submodule update --init sdk
test "$(git -C "$DEST/sdk" rev-parse HEAD)" = f961303fe3c6e3a90905b379ff4bf3de9a35a757
printf 'Prepared source: %s\n' "$DEST"
