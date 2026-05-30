import json
import re
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from services.otp_provider import MockOTPProvider, OTPProvider


OTP_TTL = timedelta(minutes=5)
OTP_LENGTH = 6
MAX_ATTEMPTS = 3


def normalize_phone(raw: str) -> str:
    """
    Normalize a phone number to E.164-ish form.

    Strips spaces, dashes, parentheses. Preserves a leading '+'.
    Does not validate country codes — just gives us a stable key.

    Args:
        raw: Raw phone string as a human might say or type it.

    Returns:
        Normalized phone string, e.g. "+15551234567".
    """
    cleaned = re.sub(r"[^\d+]", "", raw or "")
    if not cleaned:
        raise ValueError("Empty phone number")
    if not cleaned.startswith("+"):
        cleaned = "+" + cleaned
    return cleaned


class PhoneAuthService:
    """
    Manages phone-based authentication for voice users.

    OTPs are kept in memory (fine for dev; swap for Redis in prod).
    Phone-user records persist to data/phone_users.json.
    """

    def __init__(self, otp_provider: Optional[OTPProvider] = None):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.phone_users_file = self.data_dir / "phone_users.json"
        self.otp_provider = otp_provider or MockOTPProvider()
        # phone_number -> {code, expires_at, attempts}
        self._pending_otps: Dict[str, Dict[str, Any]] = {}
        self._ensure_file()

    def _ensure_file(self) -> None:
        """Make sure phone_users.json exists and is a list (migrate {} -> [])."""
        if not self.phone_users_file.exists():
            self.phone_users_file.parent.mkdir(parents=True, exist_ok=True)
            self.phone_users_file.write_text("[]")
            return
        try:
            data = json.loads(self.phone_users_file.read_text() or "[]")
        except json.JSONDecodeError:
            data = []
        if not isinstance(data, list):
            self.phone_users_file.write_text("[]")

    def _load(self) -> list:
        try:
            data = json.loads(self.phone_users_file.read_text() or "[]")
            return data if isinstance(data, list) else []
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save(self, users: list) -> None:
        self.phone_users_file.write_text(json.dumps(users, indent=2, default=str))

    def find_by_phone(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Return the phone user record or None."""
        phone = normalize_phone(phone_number)
        for u in self._load():
            if u.get("phone_number") == phone:
                return u
        return None

    def register(self, phone_number: str, name: Optional[str] = None,
                 linked_user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a phone user record (idempotent).

        Args:
            phone_number: Raw phone number.
            name: Display name spoken by caller.
            linked_user_id: If linking to an existing web account, the user id.

        Returns:
            The phone user record.
        """
        phone = normalize_phone(phone_number)
        users = self._load()
        for u in users:
            if u.get("phone_number") == phone:
                if name and not u.get("name"):
                    u["name"] = name
                if linked_user_id and not u.get("linked_user_id"):
                    u["linked_user_id"] = linked_user_id
                self._save(users)
                return u

        record = {
            "id": str(uuid.uuid4()),
            "phone_number": phone,
            "name": name,
            "linked_user_id": linked_user_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        users.append(record)
        self._save(users)
        return record

    def start_otp(self, phone_number: str) -> Dict[str, Any]:
        """
        Generate an OTP, store it, and dispatch via the provider.

        Returns:
            {"phone_number": ..., "expires_at": ..., "dev_code": ...} —
            `dev_code` is only included when using MockOTPProvider so the
            test harness can show it; remove for production providers.
        """
        phone = normalize_phone(phone_number)
        code = "".join(secrets.choice("0123456789") for _ in range(OTP_LENGTH))
        expires_at = datetime.now(timezone.utc) + OTP_TTL
        self._pending_otps[phone] = {
            "code": code,
            "expires_at": expires_at,
            "attempts": 0,
        }
        self.otp_provider.send(phone, code)

        result: Dict[str, Any] = {
            "phone_number": phone,
            "expires_at": expires_at.isoformat(),
        }
        if isinstance(self.otp_provider, MockOTPProvider):
            result["dev_code"] = code
        return result

    def verify_otp(self, phone_number: str, code: str) -> Dict[str, Any]:
        """
        Verify a code against the pending OTP for this phone.

        Returns:
            {"success": bool, "message": str, "phone_user": dict | None}
        """
        phone = normalize_phone(phone_number)
        pending = self._pending_otps.get(phone)

        if not pending:
            return {"success": False,
                    "message": "No pending verification for this number. Request a new code.",
                    "phone_user": None}

        if datetime.now(timezone.utc) > pending["expires_at"]:
            del self._pending_otps[phone]
            return {"success": False,
                    "message": "Code expired. Request a new one.",
                    "phone_user": None}

        pending["attempts"] += 1
        if pending["attempts"] > MAX_ATTEMPTS:
            del self._pending_otps[phone]
            return {"success": False,
                    "message": "Too many attempts. Request a new code.",
                    "phone_user": None}

        if (code or "").strip() != pending["code"]:
            return {"success": False,
                    "message": f"Incorrect code. {MAX_ATTEMPTS - pending['attempts']} attempt(s) left.",
                    "phone_user": None}

        # Success — consume the OTP and upsert the phone user
        del self._pending_otps[phone]
        record = self.find_by_phone(phone) or self.register(phone)
        return {"success": True, "message": "Verified.", "phone_user": record}

    def link_to_web_user(self, phone_number: str, user_id: str,
                        name: Optional[str] = None) -> Dict[str, Any]:
        """Link a phone number to an existing web user account."""
        return self.register(phone_number, name=name, linked_user_id=user_id)

    def resolve_user_id(self, phone_user: Dict[str, Any]) -> str:
        """
        Return the user id to use for bookings.

        If the phone user is linked to a web account, use that user id so
        the same bookings show up on the website. Otherwise use the phone
        user's own id.
        """
        return phone_user.get("linked_user_id") or phone_user["id"]
