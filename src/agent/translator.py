from transformers import MarianMTModel, MarianTokenizer
import torch

# Cache loaded models
MODEL_CACHE = {}

def get_marian_model(source: str, target: str):
    """
    Load a MarianMT model and tokenizer for the source->target language pair.
    """
    key = f"{source}-{target}"
    if key not in MODEL_CACHE:
        # Construct the model name
        model_name = f"Helsinki-NLP/opus-mt-{source}-{target}"
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
        model.eval()
        MODEL_CACHE[key] = (tokenizer, model)
    return MODEL_CACHE[key]

def translate_text(text: str, source_language: str, target_language: str) -> str:
    """
    Translate the text from source_language to target_language using MarianMT models.
    """
    source = source_language.lower()
    target = target_language.lower()

    # Load model + tokenizer for this language pair
    tokenizer, model = get_marian_model(source, target)

    # Tokenize
    inputs = tokenizer([text], return_tensors="pt", padding=True)

    # Generate translation
    with torch.no_grad():
        translated_tokens = model.generate(**inputs)

    # Decode and return
    translated = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)
    return translated[0] if translated else ""
