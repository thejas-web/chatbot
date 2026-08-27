import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.ingestion.vector_store import VectorDBManager
from backend.ingestion.embedding import EmbeddingManager
from backend.Retrieval.retrieve import RagRetriever
from backend.Retrieval.generate import RagGenerator
from backend.db.database import get_db
from backend.db.models import ChatSession, ChatMessage, Lead


router = APIRouter()


# ==================================================
# INITIALIZE RAG
# ==================================================

vector_db_manager = VectorDBManager()
vector_db_manager.load_vector_store()

embedding_manager = EmbeddingManager()

retriever = RagRetriever(
    vector_db_manager,
    embedding_manager
)

generator = RagGenerator()


# ==================================================
# REQUEST MODEL
# ==================================================

class ChatRequest(BaseModel):

    query: str

    # Frontend sends None on first message
    session_id: str | None = None

    top_k: int = 10

    score_threshold: float = 0.0


# ==================================================
# SESSION CONFIG
# ==================================================

# How long a session stays valid with no activity.
SESSION_TIMEOUT = timedelta(
    minutes=15
)


# ==================================================
# GET / CREATE SESSION
# ==================================================

def get_or_create_session(
    db: Session,
    session_id: str | None
) -> ChatSession:

    if session_id:

        existing = (
            db.query(ChatSession)
            .filter_by(id=session_id)
            .first()
        )

        if existing:

            # Existing session is still active
            if (
                datetime.utcnow()
                - existing.last_active_at
                <= SESSION_TIMEOUT
            ):

                existing.last_active_at = (
                    datetime.utcnow()
                )

                db.commit()

                return existing

            # Session expired.
            # Create a new session below.

    new_session = ChatSession()

    db.add(new_session)

    db.commit()

    db.refresh(new_session)

    return new_session


# ==================================================
# GET RECENT CHAT HISTORY
# ==================================================

def get_recent_history(
    db: Session,
    session: ChatSession,
    limit: int = 10
) -> list[dict]:

    rows = (
        db.query(ChatMessage)
        .filter_by(
            session_id=session.id
        )
        .order_by(
            ChatMessage.created_at.desc()
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "role": row.role,
            "content": row.content
        }
        for row in reversed(rows)
    ]


# ==================================================
# CHAT ENDPOINT
# ==================================================

@router.post("/chat")
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------
    # GET / CREATE SESSION
    # --------------------------------------------------

    session = get_or_create_session(
        db,
        request.session_id
    )

    # --------------------------------------------------
    # GET PREVIOUS HISTORY
    # --------------------------------------------------

    history = get_recent_history(
        db,
        session
    )

    # --------------------------------------------------
    # SAVE USER MESSAGE
    # --------------------------------------------------

    # Save the user's message immediately.
    #
    # This means the message is stored even if
    # retrieval or generation fails later.

    db.add(
        ChatMessage(
            session_id=session.id,
            role="user",
            content=request.query
        )
    )

    db.commit()

    # --------------------------------------------------
    # COUNT USER MESSAGES
    # --------------------------------------------------

    user_message_count = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.session_id == session.id,
            ChatMessage.role == "user"
        )
        .count()
    )

    # --------------------------------------------------
    # DETERMINE WHETHER TO SHOW LEAD FORM
    # --------------------------------------------------

    # The lead form is shown after the user's
    # second message.
    #
    # lead_form_shown prevents it from appearing
    # repeatedly on later messages.

    show_lead_form = (
        user_message_count >= 2
        and not session.lead_form_shown
    )

    # --------------------------------------------------
    # RAG RETRIEVAL
    # --------------------------------------------------

    results = retriever.retrieve(
        query=request.query,
        top_k=request.top_k,
        score_threshold=request.score_threshold,
    )

    # --------------------------------------------------
    # GENERATE ANSWER
    # --------------------------------------------------

    # There is NO LeadSignalClassifier here.
    #
    # Lead collection is handled separately through
    # the frontend form.
    #
    # The LLM's only job is to answer the user's query.

    answer = generator.generate(
        request.query,
        results,
        history=history
    )

    # --------------------------------------------------
    # FALLBACK ANSWER
    # --------------------------------------------------

    if not answer:

        answer = (
            "I don't have enough information "
            "to answer that."
        )

    # --------------------------------------------------
    # SAVE ASSISTANT MESSAGE
    # --------------------------------------------------

    db.add(
        ChatMessage(
            session_id=session.id,
            role="assistant",
            content=answer
        )
    )

    # --------------------------------------------------
    # MARK LEAD FORM AS SHOWN
    # --------------------------------------------------

    if show_lead_form:

        session.lead_form_shown = True

    # --------------------------------------------------
    # UPDATE SESSION ACTIVITY
    # --------------------------------------------------

    session.last_active_at = (
        datetime.utcnow()
    )

    db.commit()

    # --------------------------------------------------
    # BUILD SOURCES
    # --------------------------------------------------

    seen = set()

    sources = []

    for r in results:

        src = r["metadata"].get(
            "source"
        )

        if src and src not in seen:

            seen.add(src)

            sources.append(
                {
                    "title": r["metadata"].get(
                        "title",
                        src
                    ),
                    "source": src
                }
            )

    # --------------------------------------------------
    # RESPONSE
    # --------------------------------------------------

    return {
        "session_id": str(session.id),

        "query": request.query,

        "results_found": len(results),

        "sources": sources,

        "answer": answer,

        # Frontend checks this value.
        #
        # It becomes true only on the second user
        # message and only once per session.

        "show_lead_form": show_lead_form,
    }