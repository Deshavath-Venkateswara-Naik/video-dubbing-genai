import os
import subprocess
import shutil
from app.services.audio_service import adjust_audio_speed, get_audio_duration

def create_dummy_audio(filename, duration):
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"sine=frequency=1000:duration={duration}",
        filename
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def test_speed_adjustment():
    test_dir = "tests/temp_audio"
    os.makedirs(test_dir, exist_ok=True)
    
    input_file = f"{test_dir}/test_input.mp3"
    output_quick = f"{test_dir}/test_quick.mp3"
    
    # Create 5s audio
    print("Creating 5s dummy audio...")
    create_dummy_audio(input_file, 5.0)
    
    initial_duration = get_audio_duration(input_file)
    print(f"Initial Duration: {initial_duration}s")
    
    # Test 1: Speed up to 2.5s (2x speed)
    print("\nTest 1: Speeding up to 2.5s...")
    adjust_audio_speed(input_file, output_quick, 2.5)
    new_duration = get_audio_duration(output_quick)
    print(f"New Duration: {new_duration}s (Target: 2.5s)")
    assert abs(new_duration - 2.5) < 0.1, f"Failed: {new_duration} != 2.5"

    print("\n✅ All tests passed!")
    
    # Cleanup
    shutil.rmtree(test_dir)

if __name__ == "__main__":
    test_speed_adjustment()
