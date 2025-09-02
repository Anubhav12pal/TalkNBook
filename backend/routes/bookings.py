from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status

from models.booking import BookingCreate, BookingResponse, BookedSeatsRequest, BookedSeatsResponse
from services.booking_service import BookingService
from routes.auth import get_current_user


router = APIRouter(prefix="/bookings", tags=["bookings"])
booking_service = BookingService()


@router.post("/", response_model=BookingResponse)
async def create_booking(
    booking_data: BookingCreate,
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Create a new booking for the authenticated user."""
    try:
        booking = booking_service.create_booking(booking_data, current_user["id"])
        return BookingResponse(**booking)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create booking"
        )


@router.get("/", response_model=List[BookingResponse])
async def get_user_bookings(
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Get all bookings for the authenticated user."""
    try:
        bookings = booking_service.get_user_bookings(current_user["id"])
        return [BookingResponse(**booking) for booking in bookings]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve bookings"
        )


@router.post("/booked-seats", response_model=BookedSeatsResponse)
async def get_booked_seats(request: BookedSeatsRequest):
    """Get all booked seats for a specific movie and showtime."""
    try:
        booked_seats = booking_service.get_booked_seats(request.movie_id, request.showtime)
        return BookedSeatsResponse(
            movie_id=request.movie_id,
            showtime=request.showtime,
            booked_seats=booked_seats
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve booked seats"
        )


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: str,
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Get a specific booking by ID."""
    booking = booking_service.get_booking_by_id(booking_id)
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if booking["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return BookingResponse(**booking)


@router.delete("/{booking_id}")
async def cancel_booking(
    booking_id: str,
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Cancel a booking."""
    success = booking_service.cancel_booking(booking_id, current_user["id"])
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found or access denied"
        )
    
    return {"message": "Booking cancelled successfully"}