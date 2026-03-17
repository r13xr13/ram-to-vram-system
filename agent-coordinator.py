#!/usr/bin/env python3
"""
Agent Coordinator - Controls agent execution flow
Processes one agent at a time with cooldown periods
"""

import json
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class AgentCoordinator:
    def __init__(self, base_dir: str = "/home/c0smic/agent-setup/coordination"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # Agent queue file
        self.queue_file = self.base_dir / "agent_queue.json"

        # Configuration
        self.cooldown_seconds = 5  # Small cooldown between agents
        self.max_agents_per_cycle = 1  # Process one agent at a time

        # Load or create queue
        self.queue = self.load_queue()

    def load_queue(self) -> Dict[str, Any]:
        """Load agent queue from file"""
        if self.queue_file.exists():
            try:
                with open(self.queue_file, "r") as f:
                    return json.load(f)
            except:
                pass

        # Default queue structure
        return {
            "agents": [
                {
                    "name": "jack",
                    "last_run": None,
                    "priority": 1,
                    "cooldown_until": None,
                },
                {
                    "name": "sam",
                    "last_run": None,
                    "priority": 1,
                    "cooldown_until": None,
                },
                {
                    "name": "alice",
                    "last_run": None,
                    "priority": 1,
                    "cooldown_until": None,
                },
                {
                    "name": "tom",
                    "last_run": None,
                    "priority": 1,
                    "cooldown_until": None,
                },
                {
                    "name": "alex",
                    "last_run": None,
                    "priority": 1,
                    "cooldown_until": None,
                },
                {
                    "name": "riley",
                    "last_run": None,
                    "priority": 1,
                    "cooldown_until": None,
                },
                {
                    "name": "jordan",
                    "last_run": None,
                    "priority": 1,
                    "cooldown_until": None,
                },
                {
                    "name": "morgan",
                    "last_run": None,
                    "priority": 1,
                    "cooldown_until": None,
                },
                {
                    "name": "casey",
                    "last_run": None,
                    "priority": 1,
                    "cooldown_until": None,
                },
            ],
            "current_agent": None,
            "last_cycle": None,
        }

    def save_queue(self):
        """Save agent queue to file"""
        try:
            with open(self.queue_file, "w") as f:
                json.dump(self.queue, f, indent=2)
        except Exception as e:
            print(f"Error saving queue: {e}")

    def get_next_agent(self) -> str:
        """Get the next agent to process"""
        now = time.time()

        # Find agent that's not on cooldown and hasn't run recently
        available_agents = []
        for agent in self.queue["agents"]:
            cooldown_until = agent.get("cooldown_until")
            if cooldown_until and cooldown_until > now:
                continue  # Still on cooldown

            available_agents.append(agent)

        if not available_agents:
            # All agents on cooldown, reset cooldowns
            for agent in self.queue["agents"]:
                agent["cooldown_until"] = None
            available_agents = self.queue["agents"]

        # Sort by priority (highest first) and then by last run (oldest first)
        available_agents.sort(
            key=lambda x: (-x.get("priority", 1), x.get("last_run", 0))
        )

        if available_agents:
            next_agent = available_agents[0]
            return next_agent["name"]

        return "jack"  # Default fallback

    def mark_agent_run(self, agent_name: str):
        """Mark agent as having been run"""
        now = time.time()

        for agent in self.queue["agents"]:
            if agent["name"] == agent_name:
                agent["last_run"] = now
                agent["cooldown_until"] = now + self.cooldown_seconds
                break

        self.queue["current_agent"] = agent_name
        self.queue["last_cycle"] = now
        self.save_queue()

    def get_agent_status(self, agent_name: str) -> Dict[str, Any]:
        """Get status of a specific agent"""
        for agent in self.queue["agents"]:
            if agent["name"] == agent_name:
                now = time.time()
                cooldown_until = agent.get("cooldown_until", 0)
                status = {
                    "name": agent_name,
                    "last_run": agent.get("last_run"),
                    "priority": agent.get("priority", 1),
                    "on_cooldown": cooldown_until > now,
                    "cooldown_remaining": max(0, cooldown_until - now),
                    "can_run": cooldown_until <= now,
                }
                return status

        return {"name": agent_name, "error": "Agent not found"}

    def set_priority(self, agent_name: str, priority: int):
        """Set agent priority (higher = runs more often)"""
        for agent in self.queue["agents"]:
            if agent["name"] == agent_name:
                agent["priority"] = priority
                break
        self.save_queue()

    def reset_cooldowns(self):
        """Reset all cooldowns"""
        for agent in self.queue["agents"]:
            agent["cooldown_until"] = None
        self.save_queue()


# Global coordinator instance
coordinator = AgentCoordinator()


if __name__ == "__main__":
    # Test the coordinator
    coord = AgentCoordinator()

    print("=== Agent Coordinator Test ===")

    # Get next agent
    next_agent = coord.get_next_agent()
    print(f"Next agent: {next_agent}")

    # Mark agent as run
    coord.mark_agent_run(next_agent)
    print(f"Marked {next_agent} as run")

    # Check status
    status = coord.get_agent_status(next_agent)
    print(f"Agent status: {status}")

    # Get next agent (should be different due to cooldown)
    next_agent2 = coord.get_next_agent()
    print(f"Next agent (after cooldown): {next_agent2}")

    # Wait for cooldown
    print("Waiting for cooldown...")
    time.sleep(6)

    # Get next agent again
    next_agent3 = coord.get_next_agent()
    print(f"Next agent (after wait): {next_agent3}")
