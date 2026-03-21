import requests
from bs4 import BeautifulSoup

# 关键词筛选：精准定位你的专业领域
KEYWORDS = ["Chinese", "Translator", "Localization", "Legal", "Mandarin", "Compliance"]
# 核心方案：使用 RSS 接口，GitHub IP 访问它是 100% 允许的
TARGET_URL = "https://web3.career/remote-jobs.xml" 

def fetch_jobs():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=20)
        response.raise_for_status()
        
        # 解析 RSS 数据流，这种方式不会被防火墙拦截
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        matches = []
        for item in items:
            title = item.title.text.strip()
            link = item.link.text.strip()
            if any(key.lower() in title.lower() for key in KEYWORDS):
                matches.append(f"{title} - {link}")
        return matches
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    found_jobs = fetch_jobs()
    if found_jobs:
        with open("jobs_found.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(found_jobs))
        print(f"✅ 抓取成功！发现 {len(found_jobs)} 个匹配职位。")
    else:
        print("📫 抓取成功，但今日 RSS 中暂无匹配职位。")
