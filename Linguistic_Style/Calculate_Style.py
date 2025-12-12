import spacy
import json
import csv
import os
import math
from tqdm import tqdm
from multiprocessing import Pool, cpu_count

# =========================
# 参数
# =========================
SHORT_SENT_THRESHOLD = 10
LONG_SENT_THRESHOLD = 20
LONG_WORD_LENGTH = 6
SYLLABLE_EXCEPTIONS = {
    "simplified": 4, "identified": 4
}

# ================
# 全局变量：每个进程会单独初始化 spaCy
# ================
nlp = None

def init_worker():
    """每个子进程独立加载 spaCy"""
    global nlp
    nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer", "textcat"])


# =========================
# 工具函数
# =========================
def is_passive(sentence) -> bool:
    has_nsubjpass = any(token.dep_ == "nsubjpass" for token in sentence)
    has_auxpass = any(token.dep_ == "auxpass" for token in sentence)
    return has_nsubjpass and has_auxpass


def count_syllables(word: str) -> int:
    word = word.lower().strip()
    if not word.isalpha():
        return 0
    if word.endswith("e"):
        word = word[:-1]

    vowels = {"a", "e", "i", "o", "u", "y"}
    count = 0
    prev_vowel = False
    for ch in word:
        if ch in vowels:
            if not prev_vowel:
                count += 1
            prev_vowel = True
        else:
            prev_vowel = False
    return max(1, count)


# =========================
# 指标计算（可并行）
# =========================
def calculate_metrics(text: str) -> dict:
    global nlp
    doc = nlp(text)
    sentences = list(doc.sents)

    alpha_words = [t.text.lower() for t in doc if t.is_alpha]
    total_alpha = len(alpha_words) or 1
    unique_alpha = len(set(alpha_words))

    pos_tags = [(t.text, t.pos_) for t in doc]
    total_words = len(alpha_words) or 1
    total_sents = len(sentences) or 1

    # 音节缓存
    syllable_cache = {}

    def get_syllables(w: str) -> int:
        if w in syllable_cache:
            return syllable_cache[w]
        if w in SYLLABLE_EXCEPTIONS:
            cnt = SYLLABLE_EXCEPTIONS[w]
        else:
            cnt = count_syllables(w)
        syllable_cache[w] = cnt
        return cnt

    passive_counts = sum(1 for s in sentences if is_passive(s))

    # parse tree depth
    def parse_depth(tok, visited=None, depth=1, max_depth=100):
        if visited is None:
            visited = set()

        if tok in visited:
            return depth
        if depth >= max_depth:
            return max_depth

        visited.add(tok)
        children = list(tok.children)
        if not children:
            return depth
        return max(depth, max(parse_depth(ch, visited, depth + 1, max_depth) for ch in children))

    parse_depths = [parse_depth(s.root) for s in sentences] or [0]
    avg_parse_tree_depth = sum(parse_depths) / len(parse_depths)

    return {
        "Long_Sent_Rate": len([s for s in sentences if len(s) > LONG_SENT_THRESHOLD]) / total_sents,
        "Avg_Sent_Length": total_words / total_sents,
        "CTTR": unique_alpha / math.sqrt(2 * total_alpha),
        "Passive_Voice_Rate": passive_counts / total_sents,
        "Clause_Ratio": sum(1 for t in doc if t.pos_ == "SCONJ") / total_sents,
        "Auxiliary_Verbs": sum(1 for _, pos in pos_tags if pos == "AUX") / total_words,
        "ToBe_Verbs": sum(
            1 for w, _ in pos_tags if w.lower() in {"is", "am", "are", "was", "were", "be", "been"}
        ) / total_words,
        "Conjunctions": sum(1 for _, pos in pos_tags if pos == "CCONJ") / total_words,
        "Prepositions": sum(1 for _, pos in pos_tags if pos == "ADP") / total_words,
        "Pronouns": sum(1 for _, pos in pos_tags if pos == "PRON") / total_words,
        "Nominalizations": sum(1 for _, pos in pos_tags if pos == "NOUN") / total_words,
        "Long_Words_Rate": len([w for w in alpha_words if len(w) > LONG_WORD_LENGTH]) / total_alpha,
        "OneSyllable_Rate": sum(1 for w in alpha_words if get_syllables(w) == 1) / total_alpha,
        "Syllables_Per_Word": sum(get_syllables(w) for w in alpha_words) / total_alpha,
        "Start_Pronoun": sum(1 for s in sentences if len(s) > 0 and s[0].pos_ == "PRON") / total_sents,
        "Start_Article": sum(
            1 for s in sentences if len(s) > 0 and s[0].text.lower() in {"a", "an", "the"}
        ) / total_sents,
        "Avg_Parse_Tree_Depth": avg_parse_tree_depth,
    }


# =========================
# 并行处理单个记录
# =========================
def process_one_record(line: str):
    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        return None

    title = obj.get("title", "")
    content = obj.get("cleaned_content", "")

    if not content.strip():
        return None

    metrics = calculate_metrics(content)
    metrics["title"] = title
    return metrics


# =========================
# 并行处理 jsonl 文件
# =========================
def process_clean_jsonl(jsonl_path: str, output_csv: str, workers=None):
    if workers is None:
        workers = max(1, cpu_count() - 1)

    print(f"Using {workers} parallel workers.")

    with open(jsonl_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    results = []

    with Pool(processes=workers, initializer=init_worker) as pool:
        for res in tqdm(pool.imap(process_one_record, lines), total=len(lines), desc=f"Processing {os.path.basename(jsonl_path)}"):
            if res is not None:
                results.append(res)

    if not results:
        print(f"No valid records in {jsonl_path}")
        return

    fieldnames = list(results[0].keys())
    with open(output_csv, "w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Saved → {output_csv}")


# =========================
# 批量全部类别 + 年份
# =========================
base_dir_in = "Wikipedia/Extracted_Full"
base_dir_out = "Wikipedia/Metrics_Full"
os.makedirs(base_dir_out, exist_ok=True)

categories = ["Art", "Bio", "Chem", "CS", "Phy", "Math", "Philosophy", "Sports"]
years = [2020, 2021, 2022, 2023, 2024, 2025]

for cat in categories:
    for year in years:
        in_path = os.path.join(base_dir_in, f"{cat}_{year}.jsonl")
        if not os.path.exists(in_path):
            print(f"Skip missing file: {in_path}")
            continue

        out_path = os.path.join(base_dir_out, f"{cat}_{year}_metrics.csv")
        process_clean_jsonl(in_path, out_path, workers=8)  # 可修改 worker 数
