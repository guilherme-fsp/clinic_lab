import importlib.util

import httpx
import pytest

from scheduling_api.app import app
from transpiler.generators.agent_generator import AgentCodeGenerator
from transpiler.schemas.agent import AgentSpec


@pytest.mark.anyio
async def test_generated_schedule_exam_calls_fastapi(
    tmp_path,
    monkeypatch,
):
    spec = AgentSpec(
        name="integration_agent",
        description="Integration test agent.",
        instruction="Schedule laboratory exams.",
        model="gemini-2.5-flash",
        tools=[
            {
                "type": "http",
                "name": "schedule_exam",
                "description": (
                    "Submits laboratory exams "
                    "to the scheduling service."
                ),
                "base_url": "http://scheduling-api:8000",
                "method": "POST",
                "path": "/appointments",
            }
        ],
    )

    generator = AgentCodeGenerator()
    code = generator.generate(spec)

    generated_file = (
        tmp_path / "integration_agent.py"
    )

    generated_file.write_text(
        code,
        encoding="utf-8",
    )

    module_spec = (
        importlib.util.spec_from_file_location(
            "integration_agent",
            generated_file,
        )
    )

    module = importlib.util.module_from_spec(
        module_spec
    )

    module_spec.loader.exec_module(module)

    transport = httpx.ASGITransport(
        app=app
    )

    original_async_client = httpx.AsyncClient

    def create_test_client(*args, **kwargs):
        kwargs["transport"] = transport
        kwargs["base_url"] = "http://testserver"

        return original_async_client(
            *args,
            **kwargs,
        )

    monkeypatch.setattr(
        module.httpx,
        "AsyncClient",
        create_test_client,
    )

    payload = {
        "exams": [
            {
                "name": "Hemograma Completo",
                "code": "LAB001",
            },
            {
                "name": "Glicemia",
                "code": "LAB002",
            },
        ]
    }

    response = await module.schedule_exam(
        payload
    )

    assert response["status"] == "requested"

    assert response["exams"] == payload["exams"]

    assert response[
        "appointment_id"
    ].startswith("APT-")