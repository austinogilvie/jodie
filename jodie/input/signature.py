import re
from typing import List

class SignaturePreprocessor:
    """Preprocess email signatures before parsing."""

    # Noise patterns to filter out
    NOISE_PATTERNS = [
        r'^>.*$',           # Quoted replies
        r'^On .* wrote:$',  # Forwarded headers
        r'^-+\s*Original Message\s*-+$',
        r'^From:.*$',
        r'^Sent:.*$',
        r'^To:.*$',
        r'^Subject:.*$',
    ]

    # Pronouns to strip from names
    PRONOUNS = r'\s*\([^)]*(?:he|she|they|him|her|them)[^)]*\)\s*'

    # Common separators
    SEPARATORS = r'[•·|–—]'

    @classmethod
    def preprocess(cls, text: str) -> List[str]:
        """Clean and split signature text into parseable tokens."""
        if not text:
            return []

        lines = []
        for line in text.strip().split('\n'):
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Skip noise patterns
            skip = False
            for pattern in cls.NOISE_PATTERNS:
                if re.match(pattern, line, re.IGNORECASE):
                    skip = True
                    break
            if skip:
                continue

            # Strip pronouns
            line = re.sub(cls.PRONOUNS, '', line, flags=re.IGNORECASE)

            # Split by common separators
            parts = re.split(cls.SEPARATORS, line)
            for part in parts:
                part = part.strip()
                if part:
                    lines.append(part)

        return lines
