from enum import Enum

class TypeEvent(Enum):
    STEP = "step"
    TOOL = "tool"
    PROCESSING = "processing"
    FINISHED = "finished"
    ERROR = "error"