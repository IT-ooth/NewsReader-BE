import time
from sqlmodel import Session, select
from db import services, engine, init_db
from db.models import Article, Analysis
from analyzers import OllamaAnalyzer

def run_analysis_bot():
    init_db()
    analyzer = OllamaAnalyzer(model_name="llama3.1:8b")
    print("🚀 Analysis Bot 가동 중 (GPU 모드)...")

    while True:
        with Session(engine) as session:
            # 1. 분석이 아직 안 된 기사 하나 가져오기
            target_article = services.get_next_article_to_analyze(session)

            if not target_article:
                print("💤 분석할 기사가 없습니다. 대기 중...")
                time.sleep(30) # 30초마다 확인
                continue

            # 2. AI 분석 수행 (GPU 자원 사용)
            print(f"🤖 분석 시작: {target_article.title}")
            try:
                analysis_data = analyzer.analyze(target_article) 
                
                if analysis_data:
                    services.save_analysis(session, target_article.id, analysis_data)
                    print(f"✅ 분석 완료 및 저장 성공")
            except Exception as e:
                print(f"❌ 분석 실패: {e}")
                time.sleep(10)

if __name__ == "__main__":
    run_analysis_bot()