#!/usr/bin/env python3
"""Shared pytest fixtures for jodie tests."""
import pytest

@pytest.fixture
def sample_signatures():
    """Sample email signatures for testing."""
    return [
        {
            "input": "Jane Doe, Co-founder & CEO\njane@example.com • example.com",
            "expected": {
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane@example.com",
                "job_title": "Co-founder & CEO",
            }
        },
        {
            "input": "John Smith (he/him)\njohn@example.org\n555-555-5555",
            "expected": {
                "first_name": "John",
                "last_name": "Smith",
                "email": "john@example.org",
                "phone": "5555555555",
            }
        },
    ]
