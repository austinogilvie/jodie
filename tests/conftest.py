#!/usr/bin/env python3
"""Shared pytest fixtures for jodie tests."""
import pytest

@pytest.fixture
def sample_signatures():
    """Real-world email signatures for testing."""
    return [
        {
            "input": "Jane Doe, Co-founder & CEO\njane@example.com • example.com",
            "expected": {
                "first_name": "Matheus",
                "last_name": "Riolfi",
                "email": "jane@example.com",
                "job_title": "Co-founder & CEO",
            }
        },
        {
            "input": "John Smith (he/him)\njohn@example.org\n555-555-5555",
            "expected": {
                "first_name": "Keith",
                "last_name": "Hamlin",
                "email": "john@example.org",
                "phone": "5555555555",
            }
        },
    ]
