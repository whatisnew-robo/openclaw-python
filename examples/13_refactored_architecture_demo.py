"""
Example 13: Refactored Architecture Demo

This example demonstrates all the new refactoring improvements:
1. Unified Event System
2. RuntimeEnv Abstraction Layer
3. Standardized Channel Lifecycle

Features:
- Type-safe events with EventType
- RuntimeEnv for configuration isolation
- Standardized channel hooks
- Complete architecture integration

Usage:
    uv run python examples/13_refactored_architecture_demo.py
"""

import asyncio
import logging
from pathlib import Path

from openclaw.events import Event, EventType, get_event_bus
from openclaw.runtime_env import RuntimeEnv, RuntimeEnvManager
from openclaw.channels.base import ChannelPlugin, InboundMessage
from openclaw.gateway import GatewayServer, ChannelManager
from openclaw.config import ClawdbotConfig
from openclaw.monitoring import setup_logging

logger = logging.getLogger(__name__)


# ============================================================================
# Demo: Custom Channel with Standardized Lifecycle
# ============================================================================

class DemoChannel(ChannelPlugin):
    """
    Demo channel showing standardized lifecycle hooks
    """
    
    def __init__(self):
        super().__init__()
        self.id = "demo"
        self.label = "Demo Channel"
        self._connected = False
    
    # Lifecycle hooks
    
    async def on_init(self):
        """Initialize resources"""
        logger.info(f"[{self.id}] 🔧 on_init() called - initializing resources")
    
    async def on_start(self, config: dict):
        """Connect to platform"""
        logger.info(f"[{self.id}] 🚀 on_start() called - connecting to platform")
        self._connected = True
    
    async def on_ready(self):
        """Post-connection setup"""
        logger.info(f"[{self.id}] ✅ on_ready() called - channel is ready!")
    
    async def on_stop(self):
        """Disconnect from platform"""
        logger.info(f"[{self.id}] 🛑 on_stop() called - disconnecting")
        self._connected = False
    
    async def on_destroy(self):
        """Cleanup resources"""
        logger.info(f"[{self.id}] 🧹 on_destroy() called - cleaning up")
    
    # Message hooks
    
    async def on_message_received(self, message: InboundMessage):
        """Filter/modify before processing"""
        logger.info(f"[{self.id}] 📥 on_message_received() - can filter here")
        return message  # Return None to skip
    
    async def on_message_sent(self, message, message_id):
        """Post-send actions"""
        logger.info(f"[{self.id}] 📤 on_message_sent() - message sent!")
    
    # Error hooks
    
    async def on_error(self, error):
        """Custom error handling"""
        logger.error(f"[{self.id}] ❌ on_error() - {error}")
    
    async def on_connection_lost(self):
        """Handle connection loss"""
        logger.warning(f"[{self.id}] 📡 on_connection_lost() - reconnecting...")
    
    # Health check
    
    async def check_health(self):
        """Custom health check"""
        if not self._connected:
            return False, "Not connected"
        return True, "All systems operational"
    
    # Required methods
    
    async def send_text(self, target: str, text: str, reply_to: str | None = None):
        """Send text message"""
        logger.info(f"[{self.id}] Sending: {text}")
        return "msg-123"


# ============================================================================
# Demo 1: Unified Event System
# ============================================================================

async def demo_unified_events():
    """Demonstrate unified event system"""
    print("=" * 60)
    print("1️⃣  Unified Event System")
    print("=" * 60)
    print()
    
    bus = get_event_bus()
    
    # Subscribe to specific events
    events_received = []
    
    async def on_agent_event(event: Event):
        events_received.append(event.type.value)
        print(f"📡 Received: {event.type.value} from {event.source}")
    
    bus.subscribe(EventType.AGENT_TEXT, on_agent_event)
    bus.subscribe(EventType.AGENT_THINKING, on_agent_event)
    
    # Publish events
    await bus.publish(Event(
        type=EventType.AGENT_TEXT,
        source="agent-1",
        session_id="demo-session",
        data={"text": "Hello from unified events!"}
    ))
    
    await bus.publish(Event(
        type=EventType.AGENT_THINKING,
        source="agent-1",
        data={"thought": "Processing..."}
    ))
    
    print(f"\n✅ Received {len(events_received)} events: {events_received}\n")


# ============================================================================
# Demo 2: RuntimeEnv Abstraction
# ============================================================================

