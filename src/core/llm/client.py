from typing import Any, Type, cast, overload

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from src.config import config
from src.core.llm.models import LlmModel, T


def llm(
    model: str | None = None,
    temperature: float | None = None,
    top_p: float | None = None,
    frequency_penalty: float | None = None,
    reasoning_effort: str | None = None,
) -> ChatOpenAI:
    """
    Creates and returns a configured ChatOpenAI instance.

    Parameters:
    - model (str, optional): The name of the model to use (default from config).
    - temperature (float, optional): Sampling temperature for randomness in output.
    - top_p (float, optional): Top-p sampling threshold for diversity.
    - frequency_penalty (float, optional): Penalty for word/phrase repetition.
    - reasoning_effort (str, optional): Reasoning effort level for o3-mini model.
    """
    llm_config: dict[str, Any] = {
        "model": model or config.OPENAI_LLM_MODEL,
        "top_p": top_p or config.OPENAI_LLM_TOP_P,
        "frequency_penalty": frequency_penalty or config.OPENAI_LLM_FREQ_PENALTY,
    }

    if (model or config.OPENAI_LLM_MODEL) == "o3-mini":
        if reasoning_effort:
            llm_config["reasoning_effort"] = (
                reasoning_effort or config.OPENAI_LLM_REASONING_EFFORT
            )
    else:
        llm_config["temperature"] = temperature or config.OPENAI_LLM_TEMPERATURE

    return ChatOpenAI(**llm_config)


def embeddings(model: str | None = None) -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model=model or config.OPENAI_EMBEDDING_MODEL)


class Llm:
    """
    Abstraction layer for LLM interactions that provides configurable access to LLM
    providers. Supports both synchronous and asynchronous invocations with structured
    output.
    """

    def __init__(self, llm_model: LlmModel, temperature: float | None = None) -> None:
        self.llm_model = llm_model
        model_config: dict[str, Any] = {
            "model": self.llm_model.value,
            "temperature": temperature,
        }
        if self.llm_model == LlmModel.O3_MINI_HIGH:
            model_config["reasoning_effort"] = "high"
        self._chat = ChatOpenAI(**model_config)

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
        - output_type (Type[T] | None): The expected output type (defaults to str)

        Returns:
        - T | str: The response content in the specified type
        """
        messages = [SystemMessage(system), HumanMessage(human)]

        if output_type is None:
            # ChatOpenAI.invoke() always returns BaseMessage, but mypy can't infer this
            response = self._chat.invoke(messages)
            return response.content  # type: ignore
        else:
            chat = self._chat.with_structured_output(output_type)
            response = chat.invoke(messages)  # type: ignore[assignment]
            return cast(T, response)

    @overload
    async def ainvoke(self, system: str, human: str) -> str: ...

    @overload
    async def ainvoke(self, system: str, human: str, output_type: Type[T]) -> T: ...

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
        - output_type (Type[T] | None): The expected output type (defaults to str)

        Returns:
        - T | str: The response content in the specified type
        """
        messages = [SystemMessage(system), HumanMessage(human)]

        if output_type is None:
            # ChatOpenAI.ainvoke() always returns BaseMessage but mypy can't infer this
            response = await self._chat.ainvoke(messages)
            return response.content  # type: ignore
        else:
            chat = self._chat.with_structured_output(output_type)
            response = await chat.ainvoke(messages)  # type: ignore[assignment]
            return cast(T, response)
