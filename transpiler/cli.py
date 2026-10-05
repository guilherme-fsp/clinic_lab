from pathlib import Path

from transpiler.generators.agent_generator import (
    AgentCodeGenerator,
)
from transpiler.validators.spec_validator import (
    SpecValidationError,
    load_agent_spec,
)


def main() -> None:

    try:
        spec = load_agent_spec(
            "examples/agent_spec.json"
        )

    except SpecValidationError as exc:
        print(exc)
        raise SystemExit(1)

    print(
        "Specification validated successfully."
    )

    generator = AgentCodeGenerator()

    generated_code = generator.generate(
        spec
    )

    try:
        compile(
            generated_code,
            f"<generated:{spec.name}>",
            "exec",
        )
    except SyntaxError as exc:
        print(
            f"Generated code is invalid: {exc}"

        )

        raise SystemExit(1)

    output_path = Path(
        f"generated/{spec.name}.py"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        generated_code,
        encoding="utf-8",
    )

    print(
        f"Generated agent: {output_path}"
    )


if __name__ == "__main__":
    main()