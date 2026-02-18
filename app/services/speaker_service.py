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

    def process_segments(self, audio_path, text_segments):
        """
        1. Run Diarization on audio_path
        2. Map Whisper text segments to speakers
        3. Collect audio segments per speaker
        4. Detect gender per speaker (merged audio)
        5. Return mapping
        """
        if not self.pipeline:
            logger.error("Pipeline not initialized. Returning default MALE for all.")
            return {i: "MALE" for i in range(len(text_segments))}

        # 1. Run Diarization
        logger.info(f"Diarizing audio: {audio_path}...")
        try:
            diarization = self.pipeline(audio_path)
            if hasattr(diarization, "speaker_diarization"):
                 diarization = diarization.speaker_diarization
        except Exception as e:
            logger.error(f"Diarization failed: {e}")
            return {i: "MALE" for i in range(len(text_segments))}

        speaker_timeline = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speaker_timeline.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker
            })

        # 2. Map Text Segments to Speakers / Identify Speakers
        # We need to know which speakers exist and what segments they own
        segment_speaker_map = {} # segment_index -> speaker_label
        speaker_segments = {} # speaker_label -> list of (start, end) tuples
        
        for i, seg in enumerate(text_segments):
            seg_start = seg['start']
            seg_end = seg['end']
            
            # Find dominant speaker for this segment
            speaker = self._get_dominant_speaker(seg_start, seg_end, speaker_timeline)
            segment_speaker_map[i] = speaker
            
            if speaker != "UNKNOWN":
                if speaker not in speaker_segments:
                    speaker_segments[speaker] = []
                speaker_segments[speaker].append((seg_start, seg_end))

        # 3. Detect Gender Per Speaker
        speaker_gender_map = {}
        
        # Load audio once to extract chunks
        full_audio = AudioSegment.from_file(audio_path)
        
        temp_dir = "data/temp_gender"
        os.makedirs(temp_dir, exist_ok=True)
        
        for speaker, time_ranges in speaker_segments.items():
            # Check override first
            if speaker in self.gender_overrides:
                speaker_gender_map[speaker] = self.gender_overrides[speaker]
                logger.info(f"Speaker {speaker} using override: {speaker_gender_map[speaker]}")
                continue
                
            # Extract and merge audio segments for this speaker
            speaker_audio_paths = []
            
            # Limit to e.g., first 5 segments or total 10 seconds to save time/space if needed
            # But user requested "merged audio", implying utilizing available data for better accuracy.
            # We'll extract all segments assigned to this speaker.
            
            combined_audio = AudioSegment.empty()
            total_duration = 0
            
            for start, end in time_ranges:
                # pydub works in millis
                start_ms = int(start * 1000)
                end_ms = int(end * 1000)
                chunk = full_audio[start_ms:end_ms]
                combined_audio += chunk
                total_duration += (end - start)
                
                # Optimization: If we have enough audio (e.g. 30s), strictly sufficient for detection
                if total_duration > 30: 
                    break
            
            # Save merged file
            merged_filename = f"{temp_dir}/{speaker}_merged.wav"
            combined_audio.export(merged_filename, format="wav")
            
            # 4. Run Detection
            detected_gender = self.gender_classifier.detect_gender(
                [merged_filename], 
                min_duration=2.0 # Increase min duration as requested
            )
            
            speaker_gender_map[speaker] = detected_gender
            logger.info(f"Speaker {speaker} ({total_duration:.2f}s audio) -> Detected: {detected_gender}")
            
            # Cleanup
            if os.path.exists(merged_filename):
                os.remove(merged_filename)

        # 5. Build final map
        final_gender_map = {}
        for i, speaker in segment_speaker_map.items():
            final_gender_map[i] = speaker_gender_map.get(speaker, "MALE") # Default fallback
            
        return final_gender_map

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
