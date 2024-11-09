import requests
import json
from bs4 import BeautifulSoup

def get_wikipedia_revisions(page_title):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": page_title,
        "rvlimit": "max",
        "format": "json"
    }

    response = requests.get(url, params=params)
    data = response.json()
    pages = data['query']['pages']

    revisions_data = []

    for page_id in pages:
        revisions = pages[page_id]['revisions']
        for revision in revisions:

            parent_id = revision['parentid']
            new_id = revision['revid']

            parent_content = get_page_content(parent_id)
            new_content = get_page_content(new_id)

            diff = get_wikipedia_diff(parent_id, new_id)

            diff_content=parse_diff(diff)

            revisions_data.append({
                "timestamp": revision['timestamp'],
                "user": revision['user'],
                "comment": revision.get('comment', 'No comment'),
                "parent_id": parent_id,
                "new_id": new_id,
                "parent_content": parent_content,
                "new_content": new_content,
                "change_content": diff_content
            })

    filename = f"{page_title}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(revisions_data, f, ensure_ascii=False, indent=4)


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
            return pages[page_id]['revisions'][0]['*']
    else:
        return "No content found or invalid revision ID."


def get_wikipedia_diff(revid1, revid2):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "compare",
        "fromrev": revid1,
        "torev": revid2,
        "prop": "diff",
        "format": "json"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if 'compare' in data:
        return data['compare']['*']
    else:
        return "No difference found or invalid revision IDs."

def parse_diff(diff_html):
    soup = BeautifulSoup(diff_html, 'html.parser')
    changes = []

    for row in soup.find_all('tr'):
        deleted = row.find(class_='diff-deletedline')
        added = row.find(class_='diff-addedline')

        if deleted:
            changes.append({'type': 'deleted', 'content': deleted.get_text(strip=True)})
        if added:
            changes.append({'type': 'added', 'content': added.get_text(strip=True)})

    return changes


# 使用示例
get_wikipedia_revisions("Tricia Robredo")
