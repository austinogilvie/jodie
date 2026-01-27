#!/usr/bin/env python3
# jodie/cli/__doc__.py
"""jodie - Manage macOS Contacts.app from command line!

Usage:
    jodie new TEXT... [options]
    jodie new [options]
    jodie new --auto TEXT... [options]
    jodie new --paste [options]
    jodie new --stdin [options]
    jodie new --explicit EMAIL NAME [COMPANY] [TITLE] [NOTE...]
    jodie parse [options] TEXT

Arguments:
    TEXT                                Text for jodie to parse intelligently (default mode).
    EMAIL                               Email address (used with --explicit).
    NAME                                Full name (used with --explicit).
    COMPANY                             Company name (used with --explicit).
    TITLE                               Job title (used with --explicit).
    NOTE                                Note text (used with --explicit).

Options:
    --explicit                          Use strict positional parsing (EMAIL NAME COMPANY TITLE NOTE).
    -A --auto                           Smart parsing mode (default, kept for backward compatibility).
    -C COMPANY --company=COMPANY        Company name.
    -E EMAIL --email=EMAIL              Email.
    -F FIRST --first=FIRST              First name.
    --first-name=FIRST                  First name (alias for --first).
    --firstname=FIRST                   First name (alias for --first).
    -L LAST --last=LAST                 Last name.
    --last-name=LAST                    Last name (alias for --last).
    --lastname=LAST                     Last name (alias for --last).
    -U NAME --full-name=NAME            Full name.
    --name=NAME                         Full name (alias for --full-name).
    -N NOTE --note=NOTE                 Any text you want to save in the `Note` field in Contacts.app.
    --notes=NOTE                        Note text (alias for --note).
    -P PHONE --phone=PHONE              Phone.
    -T TITLE --title=TITLE              Job title.
    -X TEXT  --text=TEXT                Text for jodie to try her best to parse semi-intelligently if she can.
    -W WEBSITES --websites=WEBSITES     Comma-separated list of websites/URLs.
    --website=WEBSITES                  Website URLs (alias for --websites).
    --linkedin=URL                      LinkedIn profile URL (auto-labeled as LinkedIn).
    -D --dry-run                        Preview parsed fields without saving.
    -H --help                           Show this screen.
    -V --version                        Show version.
    --paste                             Read input from clipboard (pbpaste).
    --stdin                             Read input from stdin (pipe/heredoc).

"""

__version__     = '0.1.0'
__title__       = "jodie"
__license__     = "MIT"
__description__ = "Jodie lets you add contacts to Contacts.app on macOS from command line"
__keywords__    = "macOS Contacts.app Contact management Contacts command line tool CLI"
__author__      = "austin"
__email__       = "tips@cia.lol"
__url__         = "https://github.com/austinogilvie/jodie"


__all__ = ['__version__', '__description__', '__url__', '__doc__']
