import requests
from bs4 import BeautifulSoup
import json
# de
# URL = "https://de.wikipedia.org/wiki/Wikipedia:Exzellente_Artikel"
# es
URL = "https://fr.wikipedia.org/wiki/Cat%C3%A9gorie:Article_de_qualit%C3%A9"
OUTPUT = "Data_Collection/titles/fr_titles.jsonl"

res = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
res.raise_for_status()

soup = BeautifulSoup(res.text, "html.parser")

titles = []

# 查找所有 /wiki/... 链接，然后从 title 属性读取真正的条目标题
for a in soup.select("a[href^='/wiki/']"):
    title_attr = a.get("title")
    href = a.get("href", "")

    # 必须是条目：不包含命名空间（如 Portal:, Wikipedia:, Datei: 等）
    if title_attr and ":" not in href and ":" not in title_attr:
        titles.append(title_attr.strip())

# 去重并保持顺序
titles = list(dict.fromkeys(titles))

# 写入 JSONL
with open(OUTPUT, "w", encoding="utf-8") as f:
    for t in titles:
        f.write(json.dumps({"title": t}, ensure_ascii=False) + "\n")

print(f"Done! Extracted {len(titles)} titles.")
print(f"Saved to {OUTPUT}")
