import os
os.environ['HF_HOME'] = 'G:/ai_influence/huggingface_cache'

import json
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

def main():
    tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-de")
    model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-en-de")

    input_file = '../origin_benchmark_1.json'
    output_file = 'de_translated_output.json'

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    output_data = []

    for entry in data:
        english_text = entry['translations'].get('eng-Latn-stan1293(英语)', None)

        if english_text:
            input_ids = tokenizer.encode(english_text, return_tensors="pt")
            translated = model.generate(input_ids)
            translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)

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