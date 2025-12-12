import requests
from urllib.parse import quote
import jsonlines  # type: ignore
import csv
from tqdm import tqdm
import time
import random
from datetime import datetime, timedelta
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# ===== 配置 =====
CATEGORIES = ["Art", "Bio", "Chem", "CS", "Phy", "Math", "Philosophy", "Sports"]
# CATEGORIES = ["de"]

START_DATE = "20180101"
END_DATE   = "20251101"
USER_AGENT = "WikiPageviewsCollector/1.0 (your_site_or_repo_url; your_email@example.com)"

# 并行 & 限速
MAX_WORKERS        = 32       # 并发线程数
REQUESTS_PER_SEC   = 16        # 全局请求速率上限（所有线程合计）
BATCH_WRITE_SIZE   = 200      # 收集到多少条再批量写一次 CSV

# 每个类别处理总数上限（包含已处理+新处理）
MAX_PER_CATEGORY = 60000

# ===== 日期工具（按天）=====
def parse_day(day_str: str) -> datetime:
    return datetime.strptime(day_str, "%Y%m%d")

def to_api_ts_day(dt: datetime) -> str:
    return dt.strftime("%Y%m%d") + "00"

def generate_days(start_date: str, end_date: str):
    start = parse_day(start_date)
    end   = parse_day(end_date)
    days = []
    cur = start
    while cur <= end:
        days.append(cur.strftime("%Y%m%d"))
        cur += timedelta(days=1)
    return days, to_api_ts_day(start), to_api_ts_day(end)

# ===== 全局限速器（线程安全）=====
class RateLimiter:
    def __init__(self, rate_per_sec: float):
        self.min_interval = 1.0 / max(rate_per_sec, 1e-6)
        self.lock = threading.Lock()
        self.next_time = 0.0

    def acquire(self):
        with self.lock:
            now = time.time()
            if now < self.next_time:
                sleep_dur = self.next_time - now
                time.sleep(sleep_dur)
                now = self.next_time
            self.next_time = now + self.min_interval

rate_limiter = RateLimiter(REQUESTS_PER_SEC)

# ===== 每线程自己的 Session（线程安全）=====
_thread_local = threading.local()

def get_session() -> requests.Session:
    s = getattr(_thread_local, "session", None)
    if s is None:
        s = requests.Session()
        _thread_local.session = s
    return s

# ===== HTTP（会话+指数退避）=====
def fetch_url(url, params=None, max_retries=5, headers=None):
    backoff = 1.0
    for attempt in range(1, max_retries + 1):
        try:
            rate_limiter.acquire()  # 全局限速
            resp = get_session().get(url, headers=headers, params=params, timeout=15)
            sc = resp.status_code
            if sc == 200:
                return resp
            if sc in (429, 500, 502, 503, 504) and attempt < max_retries:
                time.sleep(backoff + random.uniform(0, 0.5))
                backoff = min(backoff * 2, 8.0)
                continue
            # 其它错误不重试
            return None
        except (requests.RequestException, requests.Timeout):
            if attempt < max_retries:
                time.sleep(backoff + random.uniform(0, 0.5))
                backoff = min(backoff * 2, 8.0)
            else:
                return None

# ===== Wikimedia Pageviews（日粒度）=====
def get_pageviews_daily(title, start_ts, end_ts):
    encoded_title = quote(title)
    url = (
        "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
        f"en.wikipedia.org/all-access/all-agents/{encoded_title}/daily/{start_ts}/{end_ts}"
    )
    headers = {"User-Agent": USER_AGENT}
    resp = fetch_url(url, headers=headers)
    if resp is not None:
        return resp.json()
    return None

# ===== IO & 工具 =====
def read_titles_from_jsonl(jsonl_file):
    titles = []
    with jsonlines.open(jsonl_file) as reader:
        for obj in reader:
            t = obj.get("title")
            if t:
                titles.append(t)
    # 去重保序
    seen, out = set(), []
    for t in titles:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out

def normalize_for_match(title: str) -> str:
    if not isinstance(title, str):
        return ""
    return title.strip().replace(" ", "_")

def read_done_titles_from_csv(csv_file):
    done = set()
    if not os.path.exists(csv_file):
        return done
    with open(csv_file, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            return done
        # 默认第一列是 Title；若不是，仍按第 0 列处理
        for row in reader:
            if row:
                done.add(normalize_for_match(row[0]))
    return done

def save_batch_to_csv(batch, csv_file, days):
    """batch: list[ (title, views_list) ]"""
    if not batch:
        return
    is_new = not os.path.exists(csv_file) or os.path.getsize(csv_file) == 0
    with open(csv_file, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        if is_new:
            header = ['Title'] + days
            writer.writerow(header)
        for title, views in batch:
            writer.writerow([title] + views)

# ===== worker =====
def worker_fetch(title, days, start_ts, end_ts):
    """返回 (title, [views...]) 或 None"""
    page = get_pageviews_daily(title, start_ts, end_ts)
    if page and 'items' in page:
        day_to_views = {item['timestamp'][:8]: item['views'] for item in page['items']}
        views_for_title = [day_to_views.get(d, "") for d in days]
        return (title, views_for_title)
    return None

# ===== 主流程 =====
def main():
    days, start_ts, end_ts = generate_days(START_DATE, END_DATE)

    for category in CATEGORIES:
        jsonl_file = f"Wikipedia/Titles/{category}_titles.jsonl"
        csv_file   = f"Wikipedia/PageViews/{category}_pageviews.csv"

        titles = read_titles_from_jsonl(jsonl_file)
        if not titles:
            print(f"[WARN] No titles in {jsonl_file}")
            continue

        done_set = read_done_titles_from_csv(csv_file)

        # 当前类别的规范化标题全集（用于交集统计）
        norm_titles = [normalize_for_match(t) for t in titles]
        already_done_in_category = sum(1 for nt in norm_titles if nt in done_set)

        # 需要处理的剩余标题
        remaining = [t for t in titles if normalize_for_match(t) not in done_set]

        # 上限约束
        cap_remaining = max(0, MAX_PER_CATEGORY - already_done_in_category)
        if cap_remaining == 0:
            print(f"[INFO] {category}: reached cap ({MAX_PER_CATEGORY}). "
                  f"Already done in-scope={already_done_in_category}, total_in_jsonl={len(titles)}. Skip.")
            continue
        remaining_capped = remaining[:cap_remaining]

        # 预抓取统计
        print(
            f"[INFO] {category}: already={already_done_in_category}, "
            f"remaining_total={len(remaining)}, cap_remaining={cap_remaining}, "
            f"will_process={len(remaining_capped)}, total_in_jsonl={len(titles)}"
        )

        if not remaining_capped:
            print(f"[SKIP] {category}: nothing to do under cap.")
            continue

        # 并发抓取
        batch = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
            futures = {ex.submit(worker_fetch, t, days, start_ts, end_ts): t for t in remaining_capped}
            for fut in tqdm(as_completed(futures), total=len(futures), desc=f"{category}: parallel fetch"):
                res = fut.result()
                if res is not None:
                    batch.append(res)
                    if len(batch) >= BATCH_WRITE_SIZE:
                        save_batch_to_csv(batch, csv_file, days)
                        batch.clear()

        # 写剩余批
        if batch:
            save_batch_to_csv(batch, csv_file, days)
            batch.clear()

        print(f"[OK] Saved daily CSV: {csv_file}")

if __name__ == "__main__":
    main()
