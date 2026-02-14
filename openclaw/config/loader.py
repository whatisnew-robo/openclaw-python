"""Configuration loader for OpenClaw.

Loads configuration from files and environment variables.
"""

from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Any, Optional, Union


_cached_config: Optional["ClawdbotConfig"] = None


def load_config(config_path: Optional[str | Path] = None, as_dict: bool = False) -> Union["ClawdbotConfig", dict[str, Any]]:
    """Load OpenClaw configuration.

    Args:
        config_path: Optional path to config file
        as_dict: If True, return dict instead of ClawdbotConfig object

    Returns:
        Configuration object (ClawdbotConfig) or dictionary if as_dict=True
    """
    from .schema import ClawdbotConfig
    
    global _cached_config

    if _cached_config is not None:
        return _cached_config.model_dump() if as_dict else _cached_config

    config_dict: dict[str, Any] = {}

    # Try to load from config file
    if config_path:
        path = Path(config_path)
    else:
        # Try default locations
        candidates = [
            Path.cwd() / "openclaw.json",
            Path.cwd() / "config" / "openclaw.json",
            Path.home() / ".openclaw" / "config.json",
        ]
        path = None
        for candidate in candidates:
            if candidate.exists():
                path = candidate
                break

    if path and path.exists():
        try:
            with open(path, "r") as f:
                config_dict = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load config from {path}: {e}")

    # Create ClawdbotConfig object from dict
    try:
        config_obj = ClawdbotConfig(**config_dict) if config_dict else ClawdbotConfig()
    except Exception as e:
        print(f"Warning: Failed to parse config: {e}")
        config_obj = ClawdbotConfig()

    _cached_config = config_obj
    return config_obj.model_dump() if as_dict else config_obj


def save_config(config: Any, config_path: Optional[str | Path] = None) -> None:
    """Save OpenClaw configuration to file.

    Args:
        config: Configuration object or dictionary to save
        config_path: Optional path to config file (defaults to ~/.openclaw/config.json)
    """
    global _cached_config

    # Determine save path
    if config_path:
        path = Path(config_path)
    else:
        # Default to user config directory
        path = Path.home() / ".openclaw" / "config.json"

    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # Convert config object to dict if needed
    if hasattr(config, "model_dump"):
        # Pydantic model
        config_dict = config.model_dump(exclude_none=True)
    elif hasattr(config, "dict"):
        # Pydantic v1 model
        config_dict = config.dict(exclude_none=True)
    elif hasattr(config, "__dict__"):
        # Regular object
        config_dict = config.__dict__
    else:
        # Already a dict
        config_dict = config

    # Write to file
    with open(path, "w") as f:
        json.dump(config_dict, f, indent=2)

    # Update cache
    _cached_config = config_dict


def get_config_path() -> Optional[Path]:
    """Get the path to the active configuration file.
    
    Returns:
        Path to config file, or None if not found
    """
    candidates = [
        Path.cwd() / "openclaw.json",
        Path.cwd() / "config" / "openclaw.json",
        Path.home() / ".openclaw" / "config.json",
    ]
    
    for candidate in candidates:
        if candidate.exists():
            return candidate
    
    return None


def get_config_value(key_path: str, default: Any = None) -> Any:
    """Get a configuration value by dot-separated key path.

    Args:
        key_path: Dot-separated key path (e.g., "channels.telegram.botToken")
        default: Default value if not found

    Returns:
        Configuration value or default
    """
    config = load_config()
    keys = key_path.split(".")
    value = config
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    return value
