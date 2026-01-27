#!/usr/bin/env python3
"""Tests for PhoneParser."""
import pytest
from jodie.parsers.parsers import PhoneParser

class TestPhoneParser:
    def test_ten_digit(self):
        assert PhoneParser.parse("5167763192") == "5167763192"

    def test_with_dashes(self):
        assert PhoneParser.parse("516-776-3192") == "5167763192"

    def test_with_dots(self):
        assert PhoneParser.parse("516.776.3192") == "5167763192"

    def test_with_parens(self):
        assert PhoneParser.parse("(516) 776-3192") == "5167763192"

    def test_with_country_code(self):
        result = PhoneParser.parse("+1 516 776 3192")
        assert result in ["5167763192", "15167763192"]

    def test_in_text(self):
        result = PhoneParser.parse("Call me at 555-555-5555")
        assert result == "5555555555"

    def test_invalid_phone(self):
        assert PhoneParser.parse("12345") is None

    def test_empty_string(self):
        assert PhoneParser.parse("") is None
