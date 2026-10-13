import re
from fastapi import HTTPException

def validate_password(password: str) -> str:
    """
    Enforces password policy: min 6 chars.
    """
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long")
    return password

def sanitize_html(text: str) -> str:
    """
    Basic HTML stripping to prevent XSS.
    """
    if not text:
        return text
    # Strip simple HTML tags
    clean_text = re.sub(r'<[^>]*>', '', text)
    return clean_text