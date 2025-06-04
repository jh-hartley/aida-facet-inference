from langchain_openai import AzureOpenAIEmbeddings
from pydantic import SecretStr

from src.config import config
from src.core.infrastructure.llm.providers.base import BaseEmbeddingClient


class AzureEmbeddingClient(BaseEmbeddingClient):
    def __init__(self) -> None:
        self._client = AzureOpenAIEmbeddings(
            api_key=SecretStr(config.AZURE_OPENAI_API_KEY),
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            api_version=config.AZURE_OPENAI_API_VERSION,
            azure_deployment=config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        )

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        return await self._client.aembed_documents(texts)
