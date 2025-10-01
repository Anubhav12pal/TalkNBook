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

# Global session storage (in production, use Redis or similar)
user_sessions = {}

# =============================================================================
# AUTHENTICATION AGENT
# =============================================================================

@function_tool
def authenticate_user(username: str, password: str) -> str:
    """Authenticate user with username and password."""
    try:
        # Load users from JSON file
        users_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'users.json')
        with open(users_file, 'r') as f:
            users = json.load(f)

        # Find user by username
        user = None
        for u in users:
            if u['username'] == username:
                user = u
                break

        if not user:
            return json.dumps({
                "success": False,
                "message": "Username not found. Please check your username or register a new account."
            })

        # Verify password
        if bcrypt.checkpw(password.encode('utf-8'), user['hashed_password'].encode('utf-8')):
            # Store session
            session_id = f"session_{user['id']}"
            user_sessions[session_id] = {
                "user_id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "authenticated": True
            }

            return json.dumps({
                "success": True,
                "message": f"Welcome {user['username']}! You are now logged in.",
                "session_id": session_id,
                "user_id": user['id'],
                "username": user['username']
            })
        else:
            return json.dumps({
                "success": False,
                "message": "Incorrect password. Please try again."
            })

    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"Authentication error: {str(e)}"
        })

@function_tool
def register_new_user(username: str, password: str, email: str) -> str:
    """Register a new user account."""
    try:
        # Load existing users
        users_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'users.json')
        with open(users_file, 'r') as f:
            users = json.load(f)

        # Check if username or email already exists
        for user in users:
            if user['username'] == username:
                return json.dumps({
                    "success": False,
                    "message": f"Username '{username}' already exists. Please choose a different username."
                })
            if user['email'] == email:
                return json.dumps({
                    "success": False,
                    "message": f"Email '{email}' already registered. Please use a different email or login."
                })

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Create new user
        import uuid
        from datetime import datetime

        new_user = {
            "id": str(uuid.uuid4()),
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "created_at": datetime.now().isoformat()
        }

        users.append(new_user)

        # Save to file
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=2)

        return json.dumps({
            "success": True,
            "message": f"Account created successfully for {username}! You can now login.",
            "user_id": new_user['id']
        })

    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"Registration error: {str(e)}"
        })

@function_tool
def logout_user(session_id: str) -> str:
    """Logout user and clear session."""
    try:
        if session_id in user_sessions:
            username = user_sessions[session_id].get('username', 'User')
            del user_sessions[session_id]
            return json.dumps({
                "success": True,
                "message": f"Goodbye {username}! You have been logged out successfully."
            })
        else:
            return json.dumps({
                "success": False,
                "message": "No active session found."
            })
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"Logout error: {str(e)}"
        })

# Authentication Agent
auth_agent = Agent(
    name="Authentication Agent",
    instructions=(
        "You are a user authentication assistant. "
        "Help users login, register, and logout. "
        "When users want to login, ask for username and password. "
        "When users want to register, ask for username, password, and email. "
        "Always be friendly and secure about handling credentials. "
        "After successful authentication, inform them they can now access booking services. "
        "If authentication fails, provide helpful error messages."
    ),
    model="gpt-4",
    tools=[authenticate_user, register_new_user, logout_user]
)

# =============================================================================
# BOOKING AGENT (Modified to require authentication)
# =============================================================================

@function_tool
def verify_session(session_id: str) -> str:
    """Verify if user session is valid."""
    if session_id in user_sessions and user_sessions[session_id]['authenticated']:
        user = user_sessions[session_id]
        return json.dumps({
            "success": True,
            "user_id": user['user_id'],
            "username": user['username']
        })
    else:
        return json.dumps({
            "success": False,
            "message": "Please login first to access booking services."
        })

