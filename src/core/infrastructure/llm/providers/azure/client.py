from typing import Type, TypeVar, cast

import backoff
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI
from openai import RateLimitError
from pydantic import BaseModel, SecretStr

from src.config import config
from src.core.infrastructure.llm.models import LlmModel
from src.core.infrastructure.llm.providers.base import BaseLlmClient
from src.core.infrastructure.llm.utils.parsing import parse_structured_output

T = TypeVar("T", bound=BaseModel)


class AzureLlm(BaseLlmClient):
    def __init__(
        self, llm_model: LlmModel, temperature: float | None = None
    ) -> None:
        self._client = AzureChatOpenAI(
            model=llm_model.value,
            temperature=temperature or config.OPENAI_LLM_TEMPERATURE,
            api_key=SecretStr(config.AZURE_OPENAI_API_KEY),
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            api_version=config.AZURE_OPENAI_API_VERSION,
            azure_deployment=llm_model.value,
        )

    @backoff.on_exception(
        backoff.expo,
        RateLimitError,
        max_tries=config.OPENAI_LLM_MAX_TRIES,
        max_time=config.OPENAI_LLM_MAX_TIME,
    )
    def invoke(
        self,
        system: str,
        human: str,
        output_type: Type[T] | None = None,
    ) -> T | str:
        messages = [
            SystemMessage(content=system),
            HumanMessage(content=human),
        ]
        response = self._client.invoke(messages)
        content = cast(str, response.content)

        if output_type is not None:
            return parse_structured_output(content, output_type)
        return content

    @backoff.on_exception(
        backoff.expo,
        RateLimitError,
        max_tries=config.OPENAI_LLM_MAX_TRIES,
        max_time=config.OPENAI_LLM_MAX_TIME,
    )
    async def ainvoke(
        self,
        system: str,
        human: str,
        output_type: Type[T] | None = None,
    ) -> T | str:
        messages = [
            SystemMessage(content=system),
            HumanMessage(content=human),
        ]
        response = await self._client.ainvoke(messages)
        content = cast(str, response.content)

        if output_type is not None:
            return parse_structured_output(content, output_type)
        return content
