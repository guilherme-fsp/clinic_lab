from pathlib import Path
import logging

import json
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from runtime.agent_runner import run_generated_agent
from transpiler.schemas.agent import AgentSpec
from transpiler.service import transpile_agent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="ADK Agent Platform API",
    version="1.0.0",
)



    


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
    }


@app.post("/agents")
async def create_agent_and_run(
    spec: AgentSpec,
) -> dict:

    #HARDCODED IMAGE PATH FOR DEMONSTRATION PURPOSES
    image_path = Path("/app/examples/imagem_qualquer.png").resolve()

    if not image_path.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"Image not found: {image_path}",
        )
    logger.info("Generating agent: %s", spec.name)

    output_path = transpile_agent(spec)
    logger.info("Agent generated successfully: %s", output_path)

    message = f"""
    Process the laboratory request image located at:
    
    {image_path}
    
    Follow your configured workflow exactly.
    """
    logger.info("Executing agent: %s", spec.name)

    try:
        response = await run_generated_agent(
            agent_name=spec.name,
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
    
    output_dir = Path("exec_evidences/agent_results")
    output_dir.mkdir(parents=True, exist_ok=True)

    counter = 1

    while (output_dir / f"_{counter}.json").exists():
        counter +=1


    result_path = output_dir / f"{counter}.json"

    result_data = {
        "agent_name": spec.name,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "response": response,
    }

    result_path.write_text(
        json.dumps(
            result_data,
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )

    logger.info("Agent result saved at: %s", result_path)

    logger.info("Agent execution finished %s", spec.name)

    return {
        "agent_name": spec.name,
        "status": "completed",
        "output_file": str(output_path),
        "response": response,
    }
