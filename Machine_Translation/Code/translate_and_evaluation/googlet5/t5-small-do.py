import os
os.environ['HF_HOME'] = 'G:/ai_influence/huggingface_cache'
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
import json
from transformers import T5Tokenizer, T5ForConditionalGeneration

def main():
    model_name = "t5-small"  # 或者 t5-base, t5-large 等
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)

    input_file = '../origin_benchmark_1.json'
    output_file = 'de_translated_output.json'

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    output_data = []

    for entry in data:
        english_text = entry['translations'].get('eng-Latn-stan1293(英语)', None)

        if english_text:

            text_to_translate = english_text
            hint = "translate English to German: "
            text_to_translate=hint+text_to_translate

            input_ids = tokenizer(text_to_translate, return_tensors="pt").input_ids

            translated_tokens = model.generate(input_ids, max_length=40, num_beams=4, early_stopping=True)

            translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)

            output_data.append({
                'id': entry['id'],
                'english': english_text,
                'translated_german': translated_text
            })
            print(entry['id'],translated_text)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print(f"翻译完成，结果已保存到 {output_file}")

if __name__ == '__main__':
    main()