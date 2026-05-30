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

# Test authentication
@function_tool
def authenticate_user(username: str, password: str) -> str:
    """Authenticate user with username and password."""
    try:
        users_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'users.json')
        with open(users_file, 'r') as f:
            users = json.load(f)

        user = None
        for u in users:
            if u['username'] == username:
                user = u
                break

        if not user:
            return json.dumps({"success": False, "message": "Username not found"})

        if bcrypt.checkpw(password.encode('utf-8'), user['hashed_password'].encode('utf-8')):
            session_id = f"session_{user['id']}"
            user_sessions[session_id] = {
                "user_id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "authenticated": True
            }
            return json.dumps({
                "success": True,
                "message": f"Welcome {user['username']}!",
                "session_id": session_id
            })
        else:
            return json.dumps({"success": False, "message": "Incorrect password"})

    except Exception as e:
        return json.dumps({"success": False, "message": f"Error: {str(e)}"})

# Test booking function
@function_tool
def book_tickets_simple(session_id: str, movie_id: str, movie_title: str, showtime: str, seats: str) -> str:
    """Book movie tickets with explicit parameters."""
    try:
        print(f"\nDEBUG book_tickets_simple called with:")
        print(f"  session_id: {session_id}")
        print(f"  movie_id: {movie_id}")
        print(f"  movie_title: {movie_title}")
        print(f"  showtime: {showtime}")
        print(f"  seats: {seats}")

        # Verify session
        if session_id not in user_sessions:
            return f"Invalid session: {session_id}. Active sessions: {list(user_sessions.keys())}"

        user = user_sessions[session_id]
        print(f"  user: {user}")

        # Parse seats
        seat_list = [s.strip() for s in seats.split(',')]
        total_price = len(seat_list) * 12.0

        # Create booking
        booking_data = BookingCreate(
            movie_id=movie_id,
            movie_title=movie_title,
            showtime=showtime,
            seats=seat_list,
            total_price=total_price
        )

        print(f"  booking_data: {booking_data}")

        result = booking_service.create_booking(booking_data, user['user_id'])

        print(f"  result: {result}")

        return f"Success! Booked {len(seat_list)} seats for {movie_title} at {showtime}. Booking ID: {result['id'][:8]}"

    except Exception as e:
        import traceback
        error = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(f"DEBUG ERROR:\n{error}")
        return error

auth_agent = Agent(
    name="Auth",
    instructions="Help users login",
    model="gpt-4",
    tools=[authenticate_user]
)

booking_agent = Agent(
    name="Booking",
    instructions="Help users book tickets using the book_tickets_simple function",
    model="gpt-4",
    tools=[book_tickets_simple]
)

async def main():
    print("=" * 60)
    print("DEBUG TEST")
    print("=" * 60)

    # Login
    print("\n1. Login...")
    result = await Runner.run(auth_agent, "Login with username 'agentuser' and password 'secure123'")
    print(f"Result: {result.final_output}\n")

    # Get session
    if user_sessions:
        session_id = list(user_sessions.keys())[0]
        print(f"Session ID: {session_id}\n")

        # Book
        print("2. Booking...")
        result = await Runner.run(
            booking_agent,
            f"Book tickets with session_id '{session_id}', movie_id 'movie-1', movie_title 'Avengers: Endgame', showtime '7:00 PM', seats 'C1,C2'"
        )
        print(f"Result: {result.final_output}\n")

    print(f"\nActive sessions: {list(user_sessions.keys())}")

if __name__ == "__main__":
    asyncio.run(main())
