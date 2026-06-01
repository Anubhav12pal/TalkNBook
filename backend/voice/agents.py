import os

from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    RunContextWrapper,
    handoff,
    set_tracing_disabled,
)
from agents.extensions import handoff_filters
from openai import AsyncOpenAI

from .context import VoiceContext
from .tools import AUTH_TOOLS, BOOKING_TOOLS, INFO_TOOLS

# -----------------------------------------------------------------------------
# Model wiring
# -----------------------------------------------------------------------------
# Provider precedence (first hit wins):
#   1. OLLAMA_BASE_URL set  -> local Ollama  (any tool-capable model: qwen2.5, llama3.1, ...)
#   2. OPENROUTER_API_KEY   -> OpenRouter   (model id like "openai/gpt-4o-mini")
#   3. OPENAI_API_KEY       -> OpenAI directly
#
# All three providers go through OpenAIChatCompletionsModel because Ollama and
# OpenRouter only implement Chat Completions, not OpenAI's Responses API (which
# is the SDK's default model class).
#
# Tracing is disabled for the non-OpenAI providers — the SDK would otherwise
# try to ship traces to OpenAI with whatever key happens to be configured.

_OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
_OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
_OPENAI_KEY = os.getenv("OPENAI_API_KEY")

if _OLLAMA_BASE_URL:
    # Ollama: any non-empty api_key works (it's ignored server-side).
    DEFAULT_MODEL_ID = os.getenv("OPENAI_AGENT_MODEL", "qwen2.5:7b")
    _client = AsyncOpenAI(api_key="ollama", base_url=_OLLAMA_BASE_URL)
    set_tracing_disabled(True)
elif _OPENROUTER_KEY:
    DEFAULT_MODEL_ID = os.getenv("OPENAI_AGENT_MODEL", "openai/gpt-4o-mini")
    _client = AsyncOpenAI(
        api_key=_OPENROUTER_KEY,
        base_url="https://openrouter.ai/api/v1",
    )
    set_tracing_disabled(True)
else:
    DEFAULT_MODEL_ID = os.getenv("OPENAI_AGENT_MODEL", "gpt-4o-mini")
    _client = AsyncOpenAI(api_key=_OPENAI_KEY) if _OPENAI_KEY else None


def _build_model() -> OpenAIChatCompletionsModel | str:
    """
    Return an OpenAIChatCompletionsModel bound to the configured client, or
    fall back to the plain model-id string if no client is configured (lets
    test imports succeed without API keys).
    """
    if _client is None:
        return DEFAULT_MODEL_ID
    return OpenAIChatCompletionsModel(model=DEFAULT_MODEL_ID, openai_client=_client)


DEFAULT_MODEL = _build_model()


def _state_block(ctx: VoiceContext) -> str:
    """A compact state dump injected at the bottom of every agent prompt."""
    return (
        "\n\n--- CURRENT CALL STATE ---\n"
        f"call_id: {ctx.call_id}\n"
        f"auth: {ctx.auth_summary()}\n"
        "--- END STATE ---"
    )


# =============================================================================
# AUTHENTICATION AGENT
# =============================================================================

def _auth_instructions(wrapper: RunContextWrapper[VoiceContext], agent: Agent) -> str:
    base = (
        "You are the Authentication Agent for TalkNBook. Your only job is to "
        "verify the caller's identity by phone-number OTP. Speak naturally — "
        "this is a voice call.\n\n"
        "CRITICAL: Always use tools — never write tool-call text like "
        "'transfer_to_bookingagent' inside your reply. Invoke tools properly.\n\n"
        "Flow:\n"
        "1. If you don't have the caller's phone number, ask for it.\n"
        "2. Call `send_phone_otp` with the number they gave you.\n"
        "3. Ask the caller to read back the 6-digit code.\n"
        "4. Call `verify_phone_otp` with the code.\n"
        "5. On success, immediately hand off to the Booking Agent so they can "
        "   continue with what they originally wanted. Do not ask further "
        "   questions yourself.\n"
        "6. If verification fails, apologize and call `send_phone_otp` again.\n\n"
        "Never ask for a password, email, or username — phone OTP only. "
        "Keep responses short — one or two sentences."
    )
    return base + _state_block(wrapper.context)


auth_agent: Agent[VoiceContext] = Agent[VoiceContext](
    name="AuthenticationAgent",
    handoff_description=(
        "Verifies the caller's identity by sending a one-time code to their phone "
        "and checking they read it back correctly. Use whenever the caller is not "
        "yet authenticated and they want to do anything that touches their bookings."
    ),
    instructions=_auth_instructions,
    model=DEFAULT_MODEL,
    tools=list(AUTH_TOOLS),
    handoffs=[],  # filled in below to avoid forward-ref cycles
)


# =============================================================================
# BOOKING AGENT (also handles info once authenticated)
# =============================================================================

