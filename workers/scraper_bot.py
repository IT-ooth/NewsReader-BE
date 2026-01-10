from scrapers import BoanNewsScraper, GeekNewsScraper, S2WScraper
from analyzers import OllamaAnalyzer
from db import services, engine, init_db

import time
from sqlmodel import Session


def run_curation_loop():
    # 1. 초기화 (DB 테이블 생성 및 엔진 준비)
    init_db()
    
    # 2. 부품 준비
    # 여러 소스를 관리할 수 있도록 리스트로 구성
    scrapers = [
        BoanNewsScraper('http://www.boannews.com/media/news_rss.xml?skind=1', 3600),
        # BoanNewsScraper('http://www.boannews.com/media/news_rss.xml?skind=5'),
        # BoanNewsScraper('http://www.boannews.com/media/news_rss.xml?skind=7'),
        # BoanNewsScraper('http://www.boannews.com/media/news_rss.xml?skind=3'),
        # BoanNewsScraper('http://www.boannews.com/media/news_rss.xml?skind=2'),
        # BoanNewsScraper('http://www.boannews.com/media/news_rss.xml?skind=6'),
        GeekNewsScraper('https://news.hada.io/rss/news', 3600),
        S2WScraper('https://medium.com/feed/s2wblog', 86400)
    ]
    analyzer = OllamaAnalyzer(model_name="llama3.1:8b")

    print("🚀 보안 뉴스 큐레이션 봇 시작...")

    while True:
        print(f"\n[시작 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}] 작업 시작...")
        
        with Session(engine) as session:
            for scraper in scrapers:
                try:
                    scraped_items = scraper.collect(session) 
                    
                    for item in scraped_items:
                        if services.is_already_analyzed(session, item.url):
                            continue
                            
                        print(f"📰 처리 중: {item.title}")

                        db_article = services.get_article_by_url(session, item.url)
                        if not db_article:
                            db_article = services.save_article(session, item)
                    
                        try:
                            print(f"🤖 AI 분석 중...")
                            analysis_data = analyzer.analyze(item) 
                            
                            if analysis_data:
                                services.save_analysis(session, db_article.id, analysis_data)
                                print(f"✅ 분석 완료 및 저장 성공")
                        except Exception as e:
                            print(f"❌ 분석 실패 (ID: {db_article.id}): {e}")

                except Exception as e:
                    print(f"❌ 스크래퍼 오류: {e}")

        print("\n💤 대기 중 (10분 뒤 다시 확인)...")
        time.sleep(600)

if __name__ == "__main__":
    run_curation_loop()