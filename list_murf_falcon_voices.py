import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("falcon_api_key")
url = "https://api.murf.ai/v1/speech/voices"
headers = {"api-key": api_key, "Content-Type": "application/json", "Accept": "application/json"}
params = {"model": "FALCON"}

try:
    print(f"Fetching Falcon voices from {url}...")
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        voices = response.json()
        print(f"Total Falcon voices: {len(voices)}")
        telugu_voices = [v for v in voices if 'telugu' in str(v).lower() or 'te-in' in str(v).lower()]
        print(f"Telugu Falcon voices: {len(telugu_voices)}")
        for v in telugu_voices:
            print(f"ID: {v.get('voiceId')}, Name: {v.get('displayName')}, Gender: {v.get('gender')}")
            
        if not telugu_voices:
             # Print a few to see format
             print("Sample voices:")
             for v in voices[:3]:
                 print(v)
    else:
        print(response.text)
except Exception as e:
    print(e)
