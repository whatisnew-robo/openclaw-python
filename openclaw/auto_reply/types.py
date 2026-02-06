"""Type definitions for Auto-Reply system.

Aligned with TypeScript src/auto-reply/types.ts
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable, Optional
from openclaw.agents.providers.base import ImageContent


@dataclass
class BlockReplyContext:
    """Context for block reply with timeout and abort signal."""
    
    abort_signal: Optional[Any] = None  # AbortSignal equivalent
    timeout_ms: Optional[int] = None


@dataclass
class ModelSelectedContext:
    """Context passed to onModelSelected callback with actual model used."""
    
    provider: str
    model: str
    think_level: Optional[str] = None


@dataclass
class GetReplyOptions:
    """Options for getting a reply from the agent.
    
    Aligned with TypeScript GetReplyOptions.
    """
    
    # Override run id for agent events (defaults to random UUID)
    run_id: Optional[str] = None
    
    # Abort signal for the underlying agent run
    abort_signal: Optional[Any] = None
    
    # Optional inbound images (used for webchat attachments)
    images: Optional[list[ImageContent]] = None
    
    # Notifies when an agent run actually starts
    on_agent_run_start: Optional[Callable[[str], None]] = None
    
    # Callback when reply starts
    on_reply_start: Optional[Callable[[], Awaitable[None] | None]] = None
    
    # Callback for typing controller
    on_typing_controller: Optional[Callable[[Any], None]] = None
    
    # Is this a heartbeat request
    is_heartbeat: bool = False
    
    # Callback for partial reply (streaming)
    on_partial_reply: Optional[Callable[[ReplyPayload], Awaitable[None] | None]] = None
    
    # Callback for reasoning stream
    on_reasoning_stream: Optional[Callable[[ReplyPayload], Awaitable[None] | None]] = None
    
    # Callback for block reply
    on_block_reply: Optional[Callable[[ReplyPayload, Optional[BlockReplyContext]], Awaitable[None] | None]] = None
    
    # Callback for tool result
    on_tool_result: Optional[Callable[[ReplyPayload], Awaitable[None] | None]] = None
    
    # Called when the actual model is selected (including after fallback)
    on_model_selected: Optional[Callable[[ModelSelectedContext], None]] = None
    
    # Disable block streaming
    disable_block_streaming: bool = False
    
    # Timeout for block reply delivery (ms)
    block_reply_timeout_ms: Optional[int] = None
    
    # If provided, only load these skills for this session (empty = no skills)
    skill_filter: Optional[list[str]] = None
    
    # Mutable ref to track if a reply was sent (for Slack "first" threading mode)
    has_replied_ref: Optional[dict[str, bool]] = None


@dataclass
class ReplyPayload:
    """Reply payload containing text, media, and metadata.
    
    Aligned with TypeScript ReplyPayload.
    """
    
    # Reply text content
    text: Optional[str] = None
    
    # Single media URL (deprecated, use mediaUrls)
    media_url: Optional[str] = None
    
    # Multiple media URLs
    media_urls: Optional[list[str]] = None
    
    # Reply to specific message ID
    reply_to_id: Optional[str] = None
    
    # Reply with tag/mention
    reply_to_tag: bool = False
    
    # True when [[reply_to_current]] was present but not yet mapped to a message id
    reply_to_current: bool = False
    
    # Send audio as voice message (bubble) instead of audio file
    audio_as_voice: bool = False
    
    # Is this an error message
    is_error: bool = False
    
    # Channel-specific payload data (per-channel envelope)
    channel_data: dict[str, Any] = field(default_factory=dict)
    
    # Silent reply (don't send)
    is_silent: bool = False
    
    def has_content(self) -> bool:
        """Check if this payload has renderable content."""
        return bool(
            self.text
            or self.media_url
            or (self.media_urls and len(self.media_urls) > 0)
            or self.audio_as_voice
        )
