from datetime import datetime
from langchain.tools import tool

@tool(return_direct=False)
def get_current_datetime():
    """
        Você retorna data e hora atual
    """

    return datetime.now()