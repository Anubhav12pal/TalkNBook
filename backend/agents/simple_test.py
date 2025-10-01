from agents import Agent, Runner, function_tool
from dotenv import load_dotenv
import asyncio

load_dotenv()

# Simple test to verify booking agent with session
@function_tool
def test_booking(user_message: str) -> str:
    """Test booking function that extracts session and books tickets."""
    print(f"DEBUG: Received message: {user_message}")

    import re

    # Try to find session ID
    session_match = re.search(r'session[_\s]+([a-f0-9-]+)', user_message.lower())
    if session_match:
        session_id = f"session_{session_match.group(1)}"
        print(f"DEBUG: Found session ID: {session_id}")
        return f"SUCCESS: Found session {session_id} and would book tickets"
    else:
        print("DEBUG: No session ID found")
        return "ERROR: No session ID found in message"

test_agent = Agent(
    name="Test Agent",
    instructions="Extract session ID from user message and book tickets.",
    model="gpt-4",
    tools=[test_booking]
)

async def simple_test():
    print("Testing session extraction...")

    test_message = "I'm logged in with session session_7a4396b2-4c6b-45db-a995-fafdb0d9aee6. Book me seats B1 and B2 for Avengers Endgame at 7:00 PM"

    result = await Runner.run(test_agent, test_message)
    print("Result:", result.final_output)

if __name__ == "__main__":
    asyncio.run(simple_test())