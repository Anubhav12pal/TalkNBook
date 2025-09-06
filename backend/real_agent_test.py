#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from voice.movie_booking_agent import MovieBookingAgent

# Load environment variables
load_dotenv()

def test_real_agent():
    # Initialize the REAL MovieBookingAgent with OpenAI
    openai_api_key = os.getenv("OPENAI_API")
    if not openai_api_key:
        print("❌ OpenAI API key not found!")
        return
    
    agent = MovieBookingAgent(openai_api_key)
    
    print("🎬 REAL OPENAI AGENT CONVERSATION")
    print("=" * 60)
    print("Using actual GPT-4 powered MovieBookingAgent")
    print("Phone number: 1555 (Demo User from phone_users.json)")
    print("=" * 60)
    
    # Step 1: Start conversation with authentication
    print("\n👤 USER: Hi, my phone is 1555. I want to book some movie tickets.")
    response1 = agent.process_message("Hi, my phone is 1555. I want to book some movie tickets.", "1555")
    print(f"🤖 AGENT: {response1}")
    
    # Step 2: Ask for specific movie booking  
    print("\n👤 USER: I want to book Dune for 10 AM show. Get me seats B7, B8, B9 please.")
    response2 = agent.process_message("I want to book Dune for 10 AM show. Get me seats B7, B8, B9 please.", "1555")
    print(f"🤖 AGENT: {response2}")
    
    # Step 3: Confirm or respond to agent
    print("\n👤 USER: Yes please confirm the booking.")
    response3 = agent.process_message("Yes please confirm the booking.", "1555")
    print(f"🤖 AGENT: {response3}")
    
    print("\n" + "=" * 60)
    print("✅ REAL AGENT CONVERSATION COMPLETED!")
    print(f"📱 Agent's current phone: {agent.current_phone}")
    print(f"👤 Agent's current user ID: {agent.current_user_id}")
    
    # Show conversation history for verification
    print(f"\n📜 CONVERSATION HISTORY ({len(agent.conversation_history)} messages):")
    for i, msg in enumerate(agent.conversation_history, 1):
        role = msg.get('role', 'unknown')
        content = msg.get('content', 'N/A')
        if content and len(str(content)) > 100:
            content = str(content)[:100] + "..."
        print(f"   {i}. {role.upper()}: {content}")

if __name__ == "__main__":
    test_real_agent()