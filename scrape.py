#coding=utf-8
import requests
import mwparserfromhell
import json
import time
from datetime import datetime, timedelta
import re
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
                print("Failed to fetch {}, status code: {}".format(url, response.status_code))
        except (requests.RequestException, requests.Timeout) as e:
            if attempt < max_retries - 1:
                print("Error fetching {}. Retrying... (Attempt {}/{})".format(url, attempt + 1, max_retries))
                time.sleep(random.uniform(2, 5)) 
            else:
                print("Failed to fetch {} after {} attempts.".format(url, max_retries))
                return None


# 获取纯文本并统计外部、内部链接数
def clean_wikipedia_content(content, language_code):

    # 使用 mwparserfromhell 解析维基百科的标记语言
    wikicode = mwparserfromhell.parse(content)

    # 提取维基百科中的内部链接 ([[...]] 格式的链接)
    internal_links = wikicode.filter_wikilinks()

    # 使用正则表达式查找所有外部链接（以 http 或 https 开头的链接）
    external_links = re.findall(r'http[s]?://[^\s<>"]+', str(wikicode))

    # 将wikitext内容转换为纯文本（去除标记）
    plain_text_content = wikicode.strip_code()

    # 清理换行符和反斜杠，简化文本以便统计字数
    plain_text_for_word_count = plain_text_content.replace('\n', '').replace('\\', '').strip()

    # 根据语言处理字数/词数
    if language_code == "zh":
        # 中文页面：直接统计字符数
        word_count = len(plain_text_for_word_count)
    else:
        # 非中文页面：按空格分割计算词数
        word_count = len(plain_text_for_word_count.split())

    # 计算外部/内部链接与字数/词数的比率
    external_links_per_word = len(external_links) / word_count if word_count > 0 else 0
    internal_links_per_word = len(internal_links) / word_count if word_count > 0 else 0

    return plain_text_content, external_links_per_word, internal_links_per_word, word_count


# 获取指定日期的文章修订内容
def get_article_revision_and_time(page_title, date, language_code, headers, max_retries=5):

    api_url = "https://{}.wikipedia.org/w/api.php?action=query&prop=revisions&titles={}&rvlimit=1&rvprop=timestamp|content&rvdir=newer&rvstart={}T00:00:00Z&redirects=1&format=json".format(language_code, page_title, date)
    response = fetch_url(api_url, headers, max_retries)
    
    if response:
        data = response.json()

        # 检查是否存在页面重定向
        if 'redirects' in data['query']:
            return None, None, 0, 0, 0
        
        page_id = list(data['query']['pages'].keys())[0]
        revisions = data['query']['pages'][page_id].get('revisions', [])

        # 提取文章内容和修订时间
        if revisions:
            raw_content = revisions[0].get('*', 'Content not found')
            revision_time = revisions[0].get('timestamp', 'Time not found')

            # 解析wikitext内容并计算链接比率及字数
            cleaned_content, external_links_per_word, internal_links_per_word, word_count = clean_wikipedia_content(raw_content, language_code)

            return cleaned_content, revision_time, external_links_per_word, internal_links_per_word, word_count
    
    return None, None, 0, 0, 0


# 获取特定日期的维基百科文章
def get_articles_for_day(year, month, day, language_code, headers, max_articles=5, existing_titles=None):

    url = "https://{}.wikipedia.org/w/index.php?title=Special:Log&day={}&page=&tagfilter=&type=patrol&user=&wpFormIdentifier=logeventslist&wpdate={}-{:02d}-{:02d}&month={}&year={}&offset=&limit=500".format(language_code, day, year, month, day, month, year)
    print("Scraping {}...".format(url))

    response = fetch_url(url, headers)
    if response:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)

        articles = []
        for link in links:
            href = link['href']
            # 排除非文章的链接和主页面
            if href.startswith('/wiki/') and ':' not in href and href != '/wiki/Main_Page':
                article_title = link.text.strip()

                # 避免返回重复的标题
                if existing_titles is None or article_title not in existing_titles:
                    full_url = "https://{}.wikipedia.org{}".format(language_code, href)

                    revision_date = "{}-{:02d}-{:02d}".format(year, month, day)
                    content, revision_time, external_links_per_word, internal_links_per_word, word_count = get_article_revision_and_time(article_title, revision_date, language_code, headers)

                    # 保存文章信息
                    if content and revision_time:
                        articles.append({
                            'title': article_title,
                            'url': full_url,
                            'content': content,
                            'time': revision_time,
                            'word_count': word_count,
                            'external_links_per_word': external_links_per_word,
                            'internal_links_per_word': internal_links_per_word
                        })

                    if len(articles) >= max_articles:
                        break  # 如果达到了需要的文章数，停止进一步爬取

        return articles
    return []


def scrape_articles_for_languages():

    start_time = datetime.now()

    headers = {
        'User-Agent': 'MyWikipediaScraper/1.0 (myemail@example.com)'
    }

    # 定义需要爬取的语言及其输出文件名
    languages = {
        'en': 'articles_en.json',
        'zh': 'articles_zh.json',
        'fr': 'articles_fr.json',
        'de': 'articles_de.json',
        'es': 'articles_es.json',
        'it': 'articles_it.json'
    }

    # 设置日期范围
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 10, 1)

    # 为每种语言爬取文章并保存到对应的文件
    for language_code, output_file in languages.items():
        all_articles = []
        current_date = start_date

        while current_date <= end_date:
            year, month, day = current_date.year, current_date.month, current_date.day

            # 直接爬取当天的文章
            articles = get_articles_for_day(year, month, day, language_code, headers, max_articles=1, existing_titles=[a['title'] for a in all_articles])

            # 将新获取的文章加入到最终结果
            all_articles.extend(articles)

            current_date += timedelta(days=5)  # 移动到下一天
            time.sleep(1)  # 加入延时，防止过多请求

        # 写入 JSON 文件时确保格式正确
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                # 确保输出是一个包含所有文章的列表
                json.dump(all_articles, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print("Error writing to file {}: {}".format(output_file, e))

    end_time = datetime.now()
    print("Scraping completed. Data saved to corresponding JSON files.")
    print("Total runtime: {}".format(end_time - start_time))


if __name__ == '__main__':
    scrape_articles_for_languages()
