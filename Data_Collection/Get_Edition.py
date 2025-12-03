import os
import json
import time
import random
import argparse
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed

import requests
from rich.progress import (
    Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
)

HEADERS = {
    'User-Agent': 'MyWikipediaScraper/1.0 (email@example.com)'
}


# ------------------------------- #
#   单标题爬取函数（子进程执行）
# ------------------------------- #
def fetch_single_title(args):
    """子进程：爬取单个 title 的目标 revision"""
    title, target_dt = args

    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": title,
        "rvlimit": "max",
        "rvdir": "older",
        "rvslots": "main",
        "rvprop": "ids|timestamp|content",
        "format": "json"
    }

    continue_token = None
    revid = None
    content = None

    # API 请求函数（减少代码复制）
    def fetch_url(url, params, max_retries=3):
        for attempt in range(max_retries):
            try:
                resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
                if resp.status_code == 200:
                    return resp
            except Exception:
                pass

            if attempt < max_retries - 1:
                time.sleep(random.uniform(1, 2))
        return None

    try:
        while True:
            if continue_token:
                params["rvcontinue"] = continue_token

            resp = fetch_url(url, params)
            if not resp:
                return {"title": title, "error": "API request failed"}

            data = resp.json()
            pages = data.get("query", {}).get("pages", {})

            for pid, page in pages.items():
                if "redirect" in page:
                    return {"title": title, "error": "Redirect page"}

                for r in page.get("revisions", []):
                    r_time = datetime.strptime(r["timestamp"], "%Y-%m-%dT%H:%M:%SZ")

                    if r_time <= target_dt:
                        revid = r["revid"]
                        content = r["slots"]["main"].get("*", "")
                        break

                if revid:
                    break

            if revid:
                break

            if "continue" in data:
                continue_token = data["continue"]["rvcontinue"]
            else:
                break

        if not revid:
            return {"title": title, "error": "No revision before target date"}

        return {"title": title, "revid": revid, "content": content}

    except Exception as e:
        return {"title": title, "error": str(e)}



# ------------------------------- #
#       主函数：并行+进度条
# ------------------------------- #
def crawl_year(category: str, year: int, workers=8):

    input_path = f"Data_Collection/titles/{category}_titles.jsonl"
    output_file = f"{category}_{year}.jsonl"
    failed_file = f"{category}_failed_{year}.jsonl"

    # Convert year
    target_timestamp = f"{year}-01-01T00:00:00Z"
    target_dt = datetime.strptime(target_timestamp, "%Y-%m-%dT%H:%M:%SZ")

    # Load titles
    titles = [
        json.loads(line)["title"]
        for line in open(input_path, "r", encoding="utf-8")
    ]

    # Load done titles
    done = {
        json.loads(line)["title"]
        for line in open(output_file, "a+", encoding="utf-8")
    }

    # Real pending list
    pending = [t for t in titles if t not in done]

    fout = open(output_file, "a", encoding="utf-8")
    ffail = open(failed_file, "a", encoding="utf-8")

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        "•",
        TimeElapsedColumn(),
        "•",
        TimeRemainingColumn(),
        refresh_per_second=2,
    ) as progress:

        task = progress.add_task(
            f"Crawling {category} ({year})...",
            total=len(titles)
        )

        # 已完成（含 resume）
        progress.update(task, advance=len(done))

        # 并行处理
        with ProcessPoolExecutor(max_workers=workers) as executor:
            future_map = {
                executor.submit(fetch_single_title, (title, target_dt)): title
                for title in pending
            }

            for future in as_completed(future_map):
                result = future.result()
                title = result["title"]

                if "error" in result:
                    ffail.write(json.dumps(result, ensure_ascii=False) + "\n")
                else:
                    fout.write(json.dumps(result, ensure_ascii=False) + "\n")

                progress.advance(task)

    fout.close()
    ffail.close()



# ------------------------------- #
#             CLI
# ------------------------------- #
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", type=str, required=True)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    crawl_year(args.category, args.year, args.workers)