@function_tool
def book_movie_tickets_auth(movie_id: str, movie_title: str, showtime: str, seats: str, session_id: str) -> str:
    """Book movie tickets for authenticated user."""
    try:
        # Verify session first
        session_check = json.loads(verify_session(session_id))
        if not session_check["success"]:
            return session_check["message"]

        user_id = session_check["user_id"]
        username = session_check["username"]

        # Parse seats
        seat_list = [seat.strip() for seat in seats.split(',')]
        total_price = len(seat_list) * 12.0

        # Create booking
        booking_data = BookingCreate(
            movie_id=movie_id,
            movie_title=movie_title,
            showtime=showtime,
            seats=seat_list,
            total_price=total_price
        )

        result = booking_service.create_booking(booking_data, user_id)

        return f"Successfully booked {len(seat_list)} seats ({', '.join(seat_list)}) for {movie_title} at {showtime} for {username}. Booking ID: {result['id']}"

    except ValueError as e:
        return f"Booking failed: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

@function_tool
def get_user_bookings_auth(session_id: str) -> str:
    """Get bookings for authenticated user."""
    try:
        # Verify session first
        session_check = json.loads(verify_session(session_id))
        if not session_check["success"]:
            return session_check["message"]

        user_id = session_check["user_id"]
        username = session_check["username"]

        bookings = booking_service.get_user_bookings(user_id)
        confirmed_bookings = [b for b in bookings if b["status"] == "confirmed"]

        if not confirmed_bookings:
            return f"Hi {username}, you have no current bookings."

        booking_list = []
        for booking in confirmed_bookings:
            booking_info = (f"Booking ID: {booking['id'][:8]}...\n"
                          f"Movie: {booking['movie_title']}\n"
                          f"Showtime: {booking['showtime']}\n"
                          f"Seats: {', '.join(booking['seats'])}\n"
                          f"Total Price: ${booking['total_price']}")
            booking_list.append(booking_info)

        return f"Hi {username}, your current bookings:\n\n" + "\n\n".join(booking_list)

    except Exception as e:
        return f"Error retrieving bookings: {str(e)}"

@function_tool
def cancel_seats_auth(seats_to_cancel: str, session_id: str) -> str:
    """Cancel specific seats for authenticated user."""
    try:
        # Verify session first
        session_check = json.loads(verify_session(session_id))
        if not session_check["success"]:
            return session_check["message"]

        user_id = session_check["user_id"]
        username = session_check["username"]

        # Parse seats
        seats_list = [seat.strip() for seat in seats_to_cancel.split(',')]

        # Get user bookings
        user_bookings = booking_service.get_user_bookings(user_id)
        confirmed_bookings = [b for b in user_bookings if b["status"] == "confirmed"]

        if not confirmed_bookings:
            return f"{username}, you have no confirmed bookings to cancel seats from."

        # Find which booking contains the seats
        found_bookings = []
        for booking in confirmed_bookings:
            booking_seats = set(booking["seats"])
            requested_seats = set(seats_list)

            if requested_seats.intersection(booking_seats):
                valid_seats = list(requested_seats.intersection(booking_seats))
                found_bookings.append({
                    "booking": booking,
                    "valid_seats": valid_seats
                })

        if not found_bookings:
            all_user_seats = []
            for booking in confirmed_bookings:
                for seat in booking["seats"]:
                    all_user_seats.append(f"{seat} ({booking['movie_title']} at {booking['showtime']})")

            return (f"{username}, none of the seats {', '.join(seats_list)} were found in your bookings.\n"
                   f"Your current seats are: {', '.join(all_user_seats)}")

        # If exactly one booking found, cancel the seats
        if len(found_bookings) == 1:
            booking_info = found_bookings[0]
            booking = booking_info["booking"]
            valid_seats = booking_info["valid_seats"]

            result = booking_service.cancel_seats(booking["id"], valid_seats, user_id)

            if result["success"]:
                return f"{username}, successfully cancelled seats {', '.join(valid_seats)} from {booking['movie_title']} at {booking['showtime']}. {result['message']}"
            else:
                return result["message"]

        # Multiple bookings found
        else:
            response = f"{username}, found seats {', '.join(seats_list)} in multiple bookings:\n"
            for i, booking_info in enumerate(found_bookings, 1):
                booking = booking_info["booking"]
                valid_seats = booking_info["valid_seats"]
                response += f"{i}. {booking['movie_title']} at {booking['showtime']} - seats {', '.join(valid_seats)}\n"

            response += "Please specify which movie/showtime you want to cancel seats from."
            return response

    except Exception as e:
        return f"Error cancelling seats: {str(e)}"

