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
    "Remote"
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

import smtplib
from email.mime.text import MIMEText
from email.header import Header

def send_to_gmail(content):
    """通过 Gmail SMTP 逻辑实现自发自收"""
    email_addr = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    if not all([email_addr, password]):
        print("❌ 邮件配置缺失，请检查 GitHub Secrets。")
        return

    # 构建邮件内容
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = email_addr
    msg['To'] = email_addr  # 发给自己
    msg['Subject'] = Header("🐕 CyberSimon_ZH 法律猎犬：今日新机遇", 'utf-8')

    try:
        # 使用 Gmail 的安全 SMTP 端口
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(email_addr, password)
            server.sendmail(email_addr, [email_addr], msg.as_string())
        print("✅ 职位报告已成功发送至你的 Gmail 收件箱。")
    except Exception as e:
        print(f"❌ 邮件发送失败: {str(e)}")

if __name__ == "__main__":
    print("🐕 猎犬开始搜寻...")
    # 临时强制跳过关键词过滤，抓取所有结果
    jobs = fetch_jobs() 
    
    # 【测试专用】如果 jobs 为空，我们伪造一条数据看看发信逻辑行不行
    if not jobs:
        jobs = ["测试职位：Web3 Legal Consultant", "https://example.com"]
        print("⚠️ 未抓取到实时数据，使用伪造数据进行发信测试...")

    print(f"✅ 准备发信，共 {len(jobs)} 条...")
    report_body = "测试邮件内容：\n\n" + "\n\n".join(jobs[:3])
    send_to_gmail(report_body)
