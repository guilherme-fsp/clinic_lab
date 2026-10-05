import asyncio
import sys
from pathlib import Path

from runtime.agent_runner import (
    run_generated_agent,
)

import logging

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)


async def main() -> None:

    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: python main.py <agent_name> <image_path>"
        )

    agent_name = sys.argv[1]

    image_path = Path(
        sys.argv[2]
    ).resolve()

    if not image_path.exists():
        raise SystemExit(
            f"Image not found: {image_path}"
        )

    message = f"""
Process the laboratory request image located at:

{image_path}

Follow your configured workflow exactly.
"""

    response = await run_generated_agent(
        agent_name=agent_name,
        message=message,
    )

    print("\nAGENT RESPONSE:\n")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())