import os
import torch
import logging
from speechbrain.inference.classifiers import EncoderClassifier

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpeechBrainGenderClassifier:
    def __init__(self, source="JaesungHuh/voice-gender-classifier", savedir="tmp_model"):
        """
        Init SpeechBrain Classifier using the `JaesungHuh/voice-gender-classifier` model.
        This model is a pre-trained ECAPA-TDNN based classifier on VoxCeleb.
        """
        self.source = source
        self.savedir = savedir
        self.classifier = None
        self._load_model()

    def _load_model(self):
        logger.info(f"Loading SpeechBrain model from {self.source}...")
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.classifier = EncoderClassifier.from_hparams(
                source=self.source,
                savedir=self.savedir,
                run_opts={"device": device}
            )
            logger.info(f"SpeechBrain model loaded successfully on {device}.")
        except Exception as e:
            logger.error(f"Failed to load SpeechBrain model: {e}")
            self.classifier = None

    def classify_file(self, audio_path):
        """
        Classify a single audio file.
        Returns: "MALE" or "FEMALE"
        """
        if not self.classifier:
            logger.error("Classifier not loaded.")
            return "MALE" # Default fallback
        
        try:
            # Load and classify
            signal = self.classifier.load_audio(audio_path)
            # Add batch dimension
            signal = signal.unsqueeze(0) 
            
            # Predict
            # Output is typically (out_prob, score, index, text_lab)
            prediction = self.classifier.classify_batch(signal)
            
            # text_lab is a list of labels for the batch
            item_labels = prediction[3]
            label = item_labels[0] # Get first item label
            
            # Normalize label
            label = label.upper()
            if "FEMALE" in label:
                return "FEMALE"
            else:
                return "MALE"
                
        except Exception as e:
            logger.error(f"Error classifying file {audio_path}: {e}")
            return "MALE"
