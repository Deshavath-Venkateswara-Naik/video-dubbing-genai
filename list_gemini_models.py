
import google.generativeai as genai
from app.config import GEMINI_API_KEY
import os

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("Listing models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
else:
    print("No key found.")
