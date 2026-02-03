"""
Gateway WebSocket server implementation

The Gateway provides:
1. ChannelManager - Manages channel plugins (Telegram, Discord, etc.)
2. WebSocket API - Serves external clients (UI, CLI, mobile)
3. Event Broadcasting - Broadcasts Agent events to all clients

Architecture:
    Gateway Server
        ├── ChannelManager (manages channel plugins)
        ├── WebSocket Server (for external clients)
        └── Event Broadcasting (Observer Pattern)
"""

from .server import GatewayServer, GatewayConnection
from .channel_manager import (
    ChannelManager,
    ChannelState,
    ChannelRuntimeEnv,
    ChannelEventListener,
    discover_channel_plugins,
    load_channel_plugins,
)
from .protocol import (
    RequestFrame,
    ResponseFrame,
    EventFrame,
    ErrorShape,
)

__all__ = [
    # Server
    "GatewayServer",
    "GatewayConnection",
    # Channel Manager
    "ChannelManager",
    "ChannelState",
    "ChannelRuntimeEnv",
    "ChannelEventListener",
    "discover_channel_plugins",
    "load_channel_plugins",
    # Protocol
    "RequestFrame",
    "ResponseFrame",
    "EventFrame",
    "ErrorShape",
]
