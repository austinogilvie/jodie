## Jodie is a command line tool to quickly save new contacts to Contacts.app on macOS

Save macOS contacts to Apple's Contacts.app from command line.

`Jodie` is named for for [Jodie Foster](https://en.wikipedia.org/wiki/Jodie_Foster) for her stellar performance in the movie[ Contact](<https://en.wikipedia.org/wiki/Contact_(1997_American_film)>).

this is a work in progress.

## Installation

clone 

```
# Clone the repo
git clone git@github.com:austinogilvie/jodie.git
cd jodie/
pip install .
```

#### Usage

```
jodie-cli --help
jodie - Manage macOS Contacts.app from command line!

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

```

#### Save a new Contact to macOS Address Book / Contacts.app


##### Examples

Pass arguments explicitly like this:

```
jodie-cli new \
    --email "john99.doe99@gmail.com" \
    --first john99 \
    --last doe99 \
    --company "AcmeCo Inc" \
    --title "Founder" \
    --websites "https://linkedin.com/in/johndoe,https://github.com/johndoe,https://example.com" \
    --phone "+1 555 555 5555"

```


Or use the `--auto` flag and Jodie will assign various arguments to the right field in Apple's Contacts.app record.

```
jodie-cli new --auto \
    "john99.doe99@gmail.com" \
    "John Q. Doe" \
    "CEO" \
    "AcmeCo Inc" \
    "https://www.linkedin.com/in/johnqdoe99/" \
    "https://www.example.io/"

# Saving...
# Contact: John Doe, Email: john99.doe99@gmail.com, Phone: None, Job Title: Ceo, Company: Acmeco Inc, Websites: LinkedIn: https://www.linkedin.com/in/johnqdoe99/, _$!<HomePage>!$_: https://www.example.io/

```
