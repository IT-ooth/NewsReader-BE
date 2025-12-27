from scrapers import BoanNewsScraper, GeekNewsScraper
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
        BoanNewsScraper('http://www.boannews.com/media/news_rss.xml?skind=1'),
        # BoanNewsScraper('http://www.boannews.com/media/news_rss.xml?skind=5'),
        # BoanNewsScraper('http://www.boannews.com/media/news_rss.xml?skind=7'),
        # BoanNewsScraper('http://www.boannews.com/media/news_rss.xml?skind=3'),
        # BoanNewsScraper('http://www.boannews.com/media/news_rss.xml?skind=2'),
        # BoanNewsScraper('http://www.boannews.com/media/news_rss.xml?skind=6'),
        # GeekNewsScraper('https://news.hada.io/rss/news'),
    ]
    analyzer = OllamaAnalyzer(model_name="llama3.1:8b")

    print("🚀 보안 뉴스 큐레이션 봇 시작...")

    while True:
        print(f"\n[시작 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}] 새로운 뉴스 확인 중...")
        
        with Session(engine) as session:
            for scraper in scrapers:
                try:
                    new_articles = scraper.collect(session)
                    
                    for article_item in new_articles:
                        print(f"📰 새 기사 발견: {article_item.title}")
                        
                        try:
                            db_article = services.save_article(session, article_item)
                            
                            print(f"🤖 AI 분석 중... ({article_item.title[:20]}...)")
                            analysis_data = analyzer.analyze(article_item)
                            
                            if analysis_data:
                                services.save_analysis(session, db_article.id, analysis_data)
                                print(f"✅ 분석 완료 및 저장 성공")
                            else:
                                print(f"⚠️ 분석 결과가 비어있습니다. (기사 ID: {db_article.id})")
                                
                        except Exception as e:
                            print(f"❌ 기사 처리 중 에러 발생 (건너뜀): {e}")
                            continue # 다음 기사로 넘어감
                            
                except Exception as e:
                    print(f"❌ 스크래퍼({scraper.__class__.__name__}) 작동 오류: {e}")
        
        print("\n💤 대기 중 (10분 뒤 다시 확인)...")
        time.sleep(6000)

if __name__ == "__main__":
    run_curation_loop()