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

def send_to_pushdeer(message):
    """通过 PushDeer 将职位信息推送到微信/手机"""
    key = os.getenv("PUSHDEER_KEY")
    if not key:
        print("❌ 未配置 PUSHDEER_KEY，无法推送消息。")
        return
        
    url = "https://api2.pushdeer.com/message/push"
    # PushDeer 的 text 参数支持简单的 Markdown
    payload = {
        "pushkey": key,
        "text": "🚀 CyberSimon_ZH 法律猎犬报告",
        "desp": message, # 详细内容放在 desp 字段
        "type": "markdown"
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ 消息已成功推送到 PushDeer。")
        else:
            print(f"⚠️ 推送失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 网络请求异常: {str(e)}")

if __name__ == "__main__":
    print("🐕 猎犬开始搜寻...")
    jobs = fetch_jobs()
    if jobs:
        # 将列表合成为一个字符串，限制长度避免推送失败
        full_message = "\n\n---\n\n".join(jobs[:8])
        send_to_pushdeer(full_message)
    else:
        print("📭 今日暂无匹配的高端 Web3 法律职位。")
