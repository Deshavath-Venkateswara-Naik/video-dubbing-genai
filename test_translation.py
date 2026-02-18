import sys
import os

# Add project root to sys path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.models.translator_model import translate_to_telugu
import time

def test_translation():
    text = "Hello, how are you effectively using Artificial Intelligence today?"
    print(f"Original: {text}")
    
    start = time.time()
    translated = translate_to_telugu(text)
    end = time.time()
    
    print(f"Translated: {translated}")
    print(f"Time taken: {end - start:.4f}s")
    
    if translated and translated != text:
        print("✅ Translation successful!")
    else:
        print("❌ Translation failed or returned original text.")

if __name__ == "__main__":
    test_translation()
