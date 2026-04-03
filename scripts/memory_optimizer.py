#!/usr/bin/env python3
"""
RAM-to-VRAM Memory Optimizer — Backend-Agnostic
Dynamically manages RAM and VRAM usage across llama.cpp, vLLM, Ollama, and LM Studio.
"""

import psutil
import subprocess
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class MemoryStats:
    ram_total_gb: float
    ram_used_gb: float
    ram_available_gb: float
    ram_percent: float
    vram_used_mb: float
    vram_total_mb: float
    vram_percent: float
    gpu_util_percent: float
    gpu_temp_c: float
    gpu_power_w: float
    swap_total_gb: float
    swap_used_gb: float
    swap_percent: float


@dataclass
class Recommendation:
    action: str
    reason: str
    suggestion: str
    backend_specific: bool = False


class MemoryOptimizer:
    """Backend-agnostic RAM/VRAM optimizer for local LLM inference."""

    def __init__(self, vram_override_mb: Optional[int] = None):
        self.total_ram_gb = psutil.virtual_memory().total / (1024**3)
        # Auto-detect VRAM, allow override
        self.total_vram_mb = vram_override_mb or self._detect_vram()

    def _detect_vram(self) -> int:
        """Detect total GPU VRAM in MB via nvidia-smi."""
        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=memory.total",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return int(result.stdout.strip().split("\n")[0])
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
            pass
        return 4096  # Default fallback: GTX 1650

    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system memory stats."""
        ram = psutil.virtual_memory()
        swap = psutil.swap_memory()
        gpu = self._get_gpu_stats()

        return {
            "ram_total_gb": round(ram.total / (1024**3), 2),
            "ram_used_gb": round(ram.used / (1024**3), 2),
            "ram_available_gb": round(ram.available / (1024**3), 2),
            "ram_percent": ram.percent,
            "swap_total_gb": round(swap.total / (1024**3), 2),
            "swap_used_gb": round(swap.used / (1024**3), 2),
            "swap_percent": swap.percent,
            "gpu": gpu,
        }

    def _get_gpu_stats(self) -> Dict[str, Any]:
        """Get GPU memory usage, temperature, and power."""
        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                parts = [x.strip() for x in result.stdout.strip().split(",")]
                return {
                    "vram_used_mb": int(parts[0]),
                    "vram_total_mb": int(parts[1]),
                    "vram_percent": round(int(parts[0]) / int(parts[1]) * 100, 1),
                    "gpu_util_percent": int(parts[2]),
                    "gpu_temp_c": int(parts[3]),
                    "gpu_power_w": float(parts[4]),
                }
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError, IndexError):
            pass
        return {
            "vram_used_mb": 0,
            "vram_total_mb": self.total_vram_mb,
            "vram_percent": 0,
            "gpu_util_percent": 0,
            "gpu_temp_c": 0,
            "gpu_power_w": 0,
        }

    def detect_backend(self) -> str:
        """Detect which inference backend is currently running."""
        backends = {
            "ollama": ["ollama serve", "ollama"],
            "vllm": ["vllm", "vllm.entrypoints"],
            "llama-cpp": ["llama-server", "llama-cli", "llama.cpp"],
            "lm-studio": ["lms", "lm-studio"],
        }

        try:
            result = subprocess.run(
                ["ps", "aux"], capture_output=True, text=True, timeout=5
            )
            processes = result.stdout.lower()

            for backend, keywords in backends.items():
                for kw in keywords:
                    if kw in processes:
                        return backend
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Check listening ports as fallback
        try:
            result = subprocess.run(
                ["ss", "-tlnp"], capture_output=True, text=True, timeout=5
            )
            ports = result.stdout

            if ":11434" in ports or ":11435" in ports:
                return "ollama"
            if ":8000" in ports:
                return "vllm"
            if ":8080" in ports:
                return "llama-cpp"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return "unknown"

    def get_backend_config(self, backend: str) -> Dict[str, Any]:
        """Get recommended configuration for the detected backend."""
        ram_gb = self.total_ram_gb
        vram_mb = self.total_vram_mb
        ram_available = psutil.virtual_memory().available / (1024**3)

        configs = {
            "ollama": {
                "env_vars": {
                    "OLLAMA_NUM_THREADS": min(16, os.cpu_count() or 8),
                    "OLLAMA_NUM_CTX": self._recommended_context(ram_available),
                    "OLLAMA_FLASH_ATTENTION": 1,
                    "OLLAMA_KV_CACHE_TYPE": "q8_0" if ram_available > 10 else "q4_0",
                    "OLLAMA_GPU_LAYERS": self._recommended_gpu_layers(vram_mb),
                    "OLLAMA_KEEP_ALIVE": "24h",
                    "OLLAMA_MAX_LOADED_MODELS": 1 if vram_mb < 6000 else 3,
                },
                "systemd_path": "/etc/systemd/system/ollama.service.d/override.conf",
            },
            "vllm": {
                "launch_args": {
                    "--max-model-len": self._recommended_context(ram_available),
                    "--gpu-memory-utilization": min(0.9, vram_mb / 8192),
                    "--max-num-seqs": 256,
                    "--swap-space": max(4, int(ram_available)),
                    "--enable-prefix-caching": True,
                    "--kv-cache-dtype": "fp8" if vram_mb < 8000 else "auto",
                },
                "env_vars": {
                    "VLLM_USE_V1": "1",
                    "VLLM_ATTENTION_BACKEND": "FLASH_ATTN",
                },
            },
            "llama-cpp": {
                "server_args": {
                    "--ctx-size": self._recommended_context(ram_available),
                    "--n-gpu-layers": self._recommended_gpu_layers(vram_mb),
                    "--flash-attn": True,
                    "--cache-type-k": "q8_0",
                    "--cache-type-v": "q8_0",
                    "--n-threads": min(16, os.cpu_count() or 8),
                    "--n-threads-batch": min(16, os.cpu_count() or 8),
                },
            },
            "lm-studio": {
                "settings": {
                    "context_length": self._recommended_context(ram_available),
                    "gpu_layers": self._recommended_gpu_layers(vram_mb),
                    "flash_attention": True,
                    "cpu_threads": min(16, os.cpu_count() or 8),
                },
                "config_path": "~/.cache/lm-studio/config.json",
            },
        }

        return configs.get(backend, {})

    def _recommended_context(self, ram_available_gb: float) -> int:
        """Recommend context window size based on available RAM."""
        if ram_available_gb > 20:
            return 131072  # 128K
        elif ram_available_gb > 10:
            return 65536  # 64K
        elif ram_available_gb > 5:
            return 32768  # 32K
        else:
            return 16384  # 16K

    def _recommended_gpu_layers(self, vram_mb: int) -> int:
        """Recommend GPU layer offload based on VRAM."""
        if vram_mb >= 24000:  # RTX 3090/4090
            return 99  # Full offload
        elif vram_mb >= 16000:  # RTX 4080
            return 80
        elif vram_mb >= 12000:  # RTX 3060 12GB
            return 60
        elif vram_mb >= 8000:  # RTX 3070/4060 Ti
            return 40
        elif vram_mb >= 6000:  # RTX 3060 6GB
            return 30
        elif vram_mb >= 4000:  # GTX 1650
            return 20
        else:
            return 10

    def optimize(self) -> Dict[str, Any]:
        """Run optimization analysis and return recommendations."""
        stats = self.get_system_stats()
        backend = self.detect_backend()
        config = self.get_backend_config(backend)
        recommendations = self._generate_recommendations(stats, backend)

        return {
            "timestamp": datetime.now().isoformat(),
            "detected_backend": backend,
            "system": stats,
            "recommended_config": config,
            "recommendations": recommendations,
        }

    def _generate_recommendations(
        self, stats: Dict[str, Any], backend: str
    ) -> list[Dict[str, str]]:
        """Generate actionable recommendations."""
        recs = []
        ram_pct = stats["ram_percent"]
        vram_pct = stats["gpu"]["vram_percent"]
        ram_avail = stats["ram_available_gb"]
        vram_total = stats["gpu"]["vram_total_mb"]

        # RAM recommendations
        if ram_pct > 85:
            recs.append(
                {
                    "level": "critical",
                    "component": "RAM",
                    "message": f"RAM at {ram_pct}% — reduce context window or close other apps",
                    "action": f"Set context to {self._recommended_context(ram_avail // 2)} tokens",
                }
            )
        elif ram_pct > 70:
            recs.append(
                {
                    "level": "warning",
                    "component": "RAM",
                    "message": f"RAM at {ram_pct}% — approaching limit",
                    "action": "Consider reducing context window or enabling swap",
                }
            )
        else:
            recs.append(
                {
                    "level": "ok",
                    "component": "RAM",
                    "message": f"RAM at {ram_pct}% — healthy",
                    "action": f"Can support up to {self._recommended_context(ram_avail)} token context",
                }
            )

        # VRAM recommendations
        if vram_pct > 90:
            recs.append(
                {
                    "level": "critical",
                    "component": "VRAM",
                    "message": f"VRAM at {vram_pct}% — model may OOM",
                    "action": f"Reduce GPU layers to {self._recommended_gpu_layers(int(vram_total * 0.7))}",
                }
            )
        elif vram_pct > 75:
            recs.append(
                {
                    "level": "warning",
                    "component": "VRAM",
                    "message": f"VRAM at {vram_pct}% — limited headroom",
                    "action": "Use q4_0 quantization or reduce GPU layers",
                }
            )
        else:
            recs.append(
                {
                    "level": "ok",
                    "component": "VRAM",
                    "message": f"VRAM at {vram_pct}% — healthy",
                    "action": f"Can offload up to {self._recommended_gpu_layers(int(vram_total))} layers",
                }
            )

        # GPU utilization
        gpu_util = stats["gpu"]["gpu_util_percent"]
        if gpu_util < 20:
            recs.append(
                {
                    "level": "info",
                    "component": "GPU",
                    "message": f"GPU utilization at {gpu_util}% — mostly running on CPU",
                    "action": "Increase GPU layers for better performance",
                }
            )
        elif gpu_util > 95:
            recs.append(
                {
                    "level": "info",
                    "component": "GPU",
                    "message": f"GPU at {gpu_util}% — fully utilized",
                    "action": "Good — GPU is the bottleneck (optimal for inference)",
                }
            )

        # Backend-specific
        if backend == "unknown":
            recs.append(
                {
                    "level": "warning",
                    "component": "Backend",
                    "message": "No inference backend detected",
                    "action": "Start Ollama, vLLM, llama.cpp, or LM Studio",
                }
            )

        return recs

    def print_report(self):
        """Print a human-readable optimization report."""
        result = self.optimize()

        print("=" * 60)
        print("  RAM-to-VRAM Memory Optimizer")
        print("=" * 60)
        print(f"  Detected Backend: {result['detected_backend'].upper()}")
        print(f"  Timestamp: {result['timestamp']}")
        print("-" * 60)

        sys_stats = result["system"]
        gpu = sys_stats["gpu"]

        print(
            f"  RAM:    {sys_stats['ram_used_gb']}/{sys_stats['ram_total_gb']} GB ({sys_stats['ram_percent']}%)"
        )
        print(
            f"  VRAM:   {gpu['vram_used_mb']}/{gpu['vram_total_mb']} MB ({gpu['vram_percent']}%)"
        )
        print(
            f"  GPU:    {gpu['gpu_util_percent']}% util | {gpu['gpu_temp_c']}°C | {gpu['gpu_power_w']}W"
        )
        print(
            f"  Swap:   {sys_stats['swap_used_gb']}/{sys_stats['swap_total_gb']} GB ({sys_stats['swap_percent']}%)"
        )
        print("-" * 60)

        print("  Recommendations:")
        for rec in result["recommendations"]:
            icon = {"ok": "✓", "warning": "⚠", "critical": "✗", "info": "ℹ"}.get(
                rec["level"], "•"
            )
            print(f"  [{icon}] {rec['component']}: {rec['message']}")
            print(f"      → {rec['action']}")

        print("-" * 60)

        # Backend-specific config
        config = result["recommended_config"]
        if config:
            print(f"  Recommended Config ({result['detected_backend']}):")
            for key, value in config.items():
                if isinstance(value, dict):
                    print(f"    {key}:")
                    for k, v in value.items():
                        print(f"      {k} = {v}")
                else:
                    print(f"    {key}: {value}")

        print("=" * 60)


if __name__ == "__main__":
    vram_override = None
    if "--vram" in sys.argv:
        idx = sys.argv.index("--vram")
        if idx + 1 < len(sys.argv):
            vram_override = int(sys.argv[idx + 1])

    optimizer = MemoryOptimizer(vram_override_mb=vram_override)

    if "--json" in sys.argv:
        print(json.dumps(optimizer.optimize(), indent=2))
    else:
        optimizer.print_report()
