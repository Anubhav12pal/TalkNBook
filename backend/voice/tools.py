import os
import sys
from typing import Optional

from agents import RunContextWrapper, function_tool

# Make `services/` and `models/` importable when this module is loaded outside
# of a uvicorn launch (e.g. when running cli.py directly).
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.booking import BookingCreate
from services.booking_service import BookingService
from services.movie_service import MovieService
from services.phone_auth_service import PhoneAuthService, normalize_phone

from .context import VoiceContext

# Service singletons — JSON-backed, so safe to share across requests.
_phone_auth = PhoneAuthService()
_movies = MovieService()
_bookings = BookingService()


def get_phone_auth_service() -> PhoneAuthService:
    """Hook for routes that want to share the same OTP store."""
    return _phone_auth


SEAT_ROWS = "ABCDEF"
SEATS_PER_ROW = 8


def _seat_grid() -> list[str]:
    return [f"{row}{n}" for row in SEAT_ROWS for n in range(1, SEATS_PER_ROW + 1)]


def _find_movie(query: str) -> Optional[dict]:
    """Best-effort movie lookup by id, substring of title, or genre."""
    q = (query or "").strip().lower()
    if not q:
        return None
    for m in _movies.get_all_movies():
        if m["id"] == q or q in m["title"].lower():
            return m
    matches = _movies.search_movies(q)
    return matches[0] if matches else None


def _find_user_booking(user_id: str, query: str) -> Optional[dict]:
    """Find a confirmed booking by movie title substring or short id."""
    q = (query or "").strip().lower()
    if not q:
        return None
    for b in _bookings.get_user_bookings(user_id):
        if b["status"] != "confirmed":
            continue
        if (q in b["movie_title"].lower()
                or q in b["id"].lower()
                or q in b["id"][:8].lower()):
            return b
    return None


# =============================================================================
# AUTH TOOLS
# =============================================================================

@function_tool
def send_phone_otp(ctx: RunContextWrapper[VoiceContext], phone_number: str) -> str:
    """
    Send a one-time 6-digit code to the caller's phone.

    Call this as soon as the caller tells you their number. Accepts any
    format ("555-123-4567", "+1 555 123 4567", etc.) — the service normalizes.
    """
    try:
        result = _phone_auth.start_otp(phone_number)
    except ValueError as e:
        return f"That phone number isn't valid: {e}"
    ctx.context.phone_number = result["phone_number"]
    msg = (f"Sent a 6-digit code to {result['phone_number']}. "
           f"Ask the caller to read it back.")
    if "dev_code" in result:
        # Mock provider — surface the code so the LLM can help the dev tester.
        msg += f" [DEV ONLY: the code is {result['dev_code']}]"
    return msg


@function_tool
def verify_phone_otp(ctx: RunContextWrapper[VoiceContext], code: str) -> str:
    """
    Check the code the caller read back. On success the caller is authenticated.

    Use this exactly once, when the caller provides the code.
    """
    if not ctx.context.phone_number:
        return "No phone number recorded yet. Ask for the number first, then call send_phone_otp."
    result = _phone_auth.verify_otp(ctx.context.phone_number, code)
    if not result["success"]:
        return result["message"]
    phone_user = result["phone_user"]
    ctx.context.is_authenticated = True
    ctx.context.phone_user_id = _phone_auth.resolve_user_id(phone_user)
    ctx.context.display_name = phone_user.get("name")
    return ("Verified. The caller is now authenticated. "
            "Hand off to the Booking Agent to help them book or manage tickets.")


@function_tool
def set_caller_name(ctx: RunContextWrapper[VoiceContext], name: str) -> str:
    """
    Record a name for a new caller so we can greet them by it.

    Use after a fresh phone number passes OTP and the caller introduces themself.
    """
    if not ctx.context.phone_number:
        return "No phone number on file."
    record = _phone_auth.register(ctx.context.phone_number, name=name)
    ctx.context.display_name = record.get("name")
    return f"Saved. I'll call them {record.get('name')}."


