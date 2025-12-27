from db.models import ArticleScraped

from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from sqlmodel import Session
from typing import List
import requests


class BaseScraper(ABC):
    def __init__(self, url: str):
        self.url = url
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

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