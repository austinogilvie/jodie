import sys

def read_stdin() -> str:
    """Read from stdin (for heredoc/pipe)."""
    if sys.stdin.isatty():
        raise RuntimeError("No input provided via stdin")
    return sys.stdin.read()
