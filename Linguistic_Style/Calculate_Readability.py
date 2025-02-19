import json
import csv
import os
import textstat
from tqdm import tqdm

def calculate_metrics(text):
    if not text.strip():
        return None
    
    metrics = {}
    try:
        metrics = {
            'Flesch Reading Ease': textstat.flesch_reading_ease(text),
            'Flesch-Kincaid Grade Level': textstat.flesch_kincaid_grade(text),
            'Automated Readability Index (ARI)': textstat.automated_readability_index(text),
            'Coleman-Liau Index': textstat.coleman_liau_index(text),
            'Gunning Fog Index': textstat.gunning_fog(text),
            'Dale-Chall Readability Score': textstat.dale_chall_readability_score(text),
            'Linsear Write Formula': textstat.linsear_write_formula(text)
        }

        try:
            metrics['SMOG Index'] = textstat.smog_index(text)
        except Exception:
            metrics['SMOG Index'] = None

        len_word = textstat.lexicon_count(text)
        metrics['Total Words'] = len_word
        
        if len_word > 0:
            metrics.update({
                'Syllable Count per word': textstat.syllable_count(text) / len_word,
                'Polysyllable Count per word': textstat.polysyllabcount(text) / len_word,
                'Difficult Words per word': textstat.difficult_words(text) / len_word
            })
        else:
            metrics.update({
                'Syllable Count per word': 0.0,
                'Polysyllable Count per word': 0.0,
                'Difficult Words per word': 0.0
            })

        metrics['Reading Time (seconds)'] = textstat.reading_time(text, ms_per_char=60) * 60

    except Exception as e:
        print(f"{str(e)}")
        return None

    return metrics

def process_jsonl_file(jsonl_path, output_dir):
    results = []
    os.makedirs(output_dir, exist_ok=True)

    with open(jsonl_path, 'r', encoding='utf-8') as infile:
        total_lines = sum(1 for _ in infile)
        infile.seek(0)
        
        for line in tqdm(infile, total=total_lines, desc=f"Processing {os.path.basename(jsonl_path)}", unit="line"):
            try:
                obj = json.loads(line)
                title = obj.get('title', '')
                content = obj.get('content', '')
                
                metrics = calculate_metrics(content)
                
                if metrics:
                    metrics['title'] = title
                    results.append(metrics)
            except json.JSONDecodeError:
                continue

    if results:
        output_csv_path = os.path.join(output_dir, "Readability_wiki.csv")
        fieldnames = list(results[0].keys())
        
        with open(output_csv_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
jsonl_path = "INPUT YOUR JSONL PATH"
output_dir = "INPUT YOUR PATH"
process_jsonl_file(jsonl_path, output_dir)