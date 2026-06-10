#!/usr/bin/env python3
# jodie/parsers/extractor.py
"""Contact field extraction shared by CLI auto mode and parser pipeline."""

import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

from jodie.constants import WEBMAIL_DOMAINS
from .parsers import EmailParser, NameParser, PhoneParser, TitleParser, WebsiteParser


EMAIL_PATTERN = re.compile(
    r'<(\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b)>'
    r'|(\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b)'
)
WEBSITE_PATTERN = re.compile(r'https?://[^\s]+|www\.[^\s]+', re.IGNORECASE)
PHONE_PATTERNS = [
    re.compile(r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'),
    re.compile(r'\b[0-9]{10}\b'),
    re.compile(r'\+?[0-9]{1,3}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}\b'),
]

BUSINESS_TERMS = {
    "inc", "inc.", "llc", "ltd", "ltd.", "corp", "corp.", "corporation",
    "co", "co.", "company", "technologies", "technology", "systems", "labs",
    "studio", "studios", "group", "partners", "ventures", "capital"
}


def parse_contact_fields(arguments: Any) -> Dict[str, Any]:
    """Extract contact fields from text independent of shell argument shape."""
    segments = _normalize_arguments(arguments)
    fields: Dict[str, Any] = {
        "first_name": None,
        "last_name": None,
        "email": None,
        "phone": None,
        "job_title": None,
        "company": None,
        "websites": [],
        "note": None,
    }

    working = _join_segments(segments)
    consumed_texts: List[str] = []

    email_match = EMAIL_PATTERN.search(working)
    if email_match:
        email_text = next((part for part in email_match.groups() if part), email_match.group(0))
        fields["email"] = EmailParser.parse(email_match.group(0)) or email_text

        name_candidate = _name_before_email(working[:email_match.start()])
        if name_candidate:
            first_name, last_name, consumed_name = name_candidate
            fields["first_name"] = first_name
            fields["last_name"] = last_name
            working = _remove_first(working, consumed_name)
            consumed_texts.append(consumed_name)

        working = _remove_first(working, email_match.group(0))
        consumed_texts.append(email_match.group(0))

    while True:
        website_match = WEBSITE_PATTERN.search(working)
        if not website_match:
            break
        website = WebsiteParser.parse(website_match.group(0))
        if website:
            fields["websites"].append(website)
        working = _remove_first(working, website_match.group(0))
        consumed_texts.append(website_match.group(0))

    if not fields["phone"]:
        phone_match = _find_phone_match(working)
        if phone_match:
            phone = PhoneParser.parse(phone_match.group(0))
            if phone:
                fields["phone"] = phone
                working = _remove_first(working, phone_match.group(0))
                consumed_texts.append(phone_match.group(0))

    if not fields["job_title"]:
        title_match = _find_title_match(working)
        if title_match:
            title, consumed_title = title_match
            fields["job_title"] = title
            working = _remove_first(working, consumed_title)
            consumed_texts.append(consumed_title)

    residual_segments = _residual_segments(segments, consumed_texts)

    if not fields["first_name"]:
        name_candidate = _pick_name_segment(residual_segments)
        if name_candidate:
            first_name, last_name, consumed_name = name_candidate
            fields["first_name"] = first_name
            fields["last_name"] = last_name
            working = _remove_first(working, consumed_name)
            consumed_texts.append(consumed_name)

    if not fields["first_name"]:
        split_fields = _split_name_company(_clean_text(working))
        if split_fields:
            first_name, last_name, company_name = split_fields
            fields["first_name"] = first_name
            fields["last_name"] = last_name
            fields["company"] = company_name

    company = _company_from_residual(working, fields["websites"])
    if not fields["company"] and company:
        fields["company"] = company

    if not fields["company"] and fields["email"]:
        fields["company"] = _company_from_email(fields["email"])

    return fields


def _normalize_arguments(arguments: Any) -> List[str]:
    if arguments is None:
        return []
    if isinstance(arguments, str):
        arguments = [arguments]
    return [str(arg).strip() for arg in arguments if str(arg).strip()]


def _join_segments(segments: Iterable[str]) -> str:
    return _clean_text(" ".join(segments))


def _clean_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text or '').strip()


def _remove_first(text: str, needle: str) -> str:
    if not needle:
        return _clean_text(text)

    index = text.lower().find(needle.lower())
    if index == -1:
        return _clean_text(text)

    return _clean_text(f"{text[:index]} {text[index + len(needle):]}")


