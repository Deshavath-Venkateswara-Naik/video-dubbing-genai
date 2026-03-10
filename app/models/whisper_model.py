from faster_whisper import WhisperModel
from app.config import MODEL_SIZE

def load_whisper():
    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    return model

def transcribe_audio(model, audio_path):
    segments_gen, info = model.transcribe(audio_path)
    segments = list(segments_gen)

    result = []
    for segment in segments:
        result.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip()
        })

    return result

def transcribe_chunk(model, chunk_path):
    segments_gen, info = model.transcribe(chunk_path)
    segments = list(segments_gen)
    text = " ".join([s.text.strip() for s in segments])
    return text.strip()
