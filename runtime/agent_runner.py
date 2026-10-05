import importlib.util
import logging
from pathlib import Path

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


logger = logging.getLogger(__name__)

APP_NAME = "generated_agent"
USER_ID = "cli_user"
SESSION_ID = "cli_session"


def load_generated_agent(agent_name: str):
    if not agent_name.isidentifier():
        raise ValueError(f"Invalid agent name: {agent_name}")

    module_path = (Path("generated")/ f"{agent_name}.py")

    if not module_path.exists():
        raise FileNotFoundError(f"Generated agent not found: {module_path}")

    logger.info("Loading generated agent | name=%s | path=%s",agent_name,module_path)

    module_spec = importlib.util.spec_from_file_location(agent_name,module_path,
)

    if (
        module_spec is None
        or module_spec.loader is None
    ):
        raise ImportError(f"Unable to load generated agent: {agent_name}")

    module = importlib.util.module_from_spec( module_spec)

    module_spec.loader.exec_module(module)

    if not hasattr(
        module,
        "root_agent",
    ):
        raise AttributeError(f"Generated module '{agent_name}' does not define root_agent"
        )

    logger.info("Generated agent loaded successfully | name=%s",agent_name)

    return module.root_agent


async def run_generated_agent(agent_name: str, message: str,) -> str:

    logger.info("Starting ADK runner | agent=%s",agent_name)

    root_agent = load_generated_agent(agent_name)

    session_service = InMemorySessionService()

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    user_message = types.Content(
        role="user",
        parts=[
            types.Part(
                text=message,
            )
        ],
    )

    final_response = ""

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=user_message,
    ):

        if event.content:
            for part in event.content.parts:

                function_call = getattr(part,"function_call",None)

                if function_call:
                    logger.info("Tool call | name=%s",function_call.name)

                function_response = getattr(part,"function_response",None)

                if function_response:
                    logger.info("Tool response | name=%s",function_response.name)

        if not event.is_final_response():
            continue

        if not event.content:
            continue

        for part in event.content.parts:
            if part.text:
                final_response += part.text

    logger.info("ADK runner finished | agent=%s",agent_name)

    return final_response