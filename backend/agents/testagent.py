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

@function_tool
def get_user_bookings(user_id: str = "test-user-123") -> str:
    """Get all bookings for the current user."""
    try:
        bookings = booking_service.get_user_bookings(user_id)

        if not bookings:
            return "You have no current bookings."

        booking_list = []
        for booking in bookings:
            if booking["status"] == "confirmed":
                booking_info = (f"Booking ID: {booking['id']}\n"
                              f"Movie: {booking['movie_title']}\n"
                              f"Showtime: {booking['showtime']}\n"
                              f"Seats: {', '.join(booking['seats'])}\n"
                              f"Total Price: ${booking['total_price']}\n"
                              f"Date: {booking['booking_date'][:10]}")
                booking_list.append(booking_info)

        if not booking_list:
            return "You have no confirmed bookings."

        return "Your current bookings:\n\n" + "\n\n".join(booking_list)

    except Exception as e:
        return f"Error retrieving bookings: {str(e)}"

@function_tool
def cancel_entire_booking(booking_id: str, user_id: str = "test-user-123") -> str:
    """Cancel an entire booking by booking ID."""
    try:
        # First check if the booking exists and belongs to the user
        booking = booking_service.get_booking_by_id(booking_id)

        if not booking:
            return f"Booking ID {booking_id} not found."

        if booking["user_id"] != user_id:
            return "You can only cancel your own bookings."

        if booking["status"] != "confirmed":
            return f"Booking {booking_id} is already cancelled or not confirmed."

        # Cancel the booking
        success = booking_service.cancel_booking(booking_id, user_id)

        if success:
            return (f"Successfully cancelled booking {booking_id}.\n"
                   f"Movie: {booking['movie_title']}\n"
                   f"Showtime: {booking['showtime']}\n"
                   f"Cancelled seats: {', '.join(booking['seats'])}")
        else:
            return f"Failed to cancel booking {booking_id}."

    except Exception as e:
        return f"Error cancelling booking: {str(e)}"

@function_tool
def cancel_specific_seats_by_seat(seats_to_cancel: str, user_id: str = "test-user-123") -> str:
    """Cancel specific seats from user's bookings. Automatically finds which booking contains the seats. Seats should be comma-separated (e.g., 'A1,A2')."""
    try:
        # Parse seats
        seats_list = [seat.strip() for seat in seats_to_cancel.split(',')]

        # Get all user bookings
        user_bookings = booking_service.get_user_bookings(user_id)
        confirmed_bookings = [b for b in user_bookings if b["status"] == "confirmed"]

        if not confirmed_bookings:
            return "You have no confirmed bookings to cancel seats from."

        # Find which booking(s) contain the requested seats
        found_bookings = []
        for booking in confirmed_bookings:
            booking_seats = set(booking["seats"])
            requested_seats = set(seats_list)

            # Check if any of the requested seats are in this booking
            if requested_seats.intersection(booking_seats):
                # Find which seats from the request are actually in this booking
                valid_seats = list(requested_seats.intersection(booking_seats))
                invalid_seats = list(requested_seats - booking_seats)

                found_bookings.append({
                    "booking": booking,
                    "valid_seats": valid_seats,
                    "invalid_seats": invalid_seats
                })

        if not found_bookings:
            # Show user what seats they actually have
            all_user_seats = []
            for booking in confirmed_bookings:
                for seat in booking["seats"]:
                    all_user_seats.append(f"{seat} (from {booking['movie_title']} at {booking['showtime']})")

            return (f"None of the seats {', '.join(seats_list)} were found in your bookings.\n"
                   f"Your current seats are: {', '.join(all_user_seats)}")

        # If exactly one booking found with valid seats, cancel them
        if len(found_bookings) == 1:
            booking_info = found_bookings[0]
            booking = booking_info["booking"]
            valid_seats = booking_info["valid_seats"]
            invalid_seats = booking_info["invalid_seats"]

            if invalid_seats:
                return (f"Seats {', '.join(invalid_seats)} are not in your booking for {booking['movie_title']} at {booking['showtime']}.\n"
                       f"Your seats in this booking are: {', '.join(booking['seats'])}.\n"
                       f"Valid seats to cancel: {', '.join(valid_seats)}")

            # Cancel the seats
            result = booking_service.cancel_seats(booking["id"], valid_seats, user_id)

            if result["success"]:
                return f"Successfully cancelled seats {', '.join(valid_seats)} from {booking['movie_title']} at {booking['showtime']}. {result['message']}"
            else:
                return result["message"]

        # If multiple bookings found, ask user to specify
        else:
            response = f"Found seats {', '.join(seats_list)} in multiple bookings:\n"
            for i, booking_info in enumerate(found_bookings, 1):
                booking = booking_info["booking"]
                valid_seats = booking_info["valid_seats"]
                response += f"{i}. {booking['movie_title']} at {booking['showtime']} - seats {', '.join(valid_seats)} (Booking ID: {booking['id'][:8]}...)\n"

            response += "Please specify which movie/showtime you want to cancel seats from."
            return response

    except Exception as e:
        return f"Error cancelling seats: {str(e)}"

