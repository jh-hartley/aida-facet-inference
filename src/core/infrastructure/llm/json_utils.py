from typing import Type, TypeVar
import re
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def parse_structured_output(content: str, output_type: Type[T]) -> T:
    """
    Parse and validate JSON content into a Pydantic model.
    Handles both raw JSON and JSON wrapped in markdown code blocks.

    Parameters:
    - content (str): The JSON content to parse
    - output_type (Type[T]): The Pydantic model type to parse into

    Returns:
    - T: The parsed and validated model instance

    Raises:
    - ValueError: If parsing or validation fails
    """
    # Remove markdown code block if present
    content = content.strip()
    if content.startswith("```") and content.endswith("```"):
        # Extract content between code blocks
        match = re.search(r"```(?:json)?\n(.*?)\n```", content, re.DOTALL)
        if match:
            content = match.group(1).strip()
    
    try:
        return output_type.model_validate_json(content)
    except Exception as e:
        raise ValueError(
            f"Failed to parse structured output as {output_type.__name__}: {str(e)}"
        ) from e 