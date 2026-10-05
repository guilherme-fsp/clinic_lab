from pathlib import Path

from transpiler.generators.agent_generator import (
    AgentCodeGenerator,
)
from transpiler.schemas.agent import AgentSpec


GENERATED_DIR = Path("generated")


def transpile_agent(spec: AgentSpec) -> Path:
    
    generator = AgentCodeGenerator()

    generated_code = generator.generate(spec)

    compile(generated_code, f"<generated:{spec.name}>", "exec")

    GENERATED_DIR.mkdir(parents=True,exist_ok=True)

    output_path = (GENERATED_DIR/ f"{spec.name}.py")

    output_path.write_text(generated_code,encoding="utf-8")

    return output_path