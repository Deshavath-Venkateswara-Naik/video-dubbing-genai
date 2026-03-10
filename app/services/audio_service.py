from moviepy import VideoFileClip
import subprocess
import os


def extract_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)
    return video


def get_audio_duration(file_path):
    """
    Returns the duration of an audio file in seconds using ffprobe.
    """
    cmd = [
        "ffprobe", 
        "-v", "error", 
        "-show_entries", "format=duration", 
        "-of", "default=noprint_wrappers=1:nokey=1", 
        file_path
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Error getting duration for {file_path}: {e}")
        return 0.0


def adjust_audio_speed(input_path, output_path, ratio):
    """
    Adjusts the speed of audio by the given ratio.
    Only called when 0.85 < ratio < 1.15 (small correction).
    
    ratio = generated_duration / target_duration
    e.g. ratio=1.1 means TTS is 10% too long → speed up by 1.1×
    """
    if abs(ratio - 1.0) < 0.02:
        # Less than 2% — no correction needed, just copy
        subprocess.run(["cp", input_path, output_path], check=True)
        return

    # ffmpeg atempo filter (supports [0.5, 2.0] range — our ratio is always 0.85-1.15)
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-filter:a", f"atempo={ratio:.4f}",
        "-vn",
        output_path
    ]
    
    print(f"  🔧 Speed correction: atempo={ratio:.3f}")
    
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error adjusting speed for {input_path}: {e}")
        subprocess.run(["cp", input_path, output_path], check=True)
