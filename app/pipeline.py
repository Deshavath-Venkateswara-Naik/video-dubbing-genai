import asyncio
import os
from app.config import *
from app.models.whisper_model import load_whisper, transcribe_audio
from app.models.translator_model import translate_to_telugu
from app.services.audio_service import extract_audio, adjust_audio_speed
from app.services.subtitle_service import create_srt
from app.services.tts_service import generate_audio_segment
from app.services.video_service import merge_audio_with_video
from app.services.speaker_service import SpeakerManager
from app.services.audio_mixer import mix_audio


async def run_pipeline():
    print("Step 1: Extracting audio...")
    video = extract_audio(VIDEO_PATH, AUDIO_PATH)

    print("Step 2: Transcribing (Whisper)...")
    model = load_whisper()
    text_segments = transcribe_audio(model, AUDIO_PATH)

    print("Step 3: Analyze Speakers & Gender...")
    speaker_manager = SpeakerManager(auth_token=HF_TOKEN)
    gender_map = speaker_manager.process_segments(AUDIO_PATH, text_segments)

    print("Step 4: Translation & TTS...")

    final_segments = []
    temp_dir = "data/temp_tts"
    os.makedirs(temp_dir, exist_ok=True)

    print(f"Step 5: Generating {len(text_segments)} TTS segments sequentially...")

    for i, seg in enumerate(text_segments):
        print(f"Generating TTS {i+1}/{len(text_segments)}")

        start = seg['start']
        end = seg['end']
        english_text = seg['text']

        gender = gender_map.get(i, "MALE")

        telugu_text = translate_to_telugu(english_text)

        seg_filename = f"{temp_dir}/seg_{i}_{gender}.mp3"
        adjusted_filename = f"{temp_dir}/seg_{i}_{gender}_adjusted.mp3"

        # ✅ Generate TTS ONE BY ONE (no parallel calls)
        await generate_audio_segment(telugu_text, gender, seg_filename)

        # ✅ Adjust Speed to Sync
        target_duration = end - start
        adjust_audio_speed(seg_filename, adjusted_filename, target_duration)

        # small delay to avoid Murf 429 rate limit
        await asyncio.sleep(1.5)

        final_segments.append({
            "start": start,
            "audio_path": adjusted_filename,
            "text": telugu_text
        })

    print("Step 6: Mixing Audio...")
    mix_audio(final_segments, video.duration, TELUGU_AUDIO_PATH)

    print("Step 7: Merging final video...")
    merge_audio_with_video(video, TELUGU_AUDIO_PATH, FINAL_VIDEO_PATH)

    print("\n🎬 ✅ Final dubbed video saved successfully!")
