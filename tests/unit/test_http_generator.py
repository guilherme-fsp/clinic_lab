from transpiler.generators.http_generator import (
    generate_http_tool,
)
from transpiler.schemas.tool import HTTPToolSpec


def test_generate_http_tool():

    tool = HTTPToolSpec(
        type="http",
        name="schedule_exam",
        description="Schedules laboratory exams.",
        base_url="http://localhost:8000",
        method="POST",
        path="/appointments",
    )

    code = generate_http_tool(tool)

    assert "async def schedule_exam" in code
    assert "client.post(" in code
    assert "'/appointments'" in code
    assert "http://localhost:8000" in code

    compile(
        code,
        "<generated-http-tool>",
        "exec",
    )

def test_generate_http_tool_uses_configured_method():

    tool = HTTPToolSpec(
        type="http",
        name="update_resource",
        base_url="http://localhost:8000",
        method="PUT",
        path="/resources/123",
    )

    code = generate_http_tool(tool)

    assert "client.put(" in code
    assert "'/resources/123'" in code

import pytest
from pydantic import ValidationError

from transpiler.schemas.tool import HTTPToolSpec


def test_http_tool_requires_valid_path():

    with pytest.raises(ValidationError):
        HTTPToolSpec(
            type="http",
            name="schedule_exam",
            base_url="http://localhost:8000",
            method="POST",
            path="appointments",
        )