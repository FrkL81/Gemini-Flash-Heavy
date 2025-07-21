#!/usr/bin/env python3
"""
Simple test to identify the core issue
"""

import os
from agent import OpenRouterAgent

def main():
    print("Testing single agent...")
    
    # Check API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not set!")
        return
    
    print(f"API key found (length: {len(api_key)})")
    
    try:
        # Test single agent
        print("Creating agent...")
        agent = OpenRouterAgent(silent=False, model="gemini-2.0-flash")
        
        print("Running simple test...")
        result = agent.run("Say hello")
        
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()