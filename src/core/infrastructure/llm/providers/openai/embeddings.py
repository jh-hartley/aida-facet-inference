from langchain_openai import OpenAIEmbeddings

from src.config import config
from src.core.infrastructure.llm.providers.base import BaseEmbeddingClient


class OpenAiEmbeddingClient(BaseEmbeddingClient):
    """OpenAI embeddings client implementation."""

    def __init__(self, model: str | None = None) -> None:
        self._client = OpenAIEmbeddings(
            model=model or config.OPENAI_EMBEDDING_MODEL
        )

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        return await self._client.aembed_documents(texts)
