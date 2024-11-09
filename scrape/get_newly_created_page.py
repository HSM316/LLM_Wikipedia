import requests
from bs4 import BeautifulSoup
import json
import time
import random
import mwparserfromhell
import re

def get_recent_articles(url, limit=2000):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    articles = []
    page_count = 0
    while len(articles) < limit:
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            time.sleep(10)
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        ul_tag = soup.find('ul', class_='mw-contributions-list')

        if ul_tag is None:
            print("Failed to find the list of articles.")
            break

        for li_tag in ul_tag.find_all('li'):
            a_tag = li_tag.find('a', class_='mw-newpages-pagename')
            if a_tag:
                article_title = a_tag['title']
                article_url = 'https://en.wikipedia.org' + a_tag['href']
                articles.append((article_title, article_url))
                if len(articles) >= limit:
                    break

        page_count += 1

        next_link = soup.find('a', class_='mw-nextlink')
        if next_link:
            url = 'https://en.wikipedia.org' + next_link['href']
        else:
            break

        time.sleep(random.uniform(1, 3))

    return articles[:limit]

def clean_wikipedia_content(content):
    wikicode = mwparserfromhell.parse(content)
    internal_titles = wikicode.filter_wikilinks()
    internal_links = ["https://en.wikipedia.org/wiki/" + str(link.title).replace(" ", "_") for link in internal_titles]
    external_links = re.findall(r'http[s]?://[^\s<>"]+', str(wikicode))

    plain_text_content = wikicode.strip_code()
    word_count = len(plain_text_content.split())

    external_links_per_word = len(external_links) / word_count if word_count > 0 else 0
    internal_links_per_word = len(internal_links) / word_count if word_count > 0 else 0

    return plain_text_content, external_links, internal_links, external_links_per_word, internal_links_per_word, word_count

def check_if_new_page(page_title):
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={page_title}&prop=revisions&rvlimit=1&rvprop=ids|user|timestamp|comment|parentid|content&format=json"
    try:
        response = requests.get(url)
        data = response.json()
        page_id = list(data['query']['pages'].keys())[0]
        revisions = data['query']['pages'][page_id].get('revisions', [])

        if revisions:
            revision = revisions[0]
            parent_id = revision.get('parentid', None)
            creator = revision.get('user', 'Unknown')
            creation_time = revision.get('timestamp', 'Unknown')
            
            # 根据 parent_id 判断
            is_new_page = parent_id == 0
            if not is_new_page:
                return False, None, None, None, 0, [], [], 0, 0
            
            content = revision.get('*', 'No content available')
            cleaned_content, external_links, internal_links, external_links_per_word, internal_links_per_word, word_count = clean_wikipedia_content(content)
            
            return True, creator, creation_time, cleaned_content, word_count, external_links, internal_links, external_links_per_word, internal_links_per_word

    except requests.RequestException as e:
        print(f"Error fetching revision data for {page_title}: {e}")
        return False, None, None, None, 0, [], [], 0, 0

def main():
    new_page_limit = 10
    recent_articles_url = 'https://en.wikipedia.org/w/index.php?title=Special:NewPages&offset=&limit=50'
    print(f"Starting to collect {new_page_limit} new pages...")

    articles = get_recent_articles(recent_articles_url, limit=new_page_limit * 15)

    collected_articles = 0
    with open('new_pages.jsonl', 'w', encoding='utf-8') as f:
        for article_title, article_url in articles:
            is_new_page, creator, creation_time, cleaned_content, word_count, external_links, internal_links, external_links_per_word, internal_links_per_word = check_if_new_page(article_title)
            if is_new_page:
                article_data = {
                    'title': article_title,
                    'url': article_url,
                    'content': cleaned_content,
                    'creator': creator,
                    'creation_time': creation_time,
                    'word_count': word_count,
                    'external_links': external_links,
                    'internal_links': internal_links,
                    'external_links_per_word': external_links_per_word,
                    'internal_links_per_word': internal_links_per_word
                }
                f.write(json.dumps(article_data, ensure_ascii=False) + '\n')
                collected_articles += 1        
            if collected_articles >= new_page_limit:
                print(f"Reached the limit of {new_page_limit} new pages. Stopping...")
                break
            time.sleep(random.uniform(0.5, 1.5))

    print(f"Scraped data has been saved to 'new_pages.jsonl'")

if __name__ == "__main__":
    main()
