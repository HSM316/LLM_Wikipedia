import os
import re
from datetime import datetime
import requests
import json

def get_wikipedia_revisions(page_title,request_time):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": page_title,
        "rvlimit": "max",
        "format": "json"
    }
    continue_token = None
    while True:
        if continue_token:
            params["rvcontinue"] = continue_token
        response = requests.get(url, params=params)
        data = response.json()
        pages = data.get('query', {}).get('pages', {})
        for page_id, page_data in pages.items():
            revisions = page_data.get('revisions', [])
            for revision in revisions:
                now_edition_time = revision['timestamp']
                if (now_edition_time <= request_time or revision['parentid'] == 0):
                    content = get_page_content(revision['revid'])
                    return content
        if "continue" in data:
            continue_token = data["continue"]["rvcontinue"]
        else:
            break

def get_page_content(revision_id):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "revids": revision_id,
        "format": "json"
    }
    response = requests.get(url, params=params)
    data = response.json()
    if 'query' in data and 'pages' in data['query']:
        pages = data['query']['pages']
        for page_id in pages:
            return pages[page_id]['revisions'][0].get('*', 'No content available')
    else:
        return "No content found or invalid revision ID."

def get_every_edition():
    titles=[]
    with open('2020_new_pages_4.jsonl', 'r', encoding='utf-8') as file:
        for line in file:
            entry = json.loads(line.strip())
            titles.append(entry)
    request_times=["2020-01-01T23:00:00Z","2021-01-01T00:00:00Z","2022-01-01T00:00:00Z","2023-01-01T00:00:00Z","2024-01-01T00:00:00Z"]
    for title_entry in titles:
        title = title_entry.get("title")
        sanitized_title = title.replace(" ", "_").replace(":", "_")
        sanitized_title = re.sub(r'[\\/*?:"<>|]', "_", sanitized_title)
        for request_time in request_times:
            dt = datetime.strptime(request_time, "%Y-%m-%dT%H:%M:%SZ")
            date_str = dt.strftime("%Y-%m-%d")
            filename = f"ver_{date_str}.txt"
            folder_path = os.path.join("articles", sanitized_title)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            file_path = os.path.join(folder_path, filename)
            if not os.path.exists(file_path):
                with open(file_path, "w", encoding="utf-8") as f:
                    content = get_wikipedia_revisions(title, request_time)
                    f.write(content)

get_every_edition()
print("end")