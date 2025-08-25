#!/usr/bin/env python3
# jodie/parsers/parsers.py
import re
from nameparser import HumanName

class BaseParser:
    """
    Base class for parsing text into specific contact properties.
    """

    def __init__(self):
        pass

    @staticmethod
    def find_matches(pattern, text):
        """
        Find all matches of a regex pattern in the given text.

        :param pattern: Regex pattern to match against the text.
        :param text: The text to search in.
        :return: A list of all matches.
        """
        return re.findall(pattern, text)

    @classmethod
    def parse(cls, text):
        """
        Parse the given text to extract information.
        This method should be implemented by subclasses.

        :param text: The text to parse.
        :return: Extracted information.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class EmailParser(BaseParser):
    @classmethod
    def parse(cls, text):
        """
        Extracts a single email from the text.
        Returns the first valid match or None.
        """
        email_pattern = r'<(\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b)>' \
                        r'|(\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b)'
        matches = cls.find_matches(email_pattern, text)
        for match in matches:
            # Return the first non-empty match
            if isinstance(match, tuple):
                return next((item for item in match if item), None)
            return match
        return None


class TitleParser(BaseParser):
    # Common job titles and their variations
    COMMON_TITLES = {
        # C-level
        "ceo", "cto", "cfo", "coo", "chief executive officer", "chief technology officer",
        "chief financial officer", "chief operating officer",
        
        # Founder/Leadership
        "founder", "co-founder", "cofounder", "president", "vice president", "vp",
        "director", "head", "lead", "principal",
        
        # Engineering
        "engineer", "developer", "architect", "scientist", "researcher",
        "software engineer", "senior engineer", "staff engineer", "full stack engineer",
        "senior full stack engineer", "senior software engineer",
        
        # Management
        "manager", "supervisor", "coordinator", "specialist", "analyst",
        "project manager", "product manager", "program manager",
        
        # Business
        "consultant", "advisor", "partner", "associate", "representative",
        "business development", "sales", "marketing",
        
        # Academic
        "professor", "lecturer", "researcher", "fellow", "scholar",
        
        # Creative
        "designer", "artist", "writer", "editor", "producer",
        
        # Other
        "intern", "assistant", "coordinator", "specialist"
    }

    # Acronyms that should stay uppercase
    ACRONYMS = {"CEO", "CTO", "CFO", "COO", "VP"}

    # Common title prefixes
    PREFIXES = {
        "senior", "lead", "principal", "staff", "associate", "junior",
        "full stack", "front end", "back end", "full-stack", "front-end", "back-end"
    }

    @classmethod
    def parse(cls, text):
        """
        Enhanced title parsing:
        - Standardizes capitalization for common titles
        - Handles variations and compound titles
        - Returns None for non-title text
        - Preserves acronym case (e.g., CEO stays as CEO)
        """
        if not isinstance(text, str) or not text.strip():
            return None

        # Normalize text for comparison
        cleaned_text = text.strip().lower()
        
        # Direct match against common titles
        if cleaned_text in cls.COMMON_TITLES:
            # Preserve original case for acronyms
            if text.upper() in cls.ACRONYMS:
                return text.upper()
            # Preserve original case for the entire title
            return text

        # Check for compound titles with prefixes
        words = cleaned_text.split()
        if len(words) >= 2:
            # First check if the entire phrase is a known title
            if cleaned_text in cls.COMMON_TITLES:
                return text
            
            # Then check for prefix + title combinations
            for i in range(len(words)):
                prefix = " ".join(words[:i+1])
                if prefix in cls.PREFIXES:
                    remaining = " ".join(words[i+1:])
                    if remaining in cls.COMMON_TITLES:
                        return text
            
            # Finally check if any part matches a known title
            for i in range(len(words)):
                for j in range(i + 1, len(words) + 1):
                    phrase = " ".join(words[i:j])
                    if phrase in cls.COMMON_TITLES:
                        return text

        return None


class WebsiteParser(BaseParser):
    @classmethod
    def parse(cls, text):
        # Match typical URL patterns
        url_pattern = r'https?://[^\s]+|www\.[^\s]+'
        urls = cls.find_matches(url_pattern, text)
        return urls[0] if urls else None


class PhoneParser(BaseParser):
    @classmethod
    def parse(cls, text):
        """
        Parse a phone number from the given text.
        Supports various phone number formats:
        - 10 digits: 5167763192
        - With country code: +15167763192, 15167763192
        - With separators: 516-776-3192, 516.776.3192, (516) 776-3192
        - International formats: +1 516 776 3192
        
        Returns the cleaned phone number or None if no valid phone found.
        """
        if not isinstance(text, str) or not text.strip():
            return None
            
        # Remove common non-digit characters for analysis
        digits_only = ''.join(ch for ch in text if ch.isdigit())
        
        # Various phone number patterns
        phone_patterns = [
            # US phone numbers with various formatting
            r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            # 10 digit number
            r'\b([0-9]{10})\b',
            # International format with country code
            r'\+?([0-9]{1,3})[-.\s]?([0-9]{3,4})[-.\s]?([0-9]{3,4})[-.\s]?([0-9]{3,4})\b'
        ]
        
        for pattern in phone_patterns:
            matches = cls.find_matches(pattern, text)
            if matches:
                # For tuple matches, join the groups
                if isinstance(matches[0], tuple):
                    # Remove empty groups and join
                    phone_digits = ''.join(group for group in matches[0] if group)
                else:
                    phone_digits = matches[0]
                
                # Validate phone number length
                if len(phone_digits) == 10:
                    # US phone number without country code
                    return phone_digits
                elif len(phone_digits) == 11 and phone_digits.startswith('1'):
                    # US phone number with country code
                    return phone_digits[1:]  # Return without country code
                elif 7 <= len(phone_digits) <= 15:
                    # International phone number
                    return phone_digits
        
        # Fallback: if we have exactly 10 or 11 digits, treat as phone
        if len(digits_only) == 10:
            return digits_only
        elif len(digits_only) == 11 and digits_only.startswith('1'):
            return digits_only[1:]
            
        return None


class NameParser(BaseParser):
    @classmethod
    def parse(cls, text):
        """
        Parse a name from the given text.
        - If an email is present in mailbox format, extract the portion before the email.
        - Use the `nameparser` package to parse the extracted name.

        :param text: The text to parse.
        :return: A tuple of (first_name, last_name).
        """
        # Check for email in the text.
        email = EmailParser.parse(text)
        if email:
            # Extract the portion of text before the email for name parsing.
            name_portion_index = text.find(email)
            name_portion = text[:name_portion_index].strip()
            name_portion = name_portion.rstrip('<').strip()
        else:
            # Use the entire text if no email is found.
            name_portion = text.strip()

        if not name_portion:
            return "", ""

        # Use the `HumanName` class to parse the name intelligently.
        name = HumanName(name_portion)

        # Return the first and last names as a tuple.
        return name.first, f"{name.middle} {name.last}".strip()
