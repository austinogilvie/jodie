#!/usr/bin/env python3
# jodie/cli/__doc__.py
"""jodie - Manage macOS Contacts.app from command line!

Usage: 
    jodie new [EMAIL NAME COMPANY TITLE NOTE...]
    jodie new [options]
    jodie new --auto TEXT...
    jodie parse [options] TEXT

Arguments:
    EMAIL                               Email address for the contact you want to create.
    NAME                                Full name for the contact you want to create.
    COMPANY                             Company name.
    TITLE                               Job title.
    NOTE                                Any text you want to save in the `Note` field in Contacts.app.
    TEXT                                Text for jodie to try her best to parse semi-intelligently if she can.

Options:
    -A --auto                           Automatically guess fields from provided text.
    -C COMPANY --company=COMPANY        Company name.
    -E EMAIL --email=EMAIL              Email.
    -F FIRST --first=FIRST              First name.
    -L LAST --last=LAST                 Last name.
    -U NAME --full-name=NAME            Full name.
    -N NOTE --note=NOTE                 Any text you want to save in the `Note` field in Contacts.app.
    -P PHONE --phone=PHONE              Phone.
    -T TITLE --title=TITLE              Job title.
    -X TEXT  --text=TEXT                Text for jodie to try her best to parse semi-intelligently if she can.    
    -W WEBSITES --websites=WEBSITES     Comma-separated list of websites/URLs (e.g. "https://linkedin.com/in/johndoe,https://github.com/johndoe").
    -H --help                           Show this screen.
    -V --version                        Show version.

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
