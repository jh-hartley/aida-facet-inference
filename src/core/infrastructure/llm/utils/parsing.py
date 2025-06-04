import re
from typing import Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def parse_structured_output(content: str, output_type: Type[T]) -> T:
    """
    Parse and validate JSON content into a Pydantic model.
    Handles both raw JSON and JSON wrapped in markdown code blocks.

    Necessary for Azure Foundry to return structured output,
    but not for OpenAI.
    """
    content = content.strip()
    if content.startswith("```") and content.endswith("```"):
        match = re.search(r"```(?:json)?\n(.*?)\n```", content, re.DOTALL)
        if match:
            content = match.group(1).strip()

    try:
        return output_type.model_validate_json(content)
    except Exception as e:
        raise ValueError(
            f"Failed to parse structured output as "
            f"{output_type.__name__}: {str(e)}"
        ) from e
