"""
router.py ─ FastAPI router for assistant
"""

import uuid
from fastapi import APIRouter
from pydantic import BaseModel
from backend.assistant.agent import run_agent

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None
    current_page: str = "home"
    page_context: dict = {}


class ChatResponse(BaseModel):
    reply: str
    thread_id: str
    ui_actions: list[dict] = []
    tools_called: list[str] = []


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    thread_id = req.thread_id or str(uuid.uuid4())

    result = run_agent(
        user_message=req.message,
        thread_id=thread_id,
        current_page=req.current_page,
        page_context=req.page_context,
    )

    return ChatResponse(
        reply=result["reply"],
        thread_id=thread_id,
        ui_actions=result["ui_actions"],
        tools_called=result["tools_called"],
    )


@router.post("/reset")
async def reset():
    return {"status": "ok", "message": "Send a new thread_id to start fresh."}
