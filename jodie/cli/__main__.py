#!/usr/bin/env python3
# jodie/cli/__main__.py
import sys
from docopt import docopt
from nameparser import HumanName
import jodie
from jodie.cli.__doc__ import __version__, __description__, __url__, __doc__

COMMANDS = ('new', 'parse',)
UTILITY_FLAGS = ('--auto', '--explicit', '--help', '--version', '--dry-run', '--paste', '--stdin')

def detect_argument_mode(args):
    """
    Mode priority:
    1. --explicit -> positional (strict order)
    2. Named flags -> named mode
    3. TEXT arguments -> auto (default)
    """
    # --explicit forces positional mode
    if args.get('--explicit'):
        return "positional"

    # Check for named options (excluding utility flags)
    named_options = {k: v for k, v in args.items()
                     if k.startswith('--') and k not in UTILITY_FLAGS}

    if any(named_options.values()):
        return "named"

    # Default: bare args -> auto-parse
    if args.get('TEXT'):
        return "auto"

    return "positional"

def parse_auto(arguments):
    detected_fields = {
        "first_name": None,
        "last_name": None,
        "email": None,
        "phone": None,
        "job_title": None,
        "company": None,
        "websites": [],
        "note": None
    }

    # Track which arguments were consumed (by original text)
    consumed_args = set()

    # First pass: identify all fields that can be unambiguously determined
    for arg in arguments:
        # 1. Email Address - Strong, unambiguous signal
        if not detected_fields["email"]:
            email = jodie.parsers.EmailParser.parse(arg)
            if email:
                detected_fields["email"] = email
                consumed_args.add(arg)
                # Infer name from mailbox format if name is not already set
                if not detected_fields["first_name"]:
                    first_name, last_name = jodie.parsers.NameParser.parse(arg)
                    if first_name or last_name:
                        detected_fields["first_name"] = first_name
                        detected_fields["last_name"] = last_name
                continue

        # 2. Website URL - High-confidence markers
        website = jodie.parsers.WebsiteParser.parse(arg)
        if website:
            if not detected_fields["websites"]:
                detected_fields["websites"] = []
            detected_fields["websites"].append(website)
            consumed_args.add(arg)
            continue

        # 3. Job Title - Common patterns, after ruling out email/URL
        if not detected_fields["job_title"]:
            title = jodie.parsers.TitleParser.parse(arg)
            if title:
                detected_fields["job_title"] = title
                consumed_args.add(arg)
                continue

        # 4. Phone Number - Look for phone patterns
        if not detected_fields["phone"]:
            phone = jodie.parsers.PhoneParser.parse(arg)
            if phone:
                detected_fields["phone"] = phone
                consumed_args.add(arg)
                continue

        # 5. Person Name - Often ambiguous without context
        if not detected_fields["first_name"]:
            first_name, last_name = jodie.parsers.NameParser.parse(arg)
            if first_name or last_name:
                detected_fields["first_name"] = first_name
                detected_fields["last_name"] = last_name
                consumed_args.add(arg)
                continue

    # Second pass: handle company name and any remaining fields
    for arg in arguments:
        # Skip if this argument was already consumed
        if arg in consumed_args:
            continue

        # 6. Company Name - Most ambiguous, use as fallback
        if not detected_fields["company"]:
            # Check for business-related terms
            if any(term in arg.lower() for term in ["inc", "llc", "ltd", "corp", "co"]):
                detected_fields["company"] = arg.strip()
                continue
            
            # Check if this matches any of the collected website domains
            if detected_fields["websites"]:
                for url in detected_fields["websites"]:
                    domain = url.split("//")[-1].split("/")[0].lower()
                    if arg.lower() in domain or domain in arg.lower():
                        detected_fields["company"] = arg.strip()
                        break
            if detected_fields["company"]:
                continue

            # If we get here and still don't have a company, this might be the company name
            if not detected_fields["company"]:
                detected_fields["company"] = arg.strip()

    # Infer company from email domain if not found
    if not detected_fields["company"] and detected_fields["email"]:
        email = detected_fields["email"]
        if "@" in email:
            domain = email.split("@")[1].lower()
            # Skip common webmail domains
            webmail = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
                       "icloud.com", "aol.com", "protonmail.com", "hey.com"}
            if domain not in webmail:
                # Extract company name from domain (e.g., "example.org" -> "Thirdprime")
                company_name = domain.split(".")[0].title()
                detected_fields["company"] = company_name

    return detected_fields


