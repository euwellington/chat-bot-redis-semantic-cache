from fastapi import APIRouter
from src.__modules__.chat.routes.store_chat_route import router as store_chat_route

chat_route = APIRouter()
chat_route.include_router(store_chat_route)