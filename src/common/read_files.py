from pathlib import Path

from src.common.exceptions import MalformedPrompt


def read_text_file(file_path: str | Path, encoding: str = "utf-8") -> str:
    try:
        with open(file_path, "r", encoding=encoding) as f:
            content = f.read().strip()

        if not content:
            raise MalformedPrompt(f"File is empty: {file_path}")

        return content

    except FileNotFoundError:
        raise MalformedPrompt(f"File not found: {file_path}")
    except UnicodeDecodeError:
        raise MalformedPrompt(
            f"File encoding error in {file_path}. Expected {encoding}"
        )
    except Exception as e:
        raise MalformedPrompt(f"Error reading file {file_path}: {str(e)}")
