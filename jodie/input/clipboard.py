import subprocess

def read_clipboard() -> str:
    """Read text from macOS clipboard via pbpaste."""
    result = subprocess.run(['pbpaste'], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("Failed to read clipboard")
    return result.stdout
