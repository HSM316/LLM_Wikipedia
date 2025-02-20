

import json
import pandas as pd

languages_to_keep = {
    "eng-Latn-stan1293": "英语",
    "cmn-Hans-beij1234": "普通话（标准北京话）",
    "deu-Latn-stan1295": "德语",
    "fra-Latn-stan1290": "法语",
    "hin-Deva-hind1269": "印度语",
    "ita-Latn-ital1282": "意大利语",
    "jpn-Jpan-nucl1643": "日语",
    "kor-Hang-kore1280": "韩语",
    "rus-Cyrl-russ1263": "俄语",
    "arb-Arab-stan1318": "现代标准阿拉伯语",
    "spa-Latn-amer1254": "西班牙语（拉丁美洲）",
    "por-Latn-braz1246": "葡萄牙语（巴西）"
}

df = pd.read_csv("validation_dataset.csv")

output_data = []

grouped = df.groupby("id")

for id_value, group in grouped:
    language_texts = {}

    for _, row in group.iterrows():
        lang_key = f"{row['iso_639_3']}-{row['iso_15924']}-{row['glottocode']}"

        if lang_key in languages_to_keep:
            language_key_with_desc = f"{lang_key}({languages_to_keep[lang_key]})"
            if language_key_with_desc in language_texts:
                language_texts[language_key_with_desc].append(row["text"])
            else:
                language_texts[language_key_with_desc] = [row["text"]]

    english_key = next((k for k in language_texts if k.startswith("eng-Latn-stan1293")), None)
    if english_key:
        language_texts = dict(
            [(english_key, language_texts[english_key])]
            + [(k, v) for k, v in language_texts.items() if k != english_key]
        )

    if language_texts: 
        output_data.append({
            "id": id_value,
            "translations": language_texts
        })

with open("validation_filtered_benchmark_full.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=4)

print("文件写入完成")
