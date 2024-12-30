from fastapi import APIRouter, Depends
from typing import List
from pydantic import BaseModel
from app.services.chatbot_service import ChatbotService

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    history: List[str] = []

class ChatResponse(BaseModel):
    response: str
    history: List[str]

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, chatbot: ChatbotService = Depends()):
    response = await chatbot.generate_response(request.message, request.history)
    
    # Update history
    updated_history = request.history.copy()
    updated_history.append(f"Human: {request.message}")
    updated_history.append(f"AI Assistant: {response}")
    
    return ChatResponse(
        response=response,
        history=updated_history
    )