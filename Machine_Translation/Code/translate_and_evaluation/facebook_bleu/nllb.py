if __name__ == "__main__":
    import os

    os.environ["HF_HOME"] = "G:/ai_influence/huggingface_cache"
    os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    model_name = "facebook/nllb-200-distilled-600M"

    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    src_lang = "eng_Latn"  # 英文
    tgt_lang = "fra_Latn"  # 法语（例如：法语的代码是 fra_Latn）

    text_to_translate = "Hello, how are you?"

    encoded = tokenizer(text_to_translate, return_tensors="pt")

    generated_tokens = model.generate(**encoded, forced_bos_token_id=tokenizer.convert_tokens_to_ids(tgt_lang))

    translation = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
    print("Translated text:", translation[0])





