import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from models.booking import BookingCreate, BookingResponse


class BookingService:
    """Service for managing bookings using JSON file storage."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.bookings_file = self.data_dir / "bookings.json"
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """Ensure the bookings data file exists."""
        if not self.bookings_file.exists():
            with open(self.bookings_file, 'w') as f:
                json.dump([], f)
    
    def _load_bookings(self) -> List[Dict[str, Any]]:
        """Load bookings from JSON file."""
        try:
            with open(self.bookings_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_bookings(self, bookings: List[Dict[str, Any]]):
        """Save bookings to JSON file."""
        with open(self.bookings_file, 'w') as f:
            json.dump(bookings, f, indent=2, default=str)
    
    def create_booking(self, booking_data: BookingCreate, user_id: str) -> Dict[str, Any]:
        """
        Create a new booking.
        
        Args:
            booking_data: The booking details
            user_id: ID of the user making the booking
            
        Returns:
            Dict containing the created booking
        """
        bookings = self._load_bookings()
        
        # Check if seats are already booked for this movie/showtime
        booked_seats = self.get_booked_seats(booking_data.movie_id, booking_data.showtime)
        conflicting_seats = set(booking_data.seats) & set(booked_seats)
        
        if conflicting_seats:
            raise ValueError(f"Seats {list(conflicting_seats)} are already booked")
        
        booking = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "movie_id": booking_data.movie_id,
            "movie_title": booking_data.movie_title,
            "showtime": booking_data.showtime,
            "seats": booking_data.seats,
            "total_price": booking_data.total_price,
            "booking_date": datetime.now().isoformat(),
            "status": "confirmed"
        }
        
        bookings.append(booking)
        self._save_bookings(bookings)
        
        return booking
    
    def get_user_bookings(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all bookings for a specific user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of user's bookings
        """
        bookings = self._load_bookings()
        return [booking for booking in bookings if booking["user_id"] == user_id]
    
    def get_booked_seats(self, movie_id: str, showtime: str) -> List[str]:
        """
        Get all booked seats for a specific movie and showtime.
        
        Args:
            movie_id: ID of the movie
            showtime: The showtime
            
        Returns:
            List of booked seat IDs
        """
        bookings = self._load_bookings()
        booked_seats = []
        
        for booking in bookings:
            if (booking["movie_id"] == movie_id and 
                booking["showtime"] == showtime and 
                booking["status"] == "confirmed"):
                booked_seats.extend(booking["seats"])
        
        return booked_seats
    
    def get_booking_by_id(self, booking_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a booking by its ID.
        
        Args:
            booking_id: ID of the booking
            
        Returns:
            Booking dict if found, None otherwise
        """
        bookings = self._load_bookings()
        for booking in bookings:
            if booking["id"] == booking_id:
                return booking
        return None
    
    def cancel_booking(self, booking_id: str, user_id: str) -> bool:
        """
        Cancel a booking.
        
        Args:
            booking_id: ID of the booking to cancel
            user_id: ID of the user (for authorization)
            
        Returns:
            True if cancelled successfully, False otherwise
        """
        bookings = self._load_bookings()
        
        for booking in bookings:
            if booking["id"] == booking_id and booking["user_id"] == user_id:
                booking["status"] = "cancelled"
                self._save_bookings(bookings)
                return True
        
        return False
    
    def cancel_seats(self, booking_id: str, seats_to_cancel: List[str], user_id: str) -> Dict[str, Any]:
        """
        Cancel specific seats from a booking.
        
        Args:
            booking_id: ID of the booking
            seats_to_cancel: List of seat IDs to cancel
            user_id: ID of the user (for authorization)
            
        Returns:
            Dict containing the updated booking info and operation result
        """
        bookings = self._load_bookings()
        
        for booking in bookings:
            if booking["id"] == booking_id and booking["user_id"] == user_id:
                if booking["status"] != "confirmed":
                    return {"success": False, "message": "Can only cancel seats from confirmed bookings"}
                
                # Check if all seats to cancel exist in the booking
                current_seats = set(booking["seats"])
                seats_to_cancel_set = set(seats_to_cancel)
                
                if not seats_to_cancel_set.issubset(current_seats):
                    invalid_seats = seats_to_cancel_set - current_seats
                    return {"success": False, "message": f"Seats {list(invalid_seats)} are not in this booking"}
                
                # Remove the seats
                remaining_seats = list(current_seats - seats_to_cancel_set)
                
                if not remaining_seats:
                    # If no seats remain, cancel the entire booking
                    booking["status"] = "cancelled"
                    booking["seats"] = []
                    booking["total_price"] = 0.0
                    self._save_bookings(bookings)
                    return {
                        "success": True, 
                        "message": "All seats cancelled, booking status changed to cancelled",
                        "booking": booking
                    }
                else:
                    # Update the booking with remaining seats and recalculate price
                    seat_price = booking["total_price"] / len(booking["seats"])  # Calculate price per seat
                    new_total_price = seat_price * len(remaining_seats)
                    
                    booking["seats"] = remaining_seats
                    booking["total_price"] = round(new_total_price, 2)
                    self._save_bookings(bookings)
                    return {
                        "success": True,
                        "message": f"Successfully cancelled {len(seats_to_cancel)} seat(s)",
                        "booking": booking
                    }
        
        return {"success": False, "message": "Booking not found or access denied"}