from db.models import ArticleScraped

from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from sqlmodel import Session
from dateutil import parser
from typing import List
import requests
import re

class BaseScraper(ABC):
    def __init__(self, url: str, period: int):
        self.url = url
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        self.period = period

    @abstractmethod
    def collect(self, session: Session) -> List[ArticleScraped]:
        """RSS 또는 크롤링을 통해 전문을 가져오는 추상 메서드"""
        pass

    def _get_soup(self, url: str):
        """공통 헬퍼 메서드: URL에 접속하여 BeautifulSoup 객체 반환"""
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            res.raise_for_status()
            return BeautifulSoup(res.text, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
        
    def _common_clean(self, text: str) -> str:
        """모든 스크래퍼가 공통으로 사용하는 고도화된 태그 정제 로직"""
        soup = BeautifulSoup(text, 'html.parser')

        if not soup: return ""

        # 1. 공통 노이즈 제거
        for s in soup(['script', 'style', 'iframe', 'noscript', 'header', 'footer', 'nav', 'form']):
            s.decompose()

        # 2. 표(Table) -> 마크다운 변환
        for table in soup.find_all('table'):
            markdown_table = self._html_table_to_markdown(table)
            table.replace_with(f"\n{markdown_table}\n")

        # 3. 이미지 -> [이미지: alt(src)] 변환
        for img in soup.find_all('img'):
            alt = img.get('alt', 'image')
            src = img.get('src', '')
            img.replace_with(f" [이미지: {alt}({src})] ")

        # 4. 첨부파일 링크 보존 (정규식 활용)
        for a in soup.find_all('a'):
            href = a.get('href', '')
            text = a.get_text(strip=True)
            if re.search(r'\.(pdf|zip|docx|xlsx|pptx|hwp)$', href.lower()):
                a.replace_with(f" [첨부파일: {text}({href})] ")
            else:
                a.replace_with(text) # 일반 링크는 텍스트만 남김

        # 5. 최종 텍스트 추출 (줄바꿈 보존)
        text = soup.get_text(separator='\n')
        return re.sub(r'\n\s*\n+', '\n\n', text).strip()
    
    def _html_table_to_markdown(self, table) -> str:
        """HTML 표를 LLM이 읽기 좋은 Markdown 형식으로 변환"""
        rows = []
        for tr in table.find_all('tr'):
            cells = [td.get_text(strip=True) for td in tr.find_all(['th', 'td'])]
            if cells:
                rows.append("| " + " | ".join(cells) + " |")
        
        if not rows:
            return ""
            
        # 헤더 구분선 추가 (Markdown 규격)
        header_line = "| " + " | ".join(['---'] * len(rows[0].split('|')[1:-1])) + " |"
        if len(rows) > 1:
            rows.insert(1, header_line)
            
        return "\n".join(rows)

    # 날짜 처리 로직
    """
        Pydantic은 기본적으로 ISO 8601 형식을 기대하기에,
        ex> 2025-12-24T03:28:18
        RSS 표준 표기 형식 RFC2822를 처리하지 못함 
        ex> 'Wed, 24 Dec 2025 03:28:18 GMT'
        이를 해결하고자 날짜 처리 로직을 추가함.
    """
    def _get_date(self, raw_date):
        return parser.parse(raw_date)