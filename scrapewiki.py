import requests
import random
import time
import json
import wikipediaapi
from bs4 import BeautifulSoup

wiki_wiki = wikipediaapi.Wikipedia('en')

def get_page_info(oldid, max_retries=3):
    page_url = f"https://en.wikipedia.org/w/index.php?oldid={oldid}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        response = requests.get(page_url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching page with oldid {oldid}: {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        title_tag = soup.find('h1', id='firstHeading')
        title = title_tag.text if title_tag else f"Unknown Title (oldid={oldid})"

        if title == "Error":
            print(f"Skipping page with title 'Error' for oldid {oldid}")
            return None

        content = get_page_content(title, max_retries)

        last_edit_time_tag = soup.find('li', id='footer-info-lastmod')
        if last_edit_time_tag:
            last_edit_time_full = last_edit_time_tag.text.strip()
            last_edit_time = last_edit_time_full.split("on ")[1].replace("at ", "").replace(".", "")
        else:
            last_edit_time = "Unknown Time"

        return {
            'title': title,
            'url': page_url,
            'last_edit_time': last_edit_time,
            'content': content
        }

    except Exception as e:
        print(f"Failed to retrieve page for oldid {oldid}: {e}")
        return None

def get_page_content(page_title, max_retries=3):
    attempt = 0
    while attempt < max_retries:
        try:
            page = wiki_wiki.page(page_title)
            if not page.exists():
                print(f"Page '{page_title}' does not exist.")
                return None
            return page.text
        except (requests.RequestException, requests.Timeout) as e:
            if attempt < max_retries - 1:
                print(f"Error scraping '{page_title}'. Retrying... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(random.uniform(2, 5))
            else:
                print(f"Failed to scrape '{page_title}' after {max_retries} attempts.")
                return None
        attempt += 1

def jump_and_collect_articles(start_oldid, num_jumps=2000, decrement_range=20000*14, min_content_length=5):
    articles = []
    current_oldid = start_oldid

    for _ in range(num_jumps):
        decrement_value = random.randint(decrement_range - 10000, decrement_range + 10000)
        current_oldid -= decrement_value
        collected_count = 0
        while collected_count < 1:
            page_info = get_page_info(current_oldid)

            if page_info and page_info['content'] and len(page_info['content']) > min_content_length:
                articles.append(page_info)
                collected_count += 1
                print(f"Collected article from oldid: {current_oldid}")
            else:
                print(f"Skipped article from oldid: {current_oldid} due to empty content.")

            current_oldid -= random.randint(4000, 6000)

        print(f"Jump {_ + 1}/{num_jumps} complete. Current oldid: {current_oldid}")

    return articles

def save_to_json_file(data, filename='articles.json'):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data successfully saved to {filename}")
    except Exception as e:
        print(f"Failed to save data to {filename}: {e}")


def print_last_edit_times(articles):
    for article in articles:
        print(f"Title: {article['title']} - Last Edit Time: {article['last_edit_time']}")


start_oldid = 1252828800
collected_articles = jump_and_collect_articles(start_oldid)

save_to_json_file(collected_articles, 'collected_articles.json')
print_last_edit_times(collected_articles)
