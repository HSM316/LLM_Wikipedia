import os

os.environ["HF_HOME"] = "G:/ai_influence/huggingface_cache"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

from transformers import T5Tokenizer, T5ForConditionalGeneration

model_name = "t5-small"  # 或者 t5-base, t5-large 等
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

text_to_translate = "translate English to French: How are you?"

input_ids = tokenizer(text_to_translate, return_tensors="pt").input_ids

translated_tokens = model.generate(input_ids, max_length=40, num_beams=4, early_stopping=True)

translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
print("Translated Text:", translated_text)
