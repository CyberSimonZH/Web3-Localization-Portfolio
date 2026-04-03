import os
import requests
from bs4 import BeautifulSoup

# --- 配置区 ---
# 搜索关键词（已加入法律和财经翻译）
KEYWORDS = ["Commercial", "Financial", "Legal", "Compliance", "Translation", "Localization"]
# 记忆文件名
MEMORY_FILE = "seen_jobs.txt"
# 通知邮箱（你脚本中原本的逻辑，请确保 Secrets 中已配置）
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL")

def get_seen_jobs():
    """读取已经推送过的职位标题，防止重复"""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_new_job(job_title):
    """将新职位标题存入记忆文件"""
    with open(MEMORY_FILE, 'a', encoding='utf-8') as f:
        f.write(job_title + '\n')

def monitor_remoteok():
    """专门针对 RemoteOK 的抓取逻辑"""
    url = "https://remoteok.com/remote-legal-jobs"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    seen_jobs = get_seen_jobs()
    new_jobs_found = []

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # RemoteOK 的职位通常在 tr.job 标签中
        for job_row in soup.find_all('tr', class_='job'):
            title_element = job_row.find('h2', itemprop='title')
            link_element = job_row.find('a', itemprop='url')
            
            if title_element and link_element:
                title = title_element.get_text().strip()
                job_url = "https://remoteok.com" + link_element['href']
                
                # 核心去重：判断标题是否已经推送过
                if title not in seen_jobs:
                    # 关键词匹配
                    if any(kw.lower() in title.lower() for kw in KEYWORDS):
                        new_jobs_found.append((title, job_url))
                        save_new_job(title) # 记录标题
                        seen_jobs.add(title)
                else:
                    print(f"跳过重复职位: {title}")

        if new_jobs_found:
            send_notification(new_jobs_found)
        else:
            print("本次运行未发现新职位。")

    except Exception as e:
        print(f"抓取失败: {e}")

def send_notification(jobs):
    """发送邮件通知的逻辑"""
    # 这里保持你原本发邮件的代码逻辑即可
    # 以下是示意性打印
    content = "为您发现以下新机遇:\n\n"
    for title, url in jobs:
        content += f"📌 {title}\n🔗 {url}\n\n"
    print(content)
    # 实际发送代码应调用你的邮件服务

if __name__ == "__main__":
    monitor_remoteok()