@function_tool
def cancel_specific_seats_by_booking_id(booking_id: str, seats_to_cancel: str, user_id: str = "test-user-123") -> str:
    """Cancel specific seats from a specific booking ID. Use this when user provides the booking ID. Seats should be comma-separated (e.g., 'A1,A2')."""
    try:
        # Parse seats
        seats_list = [seat.strip() for seat in seats_to_cancel.split(',')]

        # First check if the booking exists and belongs to the user
        booking = booking_service.get_booking_by_id(booking_id)

        if not booking:
            return f"Booking ID {booking_id} not found."

        if booking["user_id"] != user_id:
            return "You can only cancel seats from your own bookings."

        if booking["status"] != "confirmed":
            return f"Booking {booking_id} is already cancelled or not confirmed."

        # Check if the seats exist in the booking
        current_seats = set(booking["seats"])
        seats_to_cancel_set = set(seats_list)

        if not seats_to_cancel_set.issubset(current_seats):
            invalid_seats = seats_to_cancel_set - current_seats
            return (f"Cannot cancel seats {', '.join(invalid_seats)} because they are not in your booking.\n"
                   f"Your current seats are: {', '.join(booking['seats'])}")

        # Cancel the specific seats
        result = booking_service.cancel_seats(booking_id, seats_list, user_id)

        if result["success"]:
            return result["message"]
        else:
            return result["message"]

    except Exception as e:
        return f"Error cancelling seats: {str(e)}"

agent1 = Agent(
    name="Movie bookings agent",
    instructions=(
        "You are an AI movie booking assistant. "
        "Your job is to help users book movie tickets, cancel bookings, and check seat availability. "
        "When a user asks for something, figure out what they want, and call the correct tool. "
        "If details are missing (such as movie name, time, seat number, or booking ID), ask the user to clarify. "

        "Available movies: movie-1 (Avengers: Endgame), movie-2 (Spider-Man: No Way Home), movie-3 (The Batman), movie-4 (Dune), movie-5 (Top Gun: Maverick). "
        "Available showtimes: 10:00 AM, 1:00 PM, 4:00 PM, 7:00 PM, 10:00 PM. "

        "CANCELLATION RULES: "
        "- Users can only cancel their own bookings. "
        "- Users can only cancel confirmed bookings. "
        "- When users want to cancel specific seats, use cancel_specific_seats_by_seat to automatically find the booking. "
        "- Only use cancel_specific_seats_by_booking_id if the user explicitly provides a booking ID. "
        "- If a user tries to cancel seats that are not in their booking, explain what seats they actually have. "
        "- If seats are found in multiple bookings, ask which movie/showtime they want to cancel from. "
        "- If a user tries to cancel someone else's booking, politely refuse. "
        "- If a user tries to cancel an already cancelled booking, inform them it's already cancelled. "
        "- When cancelling specific seats, if all seats are cancelled, the entire booking gets cancelled. "
        "- Always confirm the cancellation details back to the user. "

        "Always confirm the outcome of tool calls back to the user in simple language. "
        "If the user asks something unrelated to booking, politely explain you only handle movie bookings."
    ),
    model="gpt-4",
    tools=[book_movie_tickets, check_seat_availability, get_user_bookings, cancel_entire_booking, cancel_specific_seats_by_seat, cancel_specific_seats_by_booking_id]
)

async def main():
    # Test 1: Get current bookings
    print("1. Testing get user bookings...")
    result1 = await Runner.run(agent1, "Show me all my current bookings")
    print("Bookings Result:", result1.final_output)
    print("\n" + "="*50 + "\n")


    # Test 2: Cancel seats without booking ID (smart lookup)
    print("2. Testing cancel seats without booking ID...")
    result3 = await Runner.run(agent1, "I want to cancel seat A4")
    print("Smart Cancel Result:", result3.final_output)
    print("\n" + "="*50 + "\n")

    # Test 3: Try to cancel seats that don't exist
    print("3. Testing cancel non-existent seats...")
    result4 = await Runner.run(agent1, "I want to cancel seats Z1 and Z2")
    print("Non-existent Seats Result:", result4.final_output)
    print("\n" + "="*50 + "\n")

    # # Test 3: Try to cancel seats that don't exist in booking
    # print("3. Testing cancel non-existent seats...")
    # result3 = await Runner.run(agent1, "I want to cancel seats Z1 and Z2 from my booking")
    # print("Invalid Seats Result:", result3.final_output)
    # print("\n" + "="*50 + "\n")

    # # Test 4: Cancel entire booking
    # print("4. Testing cancel entire booking...")
    # result4 = await Runner.run(agent1, "Cancel my entire booking with ID 62ab519c-6404-47a8-abf6-c1b38cc2c990")
    # print("Cancel Booking Result:", result4.final_output)
    # print("\n" + "="*50 + "\n")

    # # Test 5: Try to cancel already cancelled booking
    # print("5. Testing cancel already cancelled booking...")
    # result5 = await Runner.run(agent1, "Cancel booking ID 62ab519c-6404-47a8-abf6-c1b38cc2c990")
    # print("Already Cancelled Result:", result5.final_output)
    # print("\n" + "="*50 + "\n")

    # # Test 6: Check seat availability after cancellations
    # print("6. Testing seat availability after cancellations...")
    # result6 = await Runner.run(agent1, "What seats are available for Avengers Endgame at 7:00 PM?")
    # print("Updated Availability:", result6.final_output)

if __name__ == "__main__":
    asyncio.run(main())