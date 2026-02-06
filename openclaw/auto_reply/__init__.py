"""Auto-Reply System for OpenClaw.

This module implements automatic message processing and reply generation,
matching the TypeScript OpenClaw auto-reply system.
"""

from __future__ import annotations

from .types import (
    ReplyPayload,
    GetReplyOptions,
    BlockReplyContext,
    ModelSelectedContext,
)
from .tokens import (
    HEARTBEAT_TOKEN,
    SILENT_REPLY_TOKEN,
    is_silent_reply_text,
)
from .reply import get_reply

__all__ = [
    "ReplyPayload",
    "GetReplyOptions",
    "BlockReplyContext",
    "ModelSelectedContext",
    "HEARTBEAT_TOKEN",
    "SILENT_REPLY_TOKEN",
    "is_silent_reply_text",
    "get_reply",
]
