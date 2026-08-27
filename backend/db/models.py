import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class ChatSession(Base):
    """One browser session. Tracks whether/when we've already asked for
    contact info, so the LLM doesn't ask on every single turn."""
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    contact_requested = Column(Boolean, default=False)
    lead_opt_out = Column(Boolean, default=False)
    lead_form_shown = Column(Boolean,default=False,nullable=False)

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    lead = relationship("Lead", back_populates="session", uselist=False, cascade="all, delete-orphan")


class ChatMessage(Base):
    """Full conversation history, used both to give the LLM context and
    to reconstruct a session if the user reloads the page."""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")


class Lead(Base):
    """One row per session that has shown buying intent. Fields fill in
    incrementally as the conversation progresses — a row can exist with
    just an email, then get a name and company added on a later turn."""
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    phone = Column(String(50), nullable=True)
    #company = Column(String(200))
    #intent_summary = Column(Text)  # short note on what they were asking about
    status = Column(String(30), default="new")  # new | contacted | qualified | disqualified
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    session = relationship("ChatSession", back_populates="lead")