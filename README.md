# RAM-to-VRAM System for Ollama

A system to optimize RAM usage for Ollama AI models, enabling hybrid CPU+GPU processing with large context windows.

## Features

- **Hybrid CPU/GPU Processing**: Utilizes both system RAM and GPU VRAM
- **Dynamic Memory Management**: Automatically adjusts based on available resources
- **64K Context Windows**: Support for large context windows (64K tokens)
- **Agent Integration**: Ready for multi-agent systems
- **JSON-based Memory**: Persistent storage for conversations and knowledge

## System Requirements

- **CPU**: 8+ cores recommended
- **RAM**: 32GB+ (21GB+ available)
- **GPU**: NVIDIA GPU with 4GB+ VRAM (GTX 1650 or better)
- **Storage**: 260GB+ available on fast storage

## Installation

### 1. Install Ollama
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Clone this repository
```bash
git clone http://localhost:3002/r13-infrastructure/ram-to-vram-system.git
cd ram-to-vram-system
```

### 3. Configure Ollama
```bash
sudo bash setup-ollama.sh
```

### 4. Install dependencies
```bash
pip install psutil
```

## Quick Start

### 1. Installation
```bash
# Clone the repository
git clone http://localhost:3002/r13admin/ram-to-vram-system.git
cd ram-to-vram-system

# Run setup (requires sudo)
sudo bash setup-ollama.sh
```

### 2. Memory Optimization
```bash
# Check current memory usage
python3 memory_optimizer.py

# Example output:
# === Memory Optimization Report ===
# RAM: 10.12/31.2 GB (32.4%)
# VRAM: 1557/4096 MB (38.0%)
# GPU Utilization: 99%
# ✓ Plenty of RAM available - can increase context window
```

### 3. Create Models
```bash
# Create 64K context model (recommended)
bash create-64k-model.sh

# Or create custom context size
bash create-custom-model.sh 32768
```

### 4. Check System Status
```bash
bash system-status.sh
```

### 5. Test Installation
```bash
# Run the model
ollama run llama3.1:8b-64k "Hello, how are you?"

# Test conversation system
python3 conversation_coordinator.py
```

## File Structure

```
.
├── README.md                 # This file
├── setup-ollama.sh          # Ollama configuration script
├── memory_optimizer.py      # Memory optimization tool
├── conversation_coordinator.py  # Agent conversation system
├── create-64k-model.sh      # Model creation script
├── create-custom-model.sh   # Custom model script
├── system-status.sh         # System status checker
└── docs/
    ├── INSTALL.md           # Detailed installation guide
    ├── CONFIG.md            # Configuration options
    └── TROUBLESHOOTING.md   # Common issues and solutions
```

## Configuration

### Ollama Environment Variables
```bash
OLLAMA_NUM_THREADS=16          # CPU threads
OLLAMA_NUM_CTX=65536           # Context window size
OLLAMA_FLASH_ATTENTION=1       # Enable flash attention
OLLAMA_KV_CACHE_TYPE=q8_0      # KV cache quantization
OLLAMA_GPU_LAYERS=20           # GPU layers to offload
```

### Agent Configuration
- **Memory Location**: `/home/c0smic/agent-setup/agent_memory/`
- **Conversation Storage**: `/home/c0smic/agent-setup/conversations/`
- **Rate Limiting**: 5-second cooldown between agent cycles

## Memory Optimization

### Current Configuration
- **Model**: llama3.1:8b-64k (64K context)
- **RAM Usage**: ~36GB (system RAM)
- **VRAM Usage**: ~1.5GB (GPU VRAM)
- **GPU Utilization**: 98%

### Optimization Strategy
1. **CPU Offloading**: Store model weights in system RAM
2. **GPU Acceleration**: Use GPU for compute-intensive operations
3. **KV Cache**: Store attention cache in CPU RAM (2.1GB)
4. **Context Window**: 64K tokens for long conversations

## Agent System

### Available Agents
1. **Jack** - Analytical/Systems thinking
2. **Sam** - Creative/Idea generation
3. **Alice** - Supportive/Helpful
4. **Tom** - Practical/Action-oriented
5. **Alex** - Technical/Implementation
6. **Riley** - Research/Data analysis
7. **Jordan** - Strategic/Planning
8. **Morgan** - Creative/Innovative
9. **Casey** - Detailed/Documentation

### Conversation Channels
- **general**: General discussions
- **tech**: Technical topics
- **random**: Casual chat

## Monitoring

### System Status
```bash
# Memory usage
python3 memory_optimizer.py

# Agent status
ps aux | grep "r13 gateway"

# GPU utilization
nvidia-smi
```

### Logs
- **Ollama**: `journalctl -u ollama -f`
- **Agents**: `/tmp/r13-*.log`
- **MCP Server**: `/tmp/mcp-server.log`

## Troubleshooting

### High RAM Usage
- Check memory optimizer for recommendations
- Reduce context window size if needed
- Clear old conversation histories

### GPU Memory Full
- Reduce `OLLAMA_GPU_LAYERS`
- Use smaller model quantization
- Restart Ollama to clear cache

### Agent Timeout
- Increase cooldown period
- Check Ollama service status
- Verify network connectivity

## Performance Benchmarks

### Context Window Performance
- **32K tokens**: ~1.5GB RAM, 500MB VRAM
- **64K tokens**: ~3.0GB RAM, 1GB VRAM
- **128K tokens**: ~6.0GB RAM, 2GB VRAM

### Inference Speed
- **CPU only**: ~3-5 tokens/second
- **GPU only**: ~10-15 tokens/second
- **Hybrid (CPU+GPU)**: ~8-12 tokens/second

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Check `docs/TROUBLESHOOTING.md`
- Review system logs
- Contact system administrator
