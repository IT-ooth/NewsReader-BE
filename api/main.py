from fastapi import FastAPI
from api.v1.api import api_router  # 위에서 만든 통합 라우터 import

app = FastAPI(title="News-Reader API")

app.include_router(api_router, prefix="/v1")
