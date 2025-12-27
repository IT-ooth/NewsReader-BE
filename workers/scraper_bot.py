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
        GeekNewsScraper('https://news.hada.io/rss/news'),
    ]
    analyzer = OllamaAnalyzer(model_name="llama3.1:8b")

    print("🚀 보안 뉴스 큐레이션 봇 시작...")

    while True:
        print(f"\n[시작 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}] 작업 시작...")
        
        with Session(engine) as session:
            for scraper in scrapers:
                try:
                    scraper.collect(session)
                except Exception as e:
                    print(f"❌ 스크래퍼 오류: {e}")

            print("🔍 분석 대기 중인 기사 확인 중...")
            pending_articles = services.get_articles_without_analysis(session)
            
            if not pending_articles:
                print("✨ 모든 기사가 분석되었습니다.")
            
            for article in pending_articles:
                try:
                    print(f"🤖 AI 분석 중... (ID: {article.id} | {article.title[:20]}...)")
                    analysis_data = analyzer.analyze(article)
                    
                    if analysis_data:
                        services.save_analysis(session, article.id, analysis_data)
                        session.commit()
                        print(f"✅ 분석 완료 및 저장 성공")
                    else:
                        print(f"⚠️ 분석 실패 (결과 없음): {article.id}")
                except Exception as e:
                    print(f"❌ 분석 중 에러 발생 (ID: {article.id}): {e}")
                    continue

        print("\n💤 대기 중 (1분 뒤 다시 확인)...")
        time.sleep(60)

if __name__ == "__main__":
    run_curation_loop()