def _booking_instructions(wrapper: RunContextWrapper[VoiceContext], agent: Agent) -> str:
    base = (
        "You are the Booking Agent for TalkNBook. The caller is on the phone.\n\n"
        "CRITICAL: Always call a tool to answer the caller. Never claim a movie "
        "isn't playing, never claim seats aren't available, and never claim the "
        "caller has no bookings without first calling the relevant tool. If you "
        "don't know what's playing, call `list_all_movies`. If unsure a title "
        "exists, call `search_movies`. Do not write tool-call text like "
        "'transfer_to_bookingagent' inside your reply — invoke tools properly.\n\n"
        "TOOL PLAYBOOK:\n"
        "- 'What's playing?' / 'Any X movies?'  -> `list_all_movies` or `search_movies`.\n"
        "- 'Tell me about X'                     -> `get_movie_details`.\n"
        "- 'Are seats available?'                -> `check_seat_availability`.\n"
        "- 'Book me N seats for X at TIME, pick good ones' -> `book_best_available`.\n"
        "- 'Book seats A1, A2 for X at TIME'    -> `book_specific_seats`.\n"
        "- 'What are my bookings?'              -> `list_my_bookings`.\n"
        "- 'Cancel seats X from my booking'     -> `cancel_specific_seats`.\n"
        "- 'Cancel my whole booking for X'      -> `cancel_entire_booking`.\n\n"
        "RULES:\n"
        "- If `auth` in the state block below is NOT AUTHENTICATED, hand off to "
        "  the Authentication Agent immediately — booking tools will refuse.\n"
        "- NEVER book seats unless the caller has explicitly confirmed the exact "
        "  seats and showtime in their most recent message. If their response is "
        "  ambiguous, negative, unclear, or expresses frustration, ask for "
        "  clarification — do NOT book.\n"
        "- NEVER call `transfer_to_bookingagent` — you ARE the Booking Agent. "
        "  You can only hand off to the Authentication Agent or Triage Agent.\n"
        "- After a successful booking, read back the booking reference and total.\n"
        "- If a cancellation is ambiguous, call `list_my_bookings` first.\n"
        "- For non-booking questions, hand back to the Triage Agent.\n\n"
        "Be concise — voice call. Read at most three options at a time."
    )
    return base + _state_block(wrapper.context)


booking_agent: Agent[VoiceContext] = Agent[VoiceContext](
    name="BookingAgent",
    handoff_description=(
        "Handles authenticated actions: browsing movies, checking seat "
        "availability, booking tickets, viewing bookings, cancelling bookings "
        "or specific seats. Only useful if the caller is already authenticated."
    ),
    instructions=_booking_instructions,
    model=DEFAULT_MODEL,
    tools=list(INFO_TOOLS) + list(BOOKING_TOOLS),
    handoffs=[],  # filled in below
)


# =============================================================================
# TRIAGE AGENT
# =============================================================================

def _triage_instructions(wrapper: RunContextWrapper[VoiceContext], agent: Agent) -> str:
    base = (
        "You are the Triage Agent for TalkNBook, a movie ticket service the "
        "caller reached by phone. You greet callers, answer general questions "
        "about what's playing, and route to specialists.\n\n"
        "ROUTING:\n"
        "- Browsing movies, checking showtimes, checking seat availability → "
        "  answer yourself with the info tools.\n"
        "- Booking, viewing the caller's bookings, cancelling anything → "
        "  if the caller is AUTHENTICATED, hand off to the Booking Agent; "
        "  if NOT, hand off to the Authentication Agent first.\n"
        "- Anything about login / verification → hand off to the Authentication Agent.\n\n"
        "Open with a brief greeting like 'Hi, this is TalkNBook — what can I help "
        "you book today?' but only on the very first turn. Don't re-greet later. "
        "Speak naturally — short sentences."
    )
    return base + _state_block(wrapper.context)


triage_agent: Agent[VoiceContext] = Agent[VoiceContext](
    name="TriageAgent",
    handoff_description=(
        "Front-desk receptionist. Greets the caller, answers general questions "
        "about movies and showtimes, and routes booking/auth requests onward."
    ),
    instructions=_triage_instructions,
    model=DEFAULT_MODEL,
    tools=list(INFO_TOOLS),
    handoffs=[],  # filled in below
)


# -----------------------------------------------------------------------------
# Wire handoffs (deferred so all three agents exist before referencing each other)
# -----------------------------------------------------------------------------

triage_agent.handoffs = [
    handoff(auth_agent, input_filter=handoff_filters.remove_all_tools),
    handoff(booking_agent, input_filter=handoff_filters.remove_all_tools),
]

auth_agent.handoffs = [
    handoff(booking_agent, input_filter=handoff_filters.remove_all_tools),
    handoff(triage_agent, input_filter=handoff_filters.remove_all_tools),
]

booking_agent.handoffs = [
    handoff(auth_agent, input_filter=handoff_filters.remove_all_tools),
    handoff(triage_agent, input_filter=handoff_filters.remove_all_tools),
]


# Public exports for the runner / route layer.
AGENT_REGISTRY: dict[str, Agent[VoiceContext]] = {
    triage_agent.name: triage_agent,
    auth_agent.name: auth_agent,
    booking_agent.name: booking_agent,
}
