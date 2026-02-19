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

def adjust_audio_speed(input_path, output_path, target_duration):
    """
    Adjusts the speed of the audio file to match the target duration.
    Uses ffmpeg 'atempo' filter.
    """
    current_duration = get_audio_duration(input_path)
    
    if current_duration == 0 or target_duration <= 0:
        print(f"Invalid duration: current={current_duration}, target={target_duration}. Copying original.")
        # Fallback: copy file
        subprocess.run(["cp", input_path, output_path], check=True)
        return

    # Calculate speed factor
    speed_factor = current_duration / target_duration
    
    # ffmpeg 'atempo' filter is limited to [0.5, 2.0].
    # Chain filters if outside this range.
    filter_chain = []
    remaining_factor = speed_factor
    
    while remaining_factor > 2.0:
        filter_chain.append("atempo=2.0")
        remaining_factor /= 2.0
        
    while remaining_factor < 0.5:
        filter_chain.append("atempo=0.5")
        remaining_factor /= 0.5
        
    filter_chain.append(f"atempo={remaining_factor}")
    
    filter_str = ",".join(filter_chain)
    
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-filter:a", filter_str,
        "-vn",
        output_path
    ]
    
    print(f"Adjusting speed: {current_duration:.2f}s -> {target_duration:.2f}s (Factor: {speed_factor:.2f})")
    
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error adjusting speed for {input_path}: {e}")
        subprocess.run(["cp", input_path, output_path], check=True)
