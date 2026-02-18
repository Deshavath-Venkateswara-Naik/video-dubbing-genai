import google.generativeai as genai
from deep_translator import GoogleTranslator
from app.config import GEMINI_API_KEY
import time
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini if key is available
model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # using 'gemini-flash-latest' as it is available in the list
        model = genai.GenerativeModel('gemini-flash-latest') 
        logger.info("Gemini Flash (Latest) configured for translation.")
    except Exception as e:
        logger.error(f"Failed to configure Gemini: {e}")

def translate_to_telugu(text):
    """
    Translates English text to Telugu using Gemini (preferred) 
    or Google Translate (fallback).
    """
    if not text or not text.strip():
        return ""

    # Try Gemini First
    if model:
        for attempt in range(2): # Retry once for transient errors
            try:
                # Craft a prompt that encourages direct translation
                prompt = f"Translate the following English text to natural-sounding Telugu. Output ONLY the Telugu translation, no extra text.\n\nEnglish: {text}\nTelugu:"
                
                response = model.generate_content(prompt)
                
                if response and response.text:
                    translated_text = response.text.strip()
                    if translated_text:
                        logger.info(f"Gemini Translation: {text[:20]}... -> {translated_text[:20]}...")
                        return translated_text
            except Exception as e:
                if "429" in str(e):
                    if attempt == 0:
                        logger.warning(f"Gemini 429 Rate Limit. Retrying in 2s...")
                        time.sleep(2)
                        continue
                logger.error(f"Gemini translation failed: {e}. Falling back to Google Translate.")
                break # Don't retry for non-429 errors or after first retry

    # Fallback to Google Translator (Deep Translator)
    try:
        translator = GoogleTranslator(source='auto', target='te')
        result = translator.translate(text)
        logger.info(f"Google Translation (Fallback): {text[:20]}... -> {result[:20]}...")
        return result
    except Exception as e:
        logger.error(f"Google Translate failed: {e}")
        return text # Return original text if everything fails
