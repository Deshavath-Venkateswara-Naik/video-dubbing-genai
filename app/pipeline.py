import asyncio
import os
from app.config import *
from pydub import AudioSegment
from app.models.whisper_model import load_whisper, transcribe_audio, transcribe_chunk
from app.models.translator_model import translate_to_telugu
from app.services.audio_service import extract_audio, adjust_audio_speed, get_audio_duration
from app.services.subtitle_service import create_srt
from app.services.tts_service import generate_audio_segment, MALE_VOICE_POOL, FEMALE_VOICE_POOL, VOICE_MAP
from app.services.text_adapter import adapt_text_for_segment
from app.services.video_service import merge_audio_with_video
from app.services.speaker_service import SpeakerManager
from app.services.audio_mixer import mix_audio
from app.services.lipsync_service import LipSyncService


async def run_pipeline():
    # Ensure directories exist
    os.makedirs("data/input", exist_ok=True)
    os.makedirs("data/output", exist_ok=True)
    os.makedirs("data/temp_tts", exist_ok=True)

    print("=" * 60)
    print("🎬 VIDEO DUBBING PIPELINE (Text-Adaptive)")
    print("=" * 60)

    # ── Step 1: Extract Audio ──
    print("\n📹 Step 1: Extracting audio from video...")
    video = extract_audio(VIDEO_PATH, AUDIO_PATH)

    # ── Step 2: Speaker Diarization ──
    print("\n🎙 Step 2: Speaker Diarization...")
    speaker_manager = SpeakerManager(auth_token=HF_TOKEN)
    diarized_turns = speaker_manager.get_diarized_segments(AUDIO_PATH)

    if not diarized_turns:
        print("❌ No speakers detected or diarization failed. Exiting.")
        return

    # ── Step 3: Per-segment processing ──
    print(f"\n📝 Step 3: Processing {len(diarized_turns)} speaker turns...")
    whisper_model = load_whisper()

    speaker_voice_map = {}
    male_count = 0
    female_count = 0
    final_segments = []
    temp_dir = "data/temp_tts"
    os.makedirs(temp_dir, exist_ok=True)

    full_audio = AudioSegment.from_file(AUDIO_PATH)

    # Stats
    stats = {"natural": 0, "corrected": 0, "total": 0}

    for i, turn in enumerate(diarized_turns):
        start = turn['start']
        end = turn['end']
        speaker_id = turn['speaker']
        gender = turn['gender']
        target_duration = end - start

        print(f"\n{'─' * 50}")
        print(f"Turn {i+1}/{len(diarized_turns)}: {speaker_id} ({gender}) [{start:.2f}s - {end:.2f}s] ({target_duration:.2f}s)")

        # ── 1. Extract chunk + Transcribe ──
        chunk_path = f"{temp_dir}/chunk_{i}.wav"
        start_ms = int(start * 1000)
        end_ms = int(end * 1000)
        chunk = full_audio[start_ms:end_ms]
        chunk.export(chunk_path, format="wav")

        english_text = transcribe_chunk(whisper_model, chunk_path)
        if os.path.exists(chunk_path):
            os.remove(chunk_path)

        if not english_text.strip():
            print(f"  ⏭ Skipping empty segment")
            continue

        print(f"  EN: \"{english_text[:80]}{'...' if len(english_text) > 80 else ''}\"")

        # ── 2. Assign voice ──
        if speaker_id not in speaker_voice_map:
            if gender == "MALE":
                voice_id = MALE_VOICE_POOL[male_count % len(MALE_VOICE_POOL)]
                male_count += 1
            else:
                voice_id = FEMALE_VOICE_POOL[female_count % len(FEMALE_VOICE_POOL)]
                female_count += 1
            speaker_voice_map[speaker_id] = voice_id
            print(f"  🔊 Assigned voice {voice_id} to {speaker_id}")

        voice_id = speaker_voice_map[speaker_id]

        # ── 3. Translate ──
        telugu_text = translate_to_telugu(english_text)
        print(f"  TE: \"{telugu_text[:80]}{'...' if len(telugu_text) > 80 else ''}\"")

        # ── 4. Improve & shorten text via Gemini ──
        adapted_text = adapt_text_for_segment(telugu_text, english_text, target_duration)
        if adapted_text != telugu_text:
            print(f"  TE (adapted): \"{adapted_text[:80]}{'...' if len(adapted_text) > 80 else ''}\"")

        # ── 5. Generate TTS ──
        seg_filename = f"{temp_dir}/seg_{i}_{speaker_id}.mp3"
        await generate_audio_segment(adapted_text, voice_id, seg_filename, target_duration=target_duration)

        # ── 6. Timing check + small correction ──
        generated_duration = get_audio_duration(seg_filename)
        ratio = generated_duration / target_duration if target_duration > 0 else 1.0

        print(f"  ⏱ TTS: {generated_duration:.2f}s vs target: {target_duration:.2f}s (ratio: {ratio:.2f})")

        stats["total"] += 1
        final_audio_path = seg_filename  # default: use as-is

        if 0.85 < ratio < 1.15:
            # Small correction — apply gentle atempo
            adjusted_filename = f"{temp_dir}/seg_{i}_{speaker_id}_adjusted.mp3"
            adjust_audio_speed(seg_filename, adjusted_filename, ratio)
            final_audio_path = adjusted_filename
            stats["corrected"] += 1
        else:
            # Keep natural — no speed change
            print(f"  🎯 Keeping natural speed (ratio {ratio:.2f} outside correction range)")
            stats["natural"] += 1

        # Small delay to avoid Murf 429 rate limit
        await asyncio.sleep(1.0)

        final_segments.append({
            "start": start,
            "audio_path": final_audio_path,
            "text": adapted_text
        })

    # ── Diagnostics ──
    print(f"\n{'=' * 50}")
    print(f"📊 Stats: {stats['total']} segments")
    print(f"  🔧 Small speed correction: {stats['corrected']}")
    print(f"  🎯 Kept natural:           {stats['natural']}")
    print(f"{'=' * 50}")

    # ── Step 4: Audio Mixing ──
    print("\n🎶 Step 4: Mixing audio segments...")
    mix_audio(final_segments, video.duration, TELUGU_AUDIO_PATH)

    # ── Step 5: Merge with Video ──
    print("\n🎬 Step 5: Merging final video...")
    merge_audio_with_video(video, TELUGU_AUDIO_PATH, FINAL_VIDEO_PATH)

    # ── Step 6: LipSync (Optional) ──
    print("\n👄 Step 6: LipSync (Wav2Lip)...")
    lipsync_service = LipSyncService()
    if lipsync_service.is_model_available():
        LIP_SYNC_OUTPUT = "data/output/final_dubbed_synced.mp4"
        success = await lipsync_service.sync_lips(FINAL_VIDEO_PATH, TELUGU_AUDIO_PATH, LIP_SYNC_OUTPUT)
        if success:
            import shutil
            shutil.move(LIP_SYNC_OUTPUT, FINAL_VIDEO_PATH)
            print(f"  ✅ LipSync completed!")
        else:
            print("  ⚠ LipSync failed. Using non-synced video.")
    else:
        print("  ⏭ Wav2Lip weights not found. Skipping.")

    print(f"\n{'=' * 60}")
    print(f"🎬 ✅ Final dubbed video: {FINAL_VIDEO_PATH}")
    print(f"{'=' * 60}")
