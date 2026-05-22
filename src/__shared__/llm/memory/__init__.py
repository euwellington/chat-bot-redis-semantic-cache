import json
import uuid

from datetime import datetime, timezone
from typing import List, Dict

from langchain_core.documents import Document

from src.__shared__.model.message import (
    Message,
    MessageContent,
    Role
)

from src.__shared__.config.vector.redis import vector_store
from src.__shared__.config.cache import redis_client


class MemoryService:

    @staticmethod
    def build_semantic_content(message: Message) -> str:
        return "\n".join(
            f"{item.role.value}: {item.content}"
            for item in message.messages
        )

    @staticmethod
    def build_namespace(session_id: str) -> str:
        return f"session:{session_id}"

    @staticmethod
    def build_document_id(session_id: str) -> str:
        return f"{MemoryService.build_namespace(session_id)}:{uuid.uuid4()}"

    @staticmethod
    def build_history_key(session_id: str) -> str:
        return f"{MemoryService.build_namespace(session_id)}:history"

    @staticmethod
    def _get_redis_client():
        return redis_client

    @staticmethod
    def save_message(
        session_id: str,
        message: Message
    ) -> None:

        created_at = datetime.now(timezone.utc).isoformat()

        semantic_content = MemoryService.build_semantic_content(
            message
        )

        document = Document(
            page_content=semantic_content,
            metadata={
                "session_id": session_id,
                "namespace": MemoryService.build_namespace(session_id),
                "created_at": created_at,
                "message": message.model_dump_json()
            }
        )

        vector_store.add_documents(
            documents=[document],
            ids=[MemoryService.build_document_id(session_id)]
        )

        history_payload = json.dumps(
            {
                "created_at": created_at,
                "messages": [
                    {
                        "role": item.role.value,
                        "content": item.content
                    }
                    for item in message.messages
                ]
            },
            ensure_ascii=False
        )

        redis_client = MemoryService._get_redis_client()

        history_key = MemoryService.build_history_key(
            session_id
        )

        redis_client.zadd(
            history_key,
            {
                history_payload: datetime.now(
                    timezone.utc
                ).timestamp()
            }
        )

        redis_client.expire(
            history_key,
            60 * 60 * 24 * 30
        )

    @staticmethod
    def search_memories(
        session_id: str,
        query: str,
        k: int = 4
    ) -> List[Message]:

        try:
            documents = vector_store.similarity_search(
                query=query,
                k=k,
                filter={
                    "session_id": session_id
                }
            )

        except TypeError:
            documents = vector_store.similarity_search(
                query=query,
                k=k
            )

        memories: List[Message] = []

        for doc in documents:

            if doc.metadata.get("session_id") != session_id:
                continue

            memories.append(
                Message.model_validate_json(
                    doc.metadata["message"]
                )
            )

        return memories

    @staticmethod
    def get_recent_history(
        session_id: str,
        limit: int = 5
    ) -> List[Message]:

        redis_client = MemoryService._get_redis_client()

        history_key = MemoryService.build_history_key(
            session_id
        )

        raw_items = redis_client.zrevrange(
            history_key,
            0,
            limit - 1
        )

        history: List[Message] = []

        for raw_item in raw_items:

            if isinstance(raw_item, bytes):
                raw_item = raw_item.decode("utf-8")

            data = json.loads(raw_item)

            messages_data = data.get("messages")

            if messages_data is None:
                messages_data = data.get("message", [])

            if not messages_data:
                continue

            messages = [
                MessageContent(
                    role=Role(item["role"]),
                    content=item["content"]
                )
                for item in messages_data
            ]

            history.append(
                Message(
                    messages=messages
                )
            )

        return history

    @staticmethod
    def get_context(
        session_id: str,
        query: str,
        embedding_k: int = 4,
        history_limit: int = 5
    ) -> Dict[str, List[Message]]:

        return {
            "embeddings": MemoryService.search_memories(
                session_id=session_id,
                query=query,
                k=embedding_k
            ),
            "recent_history": MemoryService.get_recent_history(
                session_id=session_id,
                limit=history_limit
            )
        }