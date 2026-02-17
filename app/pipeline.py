from app.config import *
from app.models.whisper_model import load_whisper, transcribe_audio
from app.models.translator_model import translate_to_telugu
from app.services.audio_service import extract_audio
from app.services.subtitle_service import create_srt
from app.services.tts_service import generate_telugu_audio
from app.services.video_service import merge_audio_with_video

def run_pipeline():

    print("Step 1: Extracting audio...")
    video = extract_audio(VIDEO_PATH, AUDIO_PATH)

    print("Step 2: Transcribing...")
    model = load_whisper()
    english_text = transcribe_audio(model, AUDIO_PATH)

    with open(ENGLISH_TRANSCRIPT_FILE, "w", encoding="utf-8") as f:
        f.write(english_text)

    print("Step 3: Translating...")
    telugu_text = translate_to_telugu(english_text)

    with open(TELUGU_TRANSCRIPT_FILE, "w", encoding="utf-8") as f:
        f.write(telugu_text)

    print("Step 4: Creating SRT...")
    create_srt(video.duration, telugu_text, TELUGU_SRT_FILE)

    print("Step 5: Generating Telugu Audio...")
    generate_telugu_audio(telugu_text, TELUGU_AUDIO_PATH)

    print("Step 6: Merging final video...")
    merge_audio_with_video(video, TELUGU_AUDIO_PATH, FINAL_VIDEO_PATH)

    print("\n🎬 ✅ Final dubbed video saved successfully!")
