"""
Simulated phone-call REPL for the voice agent stack.

Usage (from backend/):
    python -m voice.cli                          # interactive, prompts for caller-id
    python -m voice.cli --phone +15551234567     # pre-set caller phone number
    python -m voice.cli --call-id demo --phone +15551234567

Type messages as the caller would speak. Type :quit / :exit / Ctrl-D to end.
Type :state to print the current VoiceContext.
"""

import argparse
import asyncio
import os
import sys
import uuid

# Make sibling packages (services/, models/) importable when run via `-m voice.cli`.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from voice.runner import voice_runner  # noqa: E402  (after load_dotenv)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TalkNBook voice agent REPL")
    parser.add_argument("--phone", help="Caller phone number (E.164 or any format)",
                        default=None)
    parser.add_argument("--call-id", help="Stable call id (defaults to random uuid)",
                        default=None)
    return parser.parse_args()


async def _run() -> int:
    args = _parse_args()
    if not any([os.getenv("OPENAI_API_KEY"), os.getenv("OPENROUTER_API_KEY"), os.getenv("OLLAMA_BASE_URL")]):
        print("ERROR: No LLM provider configured. Set OPENAI_API_KEY, OPENROUTER_API_KEY, or OLLAMA_BASE_URL in backend/.env.",
              file=sys.stderr)
        return 1

    call_id = args.call_id or f"cli-{uuid.uuid4().hex[:8]}"
    phone = args.phone

    print(f"\n--- TalkNBook voice REPL ---")
    print(f"call_id: {call_id}")
    if phone:
        print(f"phone:   {phone}")
    print("Type :quit to end, :state to inspect context, :clear to drop the call.\n")

    # Kick off with an empty user turn so the triage agent greets first.
    first = await voice_runner.send(call_id, "Hello", phone_number=phone)
    print(f"[{first['current_agent']}] {first['reply']}\n")

    while True:
        try:
            line = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        if line in (":quit", ":exit", ":q"):
            break
        if line == ":state":
            state = voice_runner.get(call_id)
            if state:
                print(f"  ctx = {state.context}")
                print(f"  last_agent = {state.last_agent_name}")
                print(f"  history_len = {len(state.messages)}")
            else:
                print("  (no active call)")
            continue
        if line == ":clear":
            voice_runner.end_call(call_id)
            print("  (call state cleared)")
            continue

        try:
            turn = await voice_runner.send(call_id, line)
        except Exception as e:
            print(f"  agent error: {e}")
            continue
        print(f"[{turn['current_agent']}] {turn['reply']}\n")

    voice_runner.end_call(call_id)
    print("Call ended.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_run()))
