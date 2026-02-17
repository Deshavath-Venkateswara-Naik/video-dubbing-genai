from faster_whisper import WhisperModel
from app.config import MODEL_SIZE

def load_whisper():
    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    return model

def transcribe_audio(model, audio_path):
    segments_gen, info = model.transcribe(audio_path)
    segments = list(segments_gen)

    full_text = ""
    for segment in segments:
        full_text += segment.text.strip() + " "

    return full_text
