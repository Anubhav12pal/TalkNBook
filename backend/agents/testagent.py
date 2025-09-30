from agents import Agent, Runner, function_tool
from dotenv import load_dotenv
import asyncio
import sys
import os

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.booking_service import BookingService
from models.booking import BookingCreate

# Load environment variables from .env file
load_dotenv()

# Initialize booking service
booking_service = BookingService()

@function_tool
def book_movie_tickets(movie_id: str, movie_title: str, showtime: str, seats: str) -> str:
    """Book movie tickets for specified seats and showtime. Seats should be comma-separated (e.g., 'A1,A2,A3')."""
    try:
        # Parse seats from comma-separated string
        seat_list = [seat.strip() for seat in seats.split(',')]

        # Calculate total price (assuming $12 per seat)
        total_price = len(seat_list) * 12.0

        # Create booking data
        model = BookingCreate(
            movie_id=movie_id,
            movie_title=movie_title,
            showtime=showtime,
            seats=seat_list,
            total_price=total_price
        )

        # Create booking with test user
        result = booking_service.create_booking(model, "test-user-123")

        return f"Successfully booked {len(seat_list)} seats ({', '.join(seat_list)}) for {movie_title} at {showtime}. Booking ID: {result['id']}"

    except ValueError as e:
        return f"Booking failed: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

@function_tool
def check_seat_availability(movie_id: str, showtime: str) -> str:
    """Check which seats are available for a movie and showtime."""
    try:
        booked_seats = booking_service.get_booked_seats(movie_id, showtime)
        all_seats = [f"{row}{num}" for row in "ABCDEF" for num in range(1, 11)]
        available_seats = [seat for seat in all_seats if seat not in booked_seats]

        return f"Available seats: {', '.join(available_seats)}. Booked seats: {', '.join(booked_seats)}"

    except Exception as e:
        return f"Error checking availability: {str(e)}"

agent1 = Agent(
    name="Movie bookings agent",
    instructions=(
        "You are an AI movie booking assistant. "
        "Your job is to help users book movie tickets and check seat availability. "
        "When a user asks for something, figure out what they want, and call the correct tool. "
        "If details are missing (such as movie name, time, or seat number), ask the user to clarify. "
        "Available movies: movie-1 (Avengers: Endgame), movie-2 (Spider-Man: No Way Home), movie-3 (The Batman), movie-4 (Dune), movie-5 (Top Gun: Maverick). "
        "Available showtimes: 10:00 AM, 1:00 PM, 4:00 PM, 7:00 PM, 10:00 PM. "
        "Always confirm the outcome of tool calls back to the user in simple language. "
        "If the user asks something unrelated to booking, politely explain you only handle movie bookings."
    ),
    model="gpt-4",
    tools=[book_movie_tickets, check_seat_availability]
)

async def main():
    # Test seat availability first
    print("Testing seat availability...")
    result1 = await Runner.run(agent1, "What seats are available for Avengers Endgame at 7:00 PM?")
    print("Availability Result:", result1.final_output)
    print("\n" + "="*50 + "\n")

    # Test booking already booked seats (should fail)
    print("Testing booking already booked seats...")
    result3 = await Runner.run(agent1, "I want to book seats A1 and A2 for Avengers Endgame at 7:00 PM")
    print("Conflict Result:", result3.final_output)
    print("\n" + "="*50 + "\n")

    # Test booking new seats
    print("Testing booking new seats...")
    result2 = await Runner.run(agent1, "I want to book seats F1 and F6 for Avengers Endgame at 7:00 PM")
    print("Booking Result:", result2.final_output)

if __name__ == "__main__":
    asyncio.run(main())