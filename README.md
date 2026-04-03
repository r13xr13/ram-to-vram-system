# RAM-to-VRAM System

> Hybrid CPU+GPU memory optimization for Ollama AI models with multi-agent conversation orchestration.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-3776AB.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/Ollama-latest-0891B2.svg)](https://ollama.ai)

## Overview

RAM-to-VRAM System enables running large language models on consumer hardware by intelligently splitting memory load between system RAM and GPU VRAM. Built for NVIDIA GPUs with limited VRAM (4GB+), it lets you run 8B+ parameter models with 64K+ context windows that would otherwise require enterprise hardware.

The system includes a **multi-agent conversation coordinator** — 9 specialized AI agents that can discuss, debate, and collaborate across channels, each with distinct personalities and expertise areas.

## Features

- **Hybrid CPU/GPU Processing** — Model weights in RAM, compute on GPU
- **Dynamic Memory Management** — Auto-adjusts context windows based on available resources
- **64K+ Context Windows** — Long conversations and document analysis on consumer hardware
- **Multi-Agent Orchestration** — 9 agents with cooldowns, priorities, and conversation channels
- **JSON-Based Persistence** — Conversations and agent state survive restarts
- **KV Cache Quantization** — q8_0/q4_0 cache compression for memory efficiency
- **System Monitoring** — Real-time RAM, VRAM, GPU utilization, and agent status

## Quick Start

```bash
# 1. Clone
git clone https://github.com/r13xr13/ram-to-vram-system.git
cd ram-to-vram-system

# 2. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 3. Configure Ollama (requires sudo)
sudo bash setup-ollama.sh

# 4. Install Python dependencies
pip install psutil

# 5. Create 64K context model
bash create-64k-model.sh

# 6. Check system status
bash system-status.sh
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    RAM-to-VRAM                       │
├──────────────────┬──────────────────────────────────┤
│   CPU (RAM)      │   GPU (VRAM)                     │
│                  │                                  │
│  • Model weights │  • Compute layers (20 layers)    │
│  • KV cache      │  • Compute buffer                │
│    (2.1GB)       │    (677MB)                       │
│  • Output buffer │                                  │
│    (0.5MB)       │                                  │
├──────────────────┴──────────────────────────────────┤
│                                                      │
│  Ollama Server ←→ Memory Optimizer ←→ Agents        │
│                                                      │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                │
│  │ Jack    │ │ Sam     │ │ Alice   │  ... + 6 more  │
│  │Analytic │ │Creative │ │Support  │                │
│  └─────────┘ └─────────┘ └─────────┘                │
└─────────────────────────────────────────────────────┘
```

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8+ cores, 16 threads |
| RAM | 16GB | 32GB+ |
| GPU | NVIDIA 2GB VRAM | NVIDIA 4GB+ (GTX 1650+) |
| Storage | 10GB free | 260GB+ (for models) |
| OS | Linux | Arch-based / Ubuntu |

## Project Structure

```
ram-to-vram-system/
├── setup-ollama.sh              # Ollama systemd configuration
├── memory_optimizer.py          # Real-time RAM/VRAM monitoring
├── system-status.sh             # One-command system health check
├── create-64k-model.sh          # Create 64K context model
├── create-custom-model.sh       # Create model with custom context
├── agent-coordinator.py         # Multi-agent scheduling & cooldowns
├── conversation_coordinator.py  # Agent conversation orchestration
├── docs/
│   ├── INSTALL.md               # Detailed installation guide
│   ├── CONFIG.md                # Configuration reference
│   └── TROUBLESHOOTING.md       # Common issues & solutions
└── README.md
```

## Usage

### Memory Optimization

```bash
# Check current memory usage and get recommendations
python3 memory_optimizer.py
```

Output:
```
=== Memory Optimization Report ===
RAM: 10.12/31.2 GB (32.4%)
VRAM: 1557/4096 MB (38.0%)
GPU Utilization: 99%
✓ Plenty of RAM available - can increase context window
```

### System Status

```bash
bash system-status.sh
```

Checks: Ollama service, loaded models, GPU status, RAM, and running agents.

### Model Creation

```bash
# 64K context (recommended for 32GB RAM)
bash create-64k-model.sh

# Custom context size
bash create-custom-model.sh 32768    # 32K
bash create-custom-model.sh 131072   # 128K (64GB+ RAM)
```

### Agent System

The system includes 9 agents with distinct personalities:

| Agent | Style | Expertise |
|-------|-------|-----------|
| Jack | Analytical | Systems thinking, analysis |
| Sam | Creative | Ideas, projects, design |
| Alice | Supportive | Help, assistance, feedback |
| Tom | Practical | Tasks, actions, results |
| Alex | Technical | Code, debugging, implementation |
| Riley | Research | Data, research, analysis |
| Jordan | Strategic | Planning, strategy, goals |
| Morgan | Creative | Ideas, innovation, art |
| Casey | Detailed | Documentation, details, specs |

#### Conversation Channels

- **general** — Jack, Sam, Alice, Tom (10s cooldown)
- **tech** — Alex, Riley, Jordan (8s cooldown)
- **random** — Morgan, Casey, Jack (15s cooldown)

```bash
# Test the conversation coordinator
python3 conversation_coordinator.py

# MCP server mode
python3 conversation_coordinator.py user "Hello agents, what do you think about this?"
python3 conversation_coordinator.py auto tech "AI architecture discussion"
python3 conversation_coordinator.py start general system "Morning standup"
```

### Agent Coordinator

```python
from agent_coordinator import AgentCoordinator

coord = AgentCoordinator()
next_agent = coord.get_next_agent()  # Returns agent not on cooldown
coord.mark_agent_run(next_agent)     # Marks run, starts cooldown
coord.set_priority("alex", 3)        # Higher priority = runs more often
```

## Configuration

### Ollama Environment Variables

Set in `/etc/systemd/system/ollama.service.d/override.conf`:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_NUM_THREADS` | 16 | CPU threads for inference |
| `OLLAMA_NUM_CTX` | 65536 | Context window size (tokens) |
| `OLLAMA_FLASH_ATTENTION` | 1 | Enable flash attention (faster) |
| `OLLAMA_KV_CACHE_TYPE` | q8_0 | KV cache quantization |
| `OLLAMA_GPU_LAYERS` | 20 | Layers offloaded to GPU |
| `OLLAMA_KEEP_ALIVE` | 24h | How long to keep models loaded |
| `OLLAMA_MAX_LOADED_MODELS` | 3 | Max models in memory |

### Memory Profiles

**16GB RAM:**
```bash
OLLAMA_NUM_CTX=32768
OLLAMA_GPU_LAYERS=10
OLLAMA_KV_CACHE_TYPE=q4_0
```

**32GB RAM (default):**
```bash
OLLAMA_NUM_CTX=65536
OLLAMA_GPU_LAYERS=20
OLLAMA_KV_CACHE_TYPE=q8_0
```

**64GB+ RAM:**
```bash
OLLAMA_NUM_CTX=131072
OLLAMA_GPU_LAYERS=30
OLLAMA_KV_CACHE_TYPE=q8_0
```

### Context Window Memory Usage

| Context | RAM | VRAM |
|---------|-----|------|
| 16K | ~1GB | ~200MB |
| 32K | ~2GB | ~400MB |
| 64K | ~4GB | ~800MB |
| 128K | ~8GB | ~1.6GB |

## Performance

| Mode | Speed |
|------|-------|
| CPU only | ~3-5 tokens/sec |
| GPU only | ~10-15 tokens/sec |
| Hybrid (CPU+GPU) | ~8-12 tokens/sec |

## Monitoring

```bash
# Real-time memory
watch -n 1 free -h

# GPU utilization
watch -n 1 nvidia-smi

# Ollama logs
journalctl -u ollama -f

# Memory report (JSON)
python3 -c "from memory_optimizer import MemoryOptimizer; import json; print(json.dumps(MemoryOptimizer().create_memory_report(), indent=2))"
```

## Troubleshooting

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for detailed solutions.

**Common fixes:**

| Issue | Fix |
|-------|-----|
| Ollama not starting | `journalctl -u ollama -f` |
| GPU not detected | Check `nvidia-smi` and CUDA drivers |
| High RAM usage | Reduce context window, run `memory_optimizer.py` |
| GPU memory full | Reduce `OLLAMA_GPU_LAYERS`, use q4_0 cache |
| Agent timeout | Increase cooldown, check Ollama service |

## Documentation

- [Installation Guide](docs/INSTALL.md) — Step-by-step setup
- [Configuration Reference](docs/CONFIG.md) — All options and tuning
- [Troubleshooting](docs/TROUBLESHOOTING.md) — Common issues

## License

MIT License — see [LICENSE](LICENSE) for details.
