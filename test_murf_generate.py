import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("falcon_api_key")
url = "https://api.murf.ai/v1/speech/generate"

headers = {
    "api-key": api_key,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

payload = {
    "voiceId": "en-US-zion",
    "style": "Conversational",
    "text": "Namaste, this is a test for Murf Falcon API.",
    "rate": 0,
    "pitch": 0,
    "sampleRate": 24000,
    "format": "MP3",
    "channel": "MONO",
    "encode_as_base64": False
}

try:
    print(f"Sending request to {url}...")
    response = requests.post(url, headers=headers, json=payload)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        content_type = response.headers.get('Content-Type')
        print(f"Content-Type: {content_type}")
        
        # Check if it's audio or JSON
        if 'application/json' in content_type:
            print("Response is JSON:", response.json())
        else:
            print(f"Received audio content of size: {len(response.content)} bytes")
            with open("test_output.mp3", "wb") as f:
                f.write(response.content)
            print("Saved to test_output.mp3")
    else:
        print("Error Response:")
        print(response.text)

except Exception as e:
    print(f"An error occurred: {e}")