def main():
    first, last, email, phone, title, company, websites, note = (None,) * 8

    args = docopt(__doc__, version=__version__)

    # Handle --paste: read from clipboard and parse
    if args.get('--paste'):
        from jodie.input import read_clipboard, SignaturePreprocessor
        text = read_clipboard()
        preprocessed = SignaturePreprocessor.preprocess(text)
        fields = parse_auto(preprocessed)
        if fields:
            if fields.get('first_name'):
                human_name = HumanName(f"{fields['first_name']} {fields['last_name']}".strip())
                if human_name:
                    first, last = human_name.first, human_name.last
            email = fields.get('email')
            phone = fields.get('phone')
            title = fields.get('job_title')
            company = fields.get('company')
            websites = fields.get('websites')
        # Apply explicit overrides from command line
        # TODO: Notes disabled pending AppleScript refactor (ISS-000012)
        # note = args.get('--note') or args.get('--notes')
        if args.get('--company'):
            company = args.get('--company')

    # Handle --stdin: read from stdin and parse
    elif args.get('--stdin'):
        from jodie.input import read_stdin, SignaturePreprocessor
        text = read_stdin()
        preprocessed = SignaturePreprocessor.preprocess(text)
        fields = parse_auto(preprocessed)
        if fields:
            if fields.get('first_name'):
                human_name = HumanName(f"{fields['first_name']} {fields['last_name']}".strip())
                if human_name:
                    first, last = human_name.first, human_name.last
            email = fields.get('email')
            phone = fields.get('phone')
            title = fields.get('job_title')
            company = fields.get('company')
            websites = fields.get('websites')
        # Apply explicit overrides from command line
        # TODO: Notes disabled pending AppleScript refactor (ISS-000012)
        # note = args.get('--note') or args.get('--notes')
        if args.get('--company'):
            company = args.get('--company')

    else:
        # Standard mode detection for non-paste/stdin
        mode = detect_argument_mode(args)

        if mode == "auto":
            fields = parse_auto(args['TEXT'])
            if fields:
                if fields.get('first_name'):
                    human_name = HumanName(f"{fields['first_name']} {fields['last_name']}".strip())
                    if human_name:
                        first, last = human_name.first, human_name.last

                email = fields.get('email')
                phone = fields.get('phone')
                title = fields.get('job_title')
                company = fields.get('company')
                websites = fields.get('websites')
                # TODO: Notes disabled pending AppleScript refactor (ISS-000012)
                # note = fields.get('note')

        elif mode == "positional":
            try:
                full_name = args['NAME']
                first, last = jodie.parsers.NameParser.parse(full_name)
                email = jodie.parsers.EmailParser.parse(args['EMAIL'])
            except Exception as e:
                sys.stderr.write(
                    f"Error processing positional arguments: {str(e)}\n")
                sys.exit(1)
            company = args.get('COMPANY')
            title = args.get('TITLE')
            # TODO: Notes disabled pending AppleScript refactor (ISS-000012)
            # note = args.get('NOTE')

        elif mode == "named":
            try:
                # Handle first name aliases: --first, --first-name, --firstname
                first = args.get('--first') or args.get('--first-name') or args.get('--firstname')
                # Handle last name aliases: --last, --last-name, --lastname
                last = args.get('--last') or args.get('--last-name') or args.get('--lastname')
                # Handle full name aliases: --full-name, --name
                full = args.get('--full-name') or args.get('--name')
                if full:
                    parts = full.split()
                    if first is None:
                        first = parts[0].strip()
                    if last is None:
                        last = ' '.join(parts[1:]).strip()
                email = args.get('--email')
                phone = args.get('--phone')
                title = args.get('--title')
                company = args.get('--company')
                # Handle websites aliases: --websites, --website
                websites = args.get('--websites') or args.get('--website')
                if websites and isinstance(websites, str):
                    # Only split if it's a string (from command line)
                    websites = [url.strip() for url in websites.split(',')]
                # Handle --linkedin specially (adds with LinkedIn label)
                linkedin_url = args.get('--linkedin')
                if linkedin_url:
                    if websites is None:
                        websites = []
                    elif isinstance(websites, str):
                        websites = [websites]
                    websites.append({'url': linkedin_url, 'label': 'LinkedIn'})
                # Handle note aliases: --note, --notes
                # TODO: Notes disabled pending AppleScript refactor (ISS-000012)
                # note = args.get('--note') or args.get('--notes')

            except Exception as e:
                sys.stderr.write(f"Error processing named arguments: {str(e)}\n")
                sys.exit(1)

    # Handle dry-run preview
    if args.get('--dry-run'):
        from jodie.cli.preview import format_preview
        fields = {
            'first_name': first,
            'last_name': last,
            'email': email,
            'phone': phone,
            'job_title': title,
            'company': company,
            'websites': websites,
            'note': note
        }
        preview = format_preview(fields)
        sys.stdout.write(preview + "\n")
        sys.exit(0)

    c = jodie.contact.Contact(
        first_name=first,
        last_name=last,
        email=email,
        phone=phone,
        job_title=title,
        company=company,
        websites=websites,
        note=note
    )

    sys.stdout.write(f'Saving...\n{c}\n')
    status = 0 if c.save() else 1
    sys.exit(status)


if __name__ == "__main__":
    main()
