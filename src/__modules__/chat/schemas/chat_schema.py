from pydantic import BaseModel, Field

class ChatSchema(BaseModel):
    question: str = Field(description="Pergunta do usuário")