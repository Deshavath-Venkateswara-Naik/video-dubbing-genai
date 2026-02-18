
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("Gemini_API_Key")

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

DEVICE = "cpu"

