import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agents import Agent, Runner

from .agents import AGENT_REGISTRY, triage_agent
from .context import VoiceContext


@dataclass
class _CallState:
    """One active phone call: shared context + the running message list."""
    context: VoiceContext
    messages: List[Dict[str, Any]] = field(default_factory=list)
    last_agent_name: str = triage_agent.name


class VoiceRunner:
    """
    Multi-turn driver for the voice agent graph.

    One `VoiceRunner` instance is shared across the FastAPI process. Each
    `call_id` keeps its own VoiceContext + conversation history in memory.
    For production, swap this in-memory dict for Redis (the `_calls` map
    is the only thing that needs to move out of process).
    """

    def __init__(self) -> None:
        self._calls: Dict[str, _CallState] = {}
        self._lock = asyncio.Lock()

    def get_or_create(self, call_id: str,
                      phone_number: Optional[str] = None) -> _CallState:
        if call_id not in self._calls:
            self._calls[call_id] = _CallState(
                context=VoiceContext(call_id=call_id, phone_number=phone_number),
            )
        return self._calls[call_id]

    def get(self, call_id: str) -> Optional[_CallState]:
        return self._calls.get(call_id)

    def end_call(self, call_id: str) -> None:
        self._calls.pop(call_id, None)

    async def send(self, call_id: str, user_message: str,
                   phone_number: Optional[str] = None) -> Dict[str, Any]:
        """
        Drive one turn of the conversation.

        Args:
            call_id: Stable id for this call (Retell call_id, CLI session, etc.).
            user_message: What the caller just said (or typed in dev).
            phone_number: Caller ID, if known up-front. Only applied when the
                call is first created — subsequent turns ignore it.

        Returns:
            {"reply": str, "current_agent": str, "authenticated": bool}
        """
        async with self._lock:
            state = self.get_or_create(call_id, phone_number=phone_number)

        starting_agent: Agent[VoiceContext] = (
            AGENT_REGISTRY.get(state.last_agent_name, triage_agent)
        )

        turn_input = state.messages + [{"role": "user", "content": user_message}]

        result = await Runner.run(
            starting_agent,
            input=turn_input,
            context=state.context,
            max_turns=12,
        )

        # Persist for the next turn.
        state.messages = result.to_input_list()
        state.last_agent_name = result.last_agent.name

        return {
            "reply": result.final_output or "",
            "current_agent": state.last_agent_name,
            "authenticated": state.context.is_authenticated,
        }


# Process-wide singleton — imported by the route layer and the CLI.
voice_runner = VoiceRunner()
