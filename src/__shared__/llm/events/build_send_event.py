from pydantic import BaseModel
from typing import Union

from src.__shared__.llm.events.type_event import TypeEvent

class BuildStep(BaseModel):
    content: str

class BuildTool(BaseModel):
    content: str

class BuildProcessing(BaseModel):
    content: str

class BuildFinished(BaseModel):
    content: str

class BuildError(BaseModel):
    content: str

def send_event(event: TypeEvent, data=Union[str, BaseModel]):

    payload = data.model_dump_json() if isinstance(data, BaseModel) else data

    return(
        f"event: {event.value}\n"
        f"data: {payload}\n\n"
    )