def _name_before_email(prefix: str) -> Optional[Tuple[str, str, str]]:
    candidate = prefix.strip().strip("<")
    if not candidate:
        return None

    parts = re.split(r'[\n\r|•·;,:\u2013\u2014]+', candidate)
    candidate = parts[-1].strip()
    if not candidate:
        return None

    first_name, last_name = NameParser.parse(candidate)
    if _plausible_name(candidate, first_name, last_name):
        return first_name, last_name, candidate
    return None


def _find_phone_match(text: str) -> Optional[re.Match]:
    for pattern in PHONE_PATTERNS:
        match = pattern.search(text)
        if match and PhoneParser.parse(match.group(0)):
            return match
    return None


def _find_title_match(text: str) -> Optional[Tuple[str, str]]:
    text = text or ""

    connector_match = re.search(
        r'\b(?:vp|head|director|president|vice president)\s+of\s+'
        r'[A-Za-z][A-Za-z&/-]*(?:\s+[A-Za-z][A-Za-z&/-]*){0,2}\b',
        text,
        re.IGNORECASE,
    )
    if connector_match:
        raw = connector_match.group(0)
        return TitleParser.parse(raw) or raw, raw

    for title in _title_candidates():
        pattern = r'(?<!\w)' + re.escape(title).replace(r'\ ', r'\s+') + r'(?!\w)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            raw = match.group(0)
            return TitleParser.parse(raw) or raw, raw

    return None


def _title_candidates() -> List[str]:
    candidates = set(TitleParser.COMMON_TITLES)
    for prefix in TitleParser.PREFIXES:
        for title in TitleParser.COMMON_TITLES:
            if not title.startswith(prefix + " "):
                candidates.add(f"{prefix} {title}")
    return sorted(candidates, key=lambda value: (len(value.split()), len(value)), reverse=True)


def _residual_segments(segments: List[str], consumed_texts: List[str]) -> List[str]:
    residuals = []
    for segment in segments:
        residual = segment
        for consumed in sorted(consumed_texts, key=len, reverse=True):
            residual = _remove_first(residual, consumed)
        residual = _clean_text(residual)
        if residual:
            residuals.append(residual)
    return residuals


def _pick_name_segment(segments: List[str]) -> Optional[Tuple[str, str, str]]:
    best_candidate = None
    best_score = 0

    for segment in segments:
        if EmailParser.parse(segment) or WebsiteParser.parse(segment) or PhoneParser.parse(segment):
            continue
        if _looks_like_company(segment):
            continue

        first_name, last_name = NameParser.parse(segment)
        if not _plausible_name(segment, first_name, last_name):
            continue

        score = 1
        if first_name:
            score += 1
        if last_name:
            score += 2
        if len(segment.split()) <= 3:
            score += 1

        if score > best_score:
            best_candidate = (first_name, last_name, segment)
            best_score = score

    return best_candidate


def _plausible_name(text: str, first_name: str, last_name: str) -> bool:
    if not first_name and not last_name:
        return False

    words = text.split()
    if not words or len(words) > 4:
        return False

    lowered = {word.lower().strip(".,") for word in words}
    if lowered & BUSINESS_TERMS:
        return False

    if any(char.isdigit() for char in text):
        return False

    return True


def _looks_like_company(text: str) -> bool:
    words = {word.lower().strip(".,") for word in text.split()}
    return bool(words & BUSINESS_TERMS)


def _company_from_residual(text: str, websites: List[str]) -> Optional[str]:
    residual = _clean_text(text).strip(" ,;|-")
    if not residual:
        return None

    if websites:
        for url in websites:
            domain = url.split("//")[-1].split("/")[0].lower()
            if residual.lower() in domain or domain in residual.lower():
                return residual

    return residual


def _split_name_company(text: str) -> Optional[Tuple[str, str, str]]:
    words = text.split()
    if len(words) < 3:
        return None

    business_index = None
    for index, word in enumerate(words):
        if word.lower().strip(".,") in BUSINESS_TERMS:
            business_index = index
            break

    if business_index is not None and business_index >= 3:
        company_start = max(2, business_index - 2)
        name_text = " ".join(words[:company_start])
        company_text = " ".join(words[company_start:])
    else:
        return None

    first_name, last_name = NameParser.parse(name_text)
    if _plausible_name(name_text, first_name, last_name) and len(company_text.split()) >= 2:
        return first_name, last_name, company_text
    return None


def _company_from_email(email: str) -> Optional[str]:
    if not email or "@" not in email:
        return None

    domain = email.split("@", 1)[1].lower()
    if domain in WEBMAIL_DOMAINS:
        return None

    return domain.split(".")[0].title()
