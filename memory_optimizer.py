#!/usr/bin/python3
"""
Memory Optimizer for Ollama and Agents
Dynamically manages RAM and VRAM usage
"""

import psutil
import subprocess
import json
import time
from datetime import datetime

class MemoryOptimizer:
    def __init__(self):
        self.total_ram = psutil.virtual_memory().total / (1024**3)  # GB
        self.total_vram = 4096  # GTX 1650 has 4GB VRAM
        
    def get_system_stats(self):
        """Get current system memory stats"""
        ram = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            "ram_total_gb": round(ram.total / (1024**3), 2),
            "ram_used_gb": round(ram.used / (1024**3), 2),
            "ram_available_gb": round(ram.available / (1024**3), 2),
            "ram_percent": ram.percent,
            "swap_total_gb": round(swap.total / (1024**3), 2),
            "swap_used_gb": round(swap.used / (1024**3), 2),
            "swap_percent": swap.percent
        }
    
    def get_gpu_stats(self):
        """Get GPU memory usage"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu", "--format=csv,noheader,nounits"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                used, total, util = map(int, result.stdout.strip().split(", "))
                return {
                    "vram_used_mb": used,
                    "vram_total_mb": total,
                    "vram_percent": round(used / total * 100, 1),
                    "gpu_util_percent": util
                }
        except:
            pass
        return {"vram_used_mb": 0, "vram_total_mb": self.total_vram, "vram_percent": 0, "gpu_util_percent": 0}
    
    def get_ollama_memory(self):
        """Get Ollama process memory usage"""
        try:
            result = subprocess.run(
                ["ps", "aux", "|", "grep", "ollama", "|", "grep", "-v", "grep", "|", "awk", "'{print $6}'"],
                capture_output=True, text=True, shell=True
            )
            if result.returncode == 0:
                memory_kb = sum(int(x) for x in result.stdout.strip().split() if x.isdigit())
                return round(memory_kb / 1024, 2)  # Convert to MB
        except:
            pass
        return 0
    
    def optimize_memory(self):
        """Optimize memory usage based on current load"""
        stats = self.get_system_stats()
        gpu_stats = self.get_gpu_stats()
        
        print("=== Memory Optimization Report ===")
        print(f"RAM: {stats['ram_used_gb']}/{stats['ram_total_gb']} GB ({stats['ram_percent']}%)")
        print(f"VRAM: {gpu_stats['vram_used_mb']}/{gpu_stats['vram_total_mb']} MB ({gpu_stats['vram_percent']}%)")
        print(f"GPU Utilization: {gpu_stats['gpu_util_percent']}%")
        
        # Adjust based on available memory
        if stats['ram_available_gb'] > 10:
            print("✓ Plenty of RAM available - can increase context window")
            return {"action": "increase_context", "reason": "high_ram_available"}
        elif stats['ram_percent'] > 80:
            print("⚠ High RAM usage - consider reducing context window")
            return {"action": "reduce_context", "reason": "high_ram_usage"}
        else:
            print("✓ Memory usage optimal")
            return {"action": "maintain", "reason": "optimal"}
    
    def create_memory_report(self):
        """Create a comprehensive memory report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "system": self.get_system_stats(),
            "gpu": self.get_gpu_stats(),
            "ollama_mb": self.get_ollama_memory()
        }
        
        # Save report
        with open("/tmp/memory_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        return report


if __name__ == "__main__":
    optimizer = MemoryOptimizer()
    
    # Run optimization
    optimizer.optimize_memory()
    
    # Create report
    report = optimizer.create_memory_report()
    print("\n=== Full Report ===")
    print(json.dumps(report, indent=2))
