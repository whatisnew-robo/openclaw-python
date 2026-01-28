"""
Agent module for ClawdBot
"""
from .runtime import AgentRuntime, AgentEvent
from .session import Session, SessionManager, Message
from .context import ContextManager, ContextWindow
from .errors import (
    AgentError,
    ContextOverflowError,
    RateLimitError,
    AuthenticationError,
    NetworkError,
    TimeoutError,
    ErrorRecovery,
    classify_error,
    is_retryable_error,
    format_error_message
)

__all__ = [
    # Runtime
    "AgentRuntime",
    "AgentEvent",
    # Session
    "Session",
    "SessionManager",
    "Message",
    # Context
    "ContextManager",
    "ContextWindow",
    # Errors
    "AgentError",
    "ContextOverflowError",
    "RateLimitError",
    "AuthenticationError",
    "NetworkError",
    "TimeoutError",
    "ErrorRecovery",
    "classify_error",
    "is_retryable_error",
    "format_error_message",
]
