#!/usr/bin/env python3
# jodie/parsers/pipeline.py
"""Parser pipeline for orchestrating field extraction."""

from typing import List, Dict
from .base import ParseResult
from jodie.constants import WEBMAIL_DOMAINS


class ParserPipeline:
    """Orchestrates parsers to extract contact fields from text.

    The pipeline:
    1. Runs parsers in priority order
    2. Stops processing a line when a parser matches
    3. Applies cross-field inference after all parsing
    """

    @classmethod
    def parse(cls, lines: List[str]) -> Dict[str, ParseResult]:
        """Run all parsers on input lines.

        Args:
            lines: List of text lines to parse

        Returns:
            Dict mapping field names to ParseResults
        """
        # Import parsers here to avoid circular imports
        from .parsers import (
            EmailParser, PhoneParser, WebsiteParser,
            TitleParser, NameParser
        )

        results: Dict[str, ParseResult] = {}

        # Parser configuration: (parser_class, field_name, priority)
        # Higher priority = runs first
        parsers = [
            (EmailParser, "email", 100),
            (WebsiteParser, "websites", 90),
            (TitleParser, "job_title", 70),
            (PhoneParser, "phone", 60),
            (NameParser, "name", 50),
        ]

        # Sort by priority (highest first)
        parsers.sort(key=lambda x: x[2], reverse=True)

        for line in lines:
            if not line or not line.strip():
                continue

            for parser_class, field_name, _ in parsers:
                # Skip if we already have this field
                if field_name in results:
                    continue

                # Try to parse
                try:
                    result = parser_class.parse(line)
                    if result is not None:
                        # Handle NameParser's tuple return
                        if field_name == "name" and isinstance(result, tuple):
                            first, last = result
                            if first or last:
                                results["first_name"] = ParseResult(
                                    value=first,
                                    confidence=0.95,
                                    consumed_text=line,
                                    source="parsed"
                                )
                                results["last_name"] = ParseResult(
                                    value=last,
                                    confidence=0.95,
                                    consumed_text=line,
                                    source="parsed"
                                )
                        else:
                            results[field_name] = ParseResult(
                                value=result,
                                confidence=0.95,
                                consumed_text=line,
                                source="parsed"
                            )
                        break  # Line consumed
                except Exception:
                    # Parser failed, try next
                    continue

        # Apply cross-field inference
        cls._apply_inference(results)

        return results

    @classmethod
    def _apply_inference(cls, results: Dict[str, ParseResult]) -> None:
        """Apply cross-field inference after parsing.

        Args:
            results: Dict of parsed results (modified in place)
        """
        # Infer company from email domain
        if "company" not in results and "email" in results:
            email = results["email"].value
            if email and "@" in email:
                domain = email.split("@")[1].lower()
                if domain not in WEBMAIL_DOMAINS:
                    company = domain.split(".")[0].title()
                    results["company"] = ParseResult(
                        value=company,
                        confidence=0.6,
                        consumed_text=domain,
                        source="inferred"
                    )

    @classmethod
    def to_dict(cls, results: Dict[str, ParseResult]) -> Dict[str, any]:
        """Convert ParseResults to simple dict of values.

        Args:
            results: Dict mapping field names to ParseResults

        Returns:
            Dict mapping field names to values
        """
        return {k: v.value for k, v in results.items()}
