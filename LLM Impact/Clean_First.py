import os 
import mwparserfromhell
import re
from rich.progress import Progress

input_dir = r'D:\Category\simple\simple_pages'
output_dir = r'D:\Category\simple\simple_First'

def remove_tables(text):
    wikicode = mwparserfromhell.parse(text)
    tables = [str(table) for table in wikicode.filter_tags(matches=lambda tag: tag.tag == "table")]
    for table in tables:
        text = text.replace(table, "")
    return text

def truncate_at_section(text):
    match = re.search(r'^==\s*(.*?)\s*==', text, re.MULTILINE)
    
    if match:
        section_position = match.start() 
        return text[:section_position]
    
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

            if text[start:].lower().startswith('[[image:') or text[start:].lower().startswith('[[file:') or text[start:].lower().startswith('[[category:'):
                text = text[:start] + text[i+2:]
                i = start
            else:
                i += 2
        else:
            i += 1

    return text


def process_file(file_path, folder_name):
    try:
        with open(file_path, 'r', encoding='ISO-8859-1') as file:
            text = file.read()

        text = text.encode('ISO-8859-1').decode('utf-8', errors='ignore')
        text = truncate_at_section(text)  
        text = remove_nested_tags(text)
        text = remove_tables(text) 
    
        cleaned_text = mwparserfromhell.parse(text).strip_code()
        output_page_folder = os.path.join(output_dir, folder_name)
        os.makedirs(output_page_folder, exist_ok=True)
        output_file_path = os.path.join(output_page_folder, os.path.basename(file_path))
        with open(output_file_path, "w", encoding="utf-8") as output_file:
            output_file.write(cleaned_text)

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")


def process_folder(folder_name):
    folder_path = os.path.join(input_dir, folder_name)
    if os.path.isdir(folder_path):
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".txt"):
                file_path = os.path.join(folder_path, file_name)
                process_file(file_path, folder_name)


folders = os.listdir(input_dir)

with Progress() as progress:
    task = progress.add_task("[cyan]Processing folders...", total=len(folders))
    
    for folder in folders:
        process_folder(folder)
        progress.update(task, advance=1) 

print("All files have been processed and saved.")