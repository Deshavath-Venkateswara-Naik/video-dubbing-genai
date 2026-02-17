from deep_translator import GoogleTranslator

def translate_to_telugu(text):
    translator = GoogleTranslator(source='auto', target='te')
    return translator.translate(text)
