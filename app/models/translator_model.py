import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from IndicTransToolkit.processor import IndicProcessor
from app.config import HF_TOKEN, DEVICE
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IndicTranslator:
    """
    English-to-Telugu translator using AI4Bharat's IndicTrans2 model.
    
    Pipeline:
        Whisper → English transcript
            → IndicTrans2 preprocess (normalize, entity placeholders)
            → IndicTrans2 translate (seq2seq inference)
            → IndicTrans2 postprocess (entity replacement, script fixes)
            → Natural Telugu text
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IndicTranslator, cls).__new__(cls)
            cls._instance.model_name = "ai4bharat/indictrans2-en-indic-dist-200M"
            cls._instance.device = "cuda" if torch.cuda.is_available() else DEVICE
            cls._instance.tokenizer = None
            cls._instance.model = None
            cls._instance.processor = None
            cls._instance.loaded = False
        return cls._instance

    def load_model(self):
        """Load IndicTrans2 model, tokenizer, and IndicProcessor."""
        if self.loaded:
            return

        logger.info(f"Loading IndicTrans2 model on {self.device}...")
        try:
            # 1. Load tokenizer (with custom IndicTrans2 code)
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                token=HF_TOKEN
            )

            # 2. Load model
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                token=HF_TOKEN
            ).to(self.device)

            # 3. Load IndicProcessor for pre/post processing
            self.processor = IndicProcessor(inference=True)

            self.loaded = True
            logger.info("IndicTrans2 model + IndicProcessor loaded successfully.")

        except Exception as e:
            logger.error(f"Failed to load IndicTrans2: {e}")
            self.loaded = False

    def translate(self, text, src_lang="eng_Latn", tgt_lang="tel_Telu"):
        """
        Full IndicTrans2 pipeline: preprocess → translate → postprocess.

        Args:
            text: English input text
            src_lang: Source language code (default: eng_Latn)
            tgt_lang: Target language code (default: tel_Telu)

        Returns:
            Natural Telugu text after full IndicTrans2 pipeline
        """
        if not text or not text.strip():
            return ""

        if not self.loaded:
            self.load_model()

        if not self.loaded:
            logger.error("IndicTrans2 model failed to load. Returning original text.")
            return text

        try:
            input_sentences = [text]

            # ── Step 1: IndicTrans2 Preprocess ──
            # Normalizes text, replaces entities (numbers, URLs, etc.) with
            # placeholders so the model can handle them correctly.
            batch = self.processor.preprocess_batch(
                input_sentences,
                src_lang=src_lang,
                tgt_lang=tgt_lang
            )
            logger.info(f"[Preprocess] '{text[:60]}' → '{batch[0][:60]}'")

            # ── Step 2: Tokenize ──
            inputs = self.tokenizer(
                batch,
                truncation=True,
                padding="longest",
                return_tensors="pt",
                return_attention_mask=True,
            ).to(self.device)

            # ── Step 3: IndicTrans2 Translation (Seq2Seq inference) ──
            with torch.no_grad():
                generated_tokens = self.model.generate(
                    **inputs,
                    use_cache=True,
                    min_length=0,
                    max_length=256,
                    num_beams=5,
                    num_return_sequences=1,
                )

            # ── Step 4: Decode tokens to text ──
            generated_tokens = self.tokenizer.batch_decode(
                generated_tokens,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True,
            )

            # ── Step 5: IndicTrans2 Postprocess ──
            # Replaces entity placeholders back with originals,
            # applies Indic script-specific fixes for natural output.
            translations = self.processor.postprocess_batch(
                generated_tokens,
                lang=tgt_lang
            )

            translated_text = translations[0].strip()
            logger.info(f"[Translate] '{text[:50]}' → '{translated_text[:50]}'")
            return translated_text

        except Exception as e:
            logger.error(f"IndicTrans2 translation failed: {e}")
            return text


# Global singleton instance
translator_instance = IndicTranslator()


def translate_to_telugu(text):
    """
    Translates English text to Telugu using the full IndicTrans2 pipeline:
      preprocess → translate → postprocess → natural Telugu text
    """
    return translator_instance.translate(text)
