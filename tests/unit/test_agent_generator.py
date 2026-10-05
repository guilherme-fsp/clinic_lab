from transpiler.generators.agent_generator import (
    AgentCodeGenerator,
)
from transpiler.schemas.agent import AgentSpec


def test_generated_agent_is_valid_python():

    spec = AgentSpec(
        name="test_agent",
        description="Test agent",
        instruction="You are a test agent.",
        model="gemini-2.5-flash",
        tools=[],
    )

    generator = AgentCodeGenerator()

    code = generator.generate(spec)

    compile(
        code,
        "<generated-agent>",
        "exec",
    )