# =============================================================================
# MOVIE INFO TOOLS (available without auth — discovery is fine for guests)
# =============================================================================

@function_tool
def list_all_movies(ctx: RunContextWrapper[VoiceContext]) -> str:
    """List every movie currently playing, with genre and showtimes."""
    all_m = _movies.get_all_movies()
    if not all_m:
        return "No movies playing right now."
    lines = [
        f"- {m['title']} ({m['genre']}, rated {m['rating']}). "
        f"Showtimes: {', '.join(m['showtimes'])}. ${m['price']:.2f}/seat."
        for m in all_m
    ]
    return "\n".join(lines)


@function_tool
def search_movies(ctx: RunContextWrapper[VoiceContext], query: str) -> str:
    """Find movies whose title or genre contains the query."""
    results = _movies.search_movies(query)
    if not results:
        return f"Nothing matching '{query}'. Try a different title or genre."
    lines = [
        f"- {m['title']} ({m['genre']}). Showtimes: {', '.join(m['showtimes'])}."
        for m in results
    ]
    return "\n".join(lines)


@function_tool
def get_movie_details(ctx: RunContextWrapper[VoiceContext], movie_query: str) -> str:
    """Get full details for one movie (description, duration, showtimes, price)."""
    movie = _find_movie(movie_query)
    if not movie:
        return f"No movie matching '{movie_query}'."
    return (f"{movie['title']} ({movie['genre']}, {movie['duration']}, "
            f"rated {movie['rating']}). {movie['description']} "
            f"Showtimes: {', '.join(movie['showtimes'])}. "
            f"${movie['price']:.2f} per seat.")


@function_tool
def check_seat_availability(ctx: RunContextWrapper[VoiceContext],
                            movie_query: str, showtime: str) -> str:
    """How many seats are open for a given movie + showtime."""
    movie = _find_movie(movie_query)
    if not movie:
        return f"No movie matching '{movie_query}'."
    if showtime not in movie["showtimes"]:
        return (f"{movie['title']} doesn't have a {showtime} showing. "
                f"Try one of: {', '.join(movie['showtimes'])}.")
    booked = set(_bookings.get_booked_seats(movie["id"], showtime))
    grid = _seat_grid()
    available = [s for s in grid if s not in booked]
    return (f"{movie['title']} at {showtime}: {len(available)} of {len(grid)} seats free. "
            f"Sample available seats: {', '.join(available[:8])}.")


# =============================================================================
# BOOKING TOOLS (require authentication)
# =============================================================================

def _require_auth(ctx: RunContextWrapper[VoiceContext]) -> Optional[str]:
    if not ctx.context.is_authenticated or not ctx.context.phone_user_id:
        return ("The caller isn't authenticated. "
                "Hand off to the Authentication Agent to verify their phone first.")
    return None


@function_tool
def book_specific_seats(ctx: RunContextWrapper[VoiceContext],
                        movie_query: str, showtime: str, seats: str) -> str:
    """
    Book the exact seats the caller asked for.

    `seats` is a comma-separated list like "A1,A2".
    """
    err = _require_auth(ctx)
    if err:
        return err
    movie = _find_movie(movie_query)
    if not movie:
        return f"No movie matching '{movie_query}'."
    if showtime not in movie["showtimes"]:
        return (f"{movie['title']} doesn't have a {showtime} showing. "
                f"Try: {', '.join(movie['showtimes'])}.")
    seat_list = [s.strip().upper() for s in seats.split(",") if s.strip()]
    if not seat_list:
        return "No seats specified."
    try:
        booking = _bookings.create_booking(
            BookingCreate(
                movie_id=movie["id"],
                movie_title=movie["title"],
                showtime=showtime,
                seats=seat_list,
                total_price=movie["price"] * len(seat_list),
            ),
            ctx.context.phone_user_id,
        )
    except ValueError as e:
        return f"Couldn't book: {e}"
    return (f"Booked {', '.join(seat_list)} for {booking['movie_title']} at "
            f"{booking['showtime']}. Total ${booking['total_price']:.2f}. "
            f"Booking reference: {booking['id'][:8]}.")


