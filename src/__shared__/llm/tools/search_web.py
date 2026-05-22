from langchain.tools import tool
from openai import OpenAI

client = OpenAI()


@tool(return_direct=False)
def search_web(query: str) -> str:
    """
    Faz uma pesquisa na internet e retorna os resultados.
    """

    response = client.responses.create(
        model="gpt-4o-mini",
        tools=[
            {
                "type": "web_search"
            }
        ],
        input=query
    )

    return response.output_text