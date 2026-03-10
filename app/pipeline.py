import asyncio
import os
from app.config import *
from pydub import AudioSegment
from app.models.whisper_model import load_whisper, transcribe_audio, transcribe_chunk
from app.models.translator_model import translate_to_telugu
from app.services.audio_service import extract_audio, adjust_audio_speed
from app.services.subtitle_service import create_srt
from app.services.tts_service import generate_audio_segment, MALE_VOICE_POOL, FEMALE_VOICE_POOL, VOICE_MAP
from app.services.video_service import merge_audio_with_video
from app.services.speaker_service import SpeakerManager
from app.services.audio_mixer import mix_audio
from app.services.lipsync_service import LipSyncService


async def run_pipeline():
    # Ensure directories exist
    os.makedirs("data/input", exist_ok=True)
    os.makedirs("data/output", exist_ok=True)
    os.makedirs("data/temp_tts", exist_ok=True)

    print("Step 1: Extracting audio...")
    video = extract_audio(VIDEO_PATH, AUDIO_PATH)

    print("Step 2: Analyze Speakers & Diarization...")
    speaker_manager = SpeakerManager(auth_token=HF_TOKEN)
    diarized_turns = speaker_manager.get_diarized_segments(AUDIO_PATH)

    if not diarized_turns:
        print("No speakers detected or diarization failed. Exiting.")
        return

    print(f"Step 3: Transcribing & Translating {len(diarized_turns)} speaker turns...")
    whisper_model = load_whisper()
    
    speaker_voice_map = {}
    male_count = 0
    female_count = 0
    final_segments = []
    temp_dir = "data/temp_tts"
    os.makedirs(temp_dir, exist_ok=True)
    
    full_audio = AudioSegment.from_file(AUDIO_PATH)

    for i, turn in enumerate(diarized_turns):
        start = turn['start']
        end = turn['end']
        speaker_id = turn['speaker']
        gender = turn['gender']

        print(f"Processing Turn {i+1}/{len(diarized_turns)}: {speaker_id} ({gender}) [{start:.2f}s - {end:.2f}s]")

        # 1. Extract audio chunk for transcription
        chunk_path = f"{temp_dir}/chunk_{i}.wav"
        start_ms = int(start * 1000)
        end_ms = int(end * 1000)
        chunk = full_audio[start_ms:end_ms]
        chunk.export(chunk_path, format="wav")

        # 2. Transcribe chunk
        english_text = transcribe_chunk(whisper_model, chunk_path)
        if os.path.exists(chunk_path):
            os.remove(chunk_path)

        if not english_text.strip():
            print(f"Skipping empty segment {i}")
            continue

        # 3. Assign unique voice if not already done
        if speaker_id not in speaker_voice_map:
            if gender == "MALE":
                voice_id = MALE_VOICE_POOL[male_count % len(MALE_VOICE_POOL)]
                male_count += 1
            else:
                voice_id = FEMALE_VOICE_POOL[female_count % len(FEMALE_VOICE_POOL)]
                female_count += 1
            speaker_voice_map[speaker_id] = voice_id
            print(f"Assigned voice {voice_id} to {speaker_id} ({gender})")
        
        voice_id = speaker_voice_map[speaker_id]

        # 4. Translate
        telugu_text = translate_to_telugu(english_text)

        seg_filename = f"{temp_dir}/seg_{i}_{speaker_id}.mp3"
        adjusted_filename = f"{temp_dir}/seg_{i}_{speaker_id}_adjusted.mp3"

        # 5. Generate TTS
        await generate_audio_segment(telugu_text, voice_id, seg_filename)

        # 6. Adjust Speed to Sync
        target_duration = end - start
        adjust_audio_speed(seg_filename, adjusted_filename, target_duration)

        # small delay to avoid Murf 429 rate limit
        await asyncio.sleep(1.5)

        final_segments.append({
            "start": start,
            "audio_path": adjusted_filename,
            "text": telugu_text
        })

    print("Step 4: Mixing Audio...")
    mix_audio(final_segments, video.duration, TELUGU_AUDIO_PATH)

    print("Step 5: Merging final video...")
    merge_audio_with_video(video, TELUGU_AUDIO_PATH, FINAL_VIDEO_PATH)

    print("Step 8: LipSync (Wav2Lip)...")
    lipsync_service = LipSyncService()
    if lipsync_service.is_model_available():
        LIP_SYNC_OUTPUT = "data/output/final_dubbed_synced.mp4"
        success = await lipsync_service.sync_lips(FINAL_VIDEO_PATH, TELUGU_AUDIO_PATH, LIP_SYNC_OUTPUT)
        if success:
            import shutil
            shutil.move(LIP_SYNC_OUTPUT, FINAL_VIDEO_PATH)
            print(f"LipSync completed! Final video: {FINAL_VIDEO_PATH}")
        else:
            print("LipSync failed or was skipped. Using non-synced video.")
    else:
        print("Wav2Lip model weights not found. Skipping LipSync step.")

    print("\n🎬 ✅ Final dubbed video saved successfully!")
