from moviepy import AudioFileClip

def merge_audio_with_video(video, telugu_audio_path, final_path):
    telugu_audio = AudioFileClip(telugu_audio_path)

    if telugu_audio.duration > video.duration:
        telugu_audio = telugu_audio.subclipped(0, video.duration)
    else:
        video = video.subclip(0, telugu_audio.duration)

    final_video = video.with_audio(telugu_audio)


    final_video.write_videofile(
        final_path,
        codec="libx264",
        audio_codec="aac"
    )
