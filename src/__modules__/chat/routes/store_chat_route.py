from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from src.__modules__.chat.schemas.chat_schema import ChatSchema
from src.__modules__.chat.services.store_chat_service import store_chat_service

router = APIRouter()

@router.post("/conversation")
def store_chat_route(request: Request, body: ChatSchema):
    return StreamingResponse(
        store_chat_service(body)
    )