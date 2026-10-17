from pathlib import Path
import logging

from transpiler.generators.agent_generator import (
    AgentCodeGenerator,
)
from transpiler.schemas.agent import AgentSpec

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


GENERATED_DIR = Path("generated")


def transpile_agent(spec: AgentSpec) -> Path:

    logger.info("transpile_agent: Starting transpilation for agent: %s", spec.name)
    
    generator = AgentCodeGenerator()

    generated_code = generator.generate(spec)

    compile(generated_code, f"<generated:{spec.name}>", "exec")

    GENERATED_DIR.mkdir(parents=True,exist_ok=True)

    output_path = (GENERATED_DIR/ f"{spec.name}.py")

    output_path.write_text(generated_code,encoding="utf-8")

    logger.info("transpile_agent: Agent generated successfully: %s", output_path)

    return output_path