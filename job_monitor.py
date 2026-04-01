import os
import feedparser
import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# ================= 配置区 =================
# 关键词列表（覆盖法律、合规、政策、隐私及高管岗位）
KEYWORDS = [
    "Legal", "Compliance", "Privacy", "PhD", "Regulatory", 
    "Law", "Hong Kong", "General Counsel", "Policy", "Associate"
]

# RSS 源列表（新增 RemoteOK 和专门的 Legal Feed）
RSS_SOURCES = {
    "Web3.career": "https://web3.career/remote-jobs.xml",
    "CryptoJobsList": "https://cryptojobslist.com/job/rss",
    "RemoteOK": "https://remoteok.com/remote-web3-jobs.rss",
    "CryptoCurrencyJobs": "https://cryptocurrencyjobs.co/legal/feed/",
    "Upwork": os.getenv("UPWORK_RSS") 
}

def send_to_gmail(content):
    """通过 Gmail SMTP 逻辑实现自发自收"""
    email_addr = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    if not all([email_addr, password]):
        print("❌ 邮件配置缺失，请检查 GitHub Secrets (EMAIL_USER, EMAIL_PASS)。")
        return

    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = email_addr
    msg['To'] = email_addr
    msg['Subject'] = Header("🐕 CyberSimon_ZH 法律猎犬：全球 Web3 机遇播报", 'utf-8')

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(email_addr, password)
            server.sendmail(email_addr, [email_addr], msg.as_string())
        print("✅ 职位报告已成功发送至你的 Gmail 收件箱。")
    except Exception as e:
        print(f"❌ 邮件发送失败: {str(e)}")

def fetch_jobs():
    """抓取并过滤职位"""
    all_hits = []
    # 模拟浏览器身份，防止被某些源屏蔽
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for name, url in RSS_SOURCES.items():
        if not url:
            continue
        
        print(f"正在扫描 {name}...")
        try:
            response = requests.get(url, headers=headers, timeout=15)
            feed = feedparser.parse(response.content)
            
            if not feed.entries:
                print(f"⚠️ {name} 未返回任何结果。")
                continue

            for entry in feed.entries:
                title = entry.get('title', '')
                link = entry.get('link', '')
                
                # 不区分大小写匹配
                if any(key.lower() in title.lower() for key in KEYWORDS):
                    # 格式化输出，带上来源名
                    all_hits.append(f"来自 {name}:\n📌 {title}\n🔗 {link}")
        except Exception as e:
            print(f"⚠️ 抓取 {name} 时出错: {e}")

    return all_hits

if __name__ == "__main__":
    print("🐕 猎犬开始搜寻...")
    results = fetch_jobs()
    
    if results:
        # 去重
        unique_results = []
        seen_links = set()
        for res in results:
            link = res.split('\n🔗 ')[-1]
            if link not in seen_links:
                unique_results.append(res)
                seen_links.add(link)

        print(f"✅ 抓取到 {len(unique_results)} 条匹配职位，准备发信...")
        
        report_body = (
            "Hi Simon,\n\n"
            "为您发现以下 Web3 法律/合规全球新机遇：\n\n"
            + "\n\n" + "="*40 + "\n\n"
            + "\n\n\n".join(unique_results[:20])
            + "\n\n" + "="*40 + "\n"
            + "祝 顺利！"
        )
        send_to_gmail(report_body)
    else:
        print("📭 今日暂无匹配的高端职位。")
