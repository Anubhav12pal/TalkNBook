from dataclasses import dataclass
from typing import Optional


@dataclass
class VoiceContext:
    """
    Per-call state shared across all voice agents and tools.

    Mutated in-place by tools (e.g. send_phone_otp sets phone_number;
    verify_phone_otp flips is_authenticated and resolves phone_user_id).
    The same instance flows through every handoff in a single call.
    """
    call_id: str
    phone_number: Optional[str] = None
    is_authenticated: bool = False
    phone_user_id: Optional[str] = None
    display_name: Optional[str] = None

    def auth_summary(self) -> str:
        """Plain-language description for injection into dynamic instructions."""
        if self.is_authenticated:
            who = self.display_name or "the caller"
            return f"AUTHENTICATED as {who} (phone {self.phone_number})."
        if self.phone_number:
            return f"NOT AUTHENTICATED. Phone {self.phone_number} provided but code not yet verified."
        return "NOT AUTHENTICATED. No phone number on file yet."
