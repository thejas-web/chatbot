from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.models import ChatSession
from backend.db.database import get_db

router = APIRouter()


# ==================================================
# GET ALL CHAT SESSIONS
# ==================================================

@router.get("/sessions")
def get_sessions(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    # Prevent invalid values
    if page < 1:
        page = 1

    if page_size < 1:
        page_size = 20

    # Total number of sessions
    total = db.query(ChatSession).count()

    # Pagination
    offset = (page - 1) * page_size

    sessions = (
        db.query(ChatSession)
        .order_by(ChatSession.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return {
        "items": sessions,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (
            (total + page_size - 1) // page_size
            if total > 0
            else 0
        ),
    }