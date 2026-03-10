
import os
from dotenv import load_dotenv

load_dotenv()

VIDEO_PATH = "data/input/video.mp4"

AUDIO_PATH = "data/output/audio.wav"
TELUGU_AUDIO_PATH = "data/output/telugu_output.mp3"
FINAL_VIDEO_PATH = "data/output/final_dubbed_video.mp4"

ENGLISH_TRANSCRIPT_FILE = "data/output/transcript_english.txt"
TELUGU_TRANSCRIPT_FILE = "data/output/transcript_telugu.txt"
TELUGU_SRT_FILE = "data/output/telugu_subtitles.srt"

MODEL_SIZE = "base"
MAX_CHARS = 2000


HF_TOKEN = os.getenv("HF_TOKEN")
GEMINI_API_KEY = os.getenv("Gemini_API_Key")

DEVICE = "cpu"

# ── TTS Speed Balancing ──
TELUGU_CHARS_PER_SEC = 5.0        # Avg Telugu characters spoken per second by Murf TTS
