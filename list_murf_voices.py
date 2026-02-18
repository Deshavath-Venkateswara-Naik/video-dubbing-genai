import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API Key
api_key = os.getenv("falcon_api_key")
if not api_key:
    print("Error: falcon_api_key not found in .env")
    exit(1)

print(f"Using API Key: {api_key[:5]}...")

# Murf API Endpoint for listing voices
url = "https://api.murf.ai/v1/speech/voices"

headers = {
    "api-key": api_key,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

try:
    print(f"Sending request to {url}...")
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        voices = response.json()
        print(f"Total voices found: {len(voices)}")
        
        # Filter for Telugu voices
        telugu_voices = []
        for v in voices:
            # Check various fields where language might be stored
            lang = v.get('language', '').lower()
            locale = v.get('locale', '').lower()
            display_name = v.get('displayName', '').lower()
            
            if 'telugu' in lang or 'te-in' in locale or 'telugu' in display_name:
                telugu_voices.append(v)
        
        print("\n--- Telugu Voices ---")
        for tv in telugu_voices:
            print(f"ID: {tv.get('voiceId')}, Name: {tv.get('displayName')}, Gender: {tv.get('gender')}, Styles: {tv.get('styles')}")
            
        if not telugu_voices:
            print("No Telugu voices found using the provided API key.")

    else:
        print("Error Response:")
        print(response.text)

except Exception as e:
    print(f"An error occurred: {e}")
