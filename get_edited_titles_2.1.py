#coding=utf-8
import requests
import json
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import random

# 通用的请求函数，自动处理重定向和重试逻辑
def fetch_url(url, headers, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response
            else:
                print(f"Failed to fetch {url}, status code: {response.status_code}")
        except (requests.RequestException, requests.Timeout):
            if attempt < max_retries - 1:
                print(f"Error fetching {url}. Retrying... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(random.uniform(2, 5))
    return None

# 获取指定日期的文章标题
def get_titles_for_day(year, month, day, language_code, headers, max_titles=5):
    url = "https://{}.wikipedia.org/w/index.php?title=Special:Log&day={}&page=&tagfilter=&type=patrol&user=&wpFormIdentifier=logeventslist&wpdate={}-{:02d}-{:02d}&month={}&year={}&offset=&limit=500".format(language_code, day, year, month, day, month, year)
    response = fetch_url(url, headers)
    
    if response:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        
        titles = []
        for link in links:
            href = link['href']
            # 筛选出有效的文章链接
            if href.startswith('/wiki/') and ':' not in href and href != '/wiki/Main_Page':
                title = link.get_text(strip=True)
                
                # 检查修订日期是否符合要求
                revision_date = f"{year:04d}-{month:02d}-{day:02d}"
                revision_time = get_revision_time(title, revision_date, language_code, headers)
                
                if revision_time and revision_time.startswith(revision_date):
                    titles.append({'edit_time': revision_time, 'title': title})
                
                if len(titles) >= max_titles:
                    break
        
        return titles
    return []

# 获取单个文章的修订时间
def get_revision_time(title, date, language_code, headers):
    api_url = f"https://{language_code}.wikipedia.org/w/api.php?action=query&prop=revisions&titles={title}&rvlimit=1&rvprop=timestamp&rvdir=newer&rvstart={date}T00:00:00Z&format=json"
    response = fetch_url(api_url, headers)
    
    if response:
        data = response.json()
        pages = data.get('query', {}).get('pages', {})
        page_id = list(pages.keys())[0]
        revisions = pages[page_id].get('revisions', [])
        
        if revisions:
            return revisions[0].get('timestamp')
    return None

# 爬取指定时间的文章标题并保存为JSONL格式
def scrape_titles_to_jsonl(language_code, output_file):
    headers = {
        'User-Agent': 'MyWikipediaScraper/1.0 (myemail@example.com)'
    }
    
    start_date = datetime(2024, 9, 1)
    end_date = datetime(2024, 10, 1)
    current_date = start_date
    
    with open(output_file, 'w', encoding='utf-8') as f:
        while current_date <= end_date:
            year, month, day = current_date.year, current_date.month, current_date.day
            
            titles = get_titles_for_day(year, month, day, language_code, headers, max_titles=5)
            
            for title_info in titles:
                json.dump(title_info, f, ensure_ascii=False)
                f.write('\n')
            
            current_date += timedelta(days=5) 
            time.sleep(1)  

    print(f"Scraping completed. Titles saved to {output_file}")

if __name__ == '__main__':
    scrape_titles_to_jsonl('en', 'titles_en.jsonl')
