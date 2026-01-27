#!/usr/bin/env python3
"""Tests for TitleParser."""
import pytest
from jodie.parsers.parsers import TitleParser

class TestTitleParser:
    def test_ceo(self):
        assert TitleParser.parse("CEO") is not None

    def test_engineer(self):
        assert TitleParser.parse("Software Engineer") is not None

    def test_senior_title(self):
        assert TitleParser.parse("Senior Software Engineer") is not None

    def test_cofounder(self):
        assert TitleParser.parse("Co-founder") is not None

    def test_not_a_title(self):
        assert TitleParser.parse("Random Text") is None

    def test_empty_string(self):
        assert TitleParser.parse("") is None
