from itertools import islice
from typing import Iterable, Iterator

import backoff
import numpy as np
import openai
import tiktoken

from src.config import config
from src.core.infrastructure.llm.client import embeddings


def get_current_embedding_model_name() -> str:
    """
    Return the embedding model name for the current provider.
    For OpenAI, use config.OPENAI_EMBEDDING_MODEL.
    For Azure, use config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT.
    """
    if config.LLM_PROVIDER == "azure":
        return config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
    return config.OPENAI_EMBEDDING_MODEL


def embedding_model_to_encoding(model_name: str) -> str:
    if model_name in {
        "text-embedding-ada-002",
        "text-embedding-3-small",
        "text-embedding-3-large",
    }:
        return "cl100k_base"
    if model_name in {
        "ada-002",
        "text-embedding-3-small",
        "text-embedding-3-large",
    }:
        return "cl100k_base"
    raise ValueError(f"Unknown embedding model: {model_name}")


def _batched(iterable: Iterable, n: int) -> Iterator[tuple]:
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def _chunked_tokens(text: str, chunk_length: int) -> Iterator[tuple[int]]:
    model_name = get_current_embedding_model_name()
    encoding_name = embedding_model_to_encoding(model_name)
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text)
    yield from _batched(tokens, chunk_length)


@backoff.on_exception(
    backoff.expo,
    openai.RateLimitError,
    max_tries=config.OPENAI_EMBEDDING_MAX_TRIES,
    max_time=config.OPENAI_EMBEDDING_MAX_TIME,
    base=config.OPENAI_EMBEDDING_BACKOFF_BASE,
    jitter=backoff.full_jitter if config.OPENAI_EMBEDDING_BACKOFF_JITTER else None,
)
async def get_embedding_with_backoff(chunk_text: str) -> list[float]:
    client = embeddings()
    return (await client.aembed_documents([chunk_text]))[0]


async def len_safe_get_embedding(
    text: str,
) -> tuple[list[list[float]], list[int]]:
    chunk_embeddings = []
    chunk_lengths = []

    model_name = get_current_embedding_model_name()
    encoding_name = embedding_model_to_encoding(model_name)
    encoding = tiktoken.get_encoding(encoding_name)
    for chunk in _chunked_tokens(text, config.EMBEDDING_DEFAULT_DIMENSIONS):
        chunk_text = encoding.decode(chunk)
        embedding = await get_embedding_with_backoff(chunk_text)
        chunk_embeddings.append(embedding)
        chunk_lengths.append(len(chunk))

    return chunk_embeddings, chunk_lengths


async def len_safe_get_averaged_embedding(text: str) -> list[float]:
    chunk_embeddings, chunk_lengths = await len_safe_get_embedding(text)
    averaged_embedding = np.average(
        chunk_embeddings, axis=0, weights=chunk_lengths
    )
    normalised_embedding = averaged_embedding / np.linalg.norm(
        averaged_embedding
    )
    return normalised_embedding.tolist()  # type: ignore[no-any-return]
