#!/usr/bin/env python3
# jodie/contact/contact.py
from datetime import datetime
from typing import Optional, Set, List, Any, Union, Dict
import objc
from Contacts import (CNMutableContact, CNContactStore, CNSaveRequest, CNLabeledValue,
                      CNPhoneNumber, CNLabelURLAddressHomePage)
from Foundation import NSCalendar, NSDateComponents


def get_label_for_email(email: str) -> str:
    """
    Determine the label for an email address based on its domain.

    Args:
        email (str): The email address to analyze.

    Returns:
        str: "work" if the email domain is neither a common webmail provider nor an educational institution (.edu),
             otherwise "home".
    """
    webmail_providers: Set[str] = {
        "gmail.com", "googlemail.com", "aol.com", "yahoo.com",
        "hotmail.co.uk", "hotmail.com", "hotmail.de", "hotmail.es",
        "hotmail.fr", "hotmail.it", "hushmail.com", "protonmail.com",
        "hey.com", "icloud.com", "mac.com", "qq.com", "tuta.com",
        "tutanota.com", "verizon.net", "ymail.com"
    }

    # Extract the email's domain
    email_domain: str = email.split('@')[-1] if email else ""

    # Check domain against webmail providers and education domains (.edu)
    if email_domain not in webmail_providers and not email_domain.endswith('.edu'):
        return "work"
    else:
        return "home"


def get_human_friendly_label(label: str) -> str:
    """
    Convert Apple Contacts framework label constants to human-friendly names.
    
    Args:
        label (str): The label constant from Apple Contacts framework
        
    Returns:
        str: A human-friendly label name
    """
    # Map Apple constants to friendly names
    label_map = {
        CNLabelURLAddressHomePage: "Website",
        "work": "Work",
        "home": "Home", 
        "LinkedIn": "LinkedIn",
        "GitHub": "GitHub",
        "Twitter": "Twitter",
        "Instagram": "Instagram", 
        "Facebook": "Facebook",
        "Calendar": "Calendar"
    }
    
    return label_map.get(label, label)


def get_label_for_website(url: str, email: Optional[str] = None, company: Optional[str] = None) -> str:
    """
    Determine the appropriate label for a website URL based on its domain, email, and company information.

    Args:
        url (str): The website URL to analyze.
        email (str, optional): The contact's email address to check for domain matching.
        company (str, optional): The contact's company name to check for domain matching.

    Returns:
        str: A label constant from Contacts framework (CNLabelURLAddress*) or a custom label string.
    """
    # Common professional/social networks
    professional_domains = {
        'linkedin.com': 'LinkedIn',
        'github.com': 'GitHub',
        'twitter.com': 'Twitter',
        'instagram.com': 'Instagram',
        'facebook.com': 'Facebook',
    }

    # Common calendar/scheduling domains
    calendar_domains = {
        'calendly.com': 'Calendar',
        'meet.google.com': 'Calendar',
        'zoom.us': 'Calendar',
    }

    # Extract the domain from the URL
    try:
        # Remove protocol and www if present
        domain = url.lower().replace('https://', '').replace('http://', '').replace('www.', '')
        # Get the domain part
        domain = domain.split('/')[0]
    except:
        # If URL parsing fails, default to homepage
        return CNLabelURLAddressHomePage

    # Rule 1: Check against known professional/social networks
    for known_domain, label in professional_domains.items():
        if known_domain in domain:
            return label

    # Rule 2: Check against known calendar domains
    for known_domain, label in calendar_domains.items():
        if known_domain in domain:
            return label

    # Rule 3: If email is work and domains match, set website to work
    if email:
        email_domain = email.split('@')[-1].lower()
        if get_label_for_email(email) == "work" and email_domain in domain:
            return "Work"

    # Rule 4: If email is home/webmail and company name exists, check for company name in domain
    if email and company and get_label_for_email(email) == "home":
        # Split company name into words and check if any appear in domain
        company_words = company.lower().split()
        if any(word in domain for word in company_words):
            return "Work"

    # Rule 5: Fallback to homepage
    return CNLabelURLAddressHomePage


