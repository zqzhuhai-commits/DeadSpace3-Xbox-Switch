#!/usr/bin/env bash
set -euo pipefail
SOURCE="$(cd "${1:?source checkout required}" && pwd)"
DEST="${2:?new host-tool build directory required}"
if [ -e "$DEST" ]; then
  echo "Refusing to overwrite existing path: $DEST" >&2
  exit 1
fi
mkdir -p "$DEST"
DEST="$(cd "$DEST" && pwd)"
git clone --depth 1 --branch v0.10.0 https://github.com/rexglue/rexglue-sdk.git "$DEST/sdk"
test "$(git -C "$DEST/sdk" rev-parse HEAD)" = f5337cdc947ff6d4c4196737e2c807a48f2a1fc2
git init -q "$DEST/hells-gate"
git -C "$DEST/hells-gate" remote add origin https://github.com/florinp93/hells-gate-recomp.git
git -C "$DEST/hells-gate" fetch --depth 1 origin 3ce3993b0f03c77353f8f10fdcd982160c9a2d18
git -C "$DEST/hells-gate" checkout --detach FETCH_HEAD
git -C "$DEST/sdk" submodule update --init --recursive --depth 1 -j "${JOBS:-4}"
git -C "$DEST/sdk" apply "$DEST/hells-gate/patches/sdk/rexglue-sdk-v0.10.0.patch"
for patch in "$SOURCE"/ds3/host-patches/*.patch; do
  git -C "$DEST/sdk" apply "$patch"
done
cmake -S "$DEST/sdk" -B "$DEST/build" -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ \
  -DCMAKE_C_FLAGS=-mssse3 -DCMAKE_CXX_FLAGS=-mssse3 -DREXGLUE_USE_VULKAN=ON
cmake --build "$DEST/build" --target rexglue -j "${JOBS:-4}"
"$DEST/sdk/out/linux-amd64/rexglue" --version
mkdir -p "$SOURCE/ds3/out/rexglue-host/out"
ln -s "$DEST/sdk/out/linux-amd64" "$SOURCE/ds3/out/rexglue-host/out/linux-amd64"
