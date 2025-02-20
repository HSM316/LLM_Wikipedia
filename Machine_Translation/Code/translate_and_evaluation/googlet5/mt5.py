import os

os.environ["HF_HOME"] = "G:/ai_influence/huggingface_cache"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
import torch
import gc
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

def translate_text(text, model_name="google/mt5-small"):
    print("Loading model and tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    print("Model and tokenizer loaded successfully.")

    print("Input Text:", text)
    encoded_input = tokenizer(text, return_tensors="pt")
    print("Input encoded successfully.")

    print("Generating translation...")
    output = model.generate(
        **encoded_input,
        max_length=50,   # 限制输出长度
        num_beams=5,     # Beam search 提升输出质量
        early_stopping=True
    )
    translated_text = tokenizer.decode(output, skip_special_tokens=True)
    print("Translated Text:", translated_text)

    del model
    del tokenizer
    gc.collect()
    torch.cuda.empty_cache()

if __name__ == "__main__":


    torch.set_num_threads(1)

    text_to_translate = "translate English to Chinese: How are you?"
    translate_text(text_to_translate)
