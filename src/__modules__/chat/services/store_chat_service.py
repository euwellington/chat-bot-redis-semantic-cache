from langchain.messages import HumanMessage, AIMessage, SystemMessage

from src.__modules__.chat.schemas.chat_schema import ChatSchema
from src.__shared__.llm.events.type_event import TypeEvent
from src.__shared__.llm.events.build_send_event import (
    send_event,
    BuildStep,
    BuildTool,
    BuildProcessing,
    BuildFinished,
    BuildError
)
from src.__shared__.llm.adapters.openai import gpt_4_1_mini
from src.__shared__.llm.config.agent import create_agent
from src.__shared__.llm.utils.normalize_content import normalize_content
from src.__shared__.llm.utils.normalize_usage_metadata import normalize_usage_metadata
from src.__shared__.llm.tools.get_current_datetime import get_current_datetime
from src.__shared__.llm.tools.get_info_system import get_info_system
from src.__shared__.llm.tools.search_web import search_web
from src.__shared__.llm.tools.send_email import send_email
from src.__shared__.model.message import Message, MessageContent, Role
from src.__shared__.llm.memory import MemoryService


async def store_chat_service(body: ChatSchema):
    yield send_event(
        event=TypeEvent.STEP,
        data=BuildStep(content="Processando")
    )

    session_id = "user_1"

    context = MemoryService.get_context(
        session_id=session_id,
        query=body.question,
        embedding_k=6,
        history_limit=10
    )

    embeddings = context["embeddings"]
    recent_history = context["recent_history"]

    tools = [
        get_current_datetime,
        get_info_system,
        send_email,
        search_web
    ]

    agent = create_agent(
        llm=gpt_4_1_mini,
        system_prompt="""
            Você se chama Carinha da T.I e está conversando com Wellington Felipe
            - Se a mensagem atual for curta e parecer continuação de uma tarefa anterior, trate como complemento do pedido anterior.
            - Se o usuário disser apenas cidade, email, nome, confirmação ou dado complementar, use isso para continuar o pedido em aberto.
            - Não invente um novo tema.
            - Só use ferramentas quando realmente necessário.
            - Não use ferramentas para conversa normal.
            - Responda diretamente sempre que possível.

            REGRAS PARA ENVIO DE EMAIL:
            - Sempre transforme o conteúdo do relatório em Markdown limpo antes de enviar.
            - Estruture o conteúdo pensando em renderização HTML automática.
            - Utilize:
            - títulos
            - listas
            - tabelas
            - blocos de código
            - destaques
            quando fizer sentido.

            - Nunca envie HTML bruto.
            - Nunca envie JSON no email.
            - Caso a ferramenta informe algum erro explique o motivo do erro pro usuário
            - O conteúdo deve ser otimizado para conversão Markdown -> HTML.


            Ferramentas disponíveis:
            - horário/data atual
            - enviar emails
            - informações do sistema
""",
        tools=tools
    )

    semantic_context = "\n\n".join(
        "\n".join(
            f"{item.role.value}: {item.content}"
            for item in memory.messages
        )
        for memory in embeddings
    )

    history_messages = []

    for memory in reversed(recent_history):
        for item in memory.messages:
            if item.role == Role.HUMAN.value:
                history_messages.append(
                    HumanMessage(content=item.content)
                )
            elif item.role == Role.AI.value:
                history_messages.append(
                    AIMessage(content=item.content)
                )

    conversation_context = f"""
        Contexto semântico relevante:

        {semantic_context}

        Histórico recente da conversa em ordem cronológica:

        """
    if history_messages:
        history_context_text = []
        for msg in history_messages:
            role = "human" if isinstance(msg, HumanMessage) else "ai"
            history_context_text.append(f"{role}: {msg.content}")

        conversation_context += "\n".join(history_context_text)
    else:
        conversation_context += "Sem histórico recente."

    messages = [
        SystemMessage(
            content=conversation_context
        ),
        HumanMessage(
            content=body.question
        )
    ]

    chunks = []
    used_tools = []
    usage_metadata = None

    try:
        async for chunk, _ in agent.astream(
            {
                "messages": messages
            },
            stream_mode="messages"
        ):
            if not isinstance(chunk, AIMessage):
                continue

            tool_calls = getattr(chunk, "tool_calls", [])

            for tool_call in tool_calls:
                tool_name = tool_call.get("name")

                if not tool_name:
                    continue

                if tool_name in used_tools:
                    continue

                used_tools.append(tool_name)

                yield send_event(
                    TypeEvent.TOOL,
                    data=BuildTool(content=tool_name)
                )

            content = normalize_content(
                getattr(chunk, "content", None)
            )

            current_usage = normalize_usage_metadata(
                getattr(chunk, "usage_metadata", None)
            )

            if current_usage:
                usage_metadata = current_usage

            if content:
                chunks.append(content)

                yield send_event(
                    TypeEvent.PROCESSING,
                    data=BuildProcessing(content=content)
                )

        full_content = "".join(chunks)

        message = Message(
            messages=[
                MessageContent(
                    role=Role.HUMAN.value,
                    content=body.question
                ),
                MessageContent(
                    role=Role.AI.value,
                    content=full_content
                )
            ],
            tools=used_tools
        )

        MemoryService.save_message(
            session_id=session_id,
            message=message
        )

        print("USO DA LLM")
        print(usage_metadata)

        yield send_event(
            TypeEvent.FINISHED,
            data=BuildFinished(content="Finalizado")
        )

    except Exception as e:
        yield send_event(
            TypeEvent.ERROR,
            data=BuildError(content=str(e))
        )