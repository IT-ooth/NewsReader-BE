from fastapi import APIRouter
from api.v1.endpoints import cardnews, searching

api_router = APIRouter()

# 여기서 cardnews의 라우터를 등록합니다. tags는 스와거 문서 분류용 이름입니다.
api_router.include_router(cardnews.router, tags=["Card News"])
api_router.include_router(searching.router, tags=["Searching"])

# 나중에 다른 기능이 생기면 여기에 계속 추가하면 됩니다.
# api_router.include_router(auth.router, tags=["Auth"])