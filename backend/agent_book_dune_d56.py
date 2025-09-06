#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from voice.movie_booking_agent import MovieBookingAgent

# Load environment variables
load_dotenv()

def agent_book_dune_d56():
    # Initialize the REAL MovieBookingAgent with OpenAI GPT-4
    openai_api_key = os.getenv("OPENAI_API")
    if not openai_api_key:
        print("❌ OpenAI API key not found!")
        return
    
    agent = MovieBookingAgent(openai_api_key)
    
    print("🎬 REAL AGENT BOOKING: DUNE D5, D6")
    print("=" * 60)
    print("Using GPT-4 powered MovieBookingAgent")
    print("User: aa@gmail.com (phone users don't exist for this user)")
    print("We'll use phone 1555 (Demo User) for this test")
    print("=" * 60)
    
    # Step 1: Authentication
    print("\n👤 USER: Hi, authenticate me with phone 1555")
    response1 = agent.process_message("Hi, authenticate me with phone 1555", "1555")
    print(f"🤖 AGENT: {response1}")
    
    # Step 2: Specific booking request
    print("\n👤 USER: I want to book Dune movie for 10 AM show. Book me seats D5 and D6 please.")
    response2 = agent.process_message("I want to book Dune movie for 10 AM show. Book me seats D5 and D6 please.", "1555")
    print(f"🤖 AGENT: {response2}")
    
    # Step 3: Confirmation if needed
    print("\n👤 USER: Yes, please confirm and complete the booking.")
    response3 = agent.process_message("Yes, please confirm and complete the booking.", "1555")
    print(f"🤖 AGENT: {response3}")
    
    print("\n" + "=" * 60)
    print("✅ REAL AGENT BOOKING CONVERSATION COMPLETED!")
    print(f"📱 Agent Phone: {agent.current_phone}")
    print(f"👤 Agent User ID: {agent.current_user_id}")
    
    return agent

if __name__ == "__main__":
    agent_book_dune_d56()