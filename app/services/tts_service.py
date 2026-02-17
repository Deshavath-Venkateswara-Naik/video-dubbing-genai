from gtts import gTTS
from pydub import AudioSegment
import os
from app.config import MAX_CHARS

def generate_telugu_audio(text, output_path):
    chunks = [text[i:i+MAX_CHARS] for i in range(0, len(text), MAX_CHARS)]

    temp_files = []

    for i, chunk in enumerate(chunks):
        temp_file = f"temp_part_{i}.mp3"
        tts = gTTS(text=chunk, lang='te')
        tts.save(temp_file)
        temp_files.append(temp_file)

    combined = AudioSegment.empty()
    for file in temp_files:
        combined += AudioSegment.from_mp3(file)

    combined.export(output_path, format="mp3")

    for file in temp_files:
        os.remove(file)
