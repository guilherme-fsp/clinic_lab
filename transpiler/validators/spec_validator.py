import json
from pathlib import Path

from pydantic import ValidationError

from transpiler.schemas.agent import AgentSpec


class SpecValidationError(Exception):
    """
    Raised when an agent specification cannot be parsed or validated.
    """


def load_agent_spec(
    file_path: str | Path,
) -> AgentSpec:

    path = Path(file_path)

    if not path.exists():
        raise SpecValidationError(
            f"Specification file not found: {path}"
        )

    if not path.is_file():
        raise SpecValidationError(
            f"Specification path is not a file: {path}"
        )

    try:
        raw_content = path.read_text(
            encoding="utf-8"
        )

        data = json.loads(raw_content)

    except json.JSONDecodeError as exc:
        raise SpecValidationError(
            f"Invalid JSON: {exc.msg} "
            f"(line {exc.lineno}, column {exc.colno})"
        ) from exc

    try:
        return AgentSpec.model_validate(data)

    except ValidationError as exc:
        raise SpecValidationError(
            format_validation_error(exc)
        ) from exc


def format_validation_error(
    error: ValidationError,
) -> str:

    messages: list[str] = [
        "Invalid agent specification:"
    ]

    for item in error.errors():

        location = ".".join(
            str(part)
            for part in item["loc"]
        )

        message = item["msg"]

        messages.append(
            f"  - {location}: {message}"
        )

    return "\n".join(messages)