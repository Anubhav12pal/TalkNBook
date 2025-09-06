#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from voice.movie_booking_agent import MovieBookingAgent

# Load environment variables
load_dotenv()

def force_agent_booking():
    # Initialize the REAL MovieBookingAgent with OpenAI GPT-4
    openai_api_key = os.getenv("OPENAI_API")
    if not openai_api_key:
        print("❌ OpenAI API key not found!")
        return
    
    agent = MovieBookingAgent(openai_api_key)
    
    print("🎬 FORCING REAL AGENT BOOKING: DUNE D5, D6")
    print("=" * 60)
    
    # Single comprehensive message
    print("\n👤 USER: My phone is 1555, book Dune 10:00 AM show seats D5 D6 now")
    response = agent.process_message("My phone is 1555, book Dune 10:00 AM show seats D5 D6 now", "1555")
    print(f"🤖 AGENT: {response}")
    
    print("\n" + "=" * 60)
    print("✅ AGENT RESPONSE COMPLETED!")
    print(f"User ID: {agent.current_user_id}")
    
    # Show conversation history to see what functions were called
    print(f"\n📜 CONVERSATION MESSAGES: {len(agent.conversation_history)}")
    for i, msg in enumerate(agent.conversation_history[-6:], 1):  # Show last 6 messages
        role = msg.get('role', 'unknown')
        content = str(msg.get('content', 'N/A'))
        if len(content) > 150:
            content = content[:150] + "..."
        print(f"   {i}. {role.upper()}: {content}")

if __name__ == "__main__":
    force_agent_booking()