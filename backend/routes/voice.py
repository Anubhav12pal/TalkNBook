from fastapi import APIRouter, HTTPException, status

from models.phone_user import (
    LinkPhoneRequest,
    OTPSendRequest,
    OTPVerifyRequest,
    PhoneUser,
    VoiceChatRequest,
    VoiceChatResponse,
)
from voice.runner import voice_runner
from voice.tools import get_phone_auth_service


router = APIRouter(prefix="/voice", tags=["voice"])
phone_auth = get_phone_auth_service()


@router.post("/otp/send")
async def send_otp(body: OTPSendRequest):
    """Send a one-time code to a phone number (mock provider logs it)."""
    try:
        return phone_auth.start_otp(body.phone_number)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/otp/verify")
async def verify_otp(body: OTPVerifyRequest):
    """Verify a code and return the phone user record on success."""
    try:
        result = phone_auth.verify_otp(body.phone_number, body.code)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=result["message"])
    return result


@router.post("/link-phone", response_model=PhoneUser)
async def link_phone(body: LinkPhoneRequest):
    """Link a phone number to an existing web-account user id."""
    try:
        record = phone_auth.link_to_web_user(body.phone_number, body.user_id, body.name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return record


@router.get("/phone-users", response_model=list[PhoneUser])
async def list_phone_users():
    """Debug helper — list every phone user on file."""
    return phone_auth._load()


@router.post("/chat", response_model=VoiceChatResponse)
async def chat(body: VoiceChatRequest):
    """
    Drive one turn of a simulated phone conversation through the agent graph.

    Use this from the CLI harness, or as a stand-in until Retell AI is wired up.
    `call_id` is any stable string per conversation (e.g. uuid the client picks).
    """
    try:
        result = await voice_runner.send(
            call_id=body.call_id,
            user_message=body.message,
            phone_number=body.phone_number,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Agent error: {e}")
    return VoiceChatResponse(call_id=body.call_id, **result)


@router.delete("/chat/{call_id}")
async def end_chat(call_id: str):
    """End a call (drop its in-memory state)."""
    voice_runner.end_call(call_id)
    return {"message": "Call ended"}
