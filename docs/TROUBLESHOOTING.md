# Troubleshooting

## Backend Detection

### "No inference backend detected"

Start your backend first:
```bash
# Ollama
sudo systemctl start ollama

# vLLM
vllm serve <model>

# llama.cpp
llama-server --model <path>

# LM Studio
# Launch the GUI
```

## Ollama

### Crash-looping (status 200/CHDIR)
```bash
# WorkingDirectory doesn't exist
sudo mkdir -p /mnt/vault2-docker/ollama
sudo chown $(whoami):$(whoami) /mnt/vault2-docker/ollama
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

### "Context window too large"
```bash
# Reduce context
sudo sed -i 's/OLLAMA_NUM_CTX=.*/OLLAMA_NUM_CTX=32768/' \
  /etc/systemd/system/ollama.service.d/override.conf
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

### Model won't load
```bash
ollama pull llama3.1:8b-instruct-q4_K_M
```

## vLLM

### CUDA OOM
```bash
# Reduce GPU memory utilization
vllm serve <model> --gpu-memory-utilization 0.7
```

### Slow throughput
```bash
# Enable prefix caching and flash attention
vllm serve <model> --enable-prefix-caching --max-num-seqs 512
```

## llama.cpp

### "failed to load model"
```bash
# Verify GGUF file integrity
ls -lh /path/to/model.gguf
```

### Running entirely on CPU
```bash
# Increase GPU layers
llama-server --model <path> --n-gpu-layers 20
```

## General

### High RAM usage
```bash
python3 scripts/memory_optimizer.py
# Follow recommendations to reduce context or KV cache
```

### GPU not detected
```bash
nvidia-smi
# If not found, install NVIDIA drivers
```

### System freezing during inference
```bash
# Add swap as safety net
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```
