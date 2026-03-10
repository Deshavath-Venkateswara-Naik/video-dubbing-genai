import asyncio
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==============================
# Murf API Configuration
# ==============================

MURF_API_URL = "https://api.murf.ai/v1/speech/generate"
API_KEY = os.getenv("falcon_api_key")

if not API_KEY:
    raise ValueError("Error: falcon_api_key not found in environment variables.")

# ==============================
# Voice Mapping (Falcon Voices)
# ==============================

VOICE_MAP = {
    "MALE": "en-US-zion",
    "FEMALE": "en-US-josie"
}

# Unique voice pools for diarization
MALE_VOICE_POOL = [
    "en-US-zion",
    "en-US-carter",
    "en-US-miles",
    "en-UK-peter",
    "en-AU-leyton",
    "en-US-ronnie",
    "en-UK-freddie"
]

FEMALE_VOICE_POOL = [
    "en-US-josie",
    "en-US-natalie",
    "en-US-samantha",
    "en-UK-hazel",
    "en-UK-juliet",
    "en-AU-ivy",
    "en-US-natalie"
]

# ==============================
# Sync Murf API Call
# ==============================

def _generate_audio_sync(text, voice_id, output_path):
    """
    Calls Murf API, retrieves JSON response,
    extracts audioFile URL, downloads MP3,
    and saves it locally.
    """

    headers = {
        "api-key": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "voiceId": voice_id,
        "style": "Conversational",
        "text": text,
        "rate": 0,
        "pitch": 0,
        "sampleRate": 24000,
        "format": "MP3",
        "channel": "MONO",
        "encode_as_base64": False
    }

    # Step 1: Generate audio
    response = requests.post(MURF_API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(
            f"Murf API failed with status {response.status_code}: {response.text}"
        )

    try:
        data = response.json()
    except Exception:
        raise Exception("Murf API did not return valid JSON.")

    # Step 2: Extract audio URL
    audio_url = data.get("audioFile")

    if not audio_url:
        raise Exception(f"No audioFile returned from Murf: {data}")

    # Step 3: Download MP3
    audio_response = requests.get(audio_url)

    if audio_response.status_code != 200:
        raise Exception("Failed to download audio file from Murf.")

    # Step 4: Save locally
    with open(output_path, "wb") as f:
        f.write(audio_response.content)

# ==============================
# Async Wrapper (Non-blocking)
# ==============================

async def generate_audio_segment(text, voice_id, output_path):
    """
    Async wrapper for Murf TTS.
    Runs blocking HTTP request in background thread.
    """

    # Run sync Murf call in separate thread
    await asyncio.to_thread(_generate_audio_sync, text, voice_id, output_path)

    # Small delay to avoid 429 concurrency issues (free plan safe)
    await asyncio.sleep(1.5)
