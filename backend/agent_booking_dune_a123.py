#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from services.booking_service import BookingService
from models.booking import BookingCreate

# Load environment variables
load_dotenv()

def agent_book_dune_a123():
    booking_service = BookingService()
    
    # Current logged-in user (aa@gmail.com)
    current_user_id = "b55d0934-889e-4e6e-82fe-8052945ea739"
    
    print("🎬 AGENT BOOKING: DUNE A1, A2, A3")
    print("=" * 60)
    print("🤖 Agent: Hello! I'll help you book tickets for Dune.")
    print("👤 User (aa@gmail.com): Book Dune 10 AM show, seats A1, A2, A3")
    print("🤖 Agent: Let me check availability and create your booking...")
    print("=" * 60)
    
    # Create booking data
    booking_data = BookingCreate(
        movie_id="movie-4",
        movie_title="Dune",
        showtime="10:00 AM", 
        seats=["A1", "A2", "A3"],
        total_price=36.0
    )
    
    try:
        # Create the booking (simulating agent booking)
        booking = booking_service.create_booking(booking_data, current_user_id)
        
        print("✅ AGENT BOOKING SUCCESSFUL!")
        print(f"🎬 Movie: Dune")
        print(f"🕐 Showtime: 10:00 AM")
        print(f"💺 Seats: A1, A2, A3")
        print(f"💰 Total: $36.00")
        print(f"📋 Booking ID: {booking['id']}")
        print(f"📅 Booking Date: {booking['booking_date']}")
        print(f"✔️  Status: {booking['status']}")
        
        print("\n🤖 Agent: Perfect! I've successfully booked your tickets for Dune.")
        print("   Your seats A1, A2, and A3 are confirmed for the 10:00 AM show.")
        print("   Total cost: $36.00. You can view this booking in 'My Bookings'.")
        
        return booking
        
    except Exception as e:
        print(f"❌ AGENT BOOKING FAILED: {str(e)}")
        print("🤖 Agent: I apologize, there was an issue with your booking.")
        print(f"   Error: {str(e)}")
        return None

if __name__ == "__main__":
    agent_book_dune_a123()