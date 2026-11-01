#!/usr/bin/env bash
# Instala a voz neural (espeak-ng + Kokoro v1.0 pm_santa) em $TTS_ROOT (padrão ~/tts).
# Tudo vem do GitHub. Leva ~2-4 min num ambiente novo. Idempotente.
set -euo pipefail
TTS_ROOT="${TTS_ROOT:-$HOME/tts}"
KIT="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$TTS_ROOT/kokoro"
cd "$TTS_ROOT"

if [ ! -x install/bin/espeak-ng ]; then
  echo "[setup] compilando espeak-ng..."
  [ -d src ] || git clone -q --depth 1 https://github.com/espeak-ng/espeak-ng.git src
  cmake -S src -B build -DCMAKE_INSTALL_PREFIX="$TTS_ROOT/install" -DCMAKE_BUILD_TYPE=Release \
    -DUSE_ASYNC=OFF -DUSE_MBROLA=OFF -DUSE_LIBSONIC=OFF -DUSE_LIBPCAUDIO=OFF \
    -DUSE_KLATT=OFF -DUSE_SPEECHPLAYER=OFF > /tmp/espeak_cmake.log 2>&1
  cmake --build build -j"$(nproc)" > /tmp/espeak_build.log 2>&1
  cmake --install build > /tmp/espeak_install.log 2>&1
fi

REL=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  if [ ! -s "kokoro/$f" ]; then
    echo "[setup] baixando $f..."
    curl -sSL --retry 3 -m 900 -o "kokoro/$f" "$REL/$f"
  fi
done

python3 - <<'PY'
import numpy as np, os
root = os.environ.get("TTS_ROOT", os.path.expanduser("~/tts"))
v = np.load(os.path.join(root, "kokoro", "voices-v1.0.bin"))
np.save(os.path.join(root, "kokoro", "pm_santa.npy"), v["pm_santa"])
PY

python3 -c "import onnxruntime, numpy, PIL" || pip install --break-system-packages -q onnxruntime numpy pillow

echo "[setup] teste de voz..."
TTS_ROOT="$TTS_ROOT" python3 "$KIT/neural_tts.py" "Teste de voz do canal Curiosidades do Mundo." /tmp/teste_voz.wav
echo "[setup] OK"
