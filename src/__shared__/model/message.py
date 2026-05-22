from typing import List, Dict, Optional
from enum import Enum
from pydantic import BaseModel, Field

class Role(Enum):
    HUMAN = "human"
    AI = "ai"

class MessageContent(BaseModel):
    role: Role = Field(description="Tipo da mensagem")
    content: str = Field(description="Conteúdo da mensagem")


class Message(BaseModel):
    messages: List[MessageContent] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    usage_metadata: Optional[Dict] = None