import json
import asyncio
import websockets
from typing import Dict, Any
from voice.movie_booking_agent import MovieBookingAgent


class WebSocketClient:
    """WebSocket client for handling Retell AI conversations."""
    
    def __init__(self, openai_api_key: str):
        self.agent = MovieBookingAgent(openai_api_key)
        self.active_calls: Dict[str, Dict[str, Any]] = {}
    
    async def handle_message(self, websocket, call_id: str):
        """Handle incoming WebSocket messages for a call."""
        try:
            async for message in websocket:
                data = json.loads(message)
                
                # Process different message types from Retell AI
                if data.get("type") == "transcript":
                    await self.handle_transcript(websocket, call_id, data)
                elif data.get("type") == "call_details":
                    await self.handle_call_details(call_id, data)
                elif data.get("type") == "call_ended":
                    await self.handle_call_ended(call_id, data)
                
        except websockets.exceptions.ConnectionClosed:
            print(f"WebSocket connection closed for call {call_id}")
        except Exception as e:
            print(f"Error handling WebSocket message: {e}")
        finally:
            # Clean up call data
            if call_id in self.active_calls:
                del self.active_calls[call_id]
    
    async def handle_transcript(self, websocket, call_id: str, data: Dict[str, Any]):
        """Handle transcript messages from Retell AI."""
        try:
            # Get the user's message from the transcript
            user_message = data.get("transcript", "")
            
            # Get caller's phone number from call details
            phone_number = self.active_calls.get(call_id, {}).get("from_number")
            
            # Process the message through our agent
            response = self.agent.process_message(user_message, phone_number)
            
            # Send response back to Retell AI
            response_data = {
                "type": "response",
                "response": {
                    "content": response,
                    "content_complete": True
                }
            }
            
            await websocket.send(json.dumps(response_data))
            
        except Exception as e:
            print(f"Error handling transcript: {e}")
            # Send error response
            error_response = {
                "type": "response",
                "response": {
                    "content": "I'm sorry, I encountered an error processing your request. Please try again.",
                    "content_complete": True
                }
            }
            await websocket.send(json.dumps(error_response))
    
    async def handle_call_details(self, call_id: str, data: Dict[str, Any]):
        """Handle call details from Retell AI."""
        # Store call information for context
        self.active_calls[call_id] = {
            "from_number": data.get("from_number"),
            "to_number": data.get("to_number"),
            "call_status": data.get("call_status"),
            "start_timestamp": data.get("start_timestamp")
        }
        
        # Reset agent conversation for new call
        self.agent.reset_conversation()
        
        print(f"Call started: {call_id} from {data.get('from_number')}")
    
    async def handle_call_ended(self, call_id: str, data: Dict[str, Any]):
        """Handle call ended event."""
        print(f"Call ended: {call_id}")
        
        # Clean up call data
        if call_id in self.active_calls:
            del self.active_calls[call_id]
        
        # Reset agent conversation
        self.agent.reset_conversation()