import nltk
from nltk.tokenize import sent_tokenize

nltk.download('punkt')

def format_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"

def create_srt(video_duration, telugu_text, output_path):
    sentences = sent_tokenize(telugu_text)

    time_per_sentence = video_duration / max(len(sentences), 1)

    with open(output_path, "w", encoding="utf-8") as srt:
        current_time = 0

        for i, sentence in enumerate(sentences):
            start = current_time
            end = current_time + time_per_sentence

            srt.write(f"{i+1}\n")
            srt.write(f"{format_time(start)} --> {format_time(end)}\n")
            srt.write(sentence.strip() + "\n\n")

            current_time = end

