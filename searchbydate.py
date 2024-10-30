import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def extract_last_edit_time(page_html):
    soup = BeautifulSoup(page_html, 'html.parser')
    last_edit_info = soup.find('li', id='footer-info-lastmod')

    if last_edit_info:
        last_edit_time = last_edit_info.text
        date_pattern = r"(\d{1,2} [A-Za-z]+ \d{4})"
        date_match = re.search(date_pattern, last_edit_time)
        if date_match:
            date_str = date_match.group(1)
            return datetime.strptime(date_str, '%d %B %Y')
    return None


def fetch_page_html(oldid):
    url = f'https://en.wikipedia.org/w/index.php?oldid={oldid}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching page with oldid {oldid}: {e}")
        return None


def binary_search_page_by_date(target_date, low, high):
    while low <= high:
        mid = (low + high) // 2
        print(f"Checking oldid: {mid}")

        page_html = fetch_page_html(mid)
        if page_html is None:
            return None

        last_edit_time = extract_last_edit_time(page_html)
        if last_edit_time is None:
            return None

        print(f"Page at oldid {mid} was last edited on {last_edit_time.strftime('%Y-%m-%d')}")

        if last_edit_time == target_date:
            return mid
        elif last_edit_time > target_date:
            high = mid - 1
        else:
            low = mid + 1

    return None


# 示例：查找2024年5月1日的页面
if __name__ == "__main__":
    target_date = datetime(2024, 5, 15)
    low_oldid = 1000000000
    high_oldid = 1252820000

    result_oldid = binary_search_page_by_date(target_date, low_oldid, high_oldid)

    if result_oldid:
        print(f"Found page with oldid {result_oldid} on {target_date.strftime('%Y-%m-%d')}")
    else:
        print("No page found for the target date.")
