#!/bin/bash
# Setup Ollama for RAM-to-VRAM optimization

set -e

echo "=== Setting up Ollama for RAM-to-VRAM optimization ==="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root or with sudo"
    exit 1
fi

# Create Ollama configuration directory
mkdir -p /etc/systemd/system/ollama.service.d

# Create optimized configuration
cat > /etc/systemd/system/ollama.service.d/override.conf << 'EOF'
[Service]
Environment="OLLAMA_MODELS=/mnt/vault2-docker/ollama/models"
Environment="HOME=/mnt/vault2-docker/ollama"
Environment="OLLAMA_NUM_THREADS=16"
Environment="OLLAMA_MAX_LOADED_MODELS=3"
Environment="OLLAMA_NUM_CTX=65536"
Environment="OLLAMA_FLASH_ATTENTION=1"
Environment="OLLAMA_KV_CACHE_TYPE=q8_0"
Environment="OLLAMA_GPU_LAYERS=20"
Environment="OLLAMA_KEEP_ALIVE=24h"
Environment="CUDA_VISIBLE_DEVICES=0"
WorkingDirectory=/mnt/vault2-docker/ollama
EOF

echo "✓ Created Ollama configuration"

# Reload systemd
systemctl daemon-reload

# Restart Ollama
systemctl restart ollama

echo "✓ Ollama restarted with RAM-to-VRAM configuration"

# Wait for Ollama to start
sleep 5

# Create 64K context model
cat > /tmp/Modelfile-64k << 'EOF'
FROM llama3.1:8b-instruct-q4_K_M
PARAMETER num_ctx 65536
EOF

ollama create llama3.1:8b-64k -f /tmp/Modelfile-64k

echo "✓ Created 64K context model"

# Clean up
rm -f /tmp/Modelfile-64k

echo ""
echo "=== Setup Complete ==="
echo "Ollama is now configured for RAM-to-VRAM optimization"
echo "Model: llama3.1:8b-64k (64K context window)"
echo ""
echo "To check status:"
echo "  systemctl status ollama"
echo "  curl http://localhost:11434/api/ps"
echo ""
echo "To optimize memory:"
echo "  python3 memory_optimizer.py"