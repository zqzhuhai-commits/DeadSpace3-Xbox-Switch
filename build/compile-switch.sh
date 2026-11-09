#!/usr/bin/env bash
set -euo pipefail
SOURCE="$(cd "${1:?source checkout required}" && pwd)"
test -f "$SOURCE/ds3/out/codegen/generated/awakened/sources.cmake"
cmake -S "$SOURCE/ds3" -B "$SOURCE/ds3/out/sw" -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_TOOLCHAIN_FILE="$SOURCE/tools/switch/cmake/switch-devkitA64.cmake" \
  -DREXSDK_DIR="$SOURCE/sdk" -DDS3_CODEGEN_DIR="$SOURCE/ds3/out/codegen" \
  -DREXGLUE_SWITCH_DEKO3D=ON
cmake --build "$SOURCE/ds3/out/sw" --target ds3 -j "${JOBS:-4}"
