#!/usr/bin/env python3
# jodie/cli/preview.py
"""Dry-run preview formatting for contact fields."""

def format_preview(fields: dict) -> str:
    """Format parsed fields as a preview table.

    Args:
        fields: Dict with keys like 'first_name', 'last_name', 'email', etc.
                Values can be strings or dicts with 'value', 'source', 'confidence'

    Returns:
        Formatted string table
    """
    # Normalize fields to consistent format
    normalized = {}
    field_labels = {
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'email': 'Email',
        'phone': 'Phone',
        'job_title': 'Title',
        'company': 'Company',
        'websites': 'Websites',
        'note': 'Note'
    }

    for key, value in fields.items():
        if value is None:
            continue
        label = field_labels.get(key, key.replace('_', ' ').title())
        if isinstance(value, dict):
            normalized[label] = value
        elif isinstance(value, list):
            # Handle websites list
            if value:
                normalized[label] = {'value': ', '.join(str(v) for v in value), 'source': 'parsed', 'confidence': 1.0}
        else:
            normalized[label] = {'value': str(value), 'source': 'parsed', 'confidence': 1.0}

    if not normalized:
        return "No fields detected."

    lines = []
    lines.append("┌" + "─" * 57 + "┐")
    lines.append("│" + "Contact Preview".center(57) + "│")
    lines.append("├" + "─" * 14 + "┬" + "─" * 22 + "┬" + "─" * 19 + "┤")
    lines.append("│ Field        │ Value                │ Source            │")
    lines.append("├" + "─" * 14 + "┼" + "─" * 22 + "┼" + "─" * 19 + "┤")

    for field_name, field_data in normalized.items():
        value = str(field_data.get('value', ''))[:20]
        source = field_data.get('source', 'unknown')
        confidence = field_data.get('confidence', 0)
        if confidence > 0:
            source_str = f"{source} ({int(confidence*100)}%)"
        else:
            source_str = source
        lines.append(f"│ {field_name:<12} │ {value:<20} │ {source_str:<17} │")

    lines.append("└" + "─" * 14 + "┴" + "─" * 22 + "┴" + "─" * 19 + "┘")
    lines.append("")
    lines.append("Run without --dry-run to save this contact.")

    return "\n".join(lines)
