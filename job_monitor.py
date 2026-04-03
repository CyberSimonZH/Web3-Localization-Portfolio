import os
import requests
from bs4 import BeautifulSoup

# --- 配置区 ---
# 职位关键词：你可以随时在这里增加“法律翻译”或“财经”相关的词
KEYWORDS = ["Web3", "Localization", "Legal Translation", "Financial", "Compliance", "DePIN"]
# 邮件通知的 API 或 Webhook 地址（保持你原来的设置）
NOTIFICATION_URL = os.getenv("NOTIFICATION_URL") 
# 记忆文件名
MEMORY_FILE = "seen_jobs.txt"

def get_seen_jobs():
    """读取已经发送过的职位链接，防止重复推送"""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            # 去掉换行符并转换为集合，方便快速查找
            return set(line.strip() for line in f if line.strip())
    return set()

def save_new_job(job_url):
    """将新发现的职位链接追加到记忆文件中"""
    with open(MEMORY_FILE, 'a', encoding='utf-8') as f:
        f.write(job_url + '\n')

def send_notification(title, url):
    """发送通知的逻辑（请确保你的环境变量已配置）"""
    if not NOTIFICATION_URL:
        print(f"拟发送通知: {title} - {url} (由于未配置通知URL，仅在此打印)")
        return
    
    payload = {"text": f"🚀 发现新机会!\n标题: {title}\n链接: {url}"}
    try:
        requests.post(NOTIFICATION_URL, json=payload)
    except Exception as e:
        print(f"通知发送失败: {e}")

def monitor_jobs():
    # 1. 加载已经看过的职位
    seen_jobs = get_seen_jobs()
    print(f"已记录的职位数量: {len(seen_jobs)}")

    # 2. 抓取逻辑 (这里以一个通用逻辑为例，实际会根据你具体的 source 修改)
    # 注意：这里需要根据你实际爬取的网站结构来填充，以下为逻辑框架
    target_url = "https://cryptojobslist.com/legal" # 示例地址
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(target_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 假设职位在 <a> 标签中
        for link in soup.find_all('a', href=True):
            title = link.get_text().strip()
            url = link['href']
            
            # 补全相对路径
            if url.startswith('/'):
                url = "https://cryptojobslist.com" + url

            # 3. 核心判断逻辑
            # 判断关键词是否匹配
            if any(kw.lower() in title.lower() for kw in KEYWORDS):
                # 判断是否已经推送过
                if url not in seen_jobs:
                    print(f"检测到新职位: {title}")
                    send_notification(title, url)
                    # 存入记忆，防止下次重复
                    save_new_job(url)
                    seen_jobs.add(url) # 更新内存中的集合
                else:
                    print(f"跳过已推送职位: {title}")

    except Exception as e:
        print(f"运行出错: {e}")

if __name__ == "__main__":
    monitor_jobs()
