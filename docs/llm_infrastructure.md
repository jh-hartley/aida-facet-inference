# LLM Infrastructure

This document explains the architecture and implementation of the LLM (Large Language Model) infrastructure in the project. It covers the adapter pattern, unified client, provider implementations, configuration, and extensibility.

---

## Overview

The LLM infrastructure provides a unified interface for interacting with different LLM providers (e.g., OpenAI, Azure OpenAI). It abstracts away provider-specific details and enables structured, validated output from LLM calls.

- **Adapter Pattern:** The system uses an adapter pattern to allow seamless switching between LLM providers.
- **Unified Client:** The `Llm` class exposes a consistent interface for invoking LLMs, regardless of the backend.
- **Provider Implementations:** Each provider (OpenAI, Azure) implements a common protocol for LLM and embedding operations.

---

## Key Components

### 1. Unified LLM Client (`src/core/infrastructure/llm/client.py`)
- The `Llm` class is the main entry point for LLM interactions.
- Supports both synchronous (`invoke`) and asynchronous (`ainvoke`) calls.
- Handles structured output parsing and validation using Pydantic models.
- Selects the provider based on configuration (`LLM_PROVIDER`).

### 2. Provider Implementations (`src/core/infrastructure/llm/providers/`)
- **Base Classes:**
  - `BaseLlmClient` and `BaseEmbeddingClient` define the required interface for all providers.
- **OpenAI Provider:**
  - Implements LLM and embedding clients using the OpenAI API and LangChain.
  - Handles retries, rate limiting, and structured output parsing.
- **Azure Provider:**
  - Implements LLM and embedding clients for Azure OpenAI endpoints.
  - Supports Azure-specific configuration (endpoint, deployment, API version).

### 3. Model and Protocol Definitions (`src/core/infrastructure/llm/models.py`)
- Defines the `LlmClient` and `EmbeddingClient` protocols.
- Enumerates supported LLM models.

---

## Configuration

LLM provider and model selection is controlled via environment variables:
- `LLM_PROVIDER`: `openai` or `azure`
- `OPENAI_API_KEY`, `OPENAI_LLM_MODEL`, etc.
- `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`, etc.

See [docs/environment_variables.md](environment_variables.md) for full details.

---

## Usage Example

```python
from src.core.infrastructure.llm.client import Llm
from src.core.infrastructure.llm.models import LlmModel

llm = Llm(LlmModel.GPT_4O_MINI)
result = llm.invoke(system_prompt, user_prompt)
```

For async usage:
```python
result = await llm.ainvoke(system_prompt, user_prompt)
```

To parse structured output:
```python
from pydantic import BaseModel
class MyOutput(BaseModel):
    field: str

result = llm.invoke(system_prompt, user_prompt, output_type=MyOutput)
```

---

## Extending LLM Infrastructure

- **Add a new provider:** Implement the required methods in a new class inheriting from `BaseLlmClient` and/or `BaseEmbeddingClient`.
- **Register the provider:** Update the unified client to select the new provider based on configuration.
- **Add new models:** Extend the `LlmModel` enum as needed.

---

## Design Patterns & Best Practices

- **Adapter Pattern:** Enables easy switching and extension of LLM providers.
- **Protocol-Oriented Design:** Ensures all providers implement a consistent interface.
- **Structured Output:** Uses Pydantic for robust, type-safe output parsing.
- **Retry/Backoff:** Handles rate limits and transient errors gracefully.

---

For more details, see the code in `src/core/infrastructure/llm/` and the environment variable reference. 