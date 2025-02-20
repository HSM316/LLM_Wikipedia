import os
import json
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint="<input_your_api>",
    api_key="<input_your_api>",
    api_version="2024-02-01"
)

def translate(text, target_language):
    response = client.chat.completions.create(
        model="gpt-4o-mini-llm-influence",
        messages=[
            {"role": "system", "content": f"You are a helpful assistant who translates English to {target_language}."},
            {"role": "user", "content": f"Translate the following text to {target_language}: {text}"}
        ]
    )
    return response.choices[0].message.content

input_file = "origin_benchmark_2.json"
translate_dir = "translate"
output_file = "translations_combined.json"
error_log_file = "errorsentence.txt"
null_info_file = "nullinfo.txt"

os.makedirs(translate_dir, exist_ok=True)

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    id_str = str(item["id"])
    translate_path = os.path.join(translate_dir, f"{id_str}.json")

    if os.path.exists(translate_path):
        print(f"ID {id_str} 已存在，跳过翻译...")
        continue

    english_text = item["translations"]["eng-Latn-stan1293(英语)"]
    updated_translations = {}

    for key, value in item["translations"].items():
        if key == "eng-Latn-stan1293(英语)":
            updated_translations[key] = value  # 保留英语部分
            continue

        language_name = key.split("(")[1].rstrip(")")
        print(f"Translating to {language_name} for ID {id_str}...")

        attempt_count = 0
        translated_text = None

        while attempt_count < 5:
            try:
                translated_text = translate(english_text, language_name)

                if translated_text is not None:
                    updated_translations[key] = translated_text
                    break
            except Exception as e:
                print(f"Error translating ID {id_str}, language {key}: {str(e)}")
                with open(error_log_file, "a", encoding="utf-8") as error_file:
                    error_file.write(f"id:{id_str}, error translating: {key}\n")
                break

            attempt_count += 1
            print(f"ID {id_str}, language {key}: Attempt {attempt_count} returned null. Retrying...")

        if translated_text is None:
            print(f"ID {id_str}, language {key}: Failed after 5 attempts. Keeping original version.")
            updated_translations[key] = value
            with open(null_info_file, "a", encoding="utf-8") as null_file:
                null_file.write(f"id:{id_str}, null language: {key}\n")

    item["translations"] = updated_translations
    with open(translate_path, "w", encoding="utf-8") as f:
        json.dump(item, f, ensure_ascii=False, indent=4)

    print(f"ID {id_str} 翻译完成，已保存到 {translate_path}")

combined_data = []
for filename in os.listdir(translate_dir):
    file_path = os.path.join(translate_dir, filename)
    with open(file_path, "r", encoding="utf-8") as f:
        combined_data.append(json.load(f))

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(combined_data, f, ensure_ascii=False, indent=4)

print("所有翻译完成，合并文件已保存为 translations_combined.json")
