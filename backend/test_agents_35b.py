"""
Quick smoke-test for all three agents using qwen3.5:35b.
Run from backend/: python test_agents_35b.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from voice.runner import voice_runner

PHONE = "+15551234567"

async def turn(call_id: str, msg: str, label: str = "") -> dict:
    print(f"\nyou> {msg}")
    r = await voice_runner.send(call_id, msg, phone_number=PHONE if not label else None)
    agent = r["current_agent"]
    reply = r["reply"]
    auth = r["authenticated"]
    print(f"[{agent}] {reply}")
    print(f"  (authenticated={auth})")
    return r

async def main():
    print("=" * 60)
    print("TEST 1: Greeting (TriageAgent)")
    print("=" * 60)
    cid = "test-triage"
    await turn(cid, "Hello", label="first")

    print("\n" + "=" * 60)
    print("TEST 2: Movie listing (TriageAgent info tools)")
    print("=" * 60)
    await turn(cid, "What movies are playing right now?")

    print("\n" + "=" * 60)
    print("TEST 3: Trigger auth flow (unauthenticated booking)")
    print("=" * 60)
    await turn(cid, "I want to book 2 tickets")

    print("\n" + "=" * 60)
    print("TEST 4: Auth — provide phone number")
    print("=" * 60)
    await turn(cid, f"My number is {PHONE}")

    print("\n" + "=" * 60)
    print("TEST 5: Provide OTP (fake — expect failure/retry)")
    print("=" * 60)
    await turn(cid, "The code is 000000")

    print("\n" + "=" * 60)
    print("TEST 6: Fresh call — BookingAgent query (movie details)")
    print("=" * 60)
    cid2 = "test-booking"
    await turn(cid2, "Hello", label="first")
    await turn(cid2, "Tell me about Inception")

    print("\n\nDone.")

if __name__ == "__main__":
    asyncio.run(main())
