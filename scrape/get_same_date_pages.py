# coding=utf-8   
import requests
import random
from datetime import datetime
from bs4 import BeautifulSoup
import json
import time

headers = {
    'User-Agent': 'MyWikipediaScraper/1.0 (myemail@example.com)'
}
matched_titles = set()  # 用于保存找到的匹配页面，避免重复
# 通用的请求函数，自动处理重定向和重试逻辑
def fetch_url(url, params, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response
            else:
                print("Failed to fetch {}, status code: {}".format(url, response.status_code))
        except (requests.RequestException, requests.Timeout) as e:
            if attempt < max_retries - 1:
                print("Error fetching {}. Retrying... (Attempt {}/{})".format(url, attempt + 1, max_retries))
                time.sleep(random.uniform(1, 2))
            else:
                print("Failed to fetch {} after {} attempts.".format(url, max_retries))
                return None

# 获取页面的创建时间
def get_creation_time(page_title):
    api_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": page_title,
        "rvlimit": 1,
        "rvprop": "timestamp",
        "rvdir": "newer",
        "redirects": "",  # 自动处理重定向
        "format": "json"
    }
    response = fetch_url(api_url, headers=headers, params=params)
    
    if response:
        data = response.json()
        # 检查是否存在重定向
        if 'redirects' in data['query']:
            return None
        page = next(iter(data['query']['pages'].values()))
        if 'revisions' in page:
            return page['revisions'][0]['timestamp']
    return None


# 在日志页面中查找符合指定日期的页面
def find_page_on_date(creation_date, exclude_titles):
    url = "https://en.wikipedia.org/wiki/Special:Log"
    params = {
        "type": "patrol",
        "user": "",
        "page": "",
        "wpdate": creation_date,
        "tagfilter": "",
        "wpFormIdentifier": "logeventslist",
        "limit": 5000
    }
    response = fetch_url(url, headers, params)
    if response:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            if href.startswith('/wiki/') and ':' not in href and href != '/wiki/Main_Page':
                article_title = link.text.strip()
                
                # 检查是否已经排除，避免重复
                if article_title in exclude_titles or article_title in matched_titles:
                    continue
                
                # 获取创建时间并验证是否符合要求
                creation_time = get_creation_time(article_title)
                if creation_time and creation_time.startswith(creation_date):
                    matched_titles.add(article_title)  # 添加到匹配集合中
                    return article_title, creation_time
    return None, None

# 主函数：处理每个页面，找到同天创建的其他页面
def match_creation_dates(reference_file, match_file, unmatch_file):
    count = 0
    with open(reference_file, 'r', encoding='utf-8') as infile, \
         open(match_file, 'w', encoding='utf-8') as outfile, \
         open(unmatch_file, 'w', encoding='utf-8') as no_match_outfile:
        
        for line in infile:
            entry = json.loads(line.strip())
            title = entry['title']
            creation_time = entry['creation_time']
            
            # 获取创建日期
            creation_date = creation_time[:10]
            
            # 查找同天创建的不同页面
            matched_page, matched_creation_time = find_page_on_date(creation_date, exclude_titles={title})
            if matched_page:
                output_entry = {
                    "title": matched_page,
                    "creation_time": matched_creation_time
                }
                json.dump(output_entry, outfile, ensure_ascii=False)
                outfile.write('\n')
                count += 1
                if count % 100 == 0:
                    elapsed_time = datetime.now() - start_time
                    print(f"Processed {count} pages. Elapsed time: {elapsed_time}")
                    time.sleep(1)
                
                print(f"Matched: {title} with {matched_page}")
            else:
                # 记录没有找到匹配项的页面信息
                no_match_entry = {
                    "title": title,
                    "creation_time": creation_time
                }
                json.dump(no_match_entry, no_match_outfile, ensure_ascii=False)
                no_match_outfile.write('\n')
                print(f"No match found for {title}")

if __name__ == '__main__':
    start_time = datetime.now()
    input_file = 'D:/WIKIPEDIA/sample/AI_pages.jsonl'
    output_file = 'D:/WIKIPEDIA/sample/matched_pages.jsonl'
    no_match_file = 'D:/WIKIPEDIA/sample/no_match_pages.jsonl'
    match_creation_dates(input_file, output_file, no_match_file)
    end_time = datetime.now()
    print("Scraping completed. Data saved to corresponding JSONL files.")
    print("Total runtime: {}".format(end_time - start_time))
