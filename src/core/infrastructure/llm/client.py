from typing import Type, TypeVar, overload

from pydantic import BaseModel

from src.config import config
from src.core.infrastructure.llm.models import (
    EmbeddingClient,
    LlmClient,
    LlmModel,
)
from src.core.infrastructure.llm.providers.azure.client import AzureLlm
from src.core.infrastructure.llm.providers.azure.embeddings import (
    AzureEmbeddingClient,
)
from src.core.infrastructure.llm.providers.openai.client import OpenAiClient
from src.core.infrastructure.llm.providers.openai.embeddings import (
    OpenAiEmbeddingClient,
)

T = TypeVar("T", bound=BaseModel)


def embeddings(model: str | None = None) -> EmbeddingClient:
    """
    Get an embedding client for the configured provider.
    """
    if config.LLM_PROVIDER == "azure":
        return AzureEmbeddingClient()
    return OpenAiEmbeddingClient(model=model or config.OPENAI_EMBEDDING_MODEL)


class Llm:
    """
    Adapter for LLM interactions that provides a unified interface for
    different LLM providers. Handles structured output parsing and validation.
    """

    def __init__(
        self, llm_model: LlmModel, temperature: float | None = None
    ) -> None:
        self.llm_model = llm_model
        self._client: LlmClient = (
            AzureLlm(llm_model, temperature)
            if config.LLM_PROVIDER == "azure"
            else OpenAiClient(llm_model, temperature)
        )

    @overload
    def invoke(self, system: str, human: str) -> str: ...

    @overload
    def invoke(self, system: str, human: str, output_type: Type[T]) -> T: ...

    def invoke(
        self,
        system: str,
        human: str,
        output_type: Type[T] | None = None,
    ) -> T | str:
        """
        Invoke the LLM with the provided messages.
        """
        return self._client.invoke(system, human, output_type)

    @overload
    async def ainvoke(self, system: str, human: str) -> str: ...

    @overload
    async def ainvoke(
        self, system: str, human: str, output_type: Type[T]
    ) -> T: ...

    async def ainvoke(
        self,
        system: str,
        human: str,
        output_type: Type[T] | None = None,
    ) -> T | str:
        """
        Asynchronously invoke the LLM with the provided messages.
        """
        return await self._client.ainvoke(system, human, output_type)