async def demo_runtime_env():
    """Demonstrate RuntimeEnv abstraction"""
    print("=" * 60)
    print("2️⃣  RuntimeEnv Abstraction Layer")
    print("=" * 60)
    print()
    
    # Create RuntimeEnv Manager
    manager = RuntimeEnvManager()
    
    # Create multiple environments with different configs
    prod_env = manager.create_env(
        env_id="production",
        model="anthropic/claude-sonnet-4-20250514",
        config={"temperature": 0.5, "max_tokens": 4000},
        description="Production environment"
    )
    
    dev_env = manager.create_env(
        env_id="development",
        model="anthropic/claude-haiku-3-20250514",
        config={"temperature": 0.8, "max_tokens": 2000"},
        description="Development environment"
    )
    
    # Set default
    manager.set_default("production")
    
    print(f"✅ Created environments:")
    for env_id in manager.list_envs():
        env = manager.get_env(env_id)
        print(f"   - {env_id}: {env.model}")
    
    print(f"\n🎯 Default environment: {manager.get_default_env().env_id}")
    print(f"📊 Manager stats: {manager.to_dict()['total_envs']} environments\n")
    
    return manager


# ============================================================================
# Demo 3: Standardized Channel Lifecycle
# ============================================================================

async def demo_channel_lifecycle():
    """Demonstrate standardized channel lifecycle"""
    print("=" * 60)
    print("3️⃣  Standardized Channel Lifecycle")
    print("=" * 60)
    print()
    
    channel = DemoChannel()
    
    print("Starting channel (watch the hooks):")
    print()
    
    # Start will call: on_init → on_start → on_ready
    await channel.start({"demo": "config"})
    
    print()
    print("Checking health:")
    is_healthy, reason = await channel.check_health()
    print(f"   Health: {is_healthy} - {reason}")
    
    print()
    print("Stopping channel (watch the hooks):")
    print()
    
    # Stop will call: on_stop → on_destroy
    await channel.stop()
    
    print()


# ============================================================================
# Demo 4: Integration - All Components Together
# ============================================================================

async def demo_integration(runtime_manager: RuntimeEnvManager):
    """Demonstrate all components working together"""
    print("=" * 60)
    print("4️⃣  Complete Integration")
    print("=" * 60)
    print()
    
    # Create config
    config = ClawdbotConfig(
        gateway={"port": 8765, "bind": "loopback"},
        agent={"model": "anthropic/claude-sonnet-4-20250514"}
    )
    
    # Get default RuntimeEnv
    runtime_env = runtime_manager.get_default_env()
    
    # Create Gateway with RuntimeEnv
    gateway = GatewayServer(
        config=config,
        agent_runtime=runtime_env.agent_runtime,
        session_manager=runtime_env.session_manager,
    )
    
    print(f"✅ Gateway created with RuntimeEnv: {runtime_env.env_id}")
    
    # Register demo channel
    gateway.channel_manager.register(
        channel_id="demo",
        channel_class=DemoChannel,
        config={"demo": "config"}
    )
    
    print(f"✅ Registered demo channel")
    
    # Show channel status
    status = gateway.channel_manager.get_status("demo")
    if status:
        print(f"📊 Channel status: {status['state']}")
    
    print()


# ============================================================================
# Demo 5: Event Flow
# ============================================================================

async def demo_event_flow():
    """Demonstrate event flow through the system"""
    print("=" * 60)
    print("5️⃣  Event Flow Through System")
    print("=" * 60)
    print()
    
    bus = get_event_bus()
    
    # Track event flow
    flow = []
    
    async def track_event(event: Event):
        flow.append(f"{event.source} → {event.type.value}")
    
    # Subscribe to all events
    bus.subscribe(None, track_event)
    
    # Simulate event flow
    await bus.publish(Event(
        type=EventType.CHANNEL_MESSAGE_RECEIVED,
        source="telegram",
        channel_id="telegram",
        data={"message": "Hello"}
    ))
    
    await bus.publish(Event(
        type=EventType.AGENT_STARTED,
        source="agent-runtime",
        session_id="session-1",
        data={}
    ))
    
    await bus.publish(Event(
        type=EventType.AGENT_TEXT,
        source="agent-runtime",
        data={"text": "Response"}
    ))
    
    await bus.publish(Event(
        type=EventType.CHANNEL_MESSAGE_SENT,
        source="telegram",
        channel_id="telegram",
        data={"message_id": "123"}
    ))
    
    print("Event Flow:")
    for step in flow:
        print(f"   {step}")
    
    print()


# ============================================================================
# Main Demo
# ============================================================================

async def main():
    """Run all demos"""
    setup_logging(level="INFO", format_type="colored")
    
    # Reset event bus for clean demo
    from openclaw.events import reset_event_bus
    reset_event_bus()
    
    print()
    print("🦞 OpenClaw - Refactored Architecture Demo")
    print()
    print("This demo showcases:")
    print("✨ Unified Event System (EventType, EventBus)")
    print("✨ RuntimeEnv Abstraction (configuration isolation)")
    print("✨ Standardized Channel Lifecycle (hooks pattern)")
    print()
    
    # Run demos
    await demo_unified_events()
    runtime_manager = await demo_runtime_env()
    await demo_channel_lifecycle()
    await demo_integration(runtime_manager)
    await demo_event_flow()
    
    print("=" * 60)
    print("✅ All demos completed!")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("1. Update existing channels to use new lifecycle hooks")
    print("2. Migrate to unified Event system everywhere")
    print("3. Use RuntimeEnv for configuration isolation")
    print("4. Write tests for refactored components")
    print()


if __name__ == "__main__":
    asyncio.run(main())
