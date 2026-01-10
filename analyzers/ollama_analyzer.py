import json
import ollama
from .base import BaseAnalyzer
from db.models import Article, AnalysisData, Category, Theme, Level

class OllamaAnalyzer(BaseAnalyzer):
    def __init__(self, model_name: str = "llama3:8B", prompt_version: str = 'v1'):
        self.model_name = model_name
        self.prompt_version = prompt_version

    def analyze(self, article: Article) -> dict:
        # 1. [Agent 1] Analyst: 분류 및 요약
        # DB의 Category와 Theme Enum 값을 문자열로 추출하여 프롬프트에 주입
        categories = [c.value for c in Category]
        themes = [t.value for t in Theme]
        
        analyst_res = self._run_analyst(article, categories, themes)
        if not analyst_res: return {}

        # 2. [Agent 2] Judge: 기술적 깊이(Level) 판별
        levels = [l.value for l in Level]
        final_level = self._run_judge(analyst_res, levels)

        # 3. 최종 DB Entity 규격으로 병합
        data = {
            "category": analyst_res.get("category", Category.TECH.value),
            "themes": ", ".join(analyst_res.get("themes", [])), # List -> str (콤마 구분)
            "summary": analyst_res.get("summary", ""),
            "level": final_level, # Low, Medium, High 중 하나
            "prompt_version": self.prompt_version,
            "model": self.model_name
        }
        
        analysis = AnalysisData(**data)
        
        return analysis

    def _run_analyst(self, article: Article, categories: list, themes: list) -> dict:
        """Agent 1: 추출 및 분류 (DB 스키마 준수)"""
        system_prompt = f"""
        당신은 IT 전문 뉴스 분석가입니다. 아래 지침에 따라 뉴스 본문을 분석하여 오직 유효한 JSON만 출력하세요.

        [지침]
        1. Category: 반드시 다음 중 하나만 선택하세요: {categories}
        2. Themes: 다음 리스트 중 관련 있는 항목을 모두 선택하세요(최대 3개): {themes}
        3. Summary: 뉴스 본문을 한국어 1문장으로 핵심만 요약하세요.
        
        [출력 JSON 양식]
        {{
            "category": "선택한 카테고리",
            "themes": ["테마1", "테마2"],
            "summary": "한국어 요약"
        }}
        """
        
        response = ollama.chat(
            model=self.model_name,
            format='json',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f"제목: {article.title}\n본문: {article.content[:3000]}"}
            ]
        )
        try:
            return json.loads(response['message']['content'])
        except:
            return None

    def _run_judge(self, analyst_data: dict, levels: list) -> str:
        """Agent 2: 난이도 판단 (기술적 깊이 기준)"""
        summary = analyst_data.get('summary', '')
        themes = analyst_data.get('themes', [])
        
        # [Rule-based logic] 특정 키워드 강제 매핑은 여기서 처리 가능
        if any(kw in str(themes).upper() for kw in ["SECURITY", "EXPLOIT", "AI/ML"]):
            # 특정 테마가 포함되면 최소 Medium 이상으로 판단하는 등의 로직 추가 가능
            pass

        system_prompt = f"""
        당신은 보안 뉴스 에디터입니다. 분석 데이터의 기술적 깊이를 평가하여 중요도를 결정하세요.
        출력은 오직 다음 값 중 하나만 허용됩니다: {levels}

        [평가 기준]
        - High: 취약점 분석, Exploit 코드, 복잡한 아키텍처, 0-day, 심층 연구 보고서.
        - Medium: 가이드라인, 기술적 설정 방법, 일반적인 보안 사고 분석, 클라우드 인프라 운영.
        - Low: 단순 단신, 정책 변경, 일반 IT 뉴스, 인사 이동, 단순 이벤트 소식.

        [입력 데이터]
        - Themes: {themes}
        - Summary: {summary}
        """

        response = ollama.chat(
            model=self.model_name,
            messages=[{'role': 'system', 'content': system_prompt}]
        )
        res = response['message']['content'].strip()
        
        # DB 모델 값으로 매핑 (에러 방지용)
        if "High" in res: return Level.High.value
        if "Medium" in res: return Level.Medium.value
        return Level.Low.value