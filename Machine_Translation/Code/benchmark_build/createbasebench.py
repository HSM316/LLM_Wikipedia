import csv
import json
from collections import defaultdict

csv_file_path = 'validation_dataset.csv'
json_file_path = 'validation_dataset.json'

data_by_id = defaultdict(list)

with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        id_val = row['id']
        data_by_id[id_val].append({
            'glottocode': row['glottocode'],
            'text': row['text']
        })

json_data = []

for id_val, entries in data_by_id.items():
    entries_sorted = sorted(entries, key=lambda x: x['glottocode'] != 'stan1293')

    id_structure = {'id': id_val, 'translations': {entry['glottocode']: entry['text'] for entry in entries_sorted}}

    json_data.append(id_structure)

with open(json_file_path, mode='w', encoding='utf-8') as json_file:
    json.dump(json_data, json_file, ensure_ascii=False, indent=4)

print("JSON 文件已生成。")
