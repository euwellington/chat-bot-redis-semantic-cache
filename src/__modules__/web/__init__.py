from fastapi import APIRouter
from fastapi.responses import FileResponse

web_router = APIRouter()

@web_router.get("/")
def get_web():
    return FileResponse(
        "src/__modules__/web/html/index.html"
    )