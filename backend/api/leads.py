from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db.models import Lead
from backend.db.database import get_db
from backend.api.schemas import (
    LeadCreate,
    LeadResponse,
)


router = APIRouter()


# ==================================================
# CREATE LEAD
# ==================================================

@router.post(
    "/leads",
    response_model=LeadResponse
)
def create_lead(
    request: LeadCreate,
    db: Session = Depends(get_db)
):

    # ----------------------------------------------
    # CHECK IF LEAD ALREADY EXISTS FOR SESSION
    # ----------------------------------------------

    existing_lead = (
        db.query(Lead)
        .filter(
            Lead.session_id == request.session_id
        )
        .first()
    )

    if existing_lead:

        raise HTTPException(
            status_code=409,
            detail="A lead already exists for this session."
        )

    # ----------------------------------------------
    # CREATE LEAD
    # ----------------------------------------------

    lead = Lead(
        session_id=request.session_id,
        name=request.name.strip(),
        email=request.email.strip(),
        phone=(
            request.phone.strip()
            if request.phone
            else None
        ),

        # Explicitly set this even though
        # the database also has a default.
        status="new",
    )

    db.add(lead)

    db.commit()

    db.refresh(lead)

    return lead

# ==================================================
# GET ALL LEADS - PAGINATED
# ==================================================

@router.get("/leads")
def get_leads(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):

    # ----------------------------------------------
    # VALIDATE PAGINATION
    # ----------------------------------------------

    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="Page must be greater than or equal to 1."
        )

    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=400,
            detail="Page size must be between 1 and 100."
        )

    # ----------------------------------------------
    # TOTAL NUMBER OF LEADS
    # ----------------------------------------------

    total = (
        db.query(Lead)
        .count()
    )

    # ----------------------------------------------
    # CALCULATE OFFSET
    # ----------------------------------------------

    offset = (page - 1) * page_size

    # ----------------------------------------------
    # GET CURRENT PAGE
    # ----------------------------------------------

    leads = (
        db.query(Lead)
        .order_by(
            Lead.created_at.desc()
        )
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # ----------------------------------------------
    # TOTAL PAGES
    # ----------------------------------------------

    total_pages = (
        (total + page_size - 1)
        // page_size
    )

    # ----------------------------------------------
    # RESPONSE
    # ----------------------------------------------

    return {
        "items": leads,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }