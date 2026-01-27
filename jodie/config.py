#!/usr/bin/env python3
# jodie/config.py
"""Configuration file support for jodie.

Supports .jodierc files in TOML format, checked in order:
1. Current directory (./.jodierc)
2. Home directory (~/.jodierc)

Command-line flags override config values.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Try Python 3.11+ tomllib, fall back to tomli
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


DEFAULT_CONFIG: Dict[str, Any] = {
    "defaults": {
        "company": None,
        "note_prefix": None,
        "websites": [],
        "tags": [],
    },
    "parsers": {
        "email": True,
        "phone": True,
        "website": True,
        "title": True,
        "name": True,
        "company": True,
    },
    "behavior": {
        "auto_infer_company": True,
        "strip_pronouns": True,
    }
}


def find_config_file() -> Optional[Path]:
    """Find .jodierc in current dir or home dir.

    Returns:
        Path to config file if found, None otherwise
    """
    candidates = [
        Path.cwd() / ".jodierc",
        Path.home() / ".jodierc",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base.

    Args:
        base: Base dictionary
        override: Dictionary to merge on top

    Returns:
        Merged dictionary
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config() -> Dict[str, Any]:
    """Load config from file, merged with defaults.

    Returns:
        Configuration dictionary with defaults and any user overrides
    """
    config = DEFAULT_CONFIG.copy()
    config = {k: v.copy() if isinstance(v, dict) else v for k, v in config.items()}

    if tomllib is None:
        # No TOML parser available, return defaults
        return config

    config_file = find_config_file()
    if config_file:
        try:
            with open(config_file, "rb") as f:
                user_config = tomllib.load(f)
            config = _deep_merge(config, user_config)
        except Exception as e:
            sys.stderr.write(f"Warning: Error loading {config_file}: {e}\n")

    return config


def get_default(config: Dict[str, Any], key: str, cli_value: Optional[str] = None) -> Optional[str]:
    """Get a value, preferring CLI over config.

    Args:
        config: Configuration dictionary
        key: Key to look up in defaults section
        cli_value: Value from command line (takes precedence)

    Returns:
        CLI value if provided, otherwise config default, or None
    """
    if cli_value is not None:
        return cli_value
    return config.get("defaults", {}).get(key)
