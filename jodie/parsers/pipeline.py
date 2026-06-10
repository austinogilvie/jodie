#!/usr/bin/env python3
# jodie/parsers/pipeline.py
"""Parser pipeline for orchestrating field extraction."""

from typing import Any, Dict, List
from .base import ParseResult
from .extractor import parse_contact_fields


class ParserPipeline:
    """Orchestrates parsers to extract contact fields from text.

    The pipeline delegates to the shared extract-and-remove parser used by
    CLI auto mode, then wraps values in ParseResult objects.
    """

    @classmethod
    def parse(cls, lines: List[str]) -> Dict[str, ParseResult]:
        """Run all parsers on input lines.

        Args:
            lines: List of text lines to parse

        Returns:
            Dict mapping field names to ParseResults
        """
        results: Dict[str, ParseResult] = {}
        fields = parse_contact_fields(lines)

        for field_name, value in fields.items():
            if value is None or value == []:
                continue
            results[field_name] = ParseResult(
                value=value,
                confidence=0.95,
                consumed_text=" ".join(lines),
                source="parsed",
            )

        return results

    @classmethod
    def _apply_inference(cls, results: Dict[str, ParseResult]) -> None:
        """Apply cross-field inference after parsing.

        Args:
            results: Dict of parsed results (modified in place)
        """
        # Inference is handled by parse_contact_fields.
        pass

    @classmethod
    def to_dict(cls, results: Dict[str, ParseResult]) -> Dict[str, Any]:
        """Convert ParseResults to simple dict of values.

        Args:
            results: Dict mapping field names to ParseResults

        Returns:
            Dict mapping field names to values
        """
        return {k: v.value for k, v in results.items()}
