from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.chat import router as chat_router
from backend.api.leads import router as leads_router
from backend.api.avatar import router as avatar_router
from backend.api.tts import router as tts_router
from backend.api.stt import router as stt_router
from backend.api.sessions import router as sessions_router
from backend.api.messages import router as messages_router
from backend.api.auth import router as auth_router


app = FastAPI(
    title="RAG API",
    description="RAG chatbot backend",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




app.include_router(chat_router, prefix="/api")
app.include_router(leads_router,prefix="/api")
app.include_router(avatar_router,prefix="/api")
app.include_router(tts_router,prefix="/api")
app.include_router(stt_router,prefix="/api")
app.include_router(sessions_router,prefix="/api")
app.include_router(messages_router,prefix="/api")
app.include_router(auth_router,prefix="/api")



@app.get("/")
def root():
    return {
        "message": "RAG API is running"
    }