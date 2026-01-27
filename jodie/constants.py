#!/usr/bin/env python3
# jodie/constants.py
"""Shared constants used across jodie modules."""

from typing import FrozenSet

# Common webmail/personal email providers
# Used to distinguish work emails from personal emails
# and to skip company inference from these domains
WEBMAIL_DOMAINS: FrozenSet[str] = frozenset({
    # Google
    "gmail.com",
    "googlemail.com",
    # Microsoft
    "hotmail.com",
    "hotmail.co.uk",
    "hotmail.de",
    "hotmail.es",
    "hotmail.fr",
    "hotmail.it",
    "outlook.com",
    "live.com",
    # Yahoo
    "yahoo.com",
    "ymail.com",
    # Apple
    "icloud.com",
    "mac.com",
    "me.com",
    # AOL/Verizon
    "aol.com",
    "verizon.net",
    # Privacy-focused
    "protonmail.com",
    "proton.me",
    "tutanota.com",
    "tuta.com",
    "hushmail.com",
    # Other
    "hey.com",
    "qq.com",
    "zoho.com",
    "fastmail.com",
})
