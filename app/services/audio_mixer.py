from pydub import AudioSegment
import os

def mix_audio(segments, total_duration, output_path):
    """
    Stitches generated TTS segments at correct timestamps by inserting silence.
    segments: List of dicts { 'start': float, 'audio_path': str }
    total_duration: float (seconds)
    output_path: str
    """
    # Create an empty audio segment
    final_audio = AudioSegment.empty()
    current_time_ms = 0

    # sort segments by start time to ensure order
    segments = sorted(segments, key=lambda x: x['start'])

    for segment in segments:
        try:
            start_ms = int(segment['start'] * 1000)
            audio_path = segment['audio_path']
            
            if not os.path.exists(audio_path):
                print(f"Warning: Audio segment not found: {audio_path}")
                continue
                
            segment_audio = AudioSegment.from_file(audio_path)
            
            # Calculate silence needed
            silence_duration = start_ms - current_time_ms
            
            if silence_duration > 0:
                silence = AudioSegment.silent(duration=silence_duration)
                final_audio += silence
                final_audio += segment_audio
            else:
                # Overlap handling: strictly append or maybe crossfade?
                # User asked to "Match start time" which implies we shouldn't shift if possible,
                # but if previous segment was too long, we simply append (shifting it).
                # Alternatively, we could trim previous, but appending is safer for speech completeness.
                # Let's just append.
                final_audio += segment_audio
            
            current_time_ms = len(final_audio)
            
        except Exception as e:
            print(f"Error mixing segment {segment}: {e}")

    # Pad with silence at the end if needed to match video duration
    total_duration_ms = int(total_duration * 1000)
    final_duration_ms = len(final_audio)

    if final_duration_ms < total_duration_ms:
        silence_padding = AudioSegment.silent(duration=total_duration_ms - final_duration_ms)
        final_audio += silence_padding
    
    # Export
    final_audio.export(output_path, format="mp3")