class WebsiteLabeledValue(CNLabeledValue):
    """Wrapper for CNLabeledValue that provides a better string representation and additional functionality."""
    
    def __repr__(self) -> str:
        return f"Website(label={self.label()!r}, url={self.value()!r})"
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to a dictionary representation."""
        return {"label": self.label(), "url": self.value()}


class Contact:
    """
    Simple wrapper for Apple iOS / macOS Contact record.
    Provides a Pythonic interface to interact with Apple's Contacts framework.
    """

    def __init__(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        job_title: Optional[str] = None,
        company: Optional[str] = None,
        websites: Optional[Union[str, List[str], List[Dict[str, str]], List[CNLabeledValue]]] = None,
        note: Optional[str] = None
    ) -> None:
        """
        Initialize a Contact object with optional parameters for various contact fields.
        Empty or whitespace-only values will be treated as None and not set.

        Args:
            first_name: First name of the contact
            last_name: Last name of the contact
            email: Email address of the contact
            phone: Phone number of the contact
            job_title: Job title of the contact
            company: Company name of the contact
            websites: Website URL(s) of the contact
            note: Additional notes for the contact
        """
        self.contact: CNMutableContact = CNMutableContact.alloc().init()
        
        # Convert empty strings to None
        self.first_name = first_name if first_name and first_name.strip() else None
        self.last_name = last_name if last_name and last_name.strip() else None
        self.email = email
        self.phone = phone
        self.job_title = job_title if job_title and job_title.strip() else None
        self.company = company
        self.websites = websites
        self.note = note

        # Apple Contacts.app doesnt display created date by default
        # save the created date in a custom field
        self._created_date: datetime = datetime.now()
        self._set_creation_date()

    def _set_creation_date(self) -> None:
        """
        Set the creation date for the contact using the current date and store it as a custom date field.
        """
        dateComponents: NSDateComponents = NSDateComponents.alloc().init()
        dateComponents.setYear_(self._created_date.year)
        dateComponents.setMonth_(self._created_date.month)
        dateComponents.setDay_(self._created_date.day)
        customDateValue: CNLabeledValue = CNLabeledValue.alloc().initWithLabel_value_(
            "created_date", dateComponents)
        self.contact.setDates_([customDateValue])

    def save(self) -> 'Contact':
        """
        Validate required fields and try to save to Contacts.app / Apple Address Book.

        Returns:
            Contact: The saved contact instance

        Raises:
            ValueError: If required fields (first name, last name, and either email or phone) are missing
            Exception: If the save operation fails
        """
        # Check that we have first name, last name, and at least one contact method (email or phone)
        has_first_name = bool(self.contact.givenName())
        has_last_name = bool(self.contact.familyName())
        has_email = bool(self.contact.emailAddresses())
        has_phone = bool(self.contact.phoneNumbers())
        
        if not (has_first_name and has_last_name and (has_email or has_phone)):
            raise ValueError(
                "Missing required fields. First name, last name, and at least one contact method (email or phone) are required.")

        store: CNContactStore = CNContactStore.alloc().init()
        request: CNSaveRequest = CNSaveRequest.alloc().init()
        request.addContact_toContainerWithIdentifier_(self.contact, None)

        error: Any = objc.nil
        success, error = store.executeSaveRequest_error_(request, None)
        if not success:
            raise Exception(f"Failed to save contact: {error}")
        return self

    def __str__(self) -> str:
        """String representation of the contact, showing only set fields."""
        fields = []
        
        # Name
        name_parts = []
        if self.first_name:
            name_parts.append(self.first_name)
        if self.last_name:
            name_parts.append(self.last_name)
        fields.append(f"Contact: {' '.join(name_parts)}" if name_parts else "Contact: Unknown")
        
        # Email
        fields.append(f"Email: {self.email}" if self.email else "Email: None")
        
        # Phone
        fields.append(f"Phone: {self.phone}" if self.phone else "Phone: None")
        
        # Job Title
        fields.append(f"Job Title: {self.job_title}" if self.job_title else "Job Title: None")
        
        # Company
        fields.append(f"Company: {self.company}" if self.company else "Company: None")
        
        # Websites
        if self.websites:
            website_str = ", ".join(f"{get_human_friendly_label(site.label())}: {site.value()}" for site in self.websites)
            fields.append(f"Websites: {website_str}")
        else:
            fields.append("Websites: None")
            
        return ", ".join(fields)

    def __repr__(self) -> str:
        websites = self.websites
        if websites:
            website_repr = f"[{', '.join(f'{get_human_friendly_label(site.label())}: {site.value()}' for site in websites)}]"
        else:
            website_repr = "None"
        return (f"{self.__class__.__name__}(first_name={self.first_name!r}, "
                f"last_name={self.last_name!r}, email={self.email!r}, "
                f"phone={self.phone!r}, job_title={self.job_title!r}, "
                f"company={self.company!r}, websites={website_repr})")

    @property
    def first_name(self) -> Optional[str]:
        """Get the contact's first name."""
        val = self.contact.givenName()
        return val.strip() if val and val.strip() else None

    @property
    def last_name(self) -> Optional[str]:
        """Get the contact's last name."""
        val = self.contact.familyName()
        return val.strip() if val and val.strip() else None

    @property
    def email(self) -> Optional[str]:
        """Get the contact's primary email address."""
        emailAddresses: List[CNLabeledValue] = self.contact.emailAddresses()
        return emailAddresses[0].value() if emailAddresses else None

    @email.setter
    def email(self, value: Optional[str]) -> None:
        if not value or not value.strip():
            self.contact.setEmailAddresses_([])
            return
        email_label = get_label_for_email(value)
        emailValue = CNLabeledValue.alloc().initWithLabel_value_(
            email_label, value.strip().lower())
        self.contact.setEmailAddresses_([emailValue])

    @property
    def phone(self) -> Optional[str]:
        """Get the contact's primary phone number."""
        phoneNumbers: List[CNLabeledValue] = self.contact.phoneNumbers()
        return phoneNumbers[0].value().stringValue() if phoneNumbers else None

    @phone.setter
    def phone(self, value: Optional[str]) -> None:
        if not value or not value.strip():
            self.contact.setPhoneNumbers_([])
            return
        cleaned_number = ''.join(ch for ch in value if ch.isdigit() or ch == '+')
        phone_number = CNPhoneNumber.phoneNumberWithStringValue_(cleaned_number)
        phone_label_value = CNLabeledValue.alloc().initWithLabel_value_(
            "mobile", phone_number)
        self.contact.setPhoneNumbers_([phone_label_value])

    @property
    def job_title(self) -> Optional[str]:
        """Get the contact's job title."""
        val = self.contact.jobTitle()
        return val.strip() if val and val.strip() else None

    @property
    def company(self) -> Optional[str]:
        """Get the contact's company name."""
        val = self.contact.organizationName()
        return val.strip() if val and val.strip() else None

    @company.setter
    def company(self, value: Optional[str]) -> None:
        if not value or not value.strip():
            self.contact.setOrganizationName_(None)
            return
        self.contact.setOrganizationName_(value.strip())

    @property
    def websites(self) -> Optional[List[WebsiteLabeledValue]]:
        """Get all websites as a list of WebsiteLabeledValue objects."""
        urlAddresses: List[CNLabeledValue] = self.contact.urlAddresses()
        if not urlAddresses:
            return None
        return [WebsiteLabeledValue.alloc().initWithLabel_value_(site.label(), site.value()) for site in urlAddresses]

    @websites.setter
    def websites(self, value: Union[str, List[str], List[Dict[str, str]], List[CNLabeledValue]]) -> None:
        """Set websites. Can handle:
        - Single URL string
        - List of URL strings
        - List of dicts with 'label' and 'url' keys
        - List of CNLabeledValue objects
        """
        if not value:
            self.contact.setUrlAddresses_([])
            return

        # Convert to list of WebsiteLabeledValue objects
        if isinstance(value, str):
            label = get_label_for_website(value, self.email, self.company)
            value = [WebsiteLabeledValue.alloc().initWithLabel_value_(label, value.strip().lower())]
        elif isinstance(value, list):
            if not value:
                self.contact.setUrlAddresses_([])
                return
                
            if isinstance(value[0], str):
                # List of strings
                url_values = []
                for url in value:
                    label = get_label_for_website(url, self.email, self.company)
                    url_value = WebsiteLabeledValue.alloc().initWithLabel_value_(
                        label, url.strip().lower())
                    url_values.append(url_value)
                value = url_values
            elif isinstance(value[0], dict):
                # List of dicts
                url_values = []
                for item in value:
                    url = item["url"]
                    label = item.get("label") or get_label_for_website(url, self.email, self.company)
                    url_value = WebsiteLabeledValue.alloc().initWithLabel_value_(
                        label, url.strip().lower())
                    url_values.append(url_value)
                value = url_values
            elif isinstance(value[0], CNLabeledValue):
                # Convert existing CNLabeledValue objects to WebsiteLabeledValue
                url_values = []
                for site in value:
                    url_value = WebsiteLabeledValue.alloc().initWithLabel_value_(
                        site.label(), site.value())
                    url_values.append(url_value)
                value = url_values

        self.contact.setUrlAddresses_(value)

    def add_website(self, url: str, label: Optional[str] = None) -> None:
        """Add a single website with optional label."""
        current = self.websites or []
        if not label:
            label = get_label_for_website(url, self.email, self.company)
        websiteValue = WebsiteLabeledValue.alloc().initWithLabel_value_(
            label, url.strip().lower())
        current.append(websiteValue)
        self.contact.setUrlAddresses_(current)

    def get_website(self, label: str) -> Optional[str]:
        """Get a specific website by its label."""
        websites = self.websites
        if not websites:
            return None
        for site in websites:
            if site.label() == label:
                return site.value()
        return None

    # Convenience properties for common website types
    @property
    def linkedin(self) -> Optional[str]:
        return self.get_website("LinkedIn")

    @property
    def work_website(self) -> Optional[str]:
        return self.get_website("Work")

    @property
    def home_website(self) -> Optional[str]:
        return self.get_website(CNLabelURLAddressHomePage)

    @property
    def note(self) -> Optional[str]:
        """Get the contact's notes.
        
        Note:
            This functionality is currently broken due to Apple entitlements requirements.
        """
        return self.contact.note()

    @note.setter
    def note(self, value: Optional[str]) -> None:
        """Set the contact's notes.
        
        Note:
            This functionality is currently broken due to Apple entitlements requirements.
        """
        if not value or not value.strip():
            self.contact.setNote_(None)
            return
        self.contact.setNote_(value.strip())

    def __dict__(self) -> dict:
        """
        Return a dictionary representation of the contact.
        
        Returns:
            dict: A dictionary containing all contact fields and their values.
                 Empty fields are returned as None.
                 Created date is formatted as YYYY-MM-DD.
        """
        def get_value_or_none(value):
            if value is None:
                return None
            if isinstance(value, str):
                return value if value.strip() else None
            if isinstance(value, list):
                return [item.to_dict() for item in value] if value else None
            return value

        return {
            'first_name': get_value_or_none(self.first_name),
            'last_name': get_value_or_none(self.last_name),
            'email': get_value_or_none(self.email),
            'phone': get_value_or_none(self.phone),
            'job_title': get_value_or_none(self.job_title),
            'company': get_value_or_none(self.company),
            'websites': get_value_or_none(self.websites),
            'note': get_value_or_none(self.note),
            'created_date': self._created_date.strftime('%Y-%m-%d')
        }

    def tojson(self) -> dict:
        """
        Return a JSON-serializable dictionary representation of the contact.
        
        Returns:
            dict: A dictionary containing all contact fields and their values,
                  with datetime objects converted to ISO format strings.
        """
        return self.__dict__()

    @first_name.setter
    def first_name(self, value: Optional[str]) -> None:
        """Set first name."""
        if not value or not value.strip():
            value = None
        self.contact.setGivenName_(value)

    @last_name.setter
    def last_name(self, value: Optional[str]) -> None:
        """Set last name."""
        if not value or not value.strip():
            value = None
        self.contact.setFamilyName_(value)

    @job_title.setter
    def job_title(self, value: Optional[str]) -> None:
        """Set job title."""
        if not value or not value.strip():
            value = None
        self.contact.setJobTitle_(value)

