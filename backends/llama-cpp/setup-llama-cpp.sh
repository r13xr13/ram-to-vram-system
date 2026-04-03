#!/bin/bash
# Setup llama.cpp for RAM-to-VRAM optimization
set -e

echo "=== Setting up llama.cpp for RAM-to-VRAM optimization ==="

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

cat > config/llama-cpp-launch.sh << EOF
#!/bin/bash
# Auto-generated llama.cpp launch command
llama-server \\
    --model "\$1" \\
    --ctx-size ${CTX_SIZE} \\
    --n-gpu-layers ${GPU_LAYERS} \\
    --flash-attn \\
    --cache-type-k q8_0 \\
    --cache-type-v q8_0 \\
    --n-threads ${CPU_CORES} \\
    --n-threads-batch ${CPU_CORES} \\
    --host 0.0.0.0 \\
    --port 8080
EOF

chmod +x config/llama-cpp-launch.sh

echo "✓ Created llama.cpp launch config"
echo "  Context: ${CTX_SIZE} tokens"
echo "  GPU layers: ${GPU_LAYERS}"
echo "  Threads: ${CPU_CORES}"
echo ""
echo "Usage: bash config/llama-cpp-launch.sh <path-to-gguf>"
echo "Example: bash config/llama-cpp-launch.sh /mnt/vault2-docker/models/gguf/Meta-Llama-3.1-8B-Instruct-Q4_K_S.gguf"
