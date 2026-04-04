from pathlib import Path

def get_root() -> Path:
    """Get root directory of the project"""
    return Path(__file__).parent.parent