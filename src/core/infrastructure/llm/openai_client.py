from typing import Any, Type, TypeVar, cast
from pydantic import BaseModel

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from src.config import config
from src.core.infrastructure.llm.models import LlmModel, LlmClient

T = TypeVar("T", bound=BaseModel)


class OpenAiAdapter(LlmClient):
    """Adapter for ChatOpenAI to match the LlmClient protocol."""
    
    def __init__(self, client: ChatOpenAI) -> None:
        self._client = client
    
    def invoke(
        self,
        system: str,
        human: str,
        output_type: Type[T] | None = None,
    ) -> T | str:
        messages = [SystemMessage(system), HumanMessage(human)]
        
        if output_type is None:
            response = self._client.invoke(messages)
            return response.content  # type: ignore
        else:
            chat = self._client.with_structured_output(output_type)
            response = chat.invoke(messages)  # type: ignore[assignment]
            return cast(T, response)
    
    async def ainvoke(
        self,
        system: str,
        human: str,
        output_type: Type[T] | None = None,
    ) -> T | str:
        messages = [SystemMessage(system), HumanMessage(human)]
        
        if output_type is None:
            response = await self._client.ainvoke(messages)
            return response.content  # type: ignore
        else:
            chat = self._client.with_structured_output(output_type)
            response = await chat.ainvoke(messages)  # type: ignore[assignment]
            return cast(T, response)


def llm(
    model: str | None = None,
    temperature: float | None = None,
    top_p: float | None = None,
    frequency_penalty: float | None = None,
    reasoning_effort: str | None = None,
) -> LlmClient:
    """
    Creates and returns a configured LLM client instance.

    Parameters:
    - model (str, optional): The name of the model to use
        (default from config).
    - temperature (float, optional): Sampling temperature for
        randomness in output.
    - top_p (float, optional): Top-p sampling threshold for diversity.
    - frequency_penalty (float, optional): Penalty for word/phrase repetition.
    - reasoning_effort (str, optional): Reasoning effort level for o3-mini
        model.
    """
    llm_config: dict[str, Any] = {
        "model": model or config.OPENAI_LLM_MODEL,
        "top_p": top_p or config.OPENAI_LLM_TOP_P,
        "frequency_penalty": frequency_penalty
        or config.OPENAI_LLM_FREQ_PENALTY,
    }

    if (model or config.OPENAI_LLM_MODEL) == "o3-mini":
        if reasoning_effort:
            llm_config["reasoning_effort"] = (
                reasoning_effort or config.OPENAI_LLM_REASONING_EFFORT
            )
    else:
        llm_config["temperature"] = (
            temperature or config.OPENAI_LLM_TEMPERATURE
        )

    return OpenAiAdapter(ChatOpenAI(**llm_config))


def embeddings(model: str | None = None) -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model=model or config.OPENAI_EMBEDDING_MODEL) 