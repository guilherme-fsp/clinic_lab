from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from runtime.agent_runner import run_generated_agent
from transpiler.schemas.agent import AgentSpec
from transpiler.service import transpile_agent


app = FastAPI(
    title="ADK Agent Platform API",
    version="1.0.0",
)


class RunAgentRequest(BaseModel):
    image_path: str = Field(
        ...,
        examples=["examples/imagem_qualquer.png"],
    )


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
    }


@app.post("/agents")
async def create_agent(
    spec: AgentSpec,
) -> dict:
    output_path = transpile_agent(
        spec
    )

    return {
        "status": "generated",
        "agent_name": spec.name,
        "output_file": str(output_path),
    }


@app.post("/agents/{agent_name}/run")
async def run_agent(
    agent_name: str,
    request: RunAgentRequest,
) -> dict:

    image_path = Path(
        request.image_path
    ).resolve()

    if not image_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Image not found: {image_path}",
        )

    message = f"""
Process the laboratory request image located at:

{image_path}

Follow your configured workflow exactly.
"""

    try:
        response = await run_generated_agent(
            agent_name=agent_name,
            message=message,
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "agent_name": agent_name,
        "status": "completed",
        "response": response,
    }