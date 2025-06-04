from typing import Type, TypeVar, cast, overload, Any
from pydantic import BaseModel

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from src.config import config
from src.core.infrastructure.llm.azure_client import AzureLlm, AzureEmbeddingClient
from src.core.infrastructure.llm.openai_client import OpenAiAdapter, llm
from src.core.infrastructure.llm.models import LlmModel, LlmClient, EmbeddingClient
from src.core.infrastructure.llm.json_utils import parse_structured_output

T = TypeVar("T", bound=BaseModel)


def embeddings(model: str | None = None) -> EmbeddingClient:
    """
    Get an embedding client for the configured provider.
    
    Parameters:
    - model (str | None): Optional model name to use
    
    Returns:
    - EmbeddingClient: The configured embedding client
    """
    if config.LLM_PROVIDER == "azure":
        return AzureEmbeddingClient()
    return OpenAIEmbeddings(model=model or config.OPENAI_EMBEDDING_MODEL)


class Llm:
    """
    Adapter for LLM interactions that provides a unified interface for different
    LLM providers. Handles structured output parsing and validation.
    """

    def __init__(
        self, llm_model: LlmModel, temperature: float | None = None
    ) -> None:
        self.llm_model = llm_model
        self._client = (
            AzureLlm(llm_model, temperature)
            if config.LLM_PROVIDER == "azure"
            else llm(model=llm_model.value, temperature=temperature)
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

        Parameters:
        - system (str): The system message to send
        - human (str): The user message to send
        - output_type (Type[T] | None): The expected output type
            (defaults to str)

        Returns:
        - T | str: The response content in the specified type
        """
        response = self._client.invoke(system, human, output_type)
        if output_type is not None and isinstance(response, str):
            return parse_structured_output(response, output_type)
        return response

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

        Parameters:
        - system (str): The system message to send
        - human (str): The user message to send
        - output_type (Type[T] | None): The expected output type (defaults to
            str)

        Returns:
        - T | str: The response content in the specified type
        """
        response = await self._client.ainvoke(system, human, output_type)
        if output_type is not None and isinstance(response, str):
            return parse_structured_output(response, output_type)
        return response
