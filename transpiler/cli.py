import argparse
import json
from pathlib import Path

from transpiler.schemas.agent import AgentSpec
from transpiler.service import transpile_agent


def main() -> None:
    parser = argparse.ArgumentParser(
        description=("Generate a Google ADK agent from a JSON specification.")
    )

    parser.add_argument("spec_path", type=Path, help="Path to the agent specification JSON.")

    args = parser.parse_args()

    spec_path = args.spec_path

    if not spec_path.exists():
        raise SystemExit(
            f"Specification file not found: {spec_path}"
        )

    raw_spec = json.loads(
        spec_path.read_text(encoding="utf-8")
    )

    spec = AgentSpec.model_validate(raw_spec)

    output_path = transpile_agent(spec)

    print(f"Agent generated successfully: {output_path}")


if __name__ == "__main__":
    main()