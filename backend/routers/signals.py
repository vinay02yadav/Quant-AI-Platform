# Endpoints serving cross-sectional opportunity scores

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from typing import Optional
from datetime import date

router = APIRouter()


@router.get("/")
def get_signals(
    date: Optional[date] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """
    Retrieve top cross-sectional opportunity scores.
    Optionally filter by date.
    """
    return {"date": date, "signals": [], "count": 0}


@router.get("/ranking")
def get_signal_ranking(
    date: Optional[date] = Query(None), db: Session = Depends(get_db)
):
    """
    Retrieve full ranking of signals for a given date.
    """
    return {"date": date, "ranking": []}
