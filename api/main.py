from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.api import api_router  # 위에서 만든 통합 라우터 import

app = FastAPI(title="News-Reader API")

origins = [
    "http://news.danyeon.cloud",
    "https://news.danyeon.cloud",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
    max_age=100,
)

app.include_router(api_router, prefix="/v1")
