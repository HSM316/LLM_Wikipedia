import json
import sacrebleu
import csv
from comet import download_model, load_from_checkpoint
model_path = download_model("Unbabel/wmt22-comet-da")
model = load_from_checkpoint(model_path)


def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def load_error_and_null_ids(error_file, null_file):
    error_ids = set()
    null_ids = set()

    with open(error_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(", ")
            error_id = int(parts[0].split(":")[1])
            language = parts[1].split(":")[1].strip()
            if "spa-Latn-amer1254" in language:  # 只记录中文翻译错误的ID
                error_ids.add(error_id)

    with open(null_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(", ")
            null_id = int(parts[0].split(":")[1])
            language = parts[1].split(":")[1].strip()
            if "spa-Latn-amer1254" in language:  # 只记录中文翻译空值的ID
                null_ids.add(null_id)

    return error_ids, null_ids


def compute_bleu(reference, hypothesis):
    bleu = sacrebleu.corpus_bleu([hypothesis], [[reference]], tokenize='13a')
    return bleu.score

def compute_comet(src,mt,ref):
    data = [
        {
            "src": src,
            "mt": mt,
            "ref": ref
        }
    ]
    model_output = model.predict(data, batch_size=1, gpus=0)
    return model_output[0][0]


def process_and_compare(benchmark_file_1, benchmark_file_2, translated_file, output_csv, error_file, null_file):
    error_ids, null_ids = load_error_and_null_ids(error_file, null_file)

    origin_benchmark = load_json(benchmark_file_1)
    gpt_benchmark = load_json(benchmark_file_2)
    translated_data = load_json(translated_file)

    bleu_scores = []
    origin_bleu_scores = []
    gpt_bleu_scores = []

    for translated_item in translated_data:
        origin_eng = translated_item.get('english', '')
        translated_chinese = translated_item.get('translated_spainish', '')
        id_ = translated_item.get('id', None)

        origin_translation = None
        gpt_translation = None
        origin_bleu = None
        gpt_bleu = None

        if id_ in error_ids or id_ in null_ids:
            for item in origin_benchmark:
                if item['id'] == id_:
                    origin_translation = item['translations'].get('spa-Latn-amer1254(西班牙语（拉丁美洲）)', '')
                    if origin_translation and translated_chinese:
                        origin_bleu = compute_comet(origin_eng, translated_chinese, origin_translation)
                    else:
                        origin_bleu = None
            gpt_translation = None
            gpt_bleu = None
        else:
            for item in gpt_benchmark:
                if item['id'] == id_:
                    gpt_translation = item['translations'].get('spa-Latn-amer1254(西班牙语（拉丁美洲）)', '')

            if gpt_translation and translated_chinese:
                gpt_bleu = compute_comet(origin_eng, translated_chinese, gpt_translation)
            else:
                gpt_bleu = None

            for item in origin_benchmark:
                if item['id'] == id_:
                    origin_translation = item['translations'].get('spa-Latn-amer1254(西班牙语（拉丁美洲）)', '')

            if origin_translation and translated_chinese:
                origin_bleu = compute_comet(origin_eng, translated_chinese, origin_translation)
            else:
                origin_bleu = None

        if origin_bleu is not None:
            origin_bleu_scores.append(origin_bleu)
        if gpt_bleu is not None:
            gpt_bleu_scores.append(gpt_bleu)

        bleu_scores.append({
            'id': id_,
            'translated_spainish': translated_chinese,
            'origin_translation': origin_translation if origin_translation else None,
            'origin_bleu': origin_bleu,
            'gpt_translation': gpt_translation if gpt_translation else None,
            'gpt_bleu': gpt_bleu,
        })

    origin_bleu_avg = sum(origin_bleu_scores) / len(origin_bleu_scores) if origin_bleu_scores else None
    gpt_bleu_avg = sum(gpt_bleu_scores) / len(gpt_bleu_scores) if gpt_bleu_scores else None

    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'translated_spainish', 'origin_translation', 'origin_bleu', 'gpt_translation', 'gpt_bleu']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for score in bleu_scores:
            writer.writerow(score)

    with open(output_csv, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Average BLEU'])
        writer.writerow(['origin_bleu_avg', origin_bleu_avg])
        writer.writerow(['gpt_bleu_avg', gpt_bleu_avg])


benchmark_file_1 = '../origin_benchmark_1.json'
benchmark_file_2 = '../gpt_llm_influenced_benchmark_1.json'
translated_file = 'es_translated_output.json'
output_csv = 'comet_scores_es.csv'

error_file = '../error_sentences.txt'
null_file = '../null_sentences.txt'

process_and_compare(benchmark_file_1, benchmark_file_2, translated_file, output_csv, error_file, null_file)

print("BLEU scores and averages have been written to 'bleu_scores.csv'.")