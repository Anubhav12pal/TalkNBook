#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from voice.movie_booking_agent import MovieBookingAgent

# Load environment variables
load_dotenv()

def complete_agent_booking():
    # Initialize the REAL MovieBookingAgent with OpenAI
    openai_api_key = os.getenv("OPENAI_API")
    if not openai_api_key:
        print("❌ OpenAI API key not found!")
        return
    
    agent = MovieBookingAgent(openai_api_key)
    
    print("🎬 COMPLETING REAL AGENT BOOKING")
    print("=" * 60)
    
    # Step 1: Authenticate user
    print("👤 USER: My phone is 1555")
    response1 = agent.process_message("My phone is 1555", "1555")
    print(f"🤖 AGENT: {response1}")
    
    # Step 2: Direct booking request with all details
    print("\n👤 USER: Book Dune movie, 10:00 AM show, seats B7 B8 B9, total $36")
    response2 = agent.process_message("Book Dune movie, 10:00 AM show, seats B7 B8 B9, total $36", "1555")
    print(f"🤖 AGENT: {response2}")
    
    print("\n" + "=" * 60)
    print("✅ AGENT BOOKING REQUEST COMPLETED!")
    print(f"User ID: {agent.current_user_id}")
    
    return agent

if __name__ == "__main__":
    complete_agent_booking()