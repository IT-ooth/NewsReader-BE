from db.models import ArticleScraped
from db.services import is_article_exists
from .BaseScraper import BaseScraper

from sqlmodel import Session
from typing import List
import feedparser


class BoanNewsScraper(BaseScraper):
    
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
                source="BoanNews",
                published_at=entry.get('published')
            )
            for entry in ff
        ]
        
        return results

    def _scrap_body(self, url):
        """본문 및 이미지 각주 추출 (보안뉴스 특화.ver)"""
        soup = self._get_soup(url)
        if not soup: return ""
        
        main_div = soup.find('div', id='news_content')
        if not main_div: return ""

        for img_block in main_div.find_all('div', id='news_image'):
            p_tag = img_block.find('p')
            caption = f"\n\n[이미지 설명: {p_tag.get_text().strip()}]\n\n" if p_tag else ""
            img_block.replace_with(caption)

        for s in main_div(['script', 'style', 'iframe', 'form']):
            s.decompose()

        return main_div.get_text(separator='\n').strip()[:16000]