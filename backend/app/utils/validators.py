import re
from typing import Optional, Tuple


class Validators:
    """Validation utilities"""

    @staticmethod
    def validate_email(email: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_password(password: str) -> Tuple[bool, Optional[str]]:
        if len(password) < 8:
            return False, "Password must be at least 8 characters"

        if not re.search(r"[A-Z]", password):
            return False, "Password must contain uppercase letter"

        if not re.search(r"[a-z]", password):
            return False, "Password must contain lowercase letter"

        if not re.search(r"[0-9]", password):
            return False, "Password must contain digit"

        return True, None

    @staticmethod
    def validate_username(username: str) -> bool:
        pattern = r"^[a-zA-Z0-9_-]{3,255}$"
        return re.match(pattern, username) is not None
