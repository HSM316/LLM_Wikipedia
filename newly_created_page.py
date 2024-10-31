import requests
from bs4 import BeautifulSoup
import wikipediaapi
import json
import time
import random

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

    # print(f"Finished collecting {len(articles)} articles.")
    return articles[:limit]

def check_if_new_page(page_title):

    #检查页面是否为新建页面,判断标准是revision的parentid为0,同时获取页面的创建者和创建时间
    
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={page_title}&prop=revisions&rvlimit=1&rvprop=ids|user|timestamp|comment|parentid&format=json"
    try:
        response = requests.get(url)
        data = response.json()
        pages = data.get('query', {}).get('pages', {})
        for page_id, page_info in pages.items():
            revisions = page_info.get('revisions', [])
            if revisions and revisions[0].get('parentid') == 0:
                creator = revisions[0].get('user', 'Unknown')
                creation_time = revisions[0].get('timestamp', 'Unknown')
                return True, creator, creation_time
            else:
                return False, None, None
    except requests.RequestException as e:
        print(f"Error checking revisions for '{page_title}': {e}")
        return False, None, None


def scrape_wikipedia_article(page_title, wiki_wiki, max_retries=3):
    for attempt in range(max_retries):
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

def main():
    # 需要爬取的新建页面数量，修改此变量即可
    new_page_limit = 10
    
    recent_articles_url = 'https://en.wikipedia.org/w/index.php?title=Special:NewPages&offset=&limit=50'
    print(f"Starting to collect {new_page_limit} new pages...")
    
    # 为了确保获取到足够的新建页面，获取 new_page_limit 的 15 倍页面
    articles = get_recent_articles(recent_articles_url, limit=new_page_limit * 15)
    
    wiki_wiki = wikipediaapi.Wikipedia(
        user_agent='WikipediaScraper (your_email@example.com)',
        language='en',
        timeout=30
    )

    collected_articles = 0
    with open('new_pages.jsonl', 'w', encoding='utf-8') as f:
        for article_title, article_url in articles:
            is_new_page, creator, creation_time = check_if_new_page(article_title)
            if is_new_page:
                content = scrape_wikipedia_article(article_title, wiki_wiki)
                if content:
                    article_data = {
                        'title': article_title,
                        'url': article_url,
                        'content': content,
                        'creator': creator,
                        'creation_time': creation_time
                    }
                    f.write(json.dumps(article_data, ensure_ascii=False) + '\n')
                    collected_articles += 1        
            if collected_articles >= new_page_limit:  # 达到需要的数量后暂停
                print(f"Reached the limit of {new_page_limit} new pages. Stopping...")
                break

            time.sleep(random.uniform(0.5, 1.5))

    print(f"Scraped data has been saved to 'new_pages.jsonl'")

if __name__ == "__main__":
    main()
