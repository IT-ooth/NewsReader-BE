import threading
import time
from sqlmodel import Session
from db import services, engine, init_db
from scrapers import BoanNewsScraper, GeekNewsScraper, S2WScraper

def scraper_thread(scraper):
    """각 스크래퍼별 독립 루프"""
    while True:
        print(f"📡 {scraper.source} 스크래핑 시작...")
        with Session(engine) as session:
            try:
                scraped_items = scraper.collect(session)
                for item in scraped_items:
                    if not services.get_article_by_url(session, item.url):
                        services.save_article(session, item)
                        print(f"📥 새 기사 저장: {item.title[:20]}...")
                session.commit()
            except Exception as e:
                print(f"❌ {scraper.source} 에러: {e}")
        
        time.sleep(scraper.period)

def run_scraper_bot():
    init_db()
    scrapers = [
        BoanNewsScraper('http://www.boannews.com/media/news_rss.xml?skind=1', 10800),
        GeekNewsScraper('https://news.hada.io/rss/news', 10800),
        S2WScraper('https://medium.com/feed/s2wblog', 86400) # S2W는 하루 주기
    ]
    
    for s in scrapers:
        threading.Thread(target=scraper_thread, args=(s,), daemon=True).start()
    
    print("🚀 Scraper Bot 가동 중...")
    while True: time.sleep(1)

if __name__ == "__main__":
    run_scraper_bot()