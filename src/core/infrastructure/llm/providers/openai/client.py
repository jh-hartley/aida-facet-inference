from typing import Type, TypeVar, cast
from pydantic import BaseModel, SecretStr

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.config import config
from src.core.infrastructure.llm.models import LlmModel
from src.core.infrastructure.llm.providers.base import BaseLlmClient
from src.core.infrastructure.llm.utils.parsing import parse_structured_output

T = TypeVar("T", bound=BaseModel)

class OpenAiClient(BaseLlmClient):
    """OpenAI LLM client implementation."""
    
    def __init__(self, llm_model: LlmModel, temperature: float | None = None) -> None:
        self._client = ChatOpenAI(
            model=llm_model.value,
            temperature=temperature or config.OPENAI_LLM_TEMPERATURE,
            api_key=SecretStr(config.OPENAI_API_KEY),
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