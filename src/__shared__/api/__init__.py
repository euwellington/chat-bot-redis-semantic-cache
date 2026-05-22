from fastapi import FastAPI

from src.__modules__.chat.routes import chat_route
from src.__modules__.web import web_router

def setupAPI(app: FastAPI):
    app.include_router(chat_route, prefix="/api/chat", tags=["chat"])
    app.include_router(web_router, tags=["web"])