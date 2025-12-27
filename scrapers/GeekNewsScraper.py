from db.models import ArticleScraped
from db.services import is_article_exists
from .BaseScraper import BaseScraper

from sqlmodel import Session
from typing import List
import feedparser   

class GeekNewsScraper(BaseScraper):

    def collect(self, session: Session) -> List[ArticleScraped]:
        feed = feedparser.parse(self.url)
        
        ff = [
            entry for entry in feed.entries 
            if not is_article_exists(session, entry.link)
        ]
        
        results = [
            ArticleScraped(
                title=entry.title,
                url=entry.link,
                content=self._scrap_body(entry.link),
                source="GeekNews",
                published_at=entry.get('published')
            )
            for entry in ff
        ]
        
        return results

    def _scrap_body(self, url):
        """본문 및 이미지 각주 추출 (긱뉴스 특화.ver)"""
        soup = self._get_soup(url)
        if not soup: return ""
        
        main_content = soup.find('span', id='topic_contents')
        
        if not main_content:
            main_content = soup.select_one('.topic-content')
        
        if not main_content:
            return ""

        for s in main_content(['script', 'style']):
            s.decompose()

        return main_content.get_text(separator='\n').strip()[:16000]