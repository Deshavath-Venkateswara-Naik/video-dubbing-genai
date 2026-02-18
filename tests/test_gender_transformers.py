import os
import sys
import logging
import time
import numpy as np
from pydub import AudioSegment

# Add project root to sys path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.gender_service import GenderClassifier

logging.basicConfig(level=logging.INFO)

def test_gender_classifier():
    print("Initializing classifier...")
    classifier = GenderClassifier()
    
    # Check if classifier loaded
    if classifier.classifier is None:
        print("❌ Failed to load classifier!")
        return

    print("✅ Classifier loaded successfully!")
    
    # Create dummy wav file (silence)
    test_file = "test_audio_silence.wav"
    silence = AudioSegment.silent(duration=2000) # 2 seconds
    silence.export(test_file, format="wav")
    
    print(f"Testing with dummy file: {test_file}")
    start_time = time.time()
    gender = classifier.detect_gender([test_file], min_duration=1.0)
    end_time = time.time()
    
    print(f"Prediction on Silence: {gender}")
    print(f"Time taken: {end_time - start_time:.4f}s")
    
    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)
        
    print("Test passed.")

if __name__ == "__main__":
    test_gender_classifier()
