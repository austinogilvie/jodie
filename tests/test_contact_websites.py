#!/usr/bin/env python3
"""Tests for Contact.websites handling of str / dict / mixed inputs."""
import pytest

Contacts = pytest.importorskip("Contacts")  # macOS-only (PyObjC Contacts framework)
from Contacts import CNLabelURLAddressHomePage

from jodie.contact import Contact


def _as_pairs(contact):
    return [(site.label(), site.value()) for site in (contact.websites or [])]


def test_websites_mixed_str_and_dict():
    """Regression: a list mixing plain URL strings and dicts used to raise
    AttributeError because the setter dispatched on type(value[0]) only."""
    c = Contact(
        first_name="Test",
        last_name="Person",
        email="test@example.com",
        websites=[
            "https://example.com",
            {"url": "https://www.linkedin.com/in/testperson", "label": "LinkedIn"},
        ],
    )
    assert _as_pairs(c) == [
        ("Work", "https://example.com"),
        ("LinkedIn", "https://www.linkedin.com/in/testperson"),
    ]
    assert c.linkedin == "https://www.linkedin.com/in/testperson"


def test_websites_dict_first_then_str():
    c = Contact(
        first_name="Test",
        last_name="Person",
        email="test@example.com",
        websites=[
            {"url": "https://www.linkedin.com/in/testperson"},
            "https://example.com",
        ],
    )
    assert _as_pairs(c) == [
        ("LinkedIn", "https://www.linkedin.com/in/testperson"),
        ("Work", "https://example.com"),
    ]


def test_websites_plain_strings_autolabel_linkedin():
    c = Contact(
        first_name="Test",
        last_name="Person",
        email="test@example.com",
        websites=["https://example.com", "https://www.linkedin.com/in/testperson"],
    )
    assert _as_pairs(c) == [
        ("Work", "https://example.com"),
        ("LinkedIn", "https://www.linkedin.com/in/testperson"),
    ]


def test_websites_single_string_and_single_dict():
    c = Contact(first_name="Test", last_name="Person", websites="https://github.com/testperson")
    assert _as_pairs(c) == [("GitHub", "https://github.com/testperson")]

    c.websites = {"url": "https://example.org", "label": "Blog"}
    assert _as_pairs(c) == [("Blog", "https://example.org")]


def test_websites_skips_empty_items_and_clears():
    c = Contact(first_name="Test", last_name="Person", websites=["", "  ", "https://example.org"])
    assert _as_pairs(c) == [(CNLabelURLAddressHomePage, "https://example.org")]

    c.websites = None
    assert c.websites is None


def test_websites_rejects_unknown_item_type():
    with pytest.raises(TypeError):
        Contact(first_name="Test", last_name="Person", websites=[123])
