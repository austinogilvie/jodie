#!/usr/bin/env python3
# jodie/parsers/base.py
"""Base classes for parser plugin architecture."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class ParseResult:
    """Result from a parser."""
    value: Any
    confidence: float  # 0.0 to 1.0
    consumed_text: str
    source: str = "parsed"  # "parsed", "inferred", "explicit"


class BaseParser(ABC):
    """Abstract base class for all parsers.

    To create a new parser:
    1. Create a new file in jodie/parsers/
    2. Subclass BaseParser
    3. Set name, priority, and field_name class attributes
    4. Implement the parse() classmethod

    Parsers are auto-discovered by the Pipeline.
    """
    name: str = ""
    priority: int = 0  # Higher = runs first
    field_name: str = ""

    @classmethod
    @abstractmethod
    def parse(cls, text: str) -> Optional[ParseResult]:
        """Parse text and return result or None if no match.

        Args:
            text: Input text to parse

        Returns:
            ParseResult if match found, None otherwise
        """
        pass

    @staticmethod
    def find_matches(pattern: str, text: str) -> list:
        """Find all regex matches in text.

        Args:
            pattern: Regex pattern
            text: Text to search

        Returns:
            List of matches
        """
        import re
        return re.findall(pattern, text)
