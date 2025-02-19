import spacy
import json
import csv
import os
import math
from tqdm import tqdm
from collections import defaultdict
from datetime import datetime

SHORT_SENT_THRESHOLD = 10    
LONG_SENT_THRESHOLD = 20     
LONG_WORD_LENGTH = 6         
SYLLABLE_EXCEPTIONS = {      
    'simplified': 4, 'identified': 4
}

nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer", "textcat"])

def calculate_metrics(
    text: str,
    short_thresh: int = SHORT_SENT_THRESHOLD,
    long_thresh: int = LONG_SENT_THRESHOLD,
    long_word_len: int = LONG_WORD_LENGTH
) -> dict:
    doc = nlp(text)
    sentences = list(doc.sents)
    
    alpha_words = [token.text.lower() for token in doc if token.is_alpha]
    total_alpha = len(alpha_words) or 1
    unique_alpha = len(set(alpha_words))
    
    pos_tags = [(token.text, token.pos_) for token in doc]
    total_words = len(alpha_words) or 1
    total_sents = len(sentences) or 1

    syllable_cache = {}
    
    def get_syllables(word: str) -> int:
        if word in syllable_cache:
            return syllable_cache[word]
        if word in SYLLABLE_EXCEPTIONS:
            return SYLLABLE_EXCEPTIONS[word]
        count = count_syllables(word)
        syllable_cache[word] = count
        return count

    passive_counts = sum(1 for s in sentences if is_passive(s))

    def get_parse_tree_depth(token):

        if not list(token.children):
            return 1
        return 1 + max((get_parse_tree_depth(child) for child in token.children), default=0)

    parse_tree_depths = [get_parse_tree_depth(s.root) for s in sentences]
    avg_parse_tree_depth = sum(parse_tree_depths) / len(parse_tree_depths) if parse_tree_depths else 0

    def get_dependency_depth(token, depth_cache=None):

        if depth_cache is None:
            depth_cache = {}
        if token in depth_cache:
            return depth_cache[token]
        if token.head == token:
            depth_cache[token] = 0
        else:
            depth_cache[token] = get_dependency_depth(token.head, depth_cache) + 1
        return depth_cache[token]

    dependency_depths = [get_dependency_depth(token) for token in doc]
    avg_dependency_depth = sum(dependency_depths) / len(dependency_depths) if dependency_depths else 0

    return {

        'Short_Sent_Rate': len([s for s in sentences if len(s) < short_thresh]) / total_sents,
        'Long_Sent_Rate': len([s for s in sentences if len(s) > long_thresh]) / total_sents,
        'Avg_Sent_Length': total_words / total_sents,
        

        'TTR': unique_alpha / total_alpha,
        'CTTR': unique_alpha / math.sqrt(2 * total_alpha),
        

        'Passive_Voice_Rate': passive_counts / total_sents,
        'Question_Rate': sum(1 for s in sentences if s.text.strip().endswith('?')) / total_sents,
        'Clause_Ratio': sum(1 for token in doc if token.pos_ == 'SCONJ') / total_sents,
        

        'Auxiliary_Verbs': sum(1 for _, tag in pos_tags if tag == 'AUX') / total_words,
        'ToBe_Verbs': sum(1 for word, _ in pos_tags if word.lower() in {'is', 'am', 'are', 'was', 'were', 'be', 'been'}) / total_words,
        'Conjunctions': sum(1 for _, tag in pos_tags if tag == 'CCONJ') / total_words,
        'Prepositions': sum(1 for _, tag in pos_tags if tag == 'ADP') / total_words,
        'Pronouns': sum(1 for _, tag in pos_tags if tag == 'PRON') / total_words,
        'Nominalizations': sum(1 for _, tag in pos_tags if tag == 'NOUN') / total_words,
        

        'Long_Words_Rate': len([w for w in alpha_words if len(w) > long_word_len]) / total_alpha,
        'OneSyllable_Rate': sum(1 for w in alpha_words if get_syllables(w) == 1) / total_alpha,
        'Syllables_Per_Word': sum(get_syllables(w) for w in alpha_words) / total_alpha,
        

        'Start_Pronoun': sum(1 for s in sentences if len(s) > 0 and s[0].pos_ == 'PRON') / total_sents,
        'Start_Article': sum(1 for s in sentences if len(s) > 0 and s[0].pos_ == 'DET' and s[0].text.lower() in {'a', 'an', 'the'}) / total_sents,
        'Start_Interrogative': sum(1 for s in sentences if len(s) > 0 and s[0].pos_ == 'PRON' and s[0].text.lower() in {'who', 'whom', 'whose', 'which', 'what'}) / total_sents,
        'Start_Preposition': sum(1 for s in sentences if len(s) > 0 and s[0].pos_ == 'ADP') / total_sents, 
        'Start_Conjunction': sum(1 for s in sentences if len(s) > 0 and s[0].pos_ in ('CCONJ', 'SCONJ')) / total_sents,


        'Avg_Parse_Tree_Depth': avg_parse_tree_depth,
        'Avg_Dependency_Depth': avg_dependency_depth
    }

def is_passive(sentence) -> bool:

    has_nsubjpass = any(token.dep_ == "nsubjpass" for token in sentence)
    has_auxpass = any(token.dep_ == "auxpass" for token in sentence)
    return has_nsubjpass and has_auxpass

def count_syllables(word: str) -> int:

    word = word.lower().strip()
    if not word.isalpha():
        return 0
        

    if word.endswith('e'):
        word = word[:-1]
    
    vowels = {'a', 'e', 'i', 'o', 'u', 'y'}
    count = 0
    prev_vowel = False
    
    for char in word:
        if char in vowels:
            if not prev_vowel:
                count += 1
            prev_vowel = True
        else:
            prev_vowel = False
            
    return max(1, count)


def process_jsonl_file(jsonl_path, output_dir):

    results_by_year = defaultdict(list)
    

    os.makedirs(output_dir, exist_ok=True)


    with open(jsonl_path, 'r', encoding='utf-8') as infile:

        total_lines = sum(1 for _ in infile)
        infile.seek(0) 
        

        for line in tqdm(infile, total=total_lines, desc="Processing JSONL", unit="line"):
            try:
                obj = json.loads(line)
                title = obj.get('title', '')
                versions = obj.get('versions', [])
                

                for version in versions:
                    content = version.get('content', '')
                    date = version.get('date', '')
                    
                    if date == "revised":
                        continue
                    
                    metrics = calculate_metrics(content)
                    if metrics is None:
                        continue
                    
                    metrics['title'] = title
                    
                    try:
                        year = datetime.strptime(date, "%Y-%m-%d").year
                        results_by_year[year].append(metrics)
                    except ValueError:
                        continue
            except json.JSONDecodeError as e:
                continue
    

    if results_by_year:
        for year, results in results_by_year.items():
            output_csv_path = f"{output_dir}/S_{year}.csv"
            fieldnames = list(results[0].keys())
            with open(output_csv_path, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)

categories = ["Art", "Bio", "Chem", "CS", "Phy", "Math", "Philosophy", "Sports", "simple", "Featured"]
for category in categories:
    process_jsonl_file(
        jsonl_path=f"INPUT YOUR JSONL PATH",
        output_dir=f"INPUT YOUR PATH"
    )
