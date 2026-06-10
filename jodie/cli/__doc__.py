#!/usr/bin/env python3
# jodie/cli/__doc__.py
"""jodie - Manage macOS Contacts.app from command line!

Usage:
    jodie new TEXT... [options]
    jodie new [options]
    jodie new --paste [options]
    jodie new --stdin [options]
    jodie new --explicit EMAIL NAME [COMPANY] [TITLE] [options]

Arguments:
    TEXT                                Contact text to parse automatically.
    EMAIL                               Email address for explicit positional mode.
    NAME                                Full name for explicit positional mode.
    COMPANY                             Company name for explicit positional mode.
    TITLE                               Job title for explicit positional mode.

Input Modes:
    --paste                             Read contact text from clipboard.
    --stdin                             Read contact text from stdin.
    --explicit                          Use positional fields: EMAIL NAME [COMPANY] [TITLE].
    -A --auto                           Force automatic parsing. Default for TEXT input.

Contact Fields:
    -E EMAIL --email=EMAIL              Email address.
    -F FIRST --first=FIRST              First name.
    --first-name=FIRST                  First name (alias for --first).
    --firstname=FIRST                   First name (alias for --first).
    -L LAST --last=LAST                 Last name.
    --last-name=LAST                    Last name (alias for --last).
    --lastname=LAST                     Last name (alias for --last).
    -U NAME --full-name=NAME            Full name.
    --name=NAME                         Full name (alias for --full-name).
    -P PHONE --phone=PHONE              Phone number.
    -T TITLE --title=TITLE              Job title.
    -C COMPANY --company=COMPANY        Company name.
    -W WEBSITES --websites=WEBSITES     Comma-separated list of websites/URLs.
    --website=WEBSITES                  Website URLs (alias for --websites).
    --linkedin=URL                      LinkedIn profile URL (auto-labeled as LinkedIn).

Output:
    -D --dry-run                        Preview parsed fields without saving.

General:
    -H --help                           Show this screen.
    -V --version                        Show version.

"""

__version__     = '0.1.2'
__title__       = "jodie"
__license__     = "MIT"
__description__ = "Jodie lets you add contacts to Contacts.app on macOS from command line"
__keywords__    = "macOS Contacts.app Contact management Contacts command line tool CLI"
__author__      = "austin"
__email__       = "tips@cia.lol"
__url__         = "https://github.com/austinogilvie/jodie"


__all__ = ['__version__', '__description__', '__url__', '__doc__']
