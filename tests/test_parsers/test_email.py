#!/usr/bin/env python3
"""Tests for EmailParser."""
import pytest
from jodie.parsers.parsers import EmailParser

class TestEmailParser:
    def test_simple_email(self):
        assert EmailParser.parse("john@example.com") == "john@example.com"

    def test_email_with_plus(self):
        assert EmailParser.parse("john+tag@example.com") == "john+tag@example.com"

    def test_email_in_angle_brackets(self):
        assert EmailParser.parse("<john@example.com>") == "john@example.com"

    def test_email_with_name(self):
        assert EmailParser.parse("John Doe <john@example.com>") == "john@example.com"

    def test_email_in_text(self):
        assert EmailParser.parse("Contact: john@example.com here") == "john@example.com"

    def test_invalid_email(self):
        assert EmailParser.parse("not-an-email") is None

    def test_empty_string(self):
        assert EmailParser.parse("") is None

    def test_none_input(self):
        # EmailParser uses find_matches which will fail on None
        # This tests that the behavior is defined (either returns None or raises)
        try:
            result = EmailParser.parse(None)
            # If it doesn't raise, result should be None
            assert result is None
        except (TypeError, AttributeError):
            # Acceptable behavior - None is not a valid input
            pass

    @pytest.mark.parametrize("input,expected", [
        ("john.doe@sub.example.co.uk", "john.doe@sub.example.co.uk"),
        ("a@b.co", "a@b.co"),
        ("user_name@domain.org", "user_name@domain.org"),
    ])
    def test_various_formats(self, input, expected):
        assert EmailParser.parse(input) == expected
