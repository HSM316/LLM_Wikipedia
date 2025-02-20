import os
os.environ['HF_HOME'] = 'G:/ai_influence/huggingface_cache'
import json
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

def main():
    model_name = "facebook/nllb-200-distilled-600M"

    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    input_file = '../origin_benchmark_1.json'
    output_file = 'zh_translated_output.json'

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    output_data = []

    for entry in data:
        english_text = entry['translations'].get('eng-Latn-stan1293(英语)', None)

        if english_text:
            tgt_lang = "zho_Hans"  # 简体中文

            text_to_translate = english_text

            encoded = tokenizer(text_to_translate, return_tensors="pt")

            tgt_token_id = tokenizer.convert_tokens_to_ids(tgt_lang)
            generated_tokens = model.generate(**encoded, forced_bos_token_id=tgt_token_id)

            translation = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
            translated_text=translation[0]

            output_data.append({
                'id': entry['id'],
                'english': english_text,
                'translated_chinese': translated_text
            })
            print(entry['id'],translated_text)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print(f"翻译完成，结果已保存到 {output_file}")

if __name__ == '__main__':
    main()