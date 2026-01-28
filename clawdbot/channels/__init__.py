"""
Channel plugins for ClawdBot
"""
from .base import (
    ChannelPlugin,
    ChannelCapabilities,
    InboundMessage,
    OutboundMessage,
    MessageHandler
)
from .registry import (
    ChannelRegistry,
    get_channel_registry,
    register_channel,
    get_channel
)
from .connection import (
    ConnectionManager,
    ConnectionState,
    ConnectionMetrics,
    ReconnectConfig,
    HealthChecker
)

# Import channel implementations
from .telegram import TelegramChannel
from .discord import DiscordChannel
from .slack import SlackChannel
from .webchat import WebChatChannel

# Enhanced versions
from .enhanced_telegram import EnhancedTelegramChannel
from .enhanced_discord import EnhancedDiscordChannel

__all__ = [
    # Base classes
    "ChannelPlugin",
    "ChannelCapabilities",
    "InboundMessage",
    "OutboundMessage",
    "MessageHandler",
    # Registry
    "ChannelRegistry",
    "get_channel_registry",
    "register_channel",
    "get_channel",
    # Connection management
    "ConnectionManager",
    "ConnectionState",
    "ConnectionMetrics",
    "ReconnectConfig",
    "HealthChecker",
    # Channels
    "TelegramChannel",
    "DiscordChannel",
    "SlackChannel",
    "WebChatChannel",
    "EnhancedTelegramChannel",
    "EnhancedDiscordChannel",
]
