import os
import re
import json
import mwparserfromhell
from rich.progress import Progress

# ===========================
#  清理函数（与旧代码保持一致）
# ===========================

def remove_tables(text):
    wikicode = mwparserfromhell.parse(text)
    tables = [str(t) for t in wikicode.filter_tags(matches=lambda tag: tag.tag == "table")]
    for t in tables:
        text = text.replace(t, "")
    return text


def truncate_at_section(text):
    """
    只保留第一个 section 之前的内容
    """
    match = re.search(r'^==\s*(.*?)\s*==', text, re.MULTILINE)
    if match:
        return text[:match.start()]
    return text


def remove_nested_tags(text):
    """
    删除 [[Image: ..]], [[File: ..]], [[Category: ..]]
    """
    stack = []
    i = 0
    while i < len(text):
        if text[i:i+2] == '[[':
            stack.append(i)
            i += 2
        elif text[i:i+2] == ']]' and stack:
            start = stack.pop()
            low = text[start:].lower()
            if low.startswith("[[image:") or low.startswith("[[file:") or low.startswith("[[category:"):
                text = text[:start] + text[i+2:]
                i = start
            else:
                i += 2
        else:
            i += 1
    return text


def clean_text(text):
    """
    整合所有清洗操作
    """
    text = truncate_at_section(text)
    text = remove_nested_tags(text)
    text = remove_tables(text)
    return mwparserfromhell.parse(text).strip_code()


# ===========================
#  JSONL 文件处理
# ===========================

def process_jsonl(input_path, output_path):
    """
    逐行读取 JSONL，清洗 content/cleaned_content，写出新 JSONL。
    """
    with open(input_path, "r", encoding="utf-8") as fin, \
         open(output_path, "w", encoding="utf-8") as fout:

        for line in fin:
            try:
                data = json.loads(line.strip())
            except:
                continue

            title = data.get("title", "")
            text = data.get("content", "")
            cleaned = clean_text(text)
            out = {"title": title, "cleaned_content": cleaned}
            fout.write(json.dumps(out, ensure_ascii=False) + "\n")


# ===========================
#  批量处理：遍历目录下所有 JSONL
# ===========================

def process_all_jsonl(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    files = [f for f in os.listdir(input_dir) if f.endswith(".jsonl")]

    with Progress() as progress:
        task = progress.add_task("[cyan]Cleaning JSONL files...", total=len(files))

        for fname in files:
            input_path = os.path.join(input_dir, fname)
            output_path = os.path.join(output_dir, fname.replace("_cleaned.jsonl", "_first.jsonl"))

            process_jsonl(input_path, output_path)
            progress.update(task, advance=1)

    print("All JSONL files cleaned and saved.")


# ===========================
#  主入口
# ===========================

input_dir = r"Wikipedia/Pages"          # 输入：所有类别、年份 JSONL 文件
output_dir = r"Wikipedia/clean_First"   # 输出目录（可自由修改）

process_all_jsonl(input_dir, output_dir)
