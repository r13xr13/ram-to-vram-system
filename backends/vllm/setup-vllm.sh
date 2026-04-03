#!/bin/bash
# Setup vLLM for RAM-to-VRAM optimization
set -e

echo "=== Setting up vLLM for RAM-to-VRAM optimization ==="

RAM_GB=$(free -g | awk '/^Mem:/{print $2}')
VRAM_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 || echo "4096")

echo "Detected: ${RAM_GB}GB RAM, ${VRAM_MB}MB VRAM"

# Calculate vLLM settings
if [ "$VRAM_MB" -ge 24000 ]; then
    GPU_UTIL="0.95"
    SWAP=16
    KV_DTYPE="auto"
elif [ "$VRAM_MB" -ge 12000 ]; then
    GPU_UTIL="0.9"
    SWAP=8
    KV_DTYPE="auto"
elif [ "$VRAM_MB" -ge 6000 ]; then
    GPU_UTIL="0.85"
    SWAP=4
    KV_DTYPE="fp8"
else
    GPU_UTIL="0.8"
    SWAP=4
    KV_DTYPE="fp8"
fi

CTX_SIZE=65536
if [ "$RAM_GB" -ge 64 ]; then
    CTX_SIZE=131072
elif [ "$RAM_GB" -lt 16 ]; then
    CTX_SIZE=32768
fi

cat > config/vllm-launch.sh << EOF
#!/bin/bash
# Auto-generated vLLM launch command
vllm serve "\$1" \\
    --max-model-len ${CTX_SIZE} \\
    --gpu-memory-utilization ${GPU_UTIL} \\
    --max-num-seqs 256 \\
    --swap-space ${SWAP} \\
    --enable-prefix-caching \\
    --kv-cache-dtype ${KV_DTYPE} \\
    --port 8000
EOF

chmod +x config/vllm-launch.sh

echo "✓ Created vLLM launch config"
echo "  Max context: ${CTX_SIZE} tokens"
echo "  GPU memory util: ${GPU_UTIL}"
echo "  Swap space: ${SWAP} GB"
echo "  KV cache dtype: ${KV_DTYPE}"
echo ""
echo "Usage: bash config/vllm-launch.sh <model-name>"
echo "Example: bash config/vllm-launch.sh meta-llama/Llama-3.1-8B-Instruct"
