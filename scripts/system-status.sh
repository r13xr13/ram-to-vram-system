#!/bin/bash
# System status check for RAM-to-VRAM optimization
set -e

echo "╔══════════════════════════════════════════════════╗"
echo "║        RAM-to-VRAM System Status                ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

echo "━━━ Inference Backend ━━━"
BACKEND="unknown"
if systemctl is-active --quiet ollama 2>/dev/null; then
    BACKEND="ollama (systemd)"
    echo "  ✓ Ollama running"
elif ss -tlnp 2>/dev/null | grep -q ":11434\|:11435"; then
    BACKEND="ollama (port)"
    echo "  ✓ Ollama listening on port $(ss -tlnp | grep -oP ':\K1143[45]')"
elif ss -tlnp 2>/dev/null | grep -q ":8000"; then
    BACKEND="vllm"
    echo "  ✓ vLLM listening on port 8000"
elif ss -tlnp 2>/dev/null | grep -q ":8080"; then
    BACKEND="llama.cpp"
    echo "  ✓ llama.cpp server on port 8080"
elif ps aux | grep -q "[l]m-studio\|[l]ms "; then
    BACKEND="lm-studio"
    echo "  ✓ LM Studio running"
else
    echo "  ✗ No inference backend detected"
fi
echo ""

echo "━━━ Hardware ━━━"
free -h | awk '/^Mem:/{printf "  RAM:    %s total, %s used, %s available (%.0f%%)\n", $2, $3, $7, $3/$2*100}'
nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu --format=csv,noheader,nounits 2>/dev/null | while IFS=',' read -r name used total util temp; do
    echo "  GPU:    ${name} — ${used}/${total} VRAM, ${util}% util, ${temp}°C"
done || echo "  GPU:    not available"
echo ""

echo "━━━ Models ━━━"
if command -v ollama &>/dev/null && curl -sf http://localhost:11434/api/tags &>/dev/null; then
    echo "  Ollama models:"
    curl -s http://localhost:11434/api/tags | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in data.get('models', []):
    print(f\"    - {m['name']} ({m.get('details', {}).get('parameter_size', '?')})\")
" 2>/dev/null || echo "    (unable to list)"
fi

if [ -d /mnt/vault2-docker/models/gguf ]; then
    echo "  GGUF models on disk:"
    find /mnt/vault2-docker/models/gguf -name "*.gguf" -exec basename {} \; 2>/dev/null | while read f; do
        echo "    - $f"
    done
fi
echo ""

echo "━━━ Docker ━━━"
if command -v docker &>/dev/null; then
    docker ps --format "  {{.Names}}: {{.Image}} ({{.Status}})" 2>/dev/null | grep -iE "ollama|vllm|llama|model|sigil" || echo "  No AI containers running"
else
    echo "  Docker not installed"
fi
echo ""

echo "━━━ Quick Commands ━━━"
echo "  python3 scripts/memory_optimizer.py     # Memory analysis"
echo "  bash backends/ollama/setup-ollama.sh    # Configure Ollama"
echo "  bash backends/vllm/setup-vllm.sh        # Configure vLLM"
echo "  bash backends/llama-cpp/setup-llama-cpp.sh  # Configure llama.cpp"
echo "  bash backends/lm-studio/setup-lm-studio.sh  # Configure LM Studio"
