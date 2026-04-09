
import asyncio
import os
import json
from app.config import *
from pydub import AudioSegment
from app.models.whisper_model import load_whisper, transcribe_audio
from app.services.audio_service import extract_audio, adjust_audio_speed, get_audio_duration
from app.services.openai_service import openai_service
from app.services.tts_service import generate_audio_segment, VOICE_MAP
from app.services.video_service import merge_audio_with_video
from app.services.audio_mixer import mix_audio
from app.services.google_translate_service import google_translate_service
from app.services.lipsync_service import LipSyncService


async def run_pipeline():
    # Ensure directories exist
    os.makedirs("data/input", exist_ok=True)
    os.makedirs("data/output", exist_ok=True)
    os.makedirs("data/temp_tts", exist_ok=True)

    print("=" * 60)
    print("🎬 VIDEO DUBBING PIPELINE (OpenAI Optimized)")
    print("=" * 60)

    # ── Step 1: Extract Audio ──
    print("\n📹 Step 1: Extracting audio from video...")
    video = extract_audio(VIDEO_PATH, AUDIO_PATH)

    # ── Step 2: Faster Whisper Transcription & Segmentation ──
    print("\n📝 Step 2: Transcribing and Segmenting via Faster Whisper...")
    whisper_model = load_whisper()
    english_segments = transcribe_audio(whisper_model, AUDIO_PATH)
    
    if not english_segments:
        print("❌ No speech detected. Exiting.")
        return

    # Store English segments
    openai_service.save_segments(english_segments, ENGLISH_SEGMENTS_FILE)
    print(f"  ✅ Saved {len(english_segments)} English segments to {ENGLISH_SEGMENTS_FILE}")

    # ── Step 3: Translation & Polishing ──
    # ── 3a. Initial Translation via Google Translate ──
    print("\n🌍 Step 3a: Initial Translation via Google Translate...")
    initial_telugu_segments = google_translate_service.translate_segments(english_segments)
    
    # Store Google translated segments
    openai_service.save_segments(initial_telugu_segments, TELUGU_SEGMENTS_FILE)
    print(f"  ✅ Saved Google Translated segments to {TELUGU_SEGMENTS_FILE}")

    # ── 3b. Natural Polishing via OpenAI LLM ──
    print("\n🤖 Step 3b: Polishing Telugu via OpenAI LLM...")
    polished_segments = openai_service.polish_telugu(initial_telugu_segments)
    
    # Store polished Telugu segments
    openai_service.save_segments(polished_segments, POLISHED_TELUGU_FILE)
    print(f"  ✅ Saved polished Telugu segments to {POLISHED_TELUGU_FILE}")

    # ── Step 4: Per-segment TTS Generation & Mixing ──
    print(f"\n🔊 Step 4: Generating TTS for {len(polished_segments)} segments...")
    final_segments = []
    temp_dir = "data/temp_tts"
    os.makedirs(temp_dir, exist_ok=True)

    # Stats
    stats = {"total": 0, "success": 0}

    for i, seg in enumerate(polished_segments):
        start = seg['start']
        end = seg['end']
        telugu_text = seg.get('telugu_text', '')
        target_duration = end - start

        if not telugu_text.strip():
            print(f"  ⏭ Skipping empty segment {i+1}")
            continue

        print(f"\nSegment {i+1}/{len(polished_segments)}: [{start:.2f}s - {end:.2f}s] ({target_duration:.2f}s)")
        print(f"  TE: \"{telugu_text[:60]}...\"")

        # ── Generate TTS ──
        # Defaulting to a male voice for all segments as per simplified request
        voice_id = VOICE_MAP.get("MALE", "en-US-zion") 
        seg_filename = f"{temp_dir}/seg_{i}.mp3"
        
        try:
            await generate_audio_segment(telugu_text, voice_id, seg_filename, target_duration=target_duration)
            
            # Timing check + small correction
            generated_duration = get_audio_duration(seg_filename)
            ratio = generated_duration / target_duration if target_duration > 0 else 1.0
            print(f"  ⏱ TTS: {generated_duration:.2f}s vs target: {target_duration:.2f}s (ratio: {ratio:.2f})")

            final_audio_path = seg_filename
            # Always try to match duration if it's within a broad range (0.5x to 2.0x)
            if 0.5 < ratio < 2.0:
                adjusted_filename = f"{temp_dir}/seg_{i}_adjusted.mp3"
                adjust_audio_speed(seg_filename, adjusted_filename, ratio)
                final_audio_path = adjusted_filename
                print(f"  🔧 Speed correction applied (x{ratio:.2f})")
            else:
                print(f"  🎯 Ratio {ratio:.2f} too extreme, keeping natural speed to avoid distortion")
            
            final_segments.append({
                "start": start,
                "audio_path": final_audio_path,
                "text": telugu_text
            })
            stats["success"] += 1
        except Exception as e:
            print(f"  ❌ TTS failed for segment {i}: {e}")
        
        stats["total"] += 1
        # Avoid rate limits
        await asyncio.sleep(0.5)

    # ── Step 5: Audio Mixing ──
    print("\n🎶 Step 5: Mixing audio segments...")
    mix_audio(final_segments, video.duration, TELUGU_AUDIO_PATH)

    # ── Step 6: Merge with Video ──
    print("\n🎬 Step 6: Merging final video...")
    merge_audio_with_video(video, TELUGU_AUDIO_PATH, FINAL_VIDEO_PATH)

    # ── Step 7: LipSync (Optional) ──
    print("\n👄 Step 7: LipSync (Wav2Lip)...")
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
    print(f"📊 Stats: {stats['success']}/{stats['total']} segments processed successfully")
    print(f"{'=' * 60}")
