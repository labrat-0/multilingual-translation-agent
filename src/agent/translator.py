import logging
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# Cache models so we don't reload every time
MODEL_CACHE = {}

def get_model(source: str, target: str):
    """
    Get (or load) an OPUS-MT model for the given source->target language pair.
    """
    key = f"{source}-{target}"
    if key not in MODEL_CACHE:
        # Construct Hugging Face model name
        model_name = f"Helsinki-NLP/opus-mt-{source}-{target}"
        logging.info(f"Loading model {model_name}...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        MODEL_CACHE[key] = (tokenizer, model)
    return MODEL_CACHE[key]

def translate_text(text: str, source_language: str, target_language: str) -> str:
    """
    Translate the given text from source_language -> target_language using an open-source model.
    """
    # Normalize language codes (lowercase)
    source = source_language.lower()
    target = target_language.lower()

    # Load model/tokenizer
    try:
        tokenizer, model = get_model(source, target)
    except Exception as e:
        # If this fails (model not found), raise a clear error
        raise RuntimeError(f"Translation model for {source}->{target} not available: {e}")

    # Tokenize and generate translation
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        translated = model.generate(**inputs)

    # Decode and return
    return tokenizer.decode(translated[0], skip_special_tokens=True)
