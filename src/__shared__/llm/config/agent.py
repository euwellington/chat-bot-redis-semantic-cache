from typing import Optional, List, Union, Any
from dataclasses import dataclass

from langchain.agents import create_agent as create_agent_ai
from langchain.tools import BaseTool
from langchain_core.prompts import PromptTemplate
from langchain_core.language_models import BaseChatModel

@dataclass
class AgentConfig:
    llm: BaseChatModel
    system_prompt: Optional[Union[str, PromptTemplate]] = None
    tools: Optional[List[BaseTool]] = None

    def __post_init__(self) -> None:
        if self.tools is None:
            self.tools = []

def create_agent_config(config: AgentConfig):

    system_prompt = config.system_prompt if isinstance(config.system_prompt, str) else "Você é um assistente virtual"

    return create_agent_ai(model=config.llm, system_prompt=system_prompt, tools=config.tools)


def create_agent(
    llm: BaseChatModel,
    system_prompt: Optional[Union[str, PromptTemplate]] = None,
    tools: Optional[List[BaseTool]] = None
):
    config = AgentConfig(llm=llm, system_prompt=system_prompt, tools=tools)

    return create_agent_config(config)