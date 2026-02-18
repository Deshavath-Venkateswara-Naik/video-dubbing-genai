import asyncio
from app.utils import align_text_with_speakers
# Mock services
from unittest.mock import MagicMock

# Simple mock test for logic
def test_alignment():
    print("Testing Alignment...")
    text_segments = [
        {"start": 0.0, "end": 4.0, "text": "Hello world"},
        {"start": 4.5, "end": 8.0, "text": "How are you?"}
    ]
    
    speaker_segments = [
        {"start": 0.0, "end": 4.2, "speaker": "SPEAKER_00"},
        {"start": 4.3, "end": 10.0, "speaker": "SPEAKER_01"}
    ]
    
    aligned = align_text_with_speakers(text_segments, speaker_segments)
    
    assert aligned[0]['speaker'] == "SPEAKER_00"
    assert aligned[1]['speaker'] == "SPEAKER_01"
    print("✅ Alignment Logic Passed")

def test_gender_logic():
    print("Testing Gender Logic...")
    # Mock detect_gender_for_segment
    # We can't easily mock the import inside the function unless we patch it, 
    # but let's just test the map creation logic if we can mock the service response.
    # For now, just a placeholder.
    pass

if __name__ == "__main__":
    test_alignment()
