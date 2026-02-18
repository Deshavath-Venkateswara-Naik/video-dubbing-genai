import os
import torch
import logging
import numpy as np
import librosa
from transformers import pipeline

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GenderClassifier:
    def __init__(self, model_name="alefiury/wav2vec2-large-xlsr-53-gender-recognition-librispeech"):
        """
        Init Gender Classifier using Transformers.
        """
        self.model_name = model_name
        self.classifier = None
        self._load_model()

    def _load_model(self):
        logger.info(f"Loading Gender model: {self.model_name}...")
        try:
            device = 0 if torch.cuda.is_available() else -1
            self.classifier = pipeline("audio-classification", model=self.model_name, device=device)
            logger.info("Gender model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Gender model: {e}")
            self.classifier = None

    def detect_gender(self, audio_paths, min_duration=1.0, fallback="MALE"):
        """
        Detect gender from a list of audio segments (merged).
        
        Args:
            audio_paths (list): List of file paths to merge and analyze.
            min_duration (float): Minimum duration in seconds required to attempt classification.
            fallback (str): Default gender if detection fails or audio is too short.
            
        Returns: "MALE" or "FEMALE"
        """
        if not audio_paths:
            return fallback

        try:
            # Load and merge audio files
            y_all = []
            sr = 16000
            
            for path in audio_paths:
                if os.path.exists(path):
                    try:
                        # Load with librosa (resample to 16k for wav2vec2)
                        y, _ = librosa.load(path, sr=sr)
                        y_all.append(y)
                    except Exception as e:
                        logger.warning(f"Could not load {path}: {e}")
            
            if not y_all:
                return fallback

            # Concatenate
            y_merged = np.concatenate(y_all)
            duration = len(y_merged) / sr
            
            logger.info(f"Merged audio duration: {duration:.2f}s")
            
            if duration < min_duration:
                logger.warning(f"Audio too short ({duration:.2f}s < {min_duration}s). Using fallback: {fallback}")
                return fallback

            if not self.classifier:
                logger.error("Classifier not loaded. Using fallback.")
                return fallback
                
            # Predict
            # pipeline handles raw numpy array
            predictions = self.classifier(y_merged)
            
            # predictions is list of dicts: [{'score': 0.99, 'label': 'female'}, ...]
            # We assume label is 'female' or 'male' (lowercase or other format depending on model)
            
            top_pred = predictions[0]
            label = top_pred['label'].lower()
            score = top_pred['score']
            
            logger.info(f"Gender Prediction: {label} ({score:.4f})")
            
            if "female" in label:
                return "FEMALE"
            else:
                return "MALE"
                
        except Exception as e:
            logger.error(f"Error during gender detection: {e}")
            return fallback
