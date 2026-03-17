# Configuration Guide

## Ollama Configuration

### Environment Variables
These are set in `/etc/systemd/system/ollama.service.d/override.conf`:

| Variable | Value | Description |
|----------|-------|-------------|
| `OLLAMA_NUM_THREADS` | 16 | CPU threads to use |
| `OLLAMA_NUM_CTX` | 65536 | Context window size (tokens) |
| `OLLAMA_FLASH_ATTENTION` | 1 | Enable flash attention |
| `OLLAMA_KV_CACHE_TYPE` | q8_0 | KV cache quantization |
| `OLLAMA_GPU_LAYERS` | 20 | Layers to offload to GPU |
| `OLLAMA_KEEP_ALIVE` | 24h | Keep models loaded |
| `OLLAMA_MAX_LOADED_MODELS` | 3 | Max models in memory |

### Context Window Sizes
- **16K tokens**: ~1GB RAM, 200MB VRAM
- **32K tokens**: ~2GB RAM, 400MB VRAM
- **64K tokens**: ~4GB RAM, 800MB VRAM
- **128K tokens**: ~8GB RAM, 1.6GB VRAM

## Memory Optimization

### Memory Allocator
The system uses a hybrid approach:

1. **Model Weights**: Stored in system RAM (CPU memory mapping)
2. **KV Cache**: Split between CPU (2.1GB) and GPU (68MB)
3. **Compute Buffer**: GPU-only (677MB)
4. **Output Buffer**: CPU-only (0.5MB)

### Optimization Strategies

#### For 32GB RAM System
```bash
OLLAMA_NUM_CTX=65536        # 64K context
OLLAMA_GPU_LAYERS=20        # 20 layers on GPU
OLLAMA_KV_CACHE_TYPE=q8_0   # Quantized KV cache
```

#### For 16GB RAM System
```bash
OLLAMA_NUM_CTX=32768        # 32K context
OLLAMA_GPU_LAYERS=10        # 10 layers on GPU
OLLAMA_KV_CACHE_TYPE=q4_0   # More quantized KV cache
```

#### For 64GB+ RAM System
```bash
OLLAMA_NUM_CTX=131072       # 128K context
OLLAMA_GPU_LAYERS=30        # 30 layers on GPU
OLLAMA_KV_CACHE_TYPE=q8_0   # Quantized KV cache
```

## Agent Configuration

### Agent Memory Location
```bash
# Agent memory storage
/home/c0smic/agent-setup/agent_memory/
```

### Conversation Channels
```json
{
  "general": {
    "agents": ["jack", "sam", "alice", "tom"],
    "cooldown": 10
  },
  "tech": {
    "agents": ["alex", "riley", "jordan"],
    "cooldown": 8
  },
  "random": {
    "agents": ["morgan", "casey", "jack"],
    "cooldown": 15
  }
}
```

### Rate Limiting
- **Startup Delay**: 3 seconds between agents
- **Cooldown**: 5 seconds between agent cycles
- **Max Concurrent**: 1 agent at a time

## Performance Tuning

### CPU Optimization
```bash
# Set CPU governor to performance
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Allocate more CPU threads
OLLAMA_NUM_THREADS=16
```

### GPU Optimization
```bash
# Set GPU power mode
sudo nvidia-smi -pm 1
sudo nvidia-smi -pl 75

# Monitor GPU usage
watch -n 1 nvidia-smi
```

### Memory Optimization
```bash
# Clear Ollama cache
sudo systemctl stop ollama
sudo rm -rf /mnt/vault2-docker/ollama/models/*/*.cache
sudo systemctl start ollama

# Run memory optimizer
python3 memory_optimizer.py
```

## Monitoring

### System Metrics
```bash
# Real-time memory usage
watch -n 1 free -h

# GPU utilization
watch -n 1 nvidia-smi

# Ollama logs
journalctl -u ollama -f
```

### Agent Performance
```bash
# Agent status
ps aux | grep "r13 gateway"

# Check agent logs
tail -f /tmp/r13-*.log

# Memory usage per agent
du -sh /home/c0smic/agent-setup/agent_memory/*
```

## Advanced Configuration

### Custom Models
Create custom models with specific parameters:

```bash
# Create model with custom settings
cat > /tmp/Modelfile-custom << 'EOF'
FROM llama3.1:8b-instruct-q4_K_M
PARAMETER num_ctx 49152
PARAMETER temperature 0.7
PARAMETER top_p 0.9
EOF

ollama create custom-model -f /tmp/Modelfile-custom
```

### Multiple Models
Load multiple models simultaneously:

```bash
# Load different models
ollama run llama3.1:8b-64k
ollama run mistral:latest
ollama run qwen2.5:7b

# Check loaded models
curl http://localhost:11434/api/ps
```

## Troubleshooting

### High CPU Usage
- Reduce `OLLAMA_NUM_THREADS`
- Lower context window size
- Check for background processes

### GPU Memory Full
- Reduce `OLLAMA_GPU_LAYERS`
- Use smaller quantization (q4_0 instead of q8_0)
- Restart Ollama to clear cache

### Slow Inference
- Enable flash attention
- Use GPU acceleration
- Reduce context window if too large

## Best Practices

1. **Monitor Memory**: Run `memory_optimizer.py` regularly
2. **Clear Cache**: Restart Ollama weekly
3. **Update Models**: Keep models updated
4. **Balance Load**: Don't overload CPU/GPU
5. **Use Appropriate Context**: Match context size to task

## Reference

- **Ollama Docs**: https://ollama.ai/docs
- **Model Library**: https://ollama.ai/library
- **System Monitor**: `bash system-status.sh`
