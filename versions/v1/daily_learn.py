import feedparser
import git
import smtplib
import os
from email.message import EmailMessage
from datetime import datetime

# Configuration
REPO_PATH = "/home/hulbert/Desktop/daily-learn"
FILE_NAME = "Daily-learn.txt"
RSS_FEEDS = ["https://hnrss.org/frontpage", "https://feeds.feedburner.com/TechCrunch/"]

# Email Config (Use Environment Variables for safety!)
EMAIL_SENDER = "emiliohulbert2017@gmail.com"
EMAIL_PASSWORD = os.getenv("GMAIL_APP_PASS") 
RECIPIENTS = ["emiliohulbert2017@gmail.com", "emiliobckp@gmail.com"]

def fetch_content():
    content = f"--- Learning Log: {datetime.now().strftime('%Y-%m-%d')} ---\n"
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        content += f"\nSource: {feed.feed.title}\n"
        for entry in feed.entries[:3]:
            content += f"- {entry.title}: {entry.link}\n"
    return content

def send_email(content):
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = f"Daily Learning Log - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = EMAIL_SENDER
    msg['To'] = ", ".join(RECIPIENTS)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(msg)

def update_git():
    repo = git.Repo(REPO_PATH)
    content = fetch_content()
    
    with open(f"{REPO_PATH}/{FILE_NAME}", "a") as f:
        f.write(content + "\n\n")
        
    repo.git.add(FILE_NAME)
    repo.index.commit(f"Daily auto-commit: {datetime.now().strftime('%Y-%m-%d')}")
    repo.remotes.origin.push()
    
    send_email(content)

if __name__ == "__main__":
    update_git()