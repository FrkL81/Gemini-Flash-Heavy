#!/usr/bin/env python3
"""
Debug script to see exactly what's happening with agent responses
"""

from agent import OpenRouterAgent

def test_single_agent():
    print("=== Testing Single Agent with Debug Logging ===")
    
    try:
        # Create agent with debug logging enabled
        agent = OpenRouterAgent(silent=False, model="gemini-2.0-flash")
        
        print("\n--- Testing simple query ---")
        result = agent.run("What is 2 + 2?")
        
        print(f"\n--- Final Result ---")
        print(f"Result: '{result}'")
        print(f"Result type: {type(result)}")
        print(f"Result length: {len(result)}")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_agent()