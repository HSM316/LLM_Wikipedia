import json
from openai import OpenAI
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# 初始化客户端
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

input_file = "/Users/hsm/Documents/Wikipedia_Pages/Featured_First.jsonl"
output_file = "/Users/hsm/Documents/Wikipedia_Pages/Featured_First_Revised.jsonl"

SAVE_INTERVAL = 100   # 每处理多少条保存一次
MAX_WORKERS = 5       # 并发线程数（根据 API 限制可调）

# 读取全部数据
with open(input_file, "r", encoding="utf-8") as infile:
    data = [json.loads(line.strip()) for line in infile]

def save_progress(data, output_file):
    """保存当前进度"""
    with open(output_file, "w", encoding="utf-8") as outfile:
        for entry in data:
            outfile.write(json.dumps(entry, ensure_ascii=False) + "\n")

def process_entry(entry):
    """处理单个条目，返回修改后的 entry"""
    # 如果已经有 revised_3.5，跳过
    if any(v["date"] == "revised_3.5" for v in entry["versions"]):
        return entry, False  

    # 找到 2022-01-01 版本
    target_version = None
    for version in entry["versions"]:
        if version["date"] == "2022-01-01":
            target_version = version
            break

    if not target_version:
        return entry, False  # 没有 2022 版本

    prompt = (
        "Revise the following sentences and return only the revised version.\n\n"
        + target_version["content"]
    )

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        revised_text = completion.choices[0].message.content.strip()

        # 新增 revised_3.5 版本
        entry["versions"].append({
            "date": "revised_3.5",
            "content": revised_text
        })
        return entry, True  

    except Exception as e:
        print(f"⚠️ 出错：{entry['title']} - {e}")
        return entry, False  

# 用线程池并行处理
processed_count = 0
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {executor.submit(process_entry, entry): i for i, entry in enumerate(data)}

    for future in tqdm(as_completed(futures), total=len(futures), desc="Processing entries"):
        idx = futures[future]
        try:
            entry, modified = future.result()
            data[idx] = entry
            if modified:
                processed_count += 1
                if processed_count % SAVE_INTERVAL == 0:
                    save_progress(data, output_file)
                    print(f"💾 已保存进度 ({processed_count} 条)")
        except Exception as e:
            print(f"❌ Future 出错: {e}")

# 最后保存一次
save_progress(data, output_file)
print("✅ 全部处理完成！结果已保存到", output_file)
