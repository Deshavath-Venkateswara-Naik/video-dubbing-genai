import asyncio
import os
import sys

# Add project root to sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.tts_service import generate_audio_segment

async def test_murf_tts():
    print("Testing Murf TTS Service...")
    
    # Test cases
    test_cases = [
        {"text": "Hello, this is a test for the male voice using Murf.", "gender": "MALE", "file": "test_male.mp3"},
        {"text": "Hello, this is a test for the female voice using Murf.", "gender": "FEMALE", "file": "test_female.mp3"}
    ]
    
    for case in test_cases:
        output_file = case["file"]
        if os.path.exists(output_file):
            os.remove(output_file)
            
        print(f"Generating audio for {case['gender']} voice...")
        try:
            await generate_audio_segment(case["text"], case["gender"], output_file)
            
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                print(f"✅ Success: {output_file} created ({os.path.getsize(output_file)} bytes).")
            else:
                print(f"❌ Failed: {output_file} was not created or is empty.")
                
        except Exception as e:
            print(f"❌ Error during generation: {e}")

if __name__ == "__main__":
    asyncio.run(test_murf_tts())
