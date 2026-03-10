"""
Text Adapter Service
====================
Uses Gemini API to:
  1. Improve Telugu text quality (grammar, naturalness, fluency)
  2. Shorten Telugu text when it's too long for the segment

Pipeline position:
    IndicTrans2 Translation → **Gemini Improve** → **Gemini Shorten (if needed)** → TTS
"""

import logging
from google import genai
from app.config import GEMINI_API_KEY, TELUGU_CHARS_PER_SEC

logger = logging.getLogger(__name__)

# ── Configure Gemini ──
if GEMINI_API_KEY:
    _client = genai.Client(api_key=GEMINI_API_KEY)
else:
    _client = None
    logger.warning("Gemini_API_Key not found. Text adaptation will be disabled.")


def estimate_duration(text: str, chars_per_sec: float = None) -> float:
    """
    Estimate how long TTS will take to speak this Telugu text.
    Returns estimated duration in seconds.
    """
    cps = chars_per_sec or TELUGU_CHARS_PER_SEC
    return len(text) / cps if cps > 0 else 0.0


def improve_text(telugu_text: str, english_text: str) -> str:
    """
    Ask Gemini to polish/improve the Telugu translation for naturalness,
    grammar, and fluency — without significantly changing the length.
    """
    if not _client:
        logger.warning("[TextAdapter] Gemini not available, skipping improvement")
        return telugu_text

    prompt = (
        f"You are a professional Telugu language editor for video dubbing.\n"
        f"The following Telugu text was machine-translated from the English text below.\n"
        f"Your job is to improve it so it sounds natural and grammatically correct.\n\n"
        f"English original: \"{english_text}\"\n"
        f"Telugu translation: \"{telugu_text}\"\n\n"
        f"TASK: Rewrite the Telugu text to improve its grammar, fluency, and naturalness.\n"
        f"Make it sound like a native Telugu speaker wrote it.\n\n"
        f"RULES:\n"
        f"- Output ONLY the improved Telugu text, nothing else\n"
        f"- Keep the same meaning and intent as the original\n"
        f"- Keep roughly the same length (do NOT make it significantly longer or shorter)\n"
        f"- Must be valid, natural-sounding Telugu that is easy to speak aloud\n"
        f"- Use conversational Telugu appropriate for video dubbing\n"
        f"- Fix any grammar, word order, or phrasing issues\n"
        f"- Do NOT add any explanation, notes, or English text"
    )

    try:
        response = _client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        if response and response.text:
            result = response.text.strip()
            logger.info(
                f"[TextAdapter] Improved: '{telugu_text[:40]}' → '{result[:40]}'"
            )
            return result
    except Exception as e:
        logger.error(f"Gemini improve API call failed: {e}")

    return telugu_text


def shorten_text(telugu_text: str, english_text: str, target_duration: float) -> str:
    """
    Ask Gemini to condense Telugu text so it fits within target_duration.
    """
    if not _client:
        logger.warning("[TextAdapter] Gemini not available, returning original text")
        return telugu_text

    target_chars = max(5, int(target_duration * TELUGU_CHARS_PER_SEC))

    prompt = (
        f"You are a professional Telugu language editor for video dubbing.\n"
        f"The following Telugu text is a translation of the English text below.\n"
        f"It is TOO LONG for the available time slot.\n\n"
        f"English original: \"{english_text}\"\n"
        f"Telugu translation: \"{telugu_text}\"\n"
        f"Current length: {len(telugu_text)} characters\n"
        f"Target length: approximately {target_chars} characters\n\n"
        f"TASK: Rewrite the Telugu text to be shorter (around {target_chars} characters) "
        f"while preserving the core meaning. Use concise vocabulary, remove filler words, "
        f"and use shorter synonyms where possible.\n\n"
        f"RULES:\n"
        f"- Output ONLY the shortened Telugu text, nothing else\n"
        f"- Must be valid, natural-sounding Telugu\n"
        f"- Preserve the key meaning and intent\n"
        f"- Do NOT add any explanation or English text"
    )

    try:
        response = _client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        if response and response.text:
            result = response.text.strip()
            logger.info(f"[TextAdapter] Shortened: {len(telugu_text)} → {len(result)} chars (target: {target_chars})")
            return result
    except Exception as e:
        logger.error(f"Gemini shorten API call failed: {e}")

    return telugu_text


def adapt_text_for_segment(
    telugu_text: str,
    english_text: str,
    target_duration: float
) -> str:
    """
    Main entry point:
      1. Always improve Telugu text quality via Gemini (grammar, fluency)
      2. Then shorten if estimated duration > target × 1.2
    """
    if not telugu_text or not telugu_text.strip():
        return telugu_text

    # ── Step 1: Improve quality ──
    print(f"  ✨ Improving Telugu text via Gemini...")
    improved_text = improve_text(telugu_text, english_text)
    if improved_text != telugu_text:
        print(f"  ✨ Improved: \"{improved_text[:80]}{'...' if len(improved_text) > 80 else ''}\"")

    # ── Step 2: Shorten if too long ──
    estimated = estimate_duration(improved_text)

    if estimated > target_duration * 1.2:
        print(f"  ✂ Text too long: estimated {estimated:.1f}s > target {target_duration:.1f}s × 1.2 — shortening")
        return shorten_text(improved_text, english_text, target_duration)
    else:
        print(f"  ✅ Text length OK: estimated {estimated:.1f}s for {target_duration:.1f}s slot")
        return improved_text
