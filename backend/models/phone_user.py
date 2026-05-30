from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PhoneUser(BaseModel):
    """A user identified by phone number (for voice / phone-call flows)."""
    id: str
    phone_number: str
    name: Optional[str] = None
    linked_user_id: Optional[str] = None
    created_at: datetime


class OTPSendRequest(BaseModel):
    """Body for POST /voice/otp/send."""
    phone_number: str


class OTPVerifyRequest(BaseModel):
    """Body for POST /voice/otp/verify."""
    phone_number: str
    code: str


class LinkPhoneRequest(BaseModel):
    """Body for POST /voice/link-phone — link a phone to an existing web user."""
    phone_number: str
    user_id: str
    name: Optional[str] = None


class VoiceChatRequest(BaseModel):
    """Body for POST /voice/chat — one turn of a simulated phone conversation."""
    call_id: str
    message: str
    phone_number: Optional[str] = None


class VoiceChatResponse(BaseModel):
    """Reply for POST /voice/chat."""
    call_id: str
    reply: str
    authenticated: bool
    current_agent: str
