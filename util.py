import json
from pathlib import Path
from typing import Any

DEBUG_DIR = Path("debug")


def write(output: Any, filename: str) -> Path:
    """Write any output to debug/{filename}: strings as they are, everything else as JSON."""
    DEBUG_DIR.mkdir(exist_ok=True)
    path = DEBUG_DIR / filename
    if isinstance(output, str):
        text = output
    else:
        text = json.dumps(output, indent=2, ensure_ascii=False, default=str)
    path.write_text(text, encoding="utf-8")
    return path
