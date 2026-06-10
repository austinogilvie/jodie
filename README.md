# Jodie

A command line tool to quickly save new contacts to Contacts.app on macOS.

Named for [Jodie Foster](https://en.wikipedia.org/wiki/Jodie_Foster) for her stellar performance in [Contact](https://en.wikipedia.org/wiki/Contact_(1997_American_film)).

![Jodie Foster in Contact](jodie-foster-contact.gif)

## Installation

```bash
pip install jodie
```

Or install from source:

```bash
git clone git@github.com:austinogilvie/jodie.git
cd jodie
pip install .
```

After installation, both `jodie` and `jodie-cli` commands are available.

## Quick Start

```bash
# Smart parsing (default) - jodie figures out what's what
jodie new "John Doe" john@acme.com "Acme Inc" "CEO"

# Preview before saving
jodie new "John Doe" john@acme.com --dry-run

# Parse from clipboard (copy an email signature first)
jodie new --paste

# Parse from stdin
echo "John Doe <john@acme.com>" | jodie new --stdin
```

## Usage

```
jodie - Manage macOS Contacts.app from command line!

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
```

## Examples

### Smart Parsing (Default)

Just pass the information in any order - jodie figures it out:

```bash
jodie new "John Doe" john@acme.com "Acme Inc" "CEO" "https://linkedin.com/in/johndoe"
```

### Preview with --dry-run

See what jodie parsed before saving:

```bash
jodie new "John Doe" john@acme.com "Acme Inc" --dry-run
```

Output:
```
┌─────────────────────────────────────────────────────────┐
│                     Contact Preview                     │
├──────────────┬──────────────────────┬───────────────────┤
│ Field        │ Value                │ Source            │
├──────────────┼──────────────────────┼───────────────────┤
│ First Name   │ John                 │ parsed (100%)     │
│ Last Name    │ Doe                  │ parsed (100%)     │
│ Email        │ john@acme.com        │ parsed (100%)     │
│ Company      │ Acme Inc             │ parsed (100%)     │
└──────────────┴──────────────────────┴───────────────────┘

Run without --dry-run to save this contact.
```

### Parse Email Signatures from Clipboard

Copy an email signature to your clipboard, then:

```bash
jodie new --paste --dry-run
```

Jodie handles common signature formats:
- Strips pronouns (he/him, she/her, they/them)
- Splits on bullet separators (•, |, —)
- Filters out reply headers and forwarded message noise
- Infers company from email domain

### Parse from Stdin

Pipe text directly:

```bash
echo "Jane Smith <jane@startup.io> | CEO | Startup Inc" | jodie new --stdin
```

Or use a heredoc:

```bash
jodie new --stdin << 'EOF'
Jane Smith
CEO, Startup Inc
jane@startup.io
415-555-1234
https://linkedin.com/in/janesmith
EOF
```

### Explicit Flags

For full control, use explicit flags:

```bash
jodie new \
    --first "John" \
    --last "Doe" \
    --email "john@acme.com" \
    --phone "+1 555 555 5555" \
    --title "CEO" \
    --company "Acme Inc" \
    --linkedin "https://linkedin.com/in/johndoe" \
    --websites "https://acme.com,https://github.com/johndoe"
```

### Strict Positional Mode

If you prefer explicit ordering (email first, then name, company, title):

```bash
jodie new --explicit john@acme.com "John Doe" "Acme Inc" "CEO"
```

Use `--dry-run` with explicit mode to preview before saving.

## Flag Aliases

For convenience, these aliases are supported:

| Primary | Aliases |
|---------|---------|
| `--first` | `--first-name`, `--firstname` |
| `--last` | `--last-name`, `--lastname` |
| `--full-name` | `--name` |
| `--websites` | `--website` |

## Known Limitations

- **Notes field**: Currently disabled due to macOS entitlement requirements. Will be re-enabled in a future update.

## License

MIT
