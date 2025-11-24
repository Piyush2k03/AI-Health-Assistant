#!/usr/bin/env python3
"""
Quick script to test if the Gemini API key is valid
Run this to verify your API key before using it in Docker
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("[ERROR] GEMINI_API_KEY not found in environment or .env file")
    exit(1)

api_key = api_key.strip()
print(f"[OK] API Key found (length: {len(api_key)})")
print(f"     Key starts with: {api_key[:10]}...")

try:
    genai.configure(api_key=api_key)
    print("[OK] API key configured successfully")
    
    # Try to list models (this will fail if key is invalid)
    print("     Testing API key by listing models...")
    models = genai.list_models()
    print(f"[OK] API key is VALID! Found {len(list(models))} models")
    
    # Try a simple generation with the model used in the app
    print("     Testing API key with a simple request...")
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Say 'Hello'")
        print(f"[OK] API key works with gemini-2.5-flash! Response: {response.text[:50]}")
    except Exception as e2:
        print(f"[WARNING] gemini-2.5-flash failed: {e2}")
        print("     Trying alternative model...")
        try:
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content("Say 'Hello'")
            print(f"[OK] API key works with gemini-pro! Response: {response.text[:50]}")
        except Exception as e3:
            print(f"[ERROR] Alternative model also failed: {e3}")
            raise e2
    
    print("\n[SUCCESS] Your API key is valid and working!")
    
except Exception as e:
    print(f"\n[ERROR] API key test FAILED:")
    print(f"        Error: {str(e)}")
    print("\nPossible issues:")
    print("  1. API key is invalid or expired")
    print("  2. API key doesn't have required permissions")
    print("  3. API key is for a different Google Cloud project")
    print("  4. Check your Google Cloud Console for API key status")
    print("\n  Get a new key from: https://makersuite.google.com/app/apikey")
    exit(1)

