#!/usr/bin/env python3
# jodie/cli/__main__.py
import sys
from docopt import docopt
from nameparser import HumanName
import jodie
from jodie.cli.__doc__ import __version__, __description__, __url__, __doc__

COMMANDS = ('new', 'parse',)
NOT_ARGS = ('--help', '--version', '--auto')

def detect_argument_mode(args):
    """
    Determines the mode based on provided arguments:
    - "auto": if --auto is specified.
    - "named": if named arguments are provided.
    - "positional": if positional arguments are used.
    """
    if args['--auto']:
        return "auto"
    if any(args.get(arg) for arg in NOT_ARGS if arg != '--auto'):
        return "positional"
    
    named_options = {}
    for key in args.keys():
        if key.startswith('--') and key not in NOT_ARGS:
            named_options[key] = args[key]

    if any(named_options.values()):
        return "named" 
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

    # First pass: identify all fields that can be unambiguously determined
    for arg in arguments:
        # 1. Email Address - Strong, unambiguous signal
        if not detected_fields["email"]:
            email = jodie.parsers.EmailParser.parse(arg)
            if email:
                detected_fields["email"] = email
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
            continue

        # 3. Job Title - Common patterns, after ruling out email/URL
        if not detected_fields["job_title"]:
            title = jodie.parsers.TitleParser.parse(arg)
            if title:
                detected_fields["job_title"] = title
                continue

        # 4. Phone Number - Look for phone patterns
        if not detected_fields["phone"]:
            phone = jodie.parsers.PhoneParser.parse(arg)
            if phone:
                detected_fields["phone"] = phone
                continue

        # 5. Person Name - Often ambiguous without context
        if not detected_fields["first_name"]:
            first_name, last_name = jodie.parsers.NameParser.parse(arg)
            if first_name or last_name:
                detected_fields["first_name"] = first_name
                detected_fields["last_name"] = last_name
                continue

    # Second pass: handle company name and any remaining fields
    for arg in arguments:
        # Skip if this argument was already used
        if (arg == detected_fields["email"] or
            arg in detected_fields["websites"] or
            arg == detected_fields["job_title"] or
            arg == detected_fields["phone"] or
            arg == f"{detected_fields['first_name']} {detected_fields['last_name']}".strip()):
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

    return detected_fields


def main():
    first, last, email, phone, title, company, websites, note = (None,) * 8

    args = docopt(__doc__, version=__version__)
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
            websites = fields.get('websites')  # This is already a list from parse_auto
            note = fields.get('note')

    if mode == "positional":
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
        note = args.get('NOTE')

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
            note = args.get('--note') or args.get('--notes')

        except Exception as e:
            sys.stderr.write(f"Error processing named arguments: {str(e)}\n")
            sys.exit(1)

    c = jodie.contact.Contact(
        first_name=first,
        last_name=last,
        email=email,
        phone=phone,
        job_title=title,
        company=company,
        websites=websites
        # note=note
    )

    sys.stdout.write(f'Saving...\n{c}\n')
    status = 0 if c.save() else 1
    sys.exit(status)


if __name__ == "__main__":
    main()
