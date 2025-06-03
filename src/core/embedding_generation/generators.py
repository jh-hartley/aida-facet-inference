import logging
from itertools import islice
from typing import Iterable, Iterator

import backoff
import numpy as np
import openai
import tiktoken

from src.common.logs import setup_logging
from src.config import config
from src.core.infrastructure.llm.client import embeddings

logger = logging.getLogger(__name__)
setup_logging()


def embedding_model_to_encoding(model_name: str) -> str:
    if model_name in {
        "text-embedding-ada-002",
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
    encoding = tiktoken.get_encoding(
        embedding_model_to_encoding(config.OPENAI_EMBEDDING_MODEL)
    )
    tokens = encoding.encode(text)
    yield from _batched(tokens, chunk_length)


@backoff.on_exception(
    backoff.expo,
    openai.RateLimitError,
    max_tries=config.OPENAI_EMBEDDING_MAX_TRIES,
    max_time=config.OPENAI_EMBEDDING_MAX_TIME,
)
async def get_embedding_with_backoff(chunk_text: str) -> list[float]:
    return (await embeddings().aembed_documents([chunk_text]))[0]


async def len_safe_get_embedding(
    text: str,
) -> tuple[list[list[float]], list[int]]:
    chunk_embeddings = []
    chunk_lengths = []

    for chunk in _chunked_tokens(text, config.EMBEDDING_DEFAULT_DIMENSIONS):
        chunk_text = tiktoken.get_encoding(
            embedding_model_to_encoding(config.OPENAI_EMBEDDING_MODEL)
        ).decode(chunk)
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
