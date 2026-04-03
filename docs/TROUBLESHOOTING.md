# Troubleshooting

## Ollama Issues

### Ollama Not Starting

```bash
# Check service status
systemctl status ollama

# View logs
journalctl -u ollama -f

# Common causes:
# - Invalid environment variable in override.conf
# - Model directory doesn't exist
# - Port 11434 already in use
```

**Fix invalid config:**
```bash
# Remove problematic override
sudo rm /etc/systemd/system/ollama.service.d/override.conf
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

### Model Won't Load

```bash
# Check if model exists
ollama list

# Check available disk space
df -h /mnt/vault2-docker/ollama/models

# Pull model manually
ollama pull llama3.1:8b-instruct-q4_K_M
```

### "Context Window Too Large" Error

Reduce the context window:
```bash
bash create-custom-model.sh 32768  # 32K instead of 64K
```

## GPU Issues

### GPU Not Detected

```bash
# Verify NVIDIA drivers
nvidia-smi

# If command not found, install drivers:
# Arch: sudo pacman -S nvidia nvidia-utils
# Ubuntu: sudo ubuntu-drivers autoinstall

# Check CUDA
nvcc --version
```

### GPU Memory Full (OOM)

```bash
# Reduce GPU layers
# Edit /etc/systemd/system/ollama.service.d/override.conf
# Change: OLLAMA_GPU_LAYERS=20 → OLLAMA_GPU_LAYERS=10

sudo systemctl daemon-reload
sudo systemctl restart ollama
```

**Or use more aggressive KV cache quantization:**
```bash
# Change: OLLAMA_KV_CACHE_TYPE=q8_0 → OLLAMA_KV_CACHE_TYPE=q4_0
```

### GPU Utilization Low

- Ensure `OLLAMA_FLASH_ATTENTION=1` is set
- Check that `OLLAMA_GPU_LAYERS` is high enough (at least 10)
- Verify model isn't too large for your VRAM

## Memory Issues

### High RAM Usage

```bash
# Check what's using memory
ps aux --sort=-%mem | head -10

# Run optimizer for recommendations
python3 memory_optimizer.py

# Reduce context window if RAM > 80%
bash create-custom-model.sh 16384
```

### Ollama Using Too Much Memory

```bash
# Check loaded models
curl http://localhost:11434/api/ps

# Unload all models
curl http://localhost:11434/api/generate -d '{"model":"","keep_alive":0}'

# Reduce OLLAMA_MAX_LOADED_MODELS in override.conf
```

### Memory Leak Suspected

```bash
# Restart Ollama to clear caches
sudo systemctl restart ollama

# Clear model cache
sudo systemctl stop ollama
sudo rm -rf /mnt/vault2-docker/ollama/models/*/*.cache
sudo systemctl start ollama
```

## Agent Issues

### Agent Not Responding

```bash
# Check if Ollama is running
systemctl status ollama

# Test model directly
ollama run llama3.1:8b-64k "test"

# Check agent logs
tail -f /tmp/r13-*.log
```

### Conversation Coordinator Errors

```bash
# Reset conversation state
rm -f /home/c0smic/agent-setup/conversations/conversation_state.json

# Test in isolation
python3 conversation_coordinator.py
```

### Agent Cooldown Too Long/Short

Edit `agent-coordinator.py`:
```python
self.cooldown_seconds = 5  # Change this value
```

## Performance Issues

### Slow Inference Speed

1. **Enable flash attention**: `OLLAMA_FLASH_ATTENTION=1`
2. **Increase GPU layers**: `OLLAMA_GPU_LAYERS=20` (or higher if VRAM allows)
3. **Reduce context window**: Smaller context = faster inference
4. **Set CPU governor to performance**:
   ```bash
   echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
   ```

### High CPU Usage

```bash
# Reduce threads
# Edit override.conf: OLLAMA_NUM_THREADS=16 → OLLAMA_NUM_THREADS=8
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

### System Freezing During Inference

- Reduce `OLLAMA_NUM_THREADS` to leave CPU headroom
- Lower context window size
- Ensure swap is enabled as a safety net:
  ```bash
  sudo fallocate -l 8G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  ```

## Installation Issues

### setup-ollama.sh Fails

```bash
# Check if running as root
whoami  # Must be root for setup script

# Manual setup:
sudo mkdir -p /etc/systemd/system/ollama.service.d
# Create override.conf manually (see docs/CONFIG.md)
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

### Python Dependencies Missing

```bash
# Arch Linux
sudo pacman -S python-psutil

# Ubuntu/Debian
sudo apt install python3-psutil

# pip (fallback)
pip install psutil
```

### Model Creation Fails

```bash
# Ensure base model is downloaded first
ollama pull llama3.1:8b-instruct-q4_K_M

# Check disk space
df -h

# Check Ollama is running
curl http://localhost:11434/api/tags
```

## Getting Help

If none of the above solves your issue:

1. Run `bash system-status.sh` and share the output
2. Run `python3 memory_optimizer.py` and share the report
3. Include Ollama logs: `journalctl -u ollama --no-pager -n 50`
4. Include your hardware specs (CPU, RAM, GPU)
