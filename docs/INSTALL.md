# Installation Guide

## Prerequisites

### Hardware
- **CPU**: 4+ cores (8+ recommended)
- **RAM**: 16GB+ (32GB recommended)
- **GPU**: NVIDIA 2GB+ VRAM (GTX 1650+ recommended)
- **Storage**: 10GB+ free (50GB+ for models)

### Software
- **OS**: Linux (Arch / Ubuntu)
- **Python**: 3.9+
- **NVIDIA Drivers**: CUDA-enabled

## Step 1: Install Dependencies

```bash
pip install psutil
```

## Step 2: Analyze Your Hardware

```bash
python3 scripts/memory_optimizer.py
```

This detects your GPU, RAM, and running backend, then recommends optimal settings.

## Step 3: Configure Your Backend

Pick **one** backend:

### Ollama (easiest)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Configure for your hardware
sudo bash backends/ollama/setup-ollama.sh
```

### vLLM (production)

```bash
# Install vLLM
pip install vllm

# Generate launch config
bash backends/vllm/setup-vllm.sh

# Launch with a model
bash config/vllm-launch.sh meta-llama/Llama-3.1-8B-Instruct
```

### llama.cpp (GGUF models)

```bash
# Install llama.cpp
# Arch: sudo pacman -S llama.cpp
# Or build from source: https://github.com/ggerganov/llama.cpp

# Generate server config
bash backends/llama-cpp/setup-llama-cpp.sh

# Launch with a GGUF model
bash config/llama-cpp-launch.sh /path/to/model.gguf
```

### LM Studio (GUI)

```bash
# Install LM Studio from https://lmstudio.ai
# Run the setup script to generate optimal config
bash backends/lm-studio/setup-lm-studio.sh

# Restart LM Studio to apply
```

## Step 4: Verify

```bash
bash scripts/system-status.sh
```

## Step 5: Fine-Tune

Run the memory optimizer after starting your backend:

```bash
python3 scripts/memory_optimizer.py
```

Adjust settings based on the recommendations.
