#!/bin/bash
# Setup LM Studio for RAM-to-VRAM optimization
set -e

echo "=== Setting up LM Studio for RAM-to-VRAM optimization ==="

RAM_GB=$(free -g | awk '/^Mem:/{print $2}')
VRAM_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 || echo "4096")
CPU_CORES=$(nproc)

echo "Detected: ${RAM_GB}GB RAM, ${VRAM_MB}MB VRAM, ${CPU_CORES} cores"

if [ "$RAM_GB" -ge 64 ]; then
    CTX_SIZE=131072
    GPU_LAYERS=99
elif [ "$RAM_GB" -ge 32 ]; then
    CTX_SIZE=65536
    GPU_LAYERS=60
elif [ "$RAM_GB" -ge 16 ]; then
    CTX_SIZE=32768
    GPU_LAYERS=30
else
    CTX_SIZE=16384
    GPU_LAYERS=15
fi

if [ "$VRAM_MB" -lt 4096 ]; then
    GPU_LAYERS=10
elif [ "$VRAM_MB" -lt 8192 ]; then
    GPU_LAYERS=25
fi

LMSTUDIO_CONFIG="${HOME}/.cache/lm-studio/config.json"

if [ -f "$LMSTUDIO_CONFIG" ]; then
    cp "$LMSTUDIO_CONFIG" "${LMSTUDIO_CONFIG}.bak"
    echo "✓ Backed up existing LM Studio config"
fi

cat > "$LMSTUDIO_CONFIG" << EOF
{
  "context_length": ${CTX_SIZE},
  "gpu_layers": ${GPU_LAYERS},
  "flash_attention": true,
  "cpu_threads": ${CPU_CORES},
  "cache_type_k": "q8_0",
  "cache_type_v": "q8_0"
}
EOF

echo "✓ Created LM Studio configuration"
echo "  Context: ${CTX_SIZE} tokens"
echo "  GPU layers: ${GPU_LAYERS}"
echo "  Threads: ${CPU_CORES}"
echo ""
echo "Restart LM Studio to apply changes."
