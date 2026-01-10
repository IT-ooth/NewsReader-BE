from db.models import ArticleScraped
from db.services import is_article_exists
from .BaseScraper import BaseScraper
# from scrapers.BaseScraper import BaseScraper

from sqlmodel import Session
from typing import List
import feedparser
import unicodedata
import re

class S2WScraper(BaseScraper):

    def collect(self, session: Session) -> List[ArticleScraped]:
        print("S2WScraper 작동 시작")
        feed = feedparser.parse(self.url)
        results = []
        
        for entry in feed.entries:
            print("S2WScraper feed 분석")
            if is_article_exists(session, entry.link):
                continue
            
            # RSS 피드 내부에 전문이 있는지 확인 (스크래핑 X)
            content = ""
            if hasattr(entry, 'content'):
                content_html = entry.content[0].value
                content = self._common_clean(content_html)
                print("S2WScaper content: ", content)

            results.append(ArticleScraped(
                title=entry.title,
                url=entry.link,
                content=self._clean_html(content),
                source="S2W Talon",
                published_at=self._get_date(entry.get('published'))
            ))
            
        return results

    def _clean_html(self, html_str: str) -> str:
        # 1. 공통 로직 실행
        text = self._common_clean(html_str)
        if not text: return ""

        # 2. 유니코드 정규화 (\xa0 제거 등)
        text = unicodedata.normalize("NFKD", text)

        # A. 문장 중간에 단어 하나만 두고 줄바꿈된 것 연결 (예: \nincreased\n -> increased)
        text = re.sub(r'(?<=[a-zA-Z0-9])\n([a-zA-Z0-9가-힣\s.,-]{1,20})\n(?=[a-zA-Z0-9])', r' \1 ', text)

        # B. 콜론(:) 앞의 줄바꿈 및 공백 제거 (예: \n : -> : )
        text = re.sub(r'\n\s*:', ':', text)

        # C. 불필요한 노이즈 패턴 제거 (이전 로직 유지)
        noise_patterns = [
            r"\[이미지: \(https://medium\.com/.*stat\?event=.*\)\]",
            r"originally published in.*on Medium.*",
            r"Photo by .* on Unsplash",
        ]
        for pattern in noise_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.MULTILINE)

        # 3. 최종 줄바꿈 정리
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        return text.strip()[:16000]

if __name__ == "__main__":
    s = S2WScraper(100)
    session = Session()
    for i in s.collect(session):
        print(i)