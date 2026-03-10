import torch
from pyannote.audio import Pipeline
import logging
import os
import asyncio
from app.services.gender_service import GenderClassifier
from pydub import AudioSegment
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpeakerManager:
    def __init__(self, auth_token=None):
        self.hf_token = auth_token or os.getenv("HF_TOKEN")
        if self.hf_token:
            os.environ["HF_TOKEN"] = self.hf_token
        else:
            logger.warning("HF_TOKEN not found. Pyannote pipeline might fail if not logged in via CLI.")
        
        # Initialize Gender Classifier
        self.gender_classifier = GenderClassifier()
        
        # Manual Override Config
        # In a real app, this might come from a DB or UI.
        # For now, we check env vars like SPEAKER_00_GENDER=MALE
        self.gender_overrides = {}
        self._load_overrides()

        logger.info("Initializing Pyannote Speaker Diarization Pipeline...")
        try:
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1"
            )
            
            # Send to GPU if available
            if torch.cuda.is_available():
                self.pipeline.to(torch.device("cuda"))
                logger.info("Pyannote pipeline moved to CUDA.")
            else:
                logger.info("Pyannote pipeline running on CPU.")
                
        except Exception as e:
            logger.error(f"Failed to load Pyannote pipeline: {e}")
            self.pipeline = None

    def _load_overrides(self):
        """
        Load gender overrides from environment variables.
        Format: SPEAKER_00_GENDER=FEMALE
        """
        for key, value in os.environ.items():
            if key.startswith("SPEAKER_") and key.endswith("_GENDER"):
                speaker = key.replace("_GENDER", "")
                gender = value.upper()
                if gender in ["MALE", "FEMALE"]:
                    self.gender_overrides[speaker] = gender
                    logger.info(f"Loaded override: {speaker} -> {gender}")

    def get_diarized_segments(self, audio_path):
        """
        1. Run Diarization on audio_path
        2. Group consecutive segments by speaker if they are very close
        3. Detect gender per speaker
        4. Return list of diarized turns with speaker and gender
        """
        if not self.pipeline:
            logger.error("Pipeline not initialized.")
            return []

        # 1. Run Diarization
        logger.info(f"Diarizing audio: {audio_path}...")
        try:
            diarization = self.pipeline(audio_path)
            if hasattr(diarization, "speaker_diarization"):
                 diarization = diarization.speaker_diarization
        except Exception as e:
            logger.error(f"Diarization failed: {e}")
            return []

        speaker_timeline = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speaker_timeline.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker
            })

        if not speaker_timeline:
            return []

        # 2. Group consecutive segments by same speaker if gap is small
        # This prevents over-segmentation for small pauses
        grouped_timeline = []
        if speaker_timeline:
            current = speaker_timeline[0].copy()
            for i in range(1, len(speaker_timeline)):
                next_seg = speaker_timeline[i]
                gap = next_seg['start'] - current['end']
                
                if next_seg['speaker'] == current['speaker'] and gap < 0.5:
                    current['end'] = next_seg['end']
                else:
                    grouped_timeline.append(current)
                    current = next_seg.copy()
            grouped_timeline.append(current)

        # 3. Collect unique speakers and detect gender
        speaker_segments = {}
        for seg in grouped_timeline:
            spk = seg['speaker']
            if spk not in speaker_segments:
                speaker_segments[spk] = []
            speaker_segments[spk].append((seg['start'], seg['end']))

        speaker_gender_map = {}
        full_audio = AudioSegment.from_file(audio_path)
        temp_dir = "data/temp_gender"
        os.makedirs(temp_dir, exist_ok=True)

        for speaker, time_ranges in speaker_segments.items():
            if speaker in self.gender_overrides:
                speaker_gender_map[speaker] = self.gender_overrides[speaker]
                continue

            combined_audio = AudioSegment.empty()
            total_duration = 0
            for start, end in time_ranges:
                start_ms = int(start * 1000)
                end_ms = int(end * 1000)
                combined_audio += full_audio[start_ms:end_ms]
                total_duration += (end - start)
                if total_duration > 20: break # Enough for detection

            merged_filename = f"{temp_dir}/{speaker}_merged_diarized.wav"
            combined_audio.export(merged_filename, format="wav")
            detected_gender = self.gender_classifier.detect_gender([merged_filename], min_duration=2.0)
            speaker_gender_map[speaker] = detected_gender
            if os.path.exists(merged_filename): os.remove(merged_filename)

        # 4. Final list of turns
        final_turns = []
        for seg in grouped_timeline:
            final_turns.append({
                "start": seg['start'],
                "end": seg['end'],
                "speaker": seg['speaker'],
                "gender": speaker_gender_map.get(seg['speaker'], "MALE")
            })

        return final_turns

    def _get_dominant_speaker(self, start, end, timeline):
        """
        Finds which speaker has the most overlap with the given time range.
        """
        speaker_durations = {}
        
        for item in timeline:
            # Calculate overlap
            o_start = max(start, item['start'])
            o_end = min(end, item['end'])
            overlap = o_end - o_start
            
            if overlap > 0:
                spk = item['speaker']
                speaker_durations[spk] = speaker_durations.get(spk, 0) + overlap
        
        if not speaker_durations:
            return "UNKNOWN"
            
        # Return speaker with max overlap volume
        return max(speaker_durations, key=speaker_durations.get)
