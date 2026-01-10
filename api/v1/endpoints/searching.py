from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from db.connection import get_session
from db.models import ThemeSearchRequest
from db.services import search_articles_by_all_themes, search_articles_by_any_themes, get_active_themes

router = APIRouter()

@router.post("/search/theme")
def search_any_themes(
    req: ThemeSearchRequest,
    session: Session = Depends(get_session)
):
    """
        api_type: 1 -> any search
        api_type: 2 -> all search
    """
    if req.search_type == 1:
        return search_articles_by_any_themes(session, req.themes, req.offset, req.limit)
    elif req.search_type == 2:
        return search_articles_by_all_themes(session, req.themes, req.offset, req.limit)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid api_type. Use 1 for ANY or 2 for ALL."
        )

@router.post("/theme/list")
def get_theme_list(
    session: Session = Depends(get_session)
):
    """DB내에 존재하는 테마 리스트 반환 로직"""
    return get_active_themes(session)