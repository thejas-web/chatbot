from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.models import ChatMessage
from backend.db.database import get_db

router = APIRouter()


# ==================================================
# GET ALL CHAT MESSAGES
# ==================================================

@router.get("/messages")
def get_messages(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    # Prevent invalid values
    if page < 1:
        page = 1

    if page_size < 1:
        page_size = 20

    # Total number of messages
    total = db.query(ChatMessage).count()

    # Pagination
    offset = (page - 1) * page_size

    messages = (
        db.query(ChatMessage)
        .order_by(ChatMessage.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return {
        "items": messages,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (
            (total + page_size - 1) // page_size
            if total > 0
            else 0
        ),
    }