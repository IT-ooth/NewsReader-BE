from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import List

from db.connection import get_session
from db.models import CardView, CardNewsRequest
from db.services import *

router = APIRouter()

@router.post("/cardnews", response_model=List[CardView])
def read_dashboard(
    *,
    session: Session = Depends(get_session),
    request: CardNewsRequest
):
    return get_card_view_list(
        session=session, 
        category=request.category, 
        level=request.level,
        offset=request.offset,
        limit=request.limit
    )
