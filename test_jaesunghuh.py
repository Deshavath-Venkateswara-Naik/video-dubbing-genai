from transformers import pipeline, AutoModelForAudioClassification, AutoFeatureExtractor
import torch

model_id = "JaesungHuh/voice-gender-classifier"

print(f"Attempting to load {model_id} with transformers...")
try:
    classifier = pipeline("audio-classification", model=model_id)
    print("✅ Success with pipeline!")
except Exception as e:
    print(f"❌ Pipeline failed: {e}")
    
try:
    model = AutoModelForAudioClassification.from_pretrained(model_id)
    print("✅ Success with AutoModelForAudioClassification!")
except Exception as e:
    print(f"❌ AutoModelForAudioClassification failed: {e}")