# Additional tools for booking agent to handle session extraction
@function_tool
def extract_session_and_book(user_message: str) -> str:
    """Extract session ID from user message and book tickets."""
    try:
        import re

        # Try to find session ID in the message
        session_match = re.search(r'session[_\s]+([a-f0-9-]+)', user_message.lower())
        if not session_match:
            return "Please provide your session ID to book tickets. You need to be logged in first."

        session_id = f"session_{session_match.group(1)}"

        # Extract booking details
        movie_matches = {
            "avengers": ("movie-1", "Avengers: Endgame"),
            "spider-man": ("movie-2", "Spider-Man: No Way Home"),
            "batman": ("movie-3", "The Batman"),
            "dune": ("movie-4", "Dune"),
            "top gun": ("movie-5", "Top Gun: Maverick")
        }

        movie_id, movie_title = None, None
        for key, (mid, title) in movie_matches.items():
            if key in user_message.lower():
                movie_id, movie_title = mid, title
                break

        if not movie_id:
            return "Please specify which movie you'd like to book. Available: Avengers Endgame, Spider-Man, Batman, Dune, Top Gun Maverick."

        # Extract showtime
        time_match = re.search(r'(\d{1,2}:\d{2}\s?[AP]M)', user_message, re.IGNORECASE)
        if not time_match:
            return "Please specify a showtime (10:00 AM, 1:00 PM, 4:00 PM, 7:00 PM, 10:00 PM)."

        showtime = time_match.group(1).upper()

        # Extract seats
        seat_matches = re.findall(r'[A-F]\d+', user_message.upper())
        if not seat_matches:
            return "Please specify which seats you'd like to book (e.g., A1, B2)."

        seats = ','.join(seat_matches)

        # Book the tickets
        return book_movie_tickets_auth(movie_id, movie_title, showtime, seats, session_id)

    except Exception as e:
        return f"Error processing booking: {str(e)}"

@function_tool
def extract_session_and_view_bookings(user_message: str) -> str:
    """Extract session ID and show user bookings."""
    try:
        import re

        # Try to find session ID in the message
        session_match = re.search(r'session[_\s]+([a-f0-9-]+)', user_message.lower())
        if not session_match:
            return "Please provide your session ID to view bookings. You need to be logged in first."

        session_id = f"session_{session_match.group(1)}"

        return get_user_bookings_auth(session_id)

    except Exception as e:
        return f"Error retrieving bookings: {str(e)}"

@function_tool
def extract_session_and_cancel_seats(user_message: str) -> str:
    """Extract session ID and cancel specific seats."""
    try:
        import re

        # Try to find session ID in the message
        session_match = re.search(r'session[_\s]+([a-f0-9-]+)', user_message.lower())
        if not session_match:
            return "Please provide your session ID to cancel seats. You need to be logged in first."

        session_id = f"session_{session_match.group(1)}"

        # Extract seats to cancel
        seat_matches = re.findall(r'[A-F]\d+', user_message.upper())
        if not seat_matches:
            return "Please specify which seats you'd like to cancel (e.g., A1, B2)."

        seats = ','.join(seat_matches)

        return cancel_seats_auth(seats, session_id)

    except Exception as e:
        return f"Error cancelling seats: {str(e)}"

# Booking Agent (requires authentication)
booking_agent = Agent(
    name="Movie Booking Agent",
    instructions=(
        "You are a movie booking assistant that requires user authentication. "
        "When users mention booking, viewing bookings, or cancelling seats, extract their session ID from their message and use the appropriate tool. "
        "If no session ID is provided, ask them to provide it or login first. "
        "Always use the user's name when possible to personalize responses. "
        "Available movies: movie-1 (Avengers: Endgame), movie-2 (Spider-Man: No Way Home), movie-3 (The Batman), movie-4 (Dune), movie-5 (Top Gun: Maverick). "
        "Available showtimes: 10:00 AM, 1:00 PM, 4:00 PM, 7:00 PM, 10:00 PM."
    ),
    model="gpt-4",
    tools=[extract_session_and_book, extract_session_and_view_bookings, extract_session_and_cancel_seats, verify_session]
)

