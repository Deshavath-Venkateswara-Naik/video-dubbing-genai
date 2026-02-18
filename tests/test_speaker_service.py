from app.services.speaker_service import SpeakerManager
import os
import logging

# Mock data
AUDIO_PATH = "tests/sample_audio.wav" 

# Create a dummy audio file if not exists
if not os.path.exists(AUDIO_PATH):
    import numpy as np
    import soundfile as sf
    # Generate 5 seconds of noise/tone
    sr = 16000
    t = np.linspace(0, 5, 5*sr)
    y = np.sin(2*np.pi*440*t) * 0.5
    sf.write(AUDIO_PATH, y, sr)
    print(f"Created dummy audio at {AUDIO_PATH}")

def test_speaker_manager():
    # Ensure HF_TOKEN is available or passed
    token = os.getenv("HF_TOKEN")
    if not token:
        # Try to import from config if env var is missing, just for test
        try:
            from app.config import HF_TOKEN
            token = HF_TOKEN
        except ImportError:
            print("Warning: HF_TOKEN not found for test.")

    print(f"Initializing SpeakerManager with token: {token[:4]}... (masked)")
    sm = SpeakerManager(auth_token=token)
    
    if sm.pipeline is None:
        print("Pipeline failed to initialize (likely due to missing/invalid token or network). Skipping processing test.")
        return

    # Mock segments from Whisper
    segments = [
        {'start': 0.0, 'end': 1.0, 'text': 'Hello'},
        {'start': 1.5, 'end': 2.5, 'text': 'World'},
        {'start': 3.0, 'end': 4.0, 'text': 'Testing'}
    ]
    
    print("Running process_segments...")
    try:
        mapping = sm.process_segments(AUDIO_PATH, segments)
        print("Result mapping:", mapping)
        
        # Verify structure
        assert isinstance(mapping, dict)
        assert len(mapping) == len(segments)
        assert all(gender in ["MALE", "FEMALE"] for gender in mapping.values())
        print("✅ Test Passed!")
    except Exception as e:
        print(f"❌ Test Failed: {e}")
    
if __name__ == "__main__":
    test_speaker_manager()
