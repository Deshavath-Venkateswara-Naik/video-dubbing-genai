from transformers import AutoTokenizer
from app.config import HF_TOKEN

def inspect_tokenizer():
    model_name = "ai4bharat/indictrans2-en-indic-dist-200M"
    print(f"Loading tokenizer for {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True, token=HF_TOKEN)
    
    # Search for lang tags
    all_tokens = tokenizer.get_vocab()
    tags = [t for t in all_tokens if "_" in t and len(t) < 10]
    print(f"Potential tags: {tags[:20]}")
    
    for lang in ["eng_Latn", "tel_Telu", "hin_Deva", "kan_Knda"]:
        token_id = tokenizer.convert_tokens_to_ids(lang)
        print(f"Token: {lang}, ID: {token_id}")

if __name__ == "__main__":
    inspect_tokenizer()
