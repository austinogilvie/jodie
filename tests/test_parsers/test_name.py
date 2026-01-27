#!/usr/bin/env python3
"""Tests for NameParser."""
import pytest
from jodie.parsers.parsers import NameParser

class TestNameParser:
    def test_simple_name(self):
        first, last = NameParser.parse("John Doe")
        assert first == "John"
        assert last == "Doe"

    def test_name_with_middle(self):
        first, last = NameParser.parse("John Michael Doe")
        assert first == "John"
        assert "Michael" in last or "Doe" in last

    def test_single_name(self):
        first, last = NameParser.parse("John")
        assert first == "John"

    def test_name_from_email_format(self):
        first, last = NameParser.parse("John Doe <john@example.com>")
        assert first == "John"
        assert last == "Doe"

    def test_empty_string(self):
        first, last = NameParser.parse("")
        assert first == ""
        assert last == ""
