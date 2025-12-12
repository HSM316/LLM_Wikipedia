import os
import json
import mwparserfromhell
import re
from rich.progress import Progress

END_SECTIONS = ["References", "See also", "Further reading", "External links", "Notes", "Footnotes"]

input_dir = "Wikipedia/Pages"
output_dir = "Wikipedia/clean_Pages"


# ------------------------ 清洗函数 ------------------------ #

def remove_tables(text):
    wikicode = mwparserfromhell.parse(text)
    tables = [str(table) for table in wikicode.filter_tags(matches=lambda tag: tag.tag == "table")]
    for table in tables:
        text = text.replace(table, "")
    return text

def remove_nested_tags(text):
    stack = []
    i = 0
    while i < len(text):
        if text[i:i+2] == '[[':
            stack.append(i)
            i += 2
        elif text[i:i+2] == ']]' and stack:
            start = stack.pop()
            # remove image/file/category
            low = text[start:].lower()
            if low.startswith('[[image:') or low.startswith('[[file:') or low.startswith('[[category:'):
                text = text[:start] + text[i+2:]
                i = start
            else:
                i += 2
        else:
            i += 1
    return text

def remove_section_titles(text):
    return re.sub(r'={2,}\s*.*?\s*={2,}', '', text)

def truncate_at_section(text, sections):
    wikicode = mwparserfromhell.parse(text)
    s = str(wikicode)
    earliest = len(s)

    for sec in sections:
        found = wikicode.get_sections(matches=sec, include_headings=True)
        if found:
            pos = s.find(str(found[0]))
            if 0 <= pos < earliest:
                earliest = pos

    return s[:earliest]

def clean_text_with_mwparser(text, end_sections=None):
    if end_sections is None:
        end_sections = END_SECTIONS
    text = truncate_at_section(text, end_sections)
    text = remove_tables(text)
    text = remove_section_titles(text)
    text = remove_nested_tags(text)
    return mwparserfromhell.parse(text).strip_code()


# ------------------------ 工具函数 ------------------------ #

def count_lines(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return sum(1 for _ in f)


# ------------------------ 主处理函数 ------------------------ #

def process_jsonl_file(input_file_path, output_file_path):
    total = count_lines(input_file_path)

    with open(input_file_path, "r", encoding="utf-8") as fin, \
         open(output_file_path, "w", encoding="utf-8") as fout, \
         Progress() as progress:

        task = progress.add_task(f"[cyan]Processing {os.path.basename(input_file_path)}...", total=total)

        for line in fin:
            try:
                item = json.loads(line)
                title = item.get("title", "")
                content = item.get("content", "")

                cleaned = clean_text_with_mwparser(content)

                out = {"title": title, "cleaned_content": cleaned}
                fout.write(json.dumps(out, ensure_ascii=False) + "\n")

            except Exception as e:
                print(f"Error processing line in {input_file_path}: {e}")

            progress.update(task, advance=1)


# ------------------------ 批量扫描 input_dir ------------------------ #

def main():

    files = [
        f for f in os.listdir(input_dir)
        if (f.endswith("2018.jsonl") or f.endswith("2019.jsonl"))
    ]

    if not files:
        print("No files ending with 2018.jsonl or 2019.jsonl found.")
        return

    os.makedirs(output_dir, exist_ok=True)

    for fname in files:
        input_path = os.path.join(input_dir, fname)

        # 输出：在文件名后加 _clean
        name, ext = os.path.splitext(fname)
        output_path = os.path.join(output_dir, f"{name}_clean.jsonl")

        process_jsonl_file(input_path, output_path)

    print("All JSONL files processed.")


if __name__ == "__main__":
    main()
