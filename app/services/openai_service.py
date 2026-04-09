
import os
import json
from openai import OpenAI
from app.config import OPENAI_API_KEY

class OpenAIService:
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")
        self.client = OpenAI(api_key=self.api_key)

    def polish_telugu(self, segments):
        """
        Polishes existing Telugu translations (e.g. from Google Translate) using OpenAI.
        segments: list of dicts with {'start', 'end', 'english_text', 'telugu_text'}
        """
        polished_segments = []
        
        system_prompt = (
            "You are a professional Telugu dubbing editor.\n"
            "The following Telugu segments were translated from English using Google Translate.\n"
            "Your job is to polish them to sound natural, professional, and easy to speak for video dubbing.\n"
            "Keep the meaning exact but improve flow and vocabulary.\n"
            "Maintain the exact JSON structure provided."
        )
        
        # Prepare data for LLM
        input_data = [{"id": i, "en": s["english_text"], "te": s["telugu_text"]} for i, s in enumerate(segments)]
        
        user_prompt = (
            f"Polish the following Telugu translations to sound more natural and professional for video dubbing.\n\n"
            f"Return a JSON object with a key 'polished' containing a list of objects with 'id' and 'polished_text'.\n\n"
            f"Segments:\n{json.dumps(input_data, ensure_ascii=False)}"
        )
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            result_json = json.loads(response.choices[0].message.content)
            polished_list = result_json.get("polished", [])

            # Map back to original segments
            for i, segment in enumerate(segments):
                polished_text = segment["telugu_text"] # default
                for p in polished_list:
                    if p.get("id") == i:
                        polished_text = p.get("polished_text", polished_text)
                        break
                
                polished_segments.append({
                    "start": segment["start"],
                    "end": segment["end"],
                    "english_text": segment["english_text"],
                    "telugu_text": polished_text
                })
                
            return polished_segments
        except Exception as e:
            print(f"OpenAI polishing failed: {e}")
            return segments

    def translate_and_polish(self, segments):
        """
        Backward compatibility: Translates and polishes English segments.
        """
        # ... (keep existing logic or wrap new ones)
        # For simplicity, I'll keep the logic as it is for now but the new pipeline will use polish_telugu
        return self.polish_telugu([{"start": s["start"], "end": s["end"], "english_text": s["text"], "telugu_text": ""} for s in segments])

    def save_segments(self, segments, file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)

openai_service = OpenAIService()
