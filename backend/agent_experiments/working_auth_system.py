from agents import Agent, Runner, function_tool
from dotenv import load_dotenv
import asyncio
import json
import sys
import os
import bcrypt

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.booking_service import BookingService
from models.booking import BookingCreate

# Load environment variables
load_dotenv()

# Initialize services
booking_service = BookingService()

# Global session storage
user_sessions = {}

# =============================================================================
# AUTHENTICATION FUNCTIONS
# =============================================================================

@function_tool
def authenticate_user(username: str, password: str) -> str:
    """Authenticate user with username and password."""
    try:
        # Load users
        users_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'users.json')
        with open(users_file, 'r') as f:
            users = json.load(f)

        # Find user
        user = None
        for u in users:
            if u['username'] == username:
                user = u
                break

        if not user:
            return "❌ Username not found. Please check your username."

        # Verify password
        if bcrypt.checkpw(password.encode('utf-8'), user['hashed_password'].encode('utf-8')):
            # Create session
            session_id = f"session_{user['id']}"
            user_sessions[session_id] = {
                "user_id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "authenticated": True
            }

            return f"✅ Welcome {user['username']}! You are logged in. Your session ID is: {session_id}"
        else:
            return "❌ Incorrect password. Please try again."

    except Exception as e:
        return f"❌ Authentication error: {str(e)}"

@function_tool
def smart_book_tickets(user_input: str) -> str:
    """Smart booking that extracts session, movie, time, and seats from user input."""
    try:
        import re

        print(f"🔍 Processing: {user_input}")

        # Extract session ID
        session_match = re.search(r'session[_\s]+([a-f0-9-]+)', user_input.lower())
        if not session_match:
            return "❌ Please provide your session ID. Login first or include session in your message."

        session_id = f"session_{session_match.group(1)}"

        # Verify session
        if session_id not in user_sessions:
            return "❌ Invalid session. Please login again."

        user = user_sessions[session_id]
        username = user['username']
        user_id = user['user_id']

        # Extract movie
        movie_map = {
            "avengers": ("movie-1", "Avengers: Endgame"),
            "spider": ("movie-2", "Spider-Man: No Way Home"),
            "batman": ("movie-3", "The Batman"),
            "dune": ("movie-4", "Dune"),
            "top gun": ("movie-5", "Top Gun: Maverick")
        }

        movie_id, movie_title = None, None
        for key, (mid, title) in movie_map.items():
            if key in user_input.lower():
                movie_id, movie_title = mid, title
                break

        if not movie_id:
            return "❌ Please specify a movie: Avengers, Spider-Man, Batman, Dune, or Top Gun"

        # Extract showtime
        time_match = re.search(r'(\d{1,2}:\d{2}\s?[AP]M)', user_input, re.IGNORECASE)
        if not time_match:
            return "❌ Please specify showtime: 10:00 AM, 1:00 PM, 4:00 PM, 7:00 PM, or 10:00 PM"

        showtime = time_match.group(1).upper()

        # Extract seats (but exclude session ID parts)
        # First remove the session ID from the message to avoid picking up its parts
        clean_message = re.sub(r'session[_\s]+[a-f0-9-]+', '', user_input, flags=re.IGNORECASE)
        seats = re.findall(r'[A-F]\d{1,2}', clean_message.upper())
        if not seats:
            return "❌ Please specify seats (e.g., A1, B2)"

        # Book tickets
        total_price = len(seats) * 12.0
        booking_data = BookingCreate(
            movie_id=movie_id,
            movie_title=movie_title,
            showtime=showtime,
            seats=seats,
            total_price=total_price
        )

        result = booking_service.create_booking(booking_data, user_id)

        return f"🎬 SUCCESS! Booked {len(seats)} seats ({', '.join(seats)}) for {movie_title} at {showtime} for {username}. Booking ID: {result['id'][:8]}..."

    except ValueError as e:
        return f"❌ Booking failed: {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@function_tool
