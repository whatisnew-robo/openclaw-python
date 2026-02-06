"""
Gateway error codes

Matches TypeScript src/gateway/protocol/schema/error-codes.ts
"""
from __future__ import annotations

from enum import Enum


class ErrorCode(str, Enum):
    """
    Gateway error codes (matches TS ErrorCodes lines 3-9).
    
    Used for structured error responses in gateway protocol.
    """
    NOT_LINKED = "NOT_LINKED"
    NOT_PAIRED = "NOT_PAIRED"
    AGENT_TIMEOUT = "AGENT_TIMEOUT"
    INVALID_REQUEST = "INVALID_REQUEST"
    UNAVAILABLE = "UNAVAILABLE"


class GatewayError(Exception):
    """Gateway error with structured error code."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        details: dict | None = None,
    ):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> dict:
        """Convert to dict for JSON response."""
        return {
            "error": self.error_code.value,
            "message": str(self),
            "details": self.details,
        }


class NotLinkedError(GatewayError):
    """Session/device not linked."""
    def __init__(self, message: str = "Not linked", details: dict | None = None):
        super().__init__(message, ErrorCode.NOT_LINKED, details)


class NotPairedError(GatewayError):
    """Device not paired."""
    def __init__(self, message: str = "Not paired", details: dict | None = None):
        super().__init__(message, ErrorCode.NOT_PAIRED, details)


class AgentTimeoutError(GatewayError):
    """Agent request timed out."""
    def __init__(self, message: str = "Agent timeout", details: dict | None = None):
        super().__init__(message, ErrorCode.AGENT_TIMEOUT, details)


class InvalidRequestError(GatewayError):
    """Invalid request format/parameters."""
    def __init__(self, message: str = "Invalid request", details: dict | None = None):
        super().__init__(message, ErrorCode.INVALID_REQUEST, details)


class UnavailableError(GatewayError):
    """Service unavailable."""
    def __init__(self, message: str = "Unavailable", details: dict | None = None):
        super().__init__(message, ErrorCode.UNAVAILABLE, details)
