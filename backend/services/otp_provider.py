import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class OTPProvider(ABC):
    """Delivery channel for one-time passwords."""

    @abstractmethod
    def send(self, phone_number: str, code: str) -> None:
        """Deliver `code` to `phone_number`."""


class MockOTPProvider(OTPProvider):
    """Dev provider: writes the OTP to the log instead of sending SMS."""

    def send(self, phone_number: str, code: str) -> None:
        logger.warning("=" * 50)
        logger.warning("MOCK OTP for %s -> %s", phone_number, code)
        logger.warning("=" * 50)
        print(f"\n[MOCK OTP] {phone_number} -> {code}\n", flush=True)
