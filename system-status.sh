#!/bin/bash
# Check system status for RAM-to-VRAM optimization

echo "=== System Status Report ==="
echo ""

# Check Ollama
echo "1. Ollama Status:"
if systemctl is-active --quiet ollama; then
    echo "   ✓ Ollama is running"
else
    echo "   ✗ Ollama is not running"
fi

# Check loaded models
echo ""
echo "2. Loaded Models:"
curl -s http://localhost:11434/api/ps 2>/dev/null | jq -r '.models[] | "   - \(.name) (\(.context_length) context)"' 2>/dev/null || echo "   Unable to connect to Ollama"

# Check GPU
echo ""
echo "3. GPU Status:"
nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits 2>/dev/null | while read line; do
    IFS=', ' read -r util used total <<< "$line"
    echo "   GPU: ${util}% utilized, ${used}MB/${total}MB VRAM used"
done || echo "   GPU not available"

# Check RAM
echo ""
echo "4. RAM Status:"
free -h | grep Mem | awk '{print "   Total: "$2", Used: "$3", Available: "$7}'

# Check agents
echo ""
echo "5. Agent Status:"
AGENT_COUNT=$(ps aux | grep "r13 gateway" | grep -v grep | wc -l)
echo "   ${AGENT_COUNT} agents running"

echo ""
echo "=== End of Report ==="