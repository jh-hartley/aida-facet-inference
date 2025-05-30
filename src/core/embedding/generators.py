from itertools import islice
from typing import Iterable, Iterator

import numpy as np
import tiktoken

from src.config import config
from src.core.llm import embeddings


def _batched(iterable: Iterable, n: int) -> Iterator[tuple]:
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def _chunked_tokens(text: str, chunk_length: int) -> Iterator[tuple[int]]:
    encoding = tiktoken.get_encoding(config.OPENAI_EMBEDDING_MODEL)
    tokens = encoding.encode(text)
    yield from _batched(tokens, chunk_length)


async def len_safe_get_embedding(
    text: str,
) -> tuple[list[list[float]], list[int]]:
    chunk_embeddings = []
    chunk_lengths = []

    for chunk in _chunked_tokens(text, config.EMBEDDING_DEFAULT_DIMENSIONS):
        chunk_text = tiktoken.get_encoding(
            config.OPENAI_EMBEDDING_MODEL
        ).decode(chunk)
        embedding = (await embeddings().aembed_documents([chunk_text]))[0]
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
