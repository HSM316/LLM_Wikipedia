import json
import csv
from collections import defaultdict


def convert_to_json_with_duplicates(csv_file, json_file):
    data_by_id = defaultdict(lambda: defaultdict(list))

    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            id_ = row['id']
            glottocode = row['glottocode']
            text = row['text']

            data_by_id[id_][glottocode].append(text)

    output_data = []
    for id_, glottocode_texts in data_by_id.items():
        entry = {'id': id_}

        if 'stan1293' in glottocode_texts:
            entry['translations'] = [{'glottocode': 'stan1293', 'text': glottocode_texts.pop('stan1293')}]
        else:
            entry['translations'] = []

        entry['translations'].extend(
            [{'glottocode': glottocode, 'text': texts} for glottocode, texts in glottocode_texts.items()]
        )

        output_data.append(entry)

    with open(json_file, mode='w', encoding='utf-8') as file:
        json.dump(output_data, file, ensure_ascii=False, indent=4)


csv_file = 'test_dataset.csv'
json_file = 'test_dataset_full.json'
convert_to_json_with_duplicates(csv_file, json_file)
