import importlib.util
from transpiler.generators.agent_generator import (
    AgentCodeGenerator,
)
from transpiler.schemas.agent import AgentSpec

def test_generated_agent_can_be_imported(tmp_path):

    spec = AgentSpec(
        name="test_agent",
        description="Test agent",
        instruction="You are a test agent.",
        model="gemini-2.5-flash",
        tools=[],
    )

    generator = AgentCodeGenerator()

    code = generator.generate(spec)

    file_path = tmp_path / "generated_agent.py"
    file_path.write_text(code)

    module_spec = importlib.util.spec_from_file_location(
        "generated_agent",
        file_path,
    )

    module = importlib.util.module_from_spec(
        module_spec
    )

    module_spec.loader.exec_module(module)

    assert hasattr(module, "root_agent")