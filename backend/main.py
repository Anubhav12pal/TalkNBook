import os
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import websockets
import json

# Load environment variables from .env file (but prioritize shell environment)
load_dotenv()

from routes.auth import router as auth_router
from routes.bookings import router as bookings_router
from routes.movies import router as movies_router
from voice.websocket_client import WebSocketClient

app = FastAPI(title="TalkNBook API", description="Movie booking application API")

# Initialize WebSocket client with OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_KEY") or os.getenv("OPENAI_API_KEY", "your-openai-api-key")
print(f"OpenAI API Key configured: {'✅ YES' if OPENAI_API_KEY != 'your-openai-api-key' else '❌ NO'}")
websocket_client = WebSocketClient(OPENAI_API_KEY)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(bookings_router)
app.include_router(movies_router)

@app.get("/")
def read_root():
    return {"message": "TalkNBook API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Voice AI Endpoints

@app.post("/webhook")
async def retell_webhook(request: Request):
    """Handle Retell AI webhook events."""
    try:
        data = await request.json()
        
        # Handle different webhook event types
        event_type = data.get("event")
        
        if event_type == "call_started":
            print(f"Call started: {data.get('call_id')}")
            return {"message": "Call started webhook received"}
            
        elif event_type == "call_ended":
            print(f"Call ended: {data.get('call_id')}")
            return {"message": "Call ended webhook received"}
            
        elif event_type == "call_analyzed":
            print(f"Call analyzed: {data.get('call_id')}")
            return {"message": "Call analyzed webhook received"}
            
        else:
            print(f"Unknown webhook event: {event_type}")
            return {"message": "Webhook received"}
            
    except Exception as e:
        print(f"Error handling webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@app.websocket("/llm-websocket/{call_id}")
async def llm_websocket(websocket: WebSocket, call_id: str):
    """WebSocket endpoint for Retell AI LLM integration."""
    await websocket.accept()
    
    try:
        print(f"WebSocket connection established for call: {call_id}")
        await websocket_client.handle_message(websocket, call_id)
        
    except Exception as e:
        print(f"WebSocket error for call {call_id}: {e}")
    finally:
        print(f"WebSocket connection closed for call: {call_id}")


# Voice Agent Management Endpoints

@app.post("/voice/link-phone")
async def link_phone_to_user(request: Request):
    """Link a phone number to an existing user account."""
    try:
        data = await request.json()
        phone_number = data.get("phone_number")
        user_id = data.get("user_id")
        
        if not phone_number or not user_id:
            raise HTTPException(status_code=400, detail="Phone number and user ID required")
        
        from services.phone_auth_service import PhoneAuthService
        phone_auth = PhoneAuthService()
        
        success = phone_auth.link_phone_to_user(phone_number, user_id)
        
        if success:
            return {"message": "Phone number linked successfully"}
        else:
            return {"error": "Phone number already linked to another account"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/voice/phone-users")
async def get_phone_users():
    """Get all phone-registered users (for admin/testing)."""
    try:
        from services.phone_auth_service import PhoneAuthService
        phone_auth = PhoneAuthService()
        
        phone_users = phone_auth._load_phone_users()
        return {"phone_users": phone_users}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)