#!/usr/bin/env python3
"""Regression tests for CLI auto parsing."""

from jodie.cli.__main__ import parse_auto
from jodie.parsers import ParserPipeline


def test_single_quoted_contact_extracts_all_fields():
    fields = parse_auto([
        "John Smith john@example.ai Founder Example AI 4155555555"
    ])

    assert fields["first_name"] == "John"
    assert fields["last_name"] == "Smith"
    assert fields["email"] == "john@example.ai"
    assert fields["job_title"] == "Founder"
    assert fields["company"] == "Example AI"
    assert fields["phone"] == "4155555555"


def test_pre_split_contact_extracts_same_fields():
    fields = parse_auto(
        "John Smith john@example.ai Founder Example AI 4155555555".split()
    )

    assert fields["first_name"] == "John"
    assert fields["last_name"] == "Smith"
    assert fields["email"] == "john@example.ai"
    assert fields["job_title"] == "Founder"
    assert fields["company"] == "Example AI"
    assert fields["phone"] == "4155555555"


def test_title_and_company_can_share_one_segment():
    fields = parse_auto([
        "Jane Smith <jane@startup.io>",
        "CEO, Startup Inc",
        "415-555-1234",
    ])

    assert fields["first_name"] == "Jane"
    assert fields["last_name"] == "Smith"
    assert fields["email"] == "jane@startup.io"
    assert fields["job_title"] == "CEO"
    assert fields["company"] == "Startup Inc"
    assert fields["phone"] == "4155551234"


def test_parser_pipeline_uses_auto_extractor():
    results = ParserPipeline.parse([
        "John Smith john@example.ai Founder Example AI 4155555555"
    ])
    fields = ParserPipeline.to_dict(results)

    assert fields["first_name"] == "John"
    assert fields["last_name"] == "Smith"
    assert fields["email"] == "john@example.ai"
    assert fields["job_title"] == "Founder"
    assert fields["company"] == "Example AI"
    assert fields["phone"] == "4155555555"
