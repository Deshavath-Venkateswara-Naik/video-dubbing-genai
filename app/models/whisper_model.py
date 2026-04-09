from faster_whisper import WhisperModel
from app.config import MODEL_SIZE

def load_whisper():
    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    return model

def transcribe_audio(model, audio_path):
    """
    Transcribes audio and returns segments with start, end, and text.
    Uses sentence-level segmentation where possible.
    """
    segments_gen, info = model.transcribe(
        audio_path, 
        beam_size=5, 
        word_timestamps=True, # Helps with better timing
        initial_prompt="Transcribe the following dialogue."
    )
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
