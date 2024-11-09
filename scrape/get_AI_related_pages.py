import requests
import json
from datetime import datetime
import time
import random

headers = {
    'User-Agent': 'MyWikipediaScraper/1.0 (myemail@example.com)'
}

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


def get_pages_by_category(category_name, max_pages=1050):
    before_date = "2020-01-01"
    after_date = "2008-01-01"
    url = "https://en.wikipedia.org/w/api.php"
    before_date = datetime.strptime(before_date, "%Y-%m-%d")
    after_date = datetime.strptime(after_date, "%Y-%m-%d")
    pages = set()  # 用于保存唯一的标题
    to_check_categories = [category_name]
    checked_categories = set()
    saved_count = 0  # 计数器，记录已保存的页面数

    with open("D:/WIKIPEDIA/sample/AI_related_pages.jsonl", "w", encoding="utf-8") as file:
        while to_check_categories and saved_count < max_pages:
            current_category = to_check_categories.pop(0)
            checked_categories.add(current_category)

            params = {
                "action": "query",
                "list": "categorymembers",
                "cmtitle": f"Category:{current_category}",
                "cmlimit": "max",
                "format": "json"
            }

            response = fetch_url(url, params=params)
            data = response.json()

            for page in data.get("query", {}).get("categorymembers", []):
                # 排除子类
                if page["ns"] == 14:
                    sub_category = page["title"].replace("Category:", "")
                    if sub_category not in checked_categories:
                        to_check_categories.append(sub_category)

                elif page["ns"] == 0 and saved_count < max_pages:
                    page_title = page["title"]
                    if page_title not in pages:
                        # 检查创建时间
                        creation_date = get_creation_date(page_title)
                        if creation_date and before_date > creation_date > after_date:
                            print(f"save {page_title} created in {creation_date}")
                            pages.add(page_title)
                            # 保存
                            json.dump(
                                {"title": page_title, "creation_time": creation_date.strftime("%Y-%m-%d %H:%M:%S")},
                                file, ensure_ascii=False)
                            file.write("\n")
                            saved_count += 1  # 更新计数器

                            # 每保存50篇文章输出一次提示
                            if saved_count % 50 == 0:
                                print(f"{saved_count} pages have been saved.")


def get_creation_date(page_title):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": page_title,
        "prop": "revisions",
        "rvprop": "timestamp",
        "rvlimit": 1,
        "rvdir": "newer",
        "format": "json"
    }

    response = fetch_url(url, params=params)
    data = response.json()
    page_info = list(data.get("query", {}).get("pages", {}).values())[0]

    if "revisions" in page_info:
        creation_timestamp = page_info["revisions"][0]["timestamp"]
        return datetime.strptime(creation_timestamp, "%Y-%m-%dT%H:%M:%SZ")

    return None


def main():
    start_time = datetime.now()
    category_name = "Artificial intelligence"
    get_pages_by_category(category_name)
    end_time = datetime.now()
    print("Scraping completed. Data saved to corresponding JSONL files.")
    print("Total runtime: {}".format(end_time - start_time))


if __name__ == "__main__":
    main()
