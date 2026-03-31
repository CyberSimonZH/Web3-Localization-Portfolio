import os
import feedparser
import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# ================= 配置区 =================
# 关键词列表（不区分大小写）
KEYWORDS = ["Legal", "Compliance", "Privacy", "PhD", "Regulatory", "Law", "Hong Kong"]

# RSS 源列表
RSS_SOURCES = {
    "Web3.career": "https://web3.career/remote-jobs.xml",
    "CryptoJobsList": "https://cryptojobslist.com/job/rss",
    # 如果你有特定的 Upwork RSS 链接，请通过 GitHub Secrets 传入
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
    msg['Subject'] = Header("🐕 CyberSimon_ZH 法律猎犬：今日新机遇", 'utf-8')

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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    for name, url in RSS_SOURCES.items():
        if not url:
            continue
        
        print(f"正在扫描 {name}...")
        try:
            # 使用 requests 抓取以避免被屏蔽，再交给 feedparser 解析
            response = requests.get(url, headers=headers, timeout=15)
            feed = feedparser.parse(response.content)
            
            for entry in feed.entries:
                title = entry.get('title', '')
                link = entry.get('link', '')
                
                # 核心过滤逻辑：不区分大小写匹配关键词
                if any(key.lower() in title.lower() for key in KEYWORDS):
                    all_hits.append(f"📌 {title}\n🔗 {link}")
        except Exception as e:
            print(f"⚠️ 抓取 {name} 时出错: {e}")

    return all_hits

if __name__ == "__main__":
    print("🐕 猎犬开始搜寻...")
    results = fetch_jobs()
    
    if results:
        # 去重并取前 15 条
        unique_results = list(set(results))
        print(f"✅ 抓取到 {len(unique_results)} 条匹配职位，准备发信...")
        
        report_body = (
            "Hi Simon,\n\n"
            "为您发现以下 Web3 法律/合规相关职位：\n\n"
            + "\n\n" + "-"*30 + "\n\n"
            + "\n\n\n".join(unique_results[:15])
            + "\n\n" + "-"*30 + "\n"
            + "祝 顺利！"
        )
        send_to_gmail(report_body)
    else:
        print("📭 今日暂无匹配的高端职位。")
