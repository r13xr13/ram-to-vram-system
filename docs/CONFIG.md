# Configuration Reference

## Ollama

Set in `/etc/systemd/system/ollama.service.d/override.conf`:

| Variable | Description |
|----------|-------------|
| `OLLAMA_NUM_THREADS` | CPU threads (default: min(16, nproc)) |
| `OLLAMA_NUM_CTX` | Context window in tokens |
| `OLLAMA_FLASH_ATTENTION` | Enable flash attention (1 = on) |
| `OLLAMA_KV_CACHE_TYPE` | KV cache quantization: f16, q8_0, q4_0 |
| `OLLAMA_GPU_LAYERS` | Layers offloaded to GPU |
| `OLLAMA_KEEP_ALIVE` | Keep models loaded (e.g., 24h) |
| `OLLAMA_MAX_LOADED_MODELS` | Max models in memory |

## vLLM

Launch arguments:

| Argument | Description |
|----------|-------------|
| `--max-model-len` | Context window in tokens |
| `--gpu-memory-utilization` | Fraction of VRAM to use (0.0-1.0) |
| `--max-num-seqs` | Max concurrent sequences |
| `--swap-space` | CPU swap space in GB |
| `--enable-prefix-caching` | Enable KV cache reuse |
| `--kv-cache-dtype` | KV cache dtype: auto, fp8, fp16 |

Environment variables:

| Variable | Description |
|----------|-------------|
| `VLLM_USE_V1` | Use v1 engine (1 = on) |
| `VLLM_ATTENTION_BACKEND` | Attention backend: FLASH_ATTN, XFORMERS |

## llama.cpp

Server arguments:

| Argument | Description |
|----------|-------------|
| `--ctx-size` | Context window in tokens |
| `--n-gpu-layers` | Layers offloaded to GPU |
| `--flash-attn` | Enable flash attention |
| `--cache-type-k` | K cache type: f16, q8_0, q4_0 |
| `--cache-type-v` | V cache type: f16, q8_0, q4_0 |
| `--n-threads` | CPU threads |
| `--n-threads-batch` | Batch processing threads |

## LM Studio

Config at `~/.cache/lm-studio/config.json`:

| Setting | Description |
|---------|-------------|
| `context_length` | Context window in tokens |
| `gpu_layers` | Layers offloaded to GPU |
| `flash_attention` | Enable flash attention |
| `cpu_threads` | CPU threads |
| `cache_type_k` | K cache type |
| `cache_type_v` | V cache type |

## Memory Profiles

### 16GB RAM / 4GB VRAM (GTX 1650)
```
Context: 32K
GPU Layers: 10-20
KV Cache: q4_0
Flash Attention: on
```

### 32GB RAM / 8GB VRAM (RTX 3070)
```
Context: 64K
GPU Layers: 30-40
KV Cache: q8_0
Flash Attention: on
```

### 64GB RAM / 24GB VRAM (RTX 3090)
```
Context: 128K
GPU Layers: 80-99 (full offload)
KV Cache: q8_0
Flash Attention: on
```

## Monitoring

```bash
# Real-time memory
watch -n 1 free -h

# GPU
watch -n 1 nvidia-smi

# Ollama logs
journalctl -u ollama -f

# Memory report
python3 scripts/memory_optimizer.py
```
