#!/bin/bash
# Create 64K context window model for Ollama

echo "Creating 64K context window model..."

cat > /tmp/Modelfile-64k << 'EOF'
FROM llama3.1:8b-instruct-q4_K_M
PARAMETER num_ctx 65536
EOF

ollama create llama3.1:8b-64k -f /tmp/Modelfile-64k

rm -f /tmp/Modelfile-64k

echo "✓ Model created: llama3.1:8b-64k"
echo "  Context window: 65,536 tokens"
echo ""
echo "To use this model:"
echo "  ollama run llama3.1:8b-64k"