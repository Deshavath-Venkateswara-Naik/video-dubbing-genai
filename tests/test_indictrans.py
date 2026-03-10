import asyncio
from app.models.translator_model import translate_to_telugu

def test_translation():
    text = "Hello, how are you? The weather is beautiful today."
    print(f"Original: {text}")
    translated = translate_to_telugu(text)
    print(f"Translated: {translated}")

if __name__ == "__main__":
    test_translation()
