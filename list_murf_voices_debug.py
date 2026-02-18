import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("falcon_api_key")
url = "https://api.murf.ai/v1/speech/voices"
headers = {"api-key": api_key, "Content-Type": "application/json", "Accept": "application/json"}

try:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        voices = response.json()
        languages = set()
        for v in voices:
            languages.add(f"{v.get('language')} ({v.get('locale')})")
        
        print("Available Languages:")
        for l in sorted(languages):
            print(l)
            
        # Check specifically for 'Te' or 'Telugu' in any field
        print("\nSearching for 'Te' or 'Telugu' in any field...")
        for v in voices:
            if 'telugu' in str(v).lower() or 'te-in' in str(v).lower():
                print(v)
    else:
        print(response.text)
except Exception as e:
    print(e)
