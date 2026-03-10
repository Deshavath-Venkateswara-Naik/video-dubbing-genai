import sys
import os

# Add project root to sys path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.models.translator_model import translate_to_telugu
import time

def test_translation():
    """
    Test the full IndicTrans2 pipeline:
      English text → preprocess → translate → postprocess → Telugu text
    """
    test_sentences = [
        "Hello, how are you today?",
        "Artificial Intelligence is transforming the world.",
        "Let's go for a walk in the park.",
        "The meeting is scheduled for 3:30 PM tomorrow.",
        "India has a population of 1.4 billion people.",
    ]

    print("=" * 60)
    print("IndicTrans2 Translation Test (Full Pipeline)")
    print("  preprocess → translate → postprocess")
    print("=" * 60)

    for i, text in enumerate(test_sentences, 1):
        print(f"\n--- Test {i} ---")
        print(f"English: {text}")

        start = time.time()
        translated = translate_to_telugu(text)
        elapsed = time.time() - start

        print(f"Telugu:  {translated}")
        print(f"Time:    {elapsed:.3f}s")

        if translated and translated != text:
            print("✅ Success")
        else:
            print("❌ Failed (returned original text)")

    print("\n" + "=" * 60)
    print("All tests complete.")

if __name__ == "__main__":
    test_translation()
