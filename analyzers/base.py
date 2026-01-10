from abc import ABC, abstractmethod
from db.models import Article, Analysis

class BaseAnalyzer(ABC):
    def __init__(self, model):
        self.model = model
    
    @abstractmethod
    def analyze(self, article: Article) -> Analysis:
        """입력 받은 자료를 LLM이 분석한 결과를 반환합니다."""
        pass