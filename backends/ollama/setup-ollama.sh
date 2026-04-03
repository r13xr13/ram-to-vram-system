#!/bin/bash
# Setup Ollama for RAM-to-VRAM optimization
set -e

echo "=== Setting up Ollama for RAM-to-VRAM optimization ==="

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root or with sudo"
    exit 1
fi

# Detect hardware
RAM_GB=$(free -g | awk '/^Mem:/{print $2}')
VRAM_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 || echo "4096")
CPU_CORES=$(nproc)

echo "Detected: ${RAM_GB}GB RAM, ${VRAM_MB}MB VRAM, ${CPU_CORES} cores"

# Calculate optimal settings
if [ "$RAM_GB" -ge 64 ]; then
    CTX_SIZE=131072
    GPU_LAYERS=30
    KV_CACHE="q8_0"
elif [ "$RAM_GB" -ge 32 ]; then
    CTX_SIZE=65536
    GPU_LAYERS=20
    KV_CACHE="q8_0"
elif [ "$RAM_GB" -ge 16 ]; then
    CTX_SIZE=32768
    GPU_LAYERS=10
    KV_CACHE="q4_0"
else
    CTX_SIZE=16384
    GPU_LAYERS=5
    KV_CACHE="q4_0"
fi

# Adjust GPU layers for small VRAM
if [ "$VRAM_MB" -lt 4096 ]; then
    GPU_LAYERS=10
elif [ "$VRAM_MB" -lt 6144 ]; then
    GPU_LAYERS=20
elif [ "$VRAM_MB" -lt 8192 ]; then
    GPU_LAYERS=30
fi

mkdir -p /etc/systemd/system/ollama.service.d

cat > /etc/systemd/system/ollama.service.d/override.conf << EOF
[Service]
Environment="OLLAMA_NUM_THREADS=${CPU_CORES}"
Environment="OLLAMA_MAX_LOADED_MODELS=3"
Environment="OLLAMA_NUM_CTX=${CTX_SIZE}"
Environment="OLLAMA_FLASH_ATTENTION=1"
Environment="OLLAMA_KV_CACHE_TYPE=${KV_CACHE}"
Environment="OLLAMA_GPU_LAYERS=${GPU_LAYERS}"
Environment="OLLAMA_KEEP_ALIVE=24h"
Environment="CUDA_VISIBLE_DEVICES=0"
EOF

echo "✓ Created Ollama configuration"
echo "  Context: ${CTX_SIZE} tokens"
echo "  GPU Layers: ${GPU_LAYERS}"
echo "  KV Cache: ${KV_CACHE}"

systemctl daemon-reload
systemctl restart ollama
sleep 3

if systemctl is-active --quiet ollama; then
    echo "✓ Ollama running"
else
    echo "✗ Ollama failed to start — check: journalctl -u ollama -f"
    exit 1
fi

echo ""
echo "=== Setup Complete ==="
echo "Run: python3 scripts/memory_optimizer.py"
