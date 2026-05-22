import os
import uvicorn
from fastapi import FastAPI

from src.__shared__.api import setupAPI

app = FastAPI()

setupAPI(app)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )