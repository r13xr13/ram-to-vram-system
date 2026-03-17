#!/bin/bash
# Create custom context window model

if [ $# -eq 0 ]; then
    echo "Usage: $0 <context_size>"
    echo "Example: $0 32768"
    exit 1
fi

CONTEXT_SIZE=$1
MODEL_NAME="llama3.1:8b-${CONTEXT_SIZE}k"

echo "Creating model with ${CONTEXT_SIZE} token context window..."

cat > /tmp/Modelfile-custom << EOF
FROM llama3.1:8b-instruct-q4_K_M
PARAMETER num_ctx ${CONTEXT_SIZE}
EOF

ollama create ${MODEL_NAME} -f /tmp/Modelfile-custom

rm -f /tmp/Modelfile-custom

echo "✓ Model created: ${MODEL_NAME}"
echo "  Context window: ${CONTEXT_SIZE} tokens"
echo ""
echo "To use this model:"
echo "  ollama run ${MODEL_NAME}"