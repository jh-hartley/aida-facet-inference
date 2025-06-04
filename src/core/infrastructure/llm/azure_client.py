from typing import Type, TypeVar
import aiohttp
import asyncio
import logging
from pydantic import BaseModel

from src.config import config
from src.core.infrastructure.llm.models import LlmModel, LlmClient, EmbeddingClient
from src.core.infrastructure.llm.json_utils import parse_structured_output

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class AzureLlm(LlmClient):
    """
    Azure AI Foundry implementation of the LLM client.
    Uses direct HTTP calls to the Azure AI Foundry endpoint.
    """

    def __init__(
        self, llm_model: LlmModel, temperature: float | None = None
    ) -> None:
        self.llm_model = llm_model
        self.temperature = temperature
        self.endpoint = config.AZURE_OPENAI_ENDPOINT
        self.api_key = config.AZURE_OPENAI_API_KEY
        self.api_version = config.AZURE_OPENAI_API_VERSION
        logger.info(f"Initialized Azure LLM with endpoint: {self.endpoint}")

    def invoke(
        self,
        system: str,
        human: str,
        output_type: Type[T] | None = None,
    ) -> T | str:
        """
        Invoke the Azure LLM with the provided messages.

        Parameters:
        - system (str): The system message to send
        - human (str): The user message to send
        - output_type (Type[T] | None): The expected output type (defaults to str)

        Returns:
        - T | str: The response content in the specified type
        """
        # Run the async version in a sync context
        return asyncio.run(self.ainvoke(system, human, output_type))

    async def ainvoke(
        self,
        system: str,
        human: str,
        output_type: Type[T] | None = None,
    ) -> T | str:
        """
        Asynchronously invoke the Azure LLM with the provided messages.

        Parameters:
        - system (str): The system message to send
        - human (str): The user message to send
        - output_type (Type[T] | None): The expected output type (defaults to str)

        Returns:
        - T | str: The response content in the specified type
        """
        # Construct the full URL with the deployment and API version
        base_url = self.endpoint.rstrip('/')  # Remove trailing slash if present
        url = f"{base_url}/openai/deployments/{config.AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version={self.api_version}"
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key,
            "User-Agent": "aida-facet-inference/1.0",
            "Accept": "*/*",
        }

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": human},
        ]

        payload = {
            "messages": messages,
            "temperature": self.temperature or 0.0,
            "model": config.AZURE_OPENAI_DEPLOYMENT,  # Use deployment name as model name
        }

        # Log only the essential request details
        logger.info("Azure API Request Details:")
        logger.info(f"Endpoint: {self.endpoint}")
        logger.info(f"Deployment: {config.AZURE_OPENAI_DEPLOYMENT}")
        logger.info(f"API Version: {self.api_version}")
        logger.info(f"Model: {config.AZURE_OPENAI_DEPLOYMENT}")
        logger.info(f"Temperature: {self.temperature}")
        logger.info(f"Message Count: {len(messages)}")

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Request failed with status {response.status}")
                    logger.error(f"Error response: {error_text}")
                    logger.error(f"Request URL: {url}")
                    raise Exception(f"Azure API error: {error_text}")

                result = await response.json()
                content = result["choices"][0]["message"]["content"]

                if output_type is None:
                    return content
                else:
                    return parse_structured_output(content, output_type)


class AzureEmbeddingClient(EmbeddingClient):
    """
    Azure OpenAI implementation of the embedding client.
    Uses direct HTTP calls to the Azure OpenAI endpoint.
    """

    def __init__(self) -> None:
        self.endpoint = config.AZURE_OPENAI_ENDPOINT
        self.api_key = config.AZURE_OPENAI_API_KEY
        self.api_version = config.AZURE_OPENAI_API_VERSION
        self.deployment = config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT  # Use embedding-specific deployment
        logger.info(f"Initialized Azure Embedding client with endpoint: {self.endpoint}")

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Get embeddings for a list of texts using Azure OpenAI.

        Parameters:
        - texts (list[str]): List of texts to embed

        Returns:
        - list[list[float]]: List of embedding vectors
        """
        base_url = self.endpoint.rstrip('/')
        url = f"{base_url}/openai/deployments/{self.deployment}/embeddings?api-version={self.api_version}"
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key,
            "User-Agent": "aida-facet-inference/1.0",
            "Accept": "*/*",
        }

        payload = {
            "input": texts,
            "model": "text-embedding-3-small",  # Use the actual model name, not deployment name
        }

        logger.info("Azure Embedding Request Details:")
        logger.info(f"Endpoint: {self.endpoint}")
        logger.info(f"Deployment: {self.deployment}")
        logger.info(f"API Version: {self.api_version}")
        logger.info(f"Text Count: {len(texts)}")

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Request failed with status {response.status}")
                    logger.error(f"Error response: {error_text}")
                    logger.error(f"Request URL: {url}")
                    raise Exception(f"Azure API error: {error_text}")

                result = await response.json()
                return [item["embedding"] for item in result["data"]] 