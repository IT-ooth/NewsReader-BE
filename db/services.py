from sqlmodel import Session, select
from sqlalchemy import text, or_, and_

from .models import *

from datetime import datetime
from typing import Optional

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

# For API service
def get_card_view_list(
    session: Session, 
    category: Optional[Category] = None, 
    level: Optional[Level] = None, 
    offset: int = 0,
    limit: int = 20
):
    """DB에서 필터링된 카드 뉴스 데이터를 가져오는 핵심 로직"""
    statement = select(
        Article.source, Article.url, Article.title,
        Analysis.summary, Analysis.themes, Analysis.level, Analysis.category
    ).join(Analysis, Article.id == Analysis.article_id)

    if category:
        statement = statement.where(Analysis.category == category)
    if level:
        statement = statement.where(Analysis.level == level)

    statement = statement.order_by(Analysis.created_at.desc()).offset(offset).limit(limit)
    
    return session.exec(statement).all()

def get_active_themes(session: Session) -> List[str]:
    """DB에 존재하는 테마를 반환하는 로직"""
    query = """
        SELECT DISTINCT TRIM(unnested_theme) AS theme
        FROM analysis, unnest(string_to_array(themes, ',')) AS unnested_theme
        WHERE themes IS NOT NULL AND themes != ''
        ORDER  BY theme ASC
    """
    results = session.execute(query).all()
    return [row[0] for row in results]

def search_articles_by_any_themes(session: Session, req: ThemeSearchRequest):
    """입력된 테마 중 하나라도 포함되는 기사를 반환하는 로직"""
    statement = select(
        Article.source, Article.url, Article.title,
        Analysis.summary, Analysis.themes, Analysis.level, Analysis.category
    ).join(Analysis, Article.id == Analysis.article_id)

    if req.themes:
        # 각 테마에 대해 OR 조건 생성
        filters = [Analysis.themes.contains(theme.strip()) for theme in req.themes]
        statement = statement.where(or_(*filters))

    statement = statement.order_by(Analysis.created_at.desc()).offset(req.offset).limit(req.limit)
    return session.exec(statement).all()

def search_articles_by_all_themes(session: Session, req: ThemeSearchRequest):
    """입력된 모든 테마가 포함된 기사만 반환하는 로직"""
    statement = select(
        Article.source, Article.url, Article.title,
        Analysis.summary, Analysis.themes, Analysis.level, Analysis.category
    ).join(Analysis, Article.id == Analysis.article_id)

    if req.themes:
        # 각 테마에 대해 AND 조건 생성
        filters = [Analysis.themes.contains(theme.strip()) for theme in req.themes]
        statement = statement.where(and_(*filters))

    statement = statement.order_by(Analysis.created_at.desc()).offset(req.offset).limit(req.limit)
    return session.exec(statement).all()