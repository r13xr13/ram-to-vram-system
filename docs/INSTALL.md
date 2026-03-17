# Installation Guide

## Prerequisites

### Hardware Requirements
- **CPU**: Intel i7-9700F or better (8 cores, 16 threads)
- **RAM**: 32GB+ recommended
- **GPU**: NVIDIA GTX 1650 or better (4GB+ VRAM)
- **Storage**: 260GB+ available on fast storage

### Software Requirements
- **Operating System**: Linux (Arch-based recommended)
- **Python**: 3.9+
- **Ollama**: Latest version
- **NVIDIA Drivers**: CUDA-enabled drivers

## Step-by-Step Installation

### 1. Install Ollama
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Install Python Dependencies
```bash
sudo pacman -S python-psutil
```

### 3. Clone Repository
```bash
git clone http://localhost:3002/r13-infrastructure/ram-to-vram-system.git
cd ram-to-vram-system
```

### 4. Run Setup Script
```bash
sudo bash setup-ollama.sh
```

### 5. Verify Installation
```bash
# Check Ollama status
systemctl status ollama

# Check loaded models
curl http://localhost:11434/api/ps

# Run memory optimizer
python3 memory_optimizer.py
```

## Post-Installation

### Create Models
```bash
# Create 64K context model
bash create-64k-model.sh

# Or create custom context size
bash create-custom-model.sh 32768
```

### Test Installation
```bash
# Test the model
ollama run llama3.1:8b-64k "Hello, how are you?"

# Check system status
bash system-status.sh
```

## Troubleshooting

### Ollama Not Starting
```bash
# Check logs
journalctl -u ollama -f

# Restart service
sudo systemctl restart ollama
```

### GPU Not Detected
```bash
# Check GPU
nvidia-smi

# Check CUDA
nvcc --version
```

### High RAM Usage
```bash
# Run memory optimizer
python3 memory_optimizer.py

# Reduce context window if needed
bash create-custom-model.sh 16384
```

## Next Steps

1. **Configure Agents**: Set up your agent system
2. **Monitor Performance**: Use `system-status.sh`
3. **Optimize Memory**: Run `memory_optimizer.py` regularly
4. **Update Models**: Keep models updated with latest versions