def smart_view_bookings(user_input: str) -> str:
    """View bookings for authenticated user."""
    try:
        import re

        # Extract session ID
        session_match = re.search(r'session[_\s]+([a-f0-9-]+)', user_input.lower())
        if not session_match:
            return "❌ Please provide your session ID to view bookings."

        session_id = f"session_{session_match.group(1)}"

        # Verify session
        if session_id not in user_sessions:
            return "❌ Invalid session. Please login again."

        user = user_sessions[session_id]
        username = user['username']
        user_id = user['user_id']

        # Get bookings
        bookings = booking_service.get_user_bookings(user_id)
        confirmed_bookings = [b for b in bookings if b["status"] == "confirmed"]

        if not confirmed_bookings:
            return f"📝 Hi {username}, you have no current bookings."

        booking_list = []
        for booking in confirmed_bookings:
            booking_info = (f"🎫 {booking['movie_title']} at {booking['showtime']}\n"
                          f"   Seats: {', '.join(booking['seats'])}\n"
                          f"   Price: ${booking['total_price']}\n"
                          f"   ID: {booking['id'][:8]}...")
            booking_list.append(booking_info)

        return f"📋 Hi {username}! Your bookings:\n\n" + "\n\n".join(booking_list)

    except Exception as e:
        return f"❌ Error retrieving bookings: {str(e)}"

# =============================================================================
# AGENTS
# =============================================================================

auth_agent = Agent(
    name="Authentication Agent",
    instructions=(
        "You are a user authentication assistant. "
        "Help users login with their username and password. "
        "When successful, provide the session ID clearly. "
        "Be friendly and secure."
    ),
    model="gpt-4",
    tools=[authenticate_user]
)

booking_agent = Agent(
    name="Movie Booking Agent",
    instructions=(
        "You are a movie booking assistant. "
        "Use smart_book_tickets for booking and smart_view_bookings for viewing bookings. "
        "Both functions need the user's session ID in their message. "
        "Be helpful and confirm bookings clearly."
    ),
    model="gpt-4",
    tools=[smart_book_tickets, smart_view_bookings]
)

triage_agent = Agent(
    name="TalkNBook Customer Service",
    instructions=(
        "You are customer service for TalkNBook movie theater. "
        "Route users to the right specialist: "
        "- Login/authentication requests → Authentication Agent "
        "- Booking/viewing bookings → Movie Booking Agent "
        "Be friendly and explain what you're doing."
    ),
    model="gpt-4",
    tools=[],
    handoffs=[auth_agent, booking_agent]
)

# =============================================================================
# TEST FUNCTION
# =============================================================================

async def main():
    print("🎬 TalkNBook Working Authentication System Test")
    print("=" * 55)

    # Test 1: Login through triage
    print("\n1. 🔐 Testing login through triage...")
    result1 = await Runner.run(triage_agent, "I want to login with username 'agentuser' and password 'secure123'")
    print("Result:", result1.final_output)

    # Extract session (should be in the response)
    import re
    session_match = re.search(r'session_[a-f0-9-]+', result1.final_output)
    session_id = session_match.group() if session_match else None

    if session_id:
        print(f"✅ Session extracted: {session_id}")
        print("\n" + "-" * 50)

        # Test 2: Book tickets through triage
        print("\n2. 🎫 Testing booking through triage...")
        booking_message = f"I want to book seats B1 and B2 for Avengers at 7:00 PM. My session is {session_id}"
        result2 = await Runner.run(triage_agent, booking_message)
        print("Result:", result2.final_output)
        print("\n" + "-" * 50)

        # Test 3: View bookings through triage
        print("\n3. 📋 Testing view bookings through triage...")
        view_message = f"Show my bookings. Session: {session_id}"
        result3 = await Runner.run(triage_agent, view_message)
        print("Result:", result3.final_output)

    else:
        print("❌ No session ID found, skipping authenticated tests")

    print("\n" + "=" * 55)
    print("🎉 Test Complete!")

    # Show sessions
    print(f"\n📊 Active Sessions: {len(user_sessions)}")
    for sid, session in user_sessions.items():
        print(f"   - {sid}: {session['username']}")

if __name__ == "__main__":
    asyncio.run(main())