from transformers import MarianMTModel, MarianTokenizer
import torch

def translate_text(text, source_lang, target_lang):
    model_name = f'Helsinki-NLP/opus-mt-{source_lang.lower()}-{target_lang.lower()}'
    
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)

    # Break text into sentences or chunks to avoid the 512-token limit
    paragraphs = text.split('\n')
    translated_paragraphs = []

    for para in paragraphs:
        if not para.strip(): continue
        
        # Tokenize and generate
        inputs = tokenizer(para, return_tensors="pt", padding=True, truncation=True)
        
        with torch.no_grad(): # Saves memory/RAM
            translated_tokens = model.generate(**inputs)
        
        result = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
        translated_paragraphs.append(result)

    return "\n".join(translated_paragraphs)
