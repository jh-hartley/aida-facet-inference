from enum import Enum
from typing import Protocol, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LlmClient(Protocol):
    """Protocol defining the interface for LLM clients."""

    def invoke(
        self,
        system: str,
        human: str,
        output_type: Type[T] | None = None,
    ) -> T | str: ...

    async def ainvoke(
        self,
        system: str,
        human: str,
        output_type: Type[T] | None = None,
    ) -> T | str: ...


class EmbeddingClient(Protocol):
    """Protocol defining the interface for embedding clients."""

    async def aembed_documents(
        self, texts: list[str]
    ) -> list[list[float]]: ...


class LlmModel(str, Enum):
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O = "gpt-4o"
    GPT_4_1_NANO = "gpt-4.1-nano"
    GPT_4_1_MINI = "gpt-4.1-mini"
    GPT_4_1 = "gpt-4.1"
    O4_MINI = "o4-mini"
    O4_MINI_HIGH = "o4-mini-high"
    O3_MINI = "o3-mini"
    O3_MINI_HIGH = "o3-mini-high"

    @property
    def label(self) -> str:
        return self.value
