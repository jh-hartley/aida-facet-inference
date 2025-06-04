#!/usr/bin/env python3

import argparse
import asyncio

from src.core.embedding_generation.jobs.embed_product_descriptions import (
    create_embeddings_for_products,
    embed_single_product,
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Embed product descriptions (all or single)"
    )
    parser.add_argument(
        "--product",
        type=str,
        help="Product key to embed (if omitted, embed all products)",
        default=None,
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        help="Maximum number of concurrent embedding jobs (default: 10)",
        default=10,
    )
    args = parser.parse_args()

    if args.product:
        asyncio.run(embed_single_product(args.product))
    else:
        asyncio.run(create_embeddings_for_products(max_concurrency=args.max_concurrency))
