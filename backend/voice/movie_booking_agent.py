import json
from typing import Dict, List, Any, Optional
from openai import OpenAI

from services.movie_service import MovieService
from services.booking_service import BookingService
from services.auth_service import AuthService
from services.phone_auth_service import PhoneAuthService


class MovieBookingAgent:
    """
    Main conversational agent for movie booking operations using OpenAI.
    Handles all movie-related tasks through voice interface.
    """
    
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)
        self.movie_service = MovieService()
        self.booking_service = BookingService()
        self.auth_service = AuthService()
        self.phone_auth_service = PhoneAuthService()
        
        # Conversation context
        self.conversation_history = []
        self.current_user_id = None
        self.current_phone = None
        
        # System prompt for the agent
        self.system_prompt = """You are TalkNBook, a friendly movie booking assistant. You help users:

1. Browse and search movies
2. Check showtimes and availability
3. Book movie tickets with seat selection
4. View their current bookings
5. Cancel individual seats or entire bookings
6. Authenticate using their phone number

Key Guidelines:
- Always be conversational and helpful
- Ask clarifying questions when needed
- Confirm important actions like bookings and cancellations
- Handle authentication gracefully
- Provide clear options and choices
- Keep responses concise but informative

Available Functions:
- search_movies: Find movies by title or genre
- get_movie_details: Get specific movie information
- get_showtimes: Get available showtimes for a movie
- check_availability: Check seat availability for a showtime
- create_booking: Book tickets for a user
- get_user_bookings: Get user's current bookings
- cancel_booking: Cancel an entire booking
- cancel_seats: Cancel specific seats from a booking
- authenticate_user: Authenticate user by phone number
- register_user: Register new user with phone number

Always call the appropriate function to fulfill user requests."""

    def get_function_definitions(self) -> List[Dict[str, Any]]:
        """Define all available functions for the agent."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_movies",
                    "description": "Search for movies by title, genre, or get all movies",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string", 
                                "description": "Search query (title or genre), or 'all' for all movies"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "get_movie_details",
                    "description": "Get detailed information about a specific movie",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "movie_id": {
                                "type": "string",
                                "description": "The movie ID"
                            }
                        },
                        "required": ["movie_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_seat_availability",
                    "description": "Check available seats for a movie showtime",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "movie_id": {
                                "type": "string",
                                "description": "The movie ID"
                            },
                            "showtime": {
                                "type": "string", 
                                "description": "The showtime (e.g., '7:00 PM')"
                            }
                        },
                        "required": ["movie_id", "showtime"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_booking",
                    "description": "Create a movie booking for the authenticated user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "movie_id": {
                                "type": "string",
                                "description": "The movie ID"
                            },
                            "movie_title": {
                                "type": "string",
                                "description": "The movie title"
                            },
                            "showtime": {
                                "type": "string",
                                "description": "The showtime"
                            },
                            "seats": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of seat IDs to book (e.g., ['A1', 'A2'])"
                            },
                            "total_price": {
                                "type": "number",
                                "description": "Total price for the booking"
                            }
                        },
                        "required": ["movie_id", "movie_title", "showtime", "seats", "total_price"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_user_bookings",
                    "description": "Get all bookings for the authenticated user",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "cancel_booking",
                    "description": "Cancel an entire booking",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "booking_id": {
                                "type": "string",
                                "description": "The booking ID to cancel"
                            }
                        },
                        "required": ["booking_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "cancel_seats",
                    "description": "Cancel specific seats from a booking",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "booking_id": {
                                "type": "string",
                                "description": "The booking ID"
                            },
                            "seats": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of seat IDs to cancel"
                            }
                        },
                        "required": ["booking_id", "seats"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "authenticate_user",
                    "description": "Authenticate user by phone number",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "phone_number": {
                                "type": "string",
                                "description": "User's phone number"
                            }
                        },
                        "required": ["phone_number"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "register_user",
                    "description": "Register a new user with phone number",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "phone_number": {
                                "type": "string",
                                "description": "User's phone number"
                            },
                            "name": {
                                "type": "string",
                                "description": "User's name"
                            }
                        },
                        "required": ["phone_number", "name"]
                    }
                }
            }
        ]

    def search_movies(self, query: str) -> Dict[str, Any]:
        """Search for movies."""
        try:
            if query.lower() == "all":
                movies = self.movie_service.get_all_movies()
            else:
                movies = self.movie_service.search_movies(query)
            
            return {
                "success": True,
                "movies": movies,
                "message": f"Found {len(movies)} movies"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_movie_details(self, movie_id: str) -> Dict[str, Any]:
        """Get movie details by ID."""
        try:
            movie = self.movie_service.get_movie_by_id(movie_id)
            if movie:
                return {"success": True, "movie": movie}
            else:
                return {"success": False, "error": "Movie not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def check_seat_availability(self, movie_id: str, showtime: str) -> Dict[str, Any]:
        """Check seat availability for a showtime."""
        try:
            booked_seats = self.booking_service.get_booked_seats(movie_id, showtime)
            
            # Generate available seats (A1-A10, B1-B10, C1-C10, D1-D10, E1-E10)
            all_seats = []
            for row in ['A', 'B', 'C', 'D', 'E']:
                for num in range(1, 11):
                    all_seats.append(f"{row}{num}")
            
            available_seats = [seat for seat in all_seats if seat not in booked_seats]
            
            return {
                "success": True,
                "available_seats": available_seats,
                "booked_seats": booked_seats,
                "total_seats": len(all_seats),
                "available_count": len(available_seats)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_booking(self, movie_id: str, movie_title: str, showtime: str, 
                      seats: List[str], total_price: float) -> Dict[str, Any]:
        """Create a booking for the authenticated user."""
        if not self.current_user_id:
            return {"success": False, "error": "User not authenticated"}
        
        try:
            from models.booking import BookingCreate
            
            booking_data = BookingCreate(
                movie_id=movie_id,
                movie_title=movie_title,
                showtime=showtime,
                seats=seats,
                total_price=total_price
            )
            
            booking = self.booking_service.create_booking(booking_data, self.current_user_id)
            return {"success": True, "booking": booking}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_user_bookings(self) -> Dict[str, Any]:
        """Get user's bookings."""
        if not self.current_user_id:
            return {"success": False, "error": "User not authenticated"}
        
        try:
            bookings = self.booking_service.get_user_bookings(self.current_user_id)
            return {"success": True, "bookings": bookings}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def cancel_booking(self, booking_id: str) -> Dict[str, Any]:
        """Cancel an entire booking."""
        if not self.current_user_id:
            return {"success": False, "error": "User not authenticated"}
        
        try:
            success = self.booking_service.cancel_booking(booking_id, self.current_user_id)
            if success:
                return {"success": True, "message": "Booking cancelled successfully"}
            else:
                return {"success": False, "error": "Booking not found or access denied"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def cancel_seats(self, booking_id: str, seats: List[str]) -> Dict[str, Any]:
        """Cancel specific seats from a booking."""
        if not self.current_user_id:
            return {"success": False, "error": "User not authenticated"}
        
        try:
            result = self.booking_service.cancel_seats(booking_id, seats, self.current_user_id)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def authenticate_user(self, phone_number: str) -> Dict[str, Any]:
        """Authenticate user by phone number."""
        try:
            user_id = self.phone_auth_service.get_user_by_phone(phone_number)
            if user_id:
                self.current_user_id = user_id
                self.current_phone = phone_number
                return {"success": True, "message": "Authentication successful", "user_id": user_id}
            else:
                return {"success": False, "error": "Phone number not registered"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def register_user(self, phone_number: str, name: str) -> Dict[str, Any]:
        """Register a new user with phone number."""
        try:
            if self.phone_auth_service.is_phone_registered(phone_number):
                # If already registered, try to authenticate instead
                user_id = self.phone_auth_service.get_user_by_phone(phone_number)
                if user_id:
                    self.current_user_id = user_id
                    self.current_phone = phone_number
                    return {"success": True, "message": "Phone already registered - authenticated successfully", "user_id": user_id}
                else:
                    return {"success": False, "error": "Phone number already registered but authentication failed"}
            
            user_id = self.phone_auth_service.create_phone_user(phone_number, name)
            self.current_user_id = user_id
            self.current_phone = phone_number
            
            return {"success": True, "message": "Registration successful", "user_id": user_id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a function call from the agent."""
        function_map = {
            "search_movies": lambda: self.search_movies(arguments.get("query", "")),
            "get_movie_details": lambda: self.get_movie_details(arguments.get("movie_id", "")),
            "check_seat_availability": lambda: self.check_seat_availability(
                arguments.get("movie_id", ""), 
                arguments.get("showtime", "")
            ),
            "create_booking": lambda: self.create_booking(
                arguments.get("movie_id", ""),
                arguments.get("movie_title", ""),
                arguments.get("showtime", ""),
                arguments.get("seats", []),
                arguments.get("total_price", 0.0)
            ),
            "get_user_bookings": lambda: self.get_user_bookings(),
            "cancel_booking": lambda: self.cancel_booking(arguments.get("booking_id", "")),
            "cancel_seats": lambda: self.cancel_seats(
                arguments.get("booking_id", ""),
                arguments.get("seats", [])
            ),
            "authenticate_user": lambda: self.authenticate_user(arguments.get("phone_number", "")),
            "register_user": lambda: self.register_user(
                arguments.get("phone_number", ""),
                arguments.get("name", "")
            )
        }
        
        if function_name in function_map:
            return function_map[function_name]()
        else:
            return {"success": False, "error": f"Unknown function: {function_name}"}

    def process_message(self, user_message: str, phone_number: str = None) -> str:
        """
        Process a user message and return a response.
        
        Args:
            user_message: The user's message
            phone_number: The caller's phone number (for context)
            
        Returns:
            Agent's response
        """
        # Set current phone for context
        if phone_number:
            self.current_phone = phone_number
        
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Create messages for OpenAI API
        messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history
        
        try:
            # Call OpenAI API with function calling
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                tools=self.get_function_definitions(),
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            
            # If the model wants to call a function
            if message.tool_calls:
                tool_call = message.tool_calls[0]
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                # Execute the function
                function_result = self.execute_function(function_name, arguments)
                
                # Add function call and result to conversation
                self.conversation_history.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": message.tool_calls
                })
                
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(function_result)
                })
                
                # Get the final response from the model
                messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history
                
                final_response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=messages
                )
                
                response_content = final_response.choices[0].message.content
                
            else:
                response_content = message.content
            
            # Add assistant response to conversation history
            self.conversation_history.append({"role": "assistant", "content": response_content})
            
            return response_content
            
        except Exception as e:
            error_message = f"I'm sorry, I encountered an error: {str(e)}"
            self.conversation_history.append({"role": "assistant", "content": error_message})
            return error_message

    def reset_conversation(self):
        """Reset the conversation context."""
        self.conversation_history = []
        self.current_user_id = None
        self.current_phone = None