# =============================================================================
# TRIAGE AGENT (Routes and manages handoffs)
# =============================================================================

triage_agent = Agent(
    name="Customer Service Triage",
    instructions=(
        "You are a friendly customer service triage agent for TalkNBook movie theater. "
        "Help users with their requests and route them to the appropriate specialist when needed. "

        "HANDOFF RULES: "
        "- If user wants to login, register, or logout → hand off to Authentication Agent "
        "- If user wants to book tickets, view bookings, or cancel seats → hand off to Movie Booking Agent "
        "- If user asks about their account or authentication status → hand off to Authentication Agent "

        "Always greet users warmly and explain what you're doing. "
        "If you're unsure about the user's request, ask clarifying questions before routing. "
        "You can provide general information about movies and showtimes without handoff."
    ),
    model="gpt-4",
    tools=[],
    handoffs=[auth_agent, booking_agent]
)

# =============================================================================
# MAIN TEST FUNCTION
# =============================================================================

async def main():
    print("🎬 TalkNBook Multi-Agent Authentication System Test")
    print("=" * 60)

    # Test 1: Start with triage agent - user wants to register
    print("\n1. Testing triage agent routing to registration...")
    result1 = await Runner.run(triage_agent, "Hi! I'm new here. I want to create an account to book movie tickets.")
    print("Result:", result1.final_output)
    print("\n" + "-" * 40 + "\n")

    # Test 2: Triage agent routes to booking (should fail without auth)
    print("2. Testing triage agent routing to booking without auth...")
    result2 = await Runner.run(triage_agent, "I want to book tickets for Avengers Endgame")
    print("Result:", result2.final_output)
    print("\n" + "-" * 40 + "\n")

    # Test 3: Direct authentication test - register
    print("3. Testing direct authentication - registration...")
    result3 = await Runner.run(auth_agent, "Register me with username 'agentuser', password 'secure123', and email 'agent@test.com'")
    print("Result:", result3.final_output)
    print("\n" + "-" * 40 + "\n")

    # Test 4: Direct authentication test - login
    print("4. Testing direct authentication - login...")
    result4 = await Runner.run(auth_agent, "Login with username 'agentuser' and password 'secure123'")
    print("Result:", result4.final_output)

    # Extract session_id for further testing
    session_id = None
    # Since we know the session was created, let's use the active sessions
    if user_sessions:
        session_id = list(user_sessions.keys())[0]  # Get the latest session
        print(f"📋 Session ID extracted: {session_id}")
    else:
        print("❌ No active sessions found")

    print("\n" + "-" * 40 + "\n")

    if session_id:
        # Test 5: Authenticated booking through triage
        print("5. Testing triage agent with authenticated booking...")
        result5 = await Runner.run(triage_agent, f"I'm logged in with session {session_id}. Book me seats B1 and B2 for Avengers Endgame at 7:00 PM")
        print("Result:", result5.final_output)
        print("\n" + "-" * 40 + "\n")

        # Test 6: View bookings through triage
        print("6. Testing view bookings through triage...")
        result6 = await Runner.run(triage_agent, f"Show my current bookings. My session is {session_id}")
        print("Result:", result6.final_output)
        print("\n" + "-" * 40 + "\n")

        # Test 7: Cancel seats through triage
        print("7. Testing cancel seats through triage...")
        result7 = await Runner.run(triage_agent, f"Cancel seat B1 from my bookings. Session: {session_id}")
        print("Result:", result7.final_output)
    else:
        print("❌ Skipping authenticated tests - no session ID available")

    print("\n" + "=" * 60)
    print("🎉 Multi-Agent System Test Complete!")

    # Show current session state
    print(f"\n📊 Active Sessions: {len(user_sessions)}")
    for sid, session in user_sessions.items():
        print(f"   - {sid}: {session['username']} ({session['email']})")

if __name__ == "__main__":
    asyncio.run(main())