from fastapi import FastAPI

from transpiler.schemas.agent import AgentSpec
from transpiler.service import transpile_agent


app = FastAPI(
    title="ADK Agent Transpiler API",
    description=(
        "Receives an agent specification in JSON "
        "and generates executable Google ADK Python code."
    ),
    version="1.0.0",
)


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
    }


@app.post("/transpile")
async def transpile(
    spec: AgentSpec,
) -> dict:
    output_path = transpile_agent(spec)

    generated_code = output_path.read_text(encoding="utf-8")

    return {
        "status": "generated",
        "agent_name": spec.name,
        "output_file": str(output_path),
        "generated_code": generated_code,
    }