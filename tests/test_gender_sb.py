import os
import sys
# Add project root to sys path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.gender_service_sb import SpeechBrainGenderClassifier
import logging
import time

logging.basicConfig(level=logging.INFO)

def test_gender_classifier():
    print("Initializing classifier...")
    classifier = SpeechBrainGenderClassifier()
    
    # Check if classifier loaded
    if classifier.classifier is None:
        print("❌ Failed to load classifier!")
        return

    print("✅ Classifier loaded successfully!")
    
    # Create dummy wav file for testing if real ones don't exist
    # Or just try to classify existing ones if we find them.
    # Let's create a dummy silent wav using pydub or similar if possible, 
    # but installing pydub in the test script might be risky if not in requirements.
    # Actually pydub is in requirements.
    
    from pydub import AudioSegment
    import numpy as np
    
    # Create a 1-second silence
    silence = AudioSegment.silent(duration=1000)
    test_file = "test_audio.wav"
    silence.export(test_file, format="wav")
    
    print(f"Testing with dummy file: {test_file}")
    start_time = time.time()
    gender = classifier.classify_file(test_file)
    end_time = time.time()
    
    print(f"Prediction: {gender}")
    print(f"Time taken: {end_time - start_time:.4f}s")
    
    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)
        
    print("Basic functional test passed (even if prediction on silence is random).")

if __name__ == "__main__":
    test_gender_classifier()
