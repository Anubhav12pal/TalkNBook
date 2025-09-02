from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class BookingCreate(BaseModel):
    """Model for booking creation request."""
    movie_id: str
    movie_title: str
    showtime: str
    seats: List[str]
    total_price: float


class BookingResponse(BaseModel):
    """Model for booking response."""
    id: str
    user_id: str
    movie_id: str
    movie_title: str
    showtime: str
    seats: List[str]
    total_price: float
    booking_date: datetime
    status: str = "confirmed"


class BookedSeatsRequest(BaseModel):
    """Model for getting booked seats request."""
    movie_id: str
    showtime: str


class BookedSeatsResponse(BaseModel):
    """Model for booked seats response."""
    movie_id: str
    showtime: str
    booked_seats: List[str]


class CancelSeatsRequest(BaseModel):
    """Model for selective seat cancellation request."""
    booking_id: str
    seats_to_cancel: List[str]