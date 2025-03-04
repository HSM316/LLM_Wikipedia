import requests
import jsonlines
from tqdm import tqdm 


year = "2024"
input_file = f'RAG/news/title/{year}_titles.jsonl'  
output_file = f'RAG/Plain_news/news_{year}.jsonl' 

def fetch_wikinews_content(title):
    """
    Fetch the plain text of the news article from Wikinews API based on the title.
    """
    url = f"https://en.wikinews.org/w/api.php?action=query&format=json&titles={title}&prop=extracts&exintro&explaintext"
    response = requests.get(url)
    data = response.json()
    
    pages = data.get("query", {}).get("pages", {})
    for page_id, page_info in pages.items():
        if "extract" in page_info:
            return page_info["extract"]
    return None  

with jsonlines.open(input_file, 'r') as reader, jsonlines.open(output_file, 'w') as writer:

    for line in tqdm(reader, desc="Fetching news content", unit="article"):
        title = line.get('title')
        if title:
            content = fetch_wikinews_content(title)
            if content:
                writer.write({"title": title, "content": content})

