
from deep_translator import GoogleTranslator

class GoogleTranslateService:
    def __init__(self):
        self.translator = GoogleTranslator(source='en', target='te')

    def translate_segments(self, segments):
        """
        Translates English segments to Telugu using Google Translate.
        segments: list of dicts with {'start', 'end', 'text'}
        """
        translated_segments = []
        for segment in segments:
            try:
                telugu_text = self.translator.translate(segment['text'])
                translated_segments.append({
                    "start": segment['start'],
                    "end": segment['end'],
                    "english_text": segment['text'],
                    "telugu_text": telugu_text
                })
            except Exception as e:
                print(f"Google Translation failed for segment: {segment['text']}. Error: {e}")
                translated_segments.append({
                    "start": segment['start'],
                    "end": segment['end'],
                    "english_text": segment['text'],
                    "telugu_text": segment['text'] # Fallback
                })
        return translated_segments

google_translate_service = GoogleTranslateService()
