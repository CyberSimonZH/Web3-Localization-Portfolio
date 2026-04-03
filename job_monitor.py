import os
import requests
from bs4 import BeautifulSoup

# --- 配置区 ---
# 搜索关键词
KEYWORDS = ["Commercial", "Financial", "Legal", "Compliance", "Translation", "Localization"]
# 记忆文件（存放在仓库根目录）
MEMORY_FILE = "seen_jobs.txt"
# 通知 Webhook 或 API（保持你原有的环境变量名）
NOTIFICATION_URL = os.getenv("NOTIFICATION_URL")

def get_seen_jobs():
    """读取已经发送过的职位标题"""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_new_job(job_title):
    """将新职位标题存入记忆文件"""
    with open(MEMORY_FILE, 'a', encoding='utf-8') as f:
        f.write(job_title + '\n')

def monitor_remoteok():
    """针对 RemoteOK 的抓取逻辑"""
    url = "https://remoteok.com/remote-legal-jobs"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    seen_jobs = get_seen_jobs()
    new_jobs = []

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 寻找 RemoteOK 的职位行
        for job_row in soup.find_all('tr', class_='job'):
            title_el = job_row.find('h2', itemprop='title')
            link_el = job_row.find('a', itemprop='url')
            
            if title_el and link_el:
                title = title_el.get_text().strip()
                job_url = "https://remoteok.com" + link_el['href']
                
                # 只有标题没见过，且匹配关键词时，才视为新职位
                if title not in seen_jobs:
                    if any(kw.lower() in title.lower() for kw in KEYWORDS):
                        new_jobs.append((title, job_url))
                        save_new_job(title)
                        seen_jobs.add(title)
        
        if new_jobs:
            send_notification(new_jobs)
        else:
            print("没有发现新的不重复职位。")

    except Exception as e:
        print(f"运行出错: {e}")

def send_notification(jobs):
    """发送通知"""
    if not NOTIFICATION_URL:
        for title, url in jobs:
            print(f"新职位: {title} -> {url}")
        return

    message = "为您发现以下新机遇:\n\n"
    for title, url in jobs:
        message += f"📌 {title}\n🔗 {url}\n\n"
    
    payload = {"text": message}
    requests.post(NOTIFICATION_URL, json=payload)

if __name__ == "__main__":
    monitor_remoteok()
