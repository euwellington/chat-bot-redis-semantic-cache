import os
from langchain_redis import RedisVectorStore

from src.__shared__.config.embedding import embeddings

REDIS_URL = os.getenv("REDIS_URL")

vector_store = RedisVectorStore(
    redis_url=REDIS_URL,
    index_name="chat_memory",
    embeddings=embeddings,
    ttl=6000
)