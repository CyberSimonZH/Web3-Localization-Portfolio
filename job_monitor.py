import feedparser
import requests
import os
import time

# 1. 扩展 RSS 源：加入 Upwork (需替换为你的搜索 RSS) 与 CryptoJobsList
RSS_FEEDS = [
    "https://web3.career/remote-jobs.xml",
    "https://cryptojobslist.com/feed/legal.xml",
    # 建议：登录 Upwork 搜索 "Legal Translation Crypto" 后点击搜索结果页的 RSS 图标获取链接
    "https://www.upwork.com/ab/feed/jobs/rss?q=legal+translation+crypto&sort=recency" 
]

# 2. 关键词降维打击：从“翻译”扩展到“合规与政策”
KEYWORDS = [
    "Legal", "Compliance", "Regulatory", "Privacy", "ToS", 
    "Policy", "Lawyer", "GDPR", "PIPL", "GBA", "Hong Kong"
]

# 3. 排除低价值噪音
EXCLUDE_KEYWORDS = ["Sales", "Customer Support", "Entry Level", "Marketing"]

def fetch_jobs():
    all_hits = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) CyberSimon_ZH/1.0'}
    
    for url in RSS_FEEDS:
        try:
            print(f"🔍 正在扫描源: {url}")
            feed = feedparser.parse(url)
            for entry in feed.entries:
                title = entry.title
                summary = entry.get('summary', '')
                link = entry.link
                
                # 逻辑过滤：包含关键词且排除杂讯
                if any(k.lower() in title.lower() for k in KEYWORDS):
                    if not any(e.lower() in title.lower() for e in EXCLUDE_KEYWORDS):
                        all_hits.append(f"📌 **{title}**\n🔗 {link}\n")
            
            # 随机延迟避免被封
            time.sleep(2)
        except Exception as e:
            print(f"❌ 扫描失败: {url} - {str(e)}")
            
    return all_hits

def send_to_telegram(message):
    # 沿用你之前的 Telegram Bot 配置
    token = os.getenv("TG_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        requests.post(url, json=payload)

if __name__ == "__main__":
    jobs = fetch_jobs()
    if jobs:
        header = "🚀 **CyberSimon_ZH 法律猎犬：今日新机遇**\n"
        full_msg = header + "\n".join(jobs[:10]) # 限制前10条避免过长
        send_to_telegram(full_msg)
    else:
        print("📭 暂无匹配的高端职位。")
