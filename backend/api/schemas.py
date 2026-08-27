from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


# ==================================================
# CREATE LEAD
# ==================================================

class LeadCreate(BaseModel):

    session_id: UUID

    name: str

    email: EmailStr

    phone: str | None = None


# ==================================================
# LEAD RESPONSE
# ==================================================

class LeadResponse(BaseModel):

    id: int

    session_id: UUID

    name: str | None = None

    email: str | None = None

    phone: str | None = None

    status: str | None = None

    created_at: datetime | None = None

    updated_at: datetime | None = None

    class Config:
        from_attributes = True




# ==================================================
# CHAT SESSION RESPONSE
# ==================================================

class ChatSessionResponse(BaseModel):
    id: UUID
    created_at: datetime
    last_active_at: datetime | None = None
    contact_requested: bool
    lead_opt_out: bool
    lead_form_shown: bool

    class Config:
        from_attributes = True


# ==================================================
# CHAT MESSAGE RESPONSE
# ==================================================

class ChatMessageResponse(BaseModel):
    id: int
    session_id: UUID
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True