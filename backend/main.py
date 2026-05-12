from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import init_db
from api import chat, tickets, feedback, analytics, knowledge

app = FastAPI(
    title="OMS Support API",
    description="AI-powered support system for Open Money Stack by Polygon",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(tickets.router)
app.include_router(feedback.router)
app.include_router(analytics.router)
app.include_router(knowledge.router)


@app.on_event("startup")
async def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}
