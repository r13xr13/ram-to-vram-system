#!/usr/bin/python3
"""
Conversation Coordinator for r13 Agents
Enables agents to have conversations with each other and engage with users
"""

import json
import time
import random
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import threading


class ConversationCoordinator:
    def __init__(self, base_dir: str = "/home/c0smic/agent-setup/conversations"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # Agent configuration
        self.agents = [
            "jack",
            "sam",
            "alice",
            "tom",
            "alex",
            "riley",
            "jordan",
            "morgan",
            "casey",
        ]

        # Conversation channels
        self.channels = {
            "general": {"agents": ["jack", "sam", "alice", "tom"], "cooldown": 10},
            "tech": {"agents": ["alex", "riley", "jordan"], "cooldown": 8},
            "random": {"agents": ["morgan", "casey", "jack"], "cooldown": 15},
        }

        # Active conversations
        self.active_conversations = {}

        # Load or create conversation state
        self.state_file = self.base_dir / "conversation_state.json"
        self.load_state()

    def load_state(self):
        """Load conversation state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    self.active_conversations = json.load(f)
            except:
                self.active_conversations = {}

    def save_state(self):
        """Save conversation state to file"""
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.active_conversations, f, indent=2)
        except Exception as e:
            print(f"Error saving state: {e}")

    def start_conversation(
        self, channel: str, initiator: str, topic: Optional[str] = None
    ):
        """Start a new conversation in a channel"""
        conv_id = f"{channel}_{int(time.time())}"

        if channel not in self.channels:
            channel = "general"

        conversation = {
            "id": conv_id,
            "channel": channel,
            "initiator": initiator,
            "participants": [initiator],
            "topic": topic if topic else "general",
            "messages": [],
            "started_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "status": "active",
        }

        self.active_conversations[conv_id] = conversation
        self.save_state()

        return conv_id

    def add_message(
        self, conv_id: str, agent: str, message: str, message_type: str = "chat"
    ):
        """Add a message to a conversation"""
        if conv_id not in self.active_conversations:
            return False

        conv = self.active_conversations[conv_id]

        message_obj = {
            "id": str(int(time.time() * 1000000)),
            "agent": agent,
            "message": message,
            "type": message_type,
            "timestamp": datetime.now().isoformat(),
        }

        conv["messages"].append(message_obj)
        conv["last_activity"] = datetime.now().isoformat()

        # Add agent to participants if not already there
        if agent not in conv["participants"]:
            conv["participants"].append(agent)

        self.save_state()
        return True

    def get_next_speaker(self, conv_id: str) -> Optional[str]:
        """Determine which agent should speak next"""
        if conv_id not in self.active_conversations:
            return None

        conv = self.active_conversations[conv_id]
        channel = conv["channel"]

        # Get available agents for this channel
        available_agents = self.channels[channel]["agents"]

        # Remove agents that just spoke
        recent_speakers = [msg["agent"] for msg in conv["messages"][-3:]]
        available_agents = [a for a in available_agents if a not in recent_speakers]

        if not available_agents:
            available_agents = self.channels[channel]["agents"]

        # Weight by how recently they spoke (less recent = higher chance)
        weights = []
        for agent in available_agents:
            last_spoke = None
            for msg in reversed(conv["messages"]):
                if msg["agent"] == agent:
                    last_spoke = msg["timestamp"]
                    break

            if last_spoke:
                # Less recent = higher weight
                time_diff = (
                    datetime.now() - datetime.fromisoformat(last_spoke)
                ).total_seconds()
                weight = max(1, time_diff / 60)  # Weight increases with time
            else:
                weight = 5  # Default weight for agents who haven't spoken

            weights.append(weight)

        # Select agent based on weights
        total_weight = sum(weights)
        r = random.uniform(0, total_weight)
        current = 0
        for i, agent in enumerate(available_agents):
            current += weights[i]
            if r <= current:
                return agent

        return available_agents[0] if available_agents else None

    def generate_response(self, agent: str, context: List[Dict[str, str]]) -> str:
        """Generate a response for an agent based on conversation context"""
        # Simple response generation based on agent personality
        personalities = {
            "jack": {"style": "analytical", "topics": ["tech", "system", "analysis"]},
            "sam": {"style": "creative", "topics": ["ideas", "projects", "design"]},
            "alice": {
                "style": "supportive",
                "topics": ["help", "assistance", "feedback"],
            },
            "tom": {"style": "practical", "topics": ["tasks", "actions", "results"]},
            "alex": {"style": "technical", "topics": ["code", "debug", "implement"]},
            "riley": {"style": "research", "topics": ["data", "research", "analysis"]},
            "jordan": {
                "style": "strategic",
                "topics": ["planning", "strategy", "goals"],
            },
            "morgan": {"style": "creative", "topics": ["ideas", "innovation", "art"]},
            "casey": {
                "style": "detailed",
                "topics": ["documentation", "details", "specs"],
            },
        }

        personality = personalities.get(
            agent, {"style": "neutral", "topics": ["general"]}
        )

        # Generate response based on context
        if not context:
            return f"Hey everyone! {agent} here. What's up?"

        last_message = context[-1]["message"] if context else ""
        last_agent = context[-1]["agent"] if context else ""

        # Response templates based on personality
        responses = {
            "analytical": [
                f"I've been analyzing this, and {last_message[:50]}...",
                f"From a systems perspective, {last_message[:50]}...",
                f"Let me break this down: {last_message[:50]}...",
            ],
            "creative": [
                f"Interesting thought! What if we {last_message[:50]}...",
                f"I have an idea: {last_message[:50]}...",
                f"Creative approach: {last_message[:50]}...",
            ],
            "supportive": [
                f"Great point {last_agent}! {last_message[:50]}...",
                f"I support that idea. {last_message[:50]}...",
                f"Thanks for sharing! {last_message[:50]}...",
            ],
            "practical": [
                f"Let's get this done. {last_message[:50]}...",
                f"Action item: {last_message[:50]}...",
                f"Practical approach: {last_message[:50]}...",
            ],
            "technical": [
                f"Technical note: {last_message[:50]}...",
                f"From a technical standpoint, {last_message[:50]}...",
                f"Implementation detail: {last_message[:50]}...",
            ],
        }

        style_responses = responses.get(personality["style"], responses["supportive"])
        return random.choice(style_responses)

    def process_user_message(self, user_message: str, channel: str = "general") -> str:
        """Process a user message and trigger agent responses"""
        # Start a new conversation or add to existing
        conv_id = self.start_conversation(channel, "user", "user_interaction")

        # Add user message
        self.add_message(conv_id, "user", user_message, "user")

        # Get next speaker
        next_speaker = self.get_next_speaker(conv_id)

        if next_speaker:
            # Generate response
            context = [
                {"agent": msg["agent"], "message": msg["message"]}
                for msg in self.active_conversations[conv_id]["messages"][-3:]
            ]

            response = self.generate_response(next_speaker, context)

            # Add agent response
            self.add_message(conv_id, next_speaker, response, "agent")

            return f"{next_speaker}: {response}"

        return "No agent available to respond"

    def start_agent_chat(self, channel: str = "general", topic: Optional[str] = None):
        """Start an automated agent conversation"""
        conv_id = self.start_conversation(channel, "system", topic)

        # Get initial participants
        participants = self.channels[channel]["agents"][:3]  # First 3 agents

        # Have them introduce themselves
        for agent in participants:
            intro = f"Hey everyone! {agent} here. Ready to chat about {topic or 'anything'}!"
            self.add_message(conv_id, agent, intro, "agent")

        return conv_id

    def get_conversation_history(
        self, conv_id: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get conversation history"""
        if conv_id not in self.active_conversations:
            return []

        messages = self.active_conversations[conv_id]["messages"]
        return messages[-limit:] if len(messages) > limit else messages

    def auto_conversation_cycle(self, channel: str = "general"):
        """Run an automated conversation cycle"""
        conv_id = self.start_agent_chat(channel, "automated_chat")

        for i in range(5):  # 5 exchange cycles
            time.sleep(2)  # Small delay between exchanges

            next_speaker = self.get_next_speaker(conv_id)
            if next_speaker:
                context = [
                    {"agent": msg["agent"], "message": msg["message"]}
                    for msg in self.active_conversations[conv_id]["messages"][-3:]
                ]

                response = self.generate_response(next_speaker, context)
                self.add_message(conv_id, next_speaker, response, "agent")

        return conv_id


# Global coordinator instance
conversation_coordinator = ConversationCoordinator()


if __name__ == "__main__":
    import sys

    coord = ConversationCoordinator()

    if len(sys.argv) < 2:
        # Test mode
        print("=== Testing Conversation Coordinator ===")

        # Start a test conversation
        conv_id = coord.start_conversation("general", "user", "testing")
        print(f"Started conversation: {conv_id}")

        # Add some messages
        coord.add_message(conv_id, "jack", "Hey everyone! Let's test this system.")
        coord.add_message(conv_id, "sam", "Great idea! I'm ready to chat.")

        # Get next speaker
        next_speaker = coord.get_next_speaker(conv_id)
        print(f"Next speaker: {next_speaker}")

        # Process user message
        response = coord.process_user_message("Hello agents, how are you all doing?")
        print(f"Agent response: {response}")

        # Show conversation
        print("\nConversation history:")
        for msg in coord.get_conversation_history(conv_id):
            print(f"  [{msg['agent']}] {msg['message']}")
    else:
        # MCP server mode
        command = sys.argv[1]

        if command == "start":
            # start <channel> <initiator> [topic]
            channel = sys.argv[2] if len(sys.argv) > 2 else "general"
            initiator = sys.argv[3] if len(sys.argv) > 3 else "system"
            topic_arg = sys.argv[4] if len(sys.argv) > 4 else ""

            conv_id = coord.start_conversation(
                channel, initiator, topic_arg if topic_arg else None
            )
            print(f"Started conversation: {conv_id}")

        elif command == "add":
            # add <conv_id> <agent> <message> [type]
            conv_id = sys.argv[2]
            agent = sys.argv[3]
            message = sys.argv[4]
            msg_type = sys.argv[5] if len(sys.argv) > 5 else "chat"

            success = coord.add_message(conv_id, agent, message, msg_type)
            print(f"Message added: {success}")

        elif command == "user":
            # user <message> [channel]
            message = sys.argv[2]
            channel = sys.argv[3] if len(sys.argv) > 3 else "general"

            response = coord.process_user_message(message, channel)
            print(response)

        elif command == "auto":
            # auto <channel> [topic]
            channel = sys.argv[2] if len(sys.argv) > 2 else "general"
            topic = sys.argv[3] if len(sys.argv) > 3 else None

            conv_id = coord.auto_conversation_cycle(channel)
            print(f"Auto conversation started: {conv_id}")

        else:
            print(f"Unknown command: {command}")
