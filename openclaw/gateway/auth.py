"""
Gateway authentication

Matches TypeScript src/gateway/auth.ts with timing-safe comparisons
and structured error codes.
"""
from __future__ import annotations

import hmac
import logging
from enum import Enum
from typing import NamedTuple

logger = logging.getLogger(__name__)


class AuthMode(str, Enum):
    """Gateway authentication mode."""
    TOKEN = "token"
    PASSWORD = "password"


class AuthMethod(str, Enum):
    """Authentication method used."""
    TOKEN = "token"
    PASSWORD = "password"
    TAILSCALE = "tailscale"
    DEVICE_TOKEN = "device-token"
    LOCAL_DIRECT = "local-direct"


class AuthResult(NamedTuple):
    """Result of authentication attempt."""
    ok: bool
    method: AuthMethod | None = None
    user: str | None = None
    reason: str | None = None


def safe_equal(a: str, b: str) -> bool:
    """
    Timing-safe string comparison (matches TS safeEqual lines 35-39).
    
    Uses hmac.compare_digest which is timing-safe in Python.
    Buffers are same length first (quick reject, then timing-safe compare).
    
    Args:
        a: First string
        b: Second string
    
    Returns:
        True if strings are equal
    """
    if len(a) != len(b):
        return False
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def is_loopback_address(ip: str | None) -> bool:
    """
    Check if IP is loopback (matches TS isLoopbackAddress lines 46-62).
    
    Args:
        ip: IP address string
    
    Returns:
        True if loopback
    """
    if not ip:
        return False
    
    if ip == "127.0.0.1":
        return True
    if ip.startswith("127."):
        return True
    if ip == "::1":
        return True
    if ip.startswith("::ffff:127."):
        return True
    
    return False


def authorize_gateway_token(
    config_token: str | None,
    request_token: str | None,
) -> AuthResult:
    """
    Authorize via token (matches TS token auth logic lines 263-273).
    
    Args:
        config_token: Expected token from config
        request_token: Token from request
    
    Returns:
        AuthResult
    """
    if not config_token:
        return AuthResult(ok=False, reason="token_missing_config")
    
    if not request_token:
        return AuthResult(ok=False, reason="token_missing")
    
    if not safe_equal(request_token, config_token):
        return AuthResult(ok=False, reason="token_mismatch")
    
    return AuthResult(ok=True, method=AuthMethod.TOKEN)


def authorize_gateway_password(
    config_password: str | None,
    request_password: str | None,
) -> AuthResult:
    """
    Authorize via password (matches TS password auth logic lines 276-287).
    
    Args:
        config_password: Expected password from config
        request_password: Password from request
    
    Returns:
        AuthResult
    """
    if not config_password:
        return AuthResult(ok=False, reason="password_missing_config")
    
    if not request_password:
        return AuthResult(ok=False, reason="password_missing")
    
    if not safe_equal(request_password, config_password):
        return AuthResult(ok=False, reason="password_mismatch")
    
    return AuthResult(ok=True, method=AuthMethod.PASSWORD)


def authorize_gateway_connect(
    auth_mode: AuthMode,
    config_token: str | None = None,
    config_password: str | None = None,
    request_token: str | None = None,
    request_password: str | None = None,
    allow_tailscale: bool = False,
    client_ip: str | None = None,
    trusted_proxies: list[str] | None = None,
) -> AuthResult:
    """
    Main gateway connection authorization (matches TS authorizeGatewayConnect lines 238-291).
    
    Auth modes:
    - token: Requires matching token
    - password: Requires matching password
    - tailscale: Requires verified Tailscale user (if enabled)
    - local-direct: Auto-allow for loopback connections
    
    Args:
        auth_mode: Authentication mode
        config_token: Expected token from config
        config_password: Expected password from config
        request_token: Token from request
        request_password: Password from request
        allow_tailscale: Whether to allow Tailscale auth
        client_ip: Client IP address
        trusted_proxies: List of trusted proxy addresses
    
    Returns:
        AuthResult
    """
    # Check for local direct connection (bypass auth)
    if client_ip and is_loopback_address(client_ip):
        logger.debug(f"Local direct request from {client_ip}, bypassing auth")
        return AuthResult(ok=True, method=AuthMethod.LOCAL_DIRECT)
    
    # Tailscale auth (if enabled)
    if allow_tailscale and client_ip:
        # TODO: Implement Tailscale whois lookup
        # For now, we don't have Tailscale integration in Python
        logger.debug("Tailscale auth not yet implemented in Python")
    
    # Token auth
    if auth_mode == AuthMode.TOKEN:
        return authorize_gateway_token(config_token, request_token)
    
    # Password auth
    if auth_mode == AuthMode.PASSWORD:
        return authorize_gateway_password(config_password, request_password)
    
    return AuthResult(ok=False, reason="unauthorized")


def validate_auth_config(auth_mode: AuthMode, token: str | None, password: str | None):
    """
    Validate auth configuration (matches TS guardGatewayAuth lines 225-235).
    
    Raises:
        ValueError: If configuration is invalid
    """
    if auth_mode == AuthMode.TOKEN and not token:
        raise ValueError(
            "gateway auth mode is token, but no token was configured "
            "(set gateway.auth.token or OPENCLAW_GATEWAY_TOKEN)"
        )
    
    if auth_mode == AuthMode.PASSWORD and not password:
        raise ValueError(
            "gateway auth mode is password, but no password was configured "
            "(set gateway.auth.password)"
        )