def test_website_labels():
    test_cases = [
        # Social/Professional Networks
        ("https://linkedin.com/in/johndoe", None, None, "LinkedIn"),
        ("https://github.com/johndoe", None, None, "GitHub"),
        ("https://twitter.com/johndoe", None, None, "Twitter"),

        # Calendar Links
        ("https://calendly.com/johndoe", None, None, "Calendar"),
        ("https://meet.google.com/abc-xyz", None, None, "Calendar"),

        # Work Email Domain Match
        ("https://acme.com", "john@acme.com", None, "Work"),  # work email
        ("https://acme.com", "john@gmail.com", None, CNLabelURLAddressHomePage),  # personal email

        # Company Name Match
        ("https://acme-corp.com", "john@gmail.com", "Acme Corp", "Work"),  # company name in domain
        ("https://acme.com", "john@gmail.com", "Acme Corp", "Work"),  # company name in domain
        ("https://other.com", "john@gmail.com", "Acme Corp", CNLabelURLAddressHomePage),  # no match

        # Multiple URLs for same contact
        ("https://acme.com", "john@acme.com", "Acme Corp", "Work"),  # work website
        ("https://linkedin.com/in/johndoe", "john@acme.com", "Acme Corp", "LinkedIn"),  # LinkedIn profile

        # Edge Cases
        ("invalid-url", None, None, CNLabelURLAddressHomePage),  # invalid URL
        ("", None, None, CNLabelURLAddressHomePage),  # empty URL
        (None, None, None, CNLabelURLAddressHomePage),  # None URL
    ]

    print("Testing website label determination:")
    print("-" * 80)

    for url, email, company, expected in test_cases:
        result = get_label_for_website(url, email, company)
        status = "✓" if result == expected else "✗"
        print(f"{status} URL: {url}")
        print(f"   Email: {email}")
        print(f"   Company: {company}")
        print(f"   Expected: {expected}")
        print(f"   Got: {result}")
        print("-" * 80)

    # Test __dict__ and tojson methods
    print("\nTesting Contact.__dict__ and Contact.tojson methods:")
    print("-" * 80)

    # Test case 1: Complete contact information
    contact1 = Contact(
        first_name="John",
        last_name="Doe",
        email="john@acme.com",
        phone="+1-555-123-4567",
        job_title="Software Engineer",
        company="Acme Corp",
        websites="https://acme.com",
        note="Met at conference"
    )
    
    # Test case 2: Minimal contact information
    contact2 = Contact(
        first_name="Jane",
        last_name="Smith",
        email="jane@gmail.com"
    )

    test_contacts = [
        ("Complete Contact", contact1),
        ("Minimal Contact", contact2)
    ]

    for name, contact in test_contacts:
        print(f"\nTesting {name}:")
        print("-" * 40)
        
        # Test __dict__ method
        contact_dict = contact.__dict__()
        print("__dict__() result:")
        for key, value in contact_dict.items():
            print(f"  {key}: {value}")
        
        # Test tojson method
        contact_json = contact.tojson()
        print("\ntojson() result:")
        for key, value in contact_json.items():
            print(f"  {key}: {value}")
        
        # Verify both methods return the same data
        assert contact_dict == contact_json, f"__dict__ and tojson returned different results for {name}"
        print("\n✓ __dict__ and tojson results match")
        
        # Verify all values are JSON-serializable
        import json
        try:
            json.dumps(contact_json)
            print("✓ JSON serialization successful")
        except (TypeError, ValueError) as e:
            print(f"✗ JSON serialization failed: {e}")
        
        print("-" * 40)
