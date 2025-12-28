from sqlmodel import Session, select
from .models import Article, Analysis, ArticleScraped, AnalysisData, CardView

from datetime import datetime

def is_article_exists(session: Session, url:str) -> bool:
    """URL 기준으로 기사 중복 체크"""
    statement = select(Article).where(Article.url == url)
    results = session.exec(statement).first()
    return results is not None

def save_article(session: Session, scraped_item: ArticleScraped) -> Article:
    """기사 정보를 저장하고 즉시 커밋하여 독립적인 원자성을 보장합니다."""
    try:
        db_article = Article.model_validate(scraped_item)
        session.add(db_article)
        session.commit()
        session.refresh(db_article)
        return db_article
    except Exception as e:
        session.rollback()
        print(f"❌ 기사 저장 실패: {e}")
        raise

def save_analysis(session: Session, article_id: int, analysis_data: AnalysisData) -> Analysis:
    """분석 결과만 별도의 트랜잭션으로 저장합니다."""
    try:
        db_analysis = Analysis.model_validate(
            analysis_data,
            update={
                    "article_id": article_id,
                    "created_at": datetime.now()
                }
        )
        session.add(db_analysis)
        session.commit()
        session.refresh(db_analysis)
        return db_analysis
    except Exception as e:
        session.rollback()
        print(f"❌ 분석 결과 저장 실패 (기사 ID {article_id}): {e}")
        return None
    
def is_already_analyzed(session: Session, url: str) -> bool:
    # URL로 Article을 찾고, 그 Article에 연결된 Analysis가 있는지 확인
    statement = select(Article).where(Article.url == url)
    article = session.exec(statement).first()
    if article and article.analysis:
        return True
    return False

def get_article_by_url(session: Session, url: str):
    return session.exec(select(Article).where(Article.url == url)).first()

def get_article_summaries(session: Session):
    """두 테이블을 JOIN 하여 카드 구성에 필요한 필드만 선택"""
    statement = select(
        Article.source,
        Article.url,
        Article.title,
        Analysis.summary,
        Analysis.themes,
        Analysis.level,
        Analysis.category
    ).join(Analysis, Article.id == Analysis.article_id)

    results = session.exec(statement).all()
    
    # 결과를 ArticleListView 리스트로 변환
    return [CardView.model_validate(row) for row in results]