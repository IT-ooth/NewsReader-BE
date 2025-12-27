from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from enum import StrEnum

class Level(StrEnum):
    Low = "Low"
    Medium = "Medium"
    High = "High"
class Category(StrEnum):
    TECH = "Tech"
    ECONOMY = "Economy"
    POLITICS = "Politics"
    SOCIETY = "Society"
    CULTURE = "Culture"
    WORLD = "World"   
class Theme(StrEnum):
    # TECH
    SECURITY = "Security"
    AI_ML = "AI/ML"
    INFRA_CLOUD = "Infra/Cloud"
    DEV_STACK = "Development"
    BIZ_POLICY = "Business/Policy"
    GENERAL_IT = "General IT"


class ArticleBase(SQLModel):
    title: str
    url: str = Field(index=True, unique=True)
    source: str
    published_at: Optional[datetime] = None

class Article(ArticleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 관계 설정
    analysis: Optional["Analysis"] = Relationship(back_populates="article")

class ArticleScraped(ArticleBase):
    content: str

class AnalysisData(SQLModel):
    category: Category
    themes: str
    summary: str
    level: Level
    prompt_version: str
    model: str

class Analysis(AnalysisData, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    
    article_id: int = Field(foreign_key="article.id")
    article: Optional[Article] = Relationship(back_populates="analysis")