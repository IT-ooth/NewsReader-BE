from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select, col
from typing import List, Optional
from db.connection import engine
from db.models import Article, Analysis, CardView
from db.services import *

app = FastAPI(title="news-reader API", version="v1")

origins = [
    "http://news.danyeon.cloud",
    "https://news.danyeon.cloud",
    "http://localhost",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://localhost(:\d+)?",
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB 세션 의존성
def get_session():
    with Session(engine) as session:
        yield session

# 1. GET /v1/article - 전체 기사 가져오기
@app.get("/v1/article", response_model=List[Article])
def get_articles(
    offset: int = 0, 
    limit: int = Query(default=20, le=100), 
    session: Session = Depends(get_session)
):
    """최신 순으로 스크래핑된 기사 리스트를 가져옵니다."""
    statement = select(Article).order_by(Article.id.desc()).offset(offset).limit(limit)
    return session.exec(statement).all()

# 2. GET /v1/article?tags - 태그 기반 검색
@app.get("/v1/search", response_model=List[Article])
def search_articles_by_tags(
    tags: str = Query(..., description="쉼표로 구분된 태그 (예: malware,ransomware)"),
    session: Session = Depends(get_session)
):
    """분석 결과의 themes(태그)를 기준으로 기사를 검색합니다."""
    tag_list = [t.strip() for t in tags.split(",")]
    
    # Analysis 테이블의 themes 컬럼에서 해당 태그가 포함된 기사를 Join으로 찾습니다.
    statement = (
        select(Article)
        .join(Analysis)
        .where(
            # SQL의 LIKE 연산자를 사용하여 포함 여부 확인
            col(Analysis.themes).like(f"%{tag_list[0]}%") 
        )
    )
    # 여러 태그가 있을 경우 추가 필터링 로직을 넣을 수 있습니다.
    return session.exec(statement).all()

# 3. GET /v1/analysis - 분석 결과 가져오기
@app.get("/v1/analysis")
def get_analysis_results(
    session: Session = Depends(get_session)
):
    """기사와 함께 분석된 결과를 한꺼번에 가져옵니다."""
    # 관계(Relationship)를 통해 Article 정보도 같이 포함되어 반환됩니다.
    statement = select(Analysis).order_by(Analysis.created_at.desc()).limit(10)
    results = session.exec(statement).all()
    return results

# 4. GET /v1/cardnews - 카드 뉴스 (필터링)
@app.get("/v1/cardnews", response_model=List[CardView])
def read_dashboard(
    *,
    session: Session = Depends(get_session),
    category: Optional[Category] = Query(None),
    level: Optional[Level] = Query(None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100)
):
    """카드 뉴스 구성 요소를 한꺼번에 가져옵니다."""
    # 서비스 계층에 일을 시킵니다.
    return get_card_view_list(
        session=session, 
        category=category, 
        level=level,
        offset=offset,
        limit=limit
    )