@function_tool
def book_best_available(ctx: RunContextWrapper[VoiceContext],
                        movie_query: str, showtime: str, num_seats: int) -> str:
    """
    Pick the first N open seats and book them.

    Use when the caller says 'just pick good seats' or doesn't specify rows.
    """
    err = _require_auth(ctx)
    if err:
        return err
    if num_seats < 1 or num_seats > 12:
        return "Please book between 1 and 12 seats."
    movie = _find_movie(movie_query)
    if not movie:
        return f"No movie matching '{movie_query}'."
    if showtime not in movie["showtimes"]:
        return (f"{movie['title']} doesn't have a {showtime} showing. "
                f"Try: {', '.join(movie['showtimes'])}.")
    booked = set(_bookings.get_booked_seats(movie["id"], showtime))
    available = [s for s in _seat_grid() if s not in booked]
    if len(available) < num_seats:
        return f"Only {len(available)} seats free for that showing."
    chosen = available[:num_seats]
    try:
        booking = _bookings.create_booking(
            BookingCreate(
                movie_id=movie["id"],
                movie_title=movie["title"],
                showtime=showtime,
                seats=chosen,
                total_price=movie["price"] * num_seats,
            ),
            ctx.context.phone_user_id,
        )
    except ValueError as e:
        return f"Couldn't book: {e}"
    return (f"Booked {', '.join(chosen)} for {booking['movie_title']} at "
            f"{booking['showtime']}. Total ${booking['total_price']:.2f}. "
            f"Booking reference: {booking['id'][:8]}.")


@function_tool
def list_my_bookings(ctx: RunContextWrapper[VoiceContext]) -> str:
    """Show the caller's confirmed bookings."""
    err = _require_auth(ctx)
    if err:
        return err
    confirmed = [b for b in _bookings.get_user_bookings(ctx.context.phone_user_id)
                 if b["status"] == "confirmed"]
    if not confirmed:
        return "No current bookings."
    lines = [
        f"- {b['movie_title']} at {b['showtime']}, seats {', '.join(b['seats'])} "
        f"(ref {b['id'][:8]}). ${b['total_price']:.2f}."
        for b in confirmed
    ]
    return "\n".join(lines)


@function_tool
def cancel_entire_booking(ctx: RunContextWrapper[VoiceContext],
                          booking_query: str) -> str:
    """
    Cancel a whole booking. `booking_query` can be the movie title or
    a short booking reference like 'a1b2c3d4'.
    """
    err = _require_auth(ctx)
    if err:
        return err
    booking = _find_user_booking(ctx.context.phone_user_id, booking_query)
    if not booking:
        return f"No active booking matching '{booking_query}'."
    ok = _bookings.cancel_booking(booking["id"], ctx.context.phone_user_id)
    if not ok:
        return "Couldn't cancel — that booking may already be cancelled."
    return f"Cancelled {booking['movie_title']} at {booking['showtime']} (ref {booking['id'][:8]})."


@function_tool
def cancel_specific_seats(ctx: RunContextWrapper[VoiceContext],
                          booking_query: str, seats: str) -> str:
    """
    Drop only some seats from a booking; the rest remain confirmed.

    `seats` is comma-separated like "A1,A2".
    """
    err = _require_auth(ctx)
    if err:
        return err
    booking = _find_user_booking(ctx.context.phone_user_id, booking_query)
    if not booking:
        return f"No active booking matching '{booking_query}'."
    seat_list = [s.strip().upper() for s in seats.split(",") if s.strip()]
    if not seat_list:
        return "No seats specified."
    result = _bookings.cancel_seats(booking["id"], seat_list, ctx.context.phone_user_id)
    return result["message"]


AUTH_TOOLS = [send_phone_otp, verify_phone_otp, set_caller_name]

INFO_TOOLS = [list_all_movies, search_movies, get_movie_details, check_seat_availability]

BOOKING_TOOLS = [
    book_specific_seats,
    book_best_available,
    list_my_bookings,
    cancel_entire_booking,
    cancel_specific_seats,
]
