# TalkNBook Voice Integration Setup

This guide explains how to set up and use the voice integration functionality for TalkNBook using Retell AI and OpenAI.

## Prerequisites

1. **OpenAI API Key**: Required for the conversational agent
2. **Retell AI Account**: For voice call handling (optional for testing)
3. **Python Environment**: Backend should be running with all dependencies

## Setup Steps

### 1. Install Dependencies

The required dependencies should already be installed:
```bash
cd backend
source virtual/bin/activate
pip install openai retell-sdk websockets
```

### 2. Environment Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit the `.env` file and add your API keys:
```env
OPENAI_API_KEY=your-actual-openai-api-key-here
RETELL_API_KEY=your-retell-api-key-here  # Optional for testing
```

### 3. Start the Backend Server

```bash
cd backend
source virtual/bin/activate
python main.py
```

The server will start on `http://localhost:8000` with the following new endpoints:
- `POST /webhook` - Retell AI webhook endpoint
- `WebSocket /llm-websocket/{call_id}` - Real-time conversation handling
- `POST /voice/link-phone` - Link phone numbers to user accounts
- `GET /voice/phone-users` - View phone-registered users

## Voice Agent Capabilities

The voice agent can handle the following tasks through natural conversation:

### 1. User Authentication
- **Phone-based login**: "I want to book a movie, my number is +1-555-123-4567"
- **New user registration**: "I'm a new user, my name is John and my number is +1-555-123-4567"

### 2. Movie Discovery
- **Browse all movies**: "What movies are playing?"
- **Search by title**: "Do you have Avengers playing?"
- **Search by genre**: "Show me action movies"
- **Get movie details**: "Tell me about Avengers Endgame"
- **Check showtimes**: "What times is Avengers playing?"

### 3. Booking Operations
- **Check availability**: "Are there seats available for Avengers at 7 PM?"
- **Book tickets**: "Book 2 seats for Avengers at 7 PM"
- **Specify seats**: "I want seats A1 and A2 for the 7 PM show"

### 4. Booking Management
- **View bookings**: "What are my current bookings?"
- **Cancel entire booking**: "Cancel my booking for Avengers tonight"
- **Cancel specific seats**: "Cancel seats A1 and A2 from my Avengers booking"

## Example Conversation Flow

```
User: "Hi, I want to book a movie tonight"
Agent: "Hello! I'd be happy to help you book a movie. First, I need to authenticate you. Can you provide your phone number?"

User: "It's +1-555-123-4567"
Agent: "I don't have that phone number registered. Are you a new user? If so, what's your name?"

User: "Yes, I'm new. My name is John"
Agent: "Great! I've registered you successfully. Now, what movie would you like to see tonight?"

User: "What action movies do you have?"
Agent: "We have several action movies playing: Avengers Endgame, Fast & Furious 9, and Mission Impossible. Which one interests you?"

User: "I'll take Avengers"
Agent: "Avengers Endgame is a great choice! Here are the available showtimes: 10:00 AM, 1:00 PM, 4:00 PM, 7:00 PM, 10:00 PM. What time works for you?"

User: "7 PM please"
Agent: "Perfect! How many seats would you like to book for the 7:00 PM show?"

User: "2 seats"
Agent: "I have plenty of seats available. Would you like me to select the best available seats, or do you have a preference?"

User: "Just pick good ones"
Agent: "I've booked seats A5 and A6 for you for Avengers Endgame at 7:00 PM. The total cost is $24.00. Your booking is confirmed!"
```

## Testing the Voice Integration

### Method 1: Direct API Testing

1. **Register a phone user**:
```bash
curl -X POST http://localhost:8000/voice/link-phone \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1-555-123-4567", "user_id": "existing-user-id"}'
```

2. **Test the agent directly** (you can create a test script):
```python
from voice.movie_booking_agent import MovieBookingAgent

agent = MovieBookingAgent("your-openai-api-key")
response = agent.process_message("What movies are available?", "+1-555-123-4567")
print(response)
```

### Method 2: WebSocket Testing

You can test the WebSocket endpoint using a WebSocket client to simulate Retell AI messages.

### Method 3: Retell AI Integration (Production)

1. Create a Retell AI agent in their dashboard
2. Set the LLM WebSocket URL to: `wss://your-domain.com/llm-websocket/{call_id}`
3. Set the webhook URL to: `https://your-domain.com/webhook`
4. Configure a phone number in Retell AI
5. Call the number to test end-to-end

## Phone Authentication System

The system uses a separate phone authentication service that:
- Links phone numbers to user accounts
- Allows new user registration via phone
- Maintains a separate `phone_users.json` file
- Integrates with existing user system

### Phone Number Linking

Existing web users can link their phone numbers:
```javascript
// From your web app
await fetch('/voice/link-phone', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phone_number: '+1-555-123-4567',
    user_id: 'existing-user-id'
  })
});
```

## Architecture Overview

```
User calls phone number
    ↓
Retell AI receives call
    ↓
Retell AI sends WebSocket messages to /llm-websocket/{call_id}
    ↓
WebSocketClient handles messages
    ↓
MovieBookingAgent processes user requests
    ↓
Agent calls appropriate service functions
    ↓
Response sent back through WebSocket
    ↓
Retell AI converts to speech for user
```

## Troubleshooting

### Common Issues

1. **OpenAI API Errors**: Ensure your API key is valid and has sufficient credits
2. **WebSocket Connection Failed**: Check that the server is running on the correct port
3. **Phone Authentication Fails**: Verify phone number format and registration
4. **Function Calls Fail**: Check that all services are properly initialized

### Debug Mode

Add logging to see what's happening:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testing Without Retell AI

You can test the agent functionality directly without Retell AI by creating a simple script that calls the agent methods directly.

## Production Deployment

For production use:
1. Deploy your FastAPI app to a server with HTTPS
2. Update Retell AI configuration with your production URLs
3. Set up proper environment variables
4. Consider using a real database instead of JSON files
5. Implement proper logging and monitoring

## Next Steps

- Add more sophisticated seat selection logic
- Implement payment processing integration
- Add movie recommendations based on user history
- Implement multi-language support
- Add voice authentication verification