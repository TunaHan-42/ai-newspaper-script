import time
from urllib import response, request

import feedparser
import requests
from newspaper import Article
import firebase_admin
from firebase_admin import credentials, firestore



import model
import rssConfig

# bazı haberlerin tarihi çekilemiyor rss xmlinden çekelim
# maç hangi kanalda?, nezaman, canlı izle vb. haberleri atlayalım




headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
}

processed_links = set()
collected_news = []

print("🚀 Raw news scraping started...\n")

for source_name, rss_url in rssConfig.rssLinks.items():
    feed = feedparser.parse(rss_url)

    for entry in feed.entries[:3]:
        article_link = entry.link
        if article_link in processed_links:
            continue
        processed_links.add(article_link)

        try:
            time.sleep(2)
            response = requests.get(article_link, headers=headers, timeout=10)

            if response.status_code == 200:
                if "Just a moment" not in response.text and "cloudflare" not in response.text.lower():
                    article = Article(article_link)
                    article.set_html(response.text)
                    article.parse()

                    raw_title = article.title
                    raw_text = article.text
                    raw_date = article.publish_date

                    raw_news = model.NewsModel(title=raw_title, text=raw_text, link=article_link, source=source_name, date=raw_date)

                    collected_news.append(raw_news)
                    print(f"✅ [{source_name}] Added: {raw_title}...")
        except Exception as e:
            print("Hata oluştu: ", e)
    print(f"\n✨ Total {len(collected_news)} raw news items successfully collected!")

    print("\n🔥 Connecting to Firebase Firestore...")

    cred = credentials.Certificate("firebase_key.json")

    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    db = firestore.client()

    print("📤 Uploading news to Firestore...\n")


    for news in collected_news:

        document_id = str(abs(hash(news.link)))

        db.collection("Raw_News").document(document_id).set(news.to_dict())

        print(f"💾 Saved to DB: {news.title[:40]}...")

    print("\n✅ All news items have been successfully saved to Firestore!")




