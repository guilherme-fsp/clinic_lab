from transpiler.schemas.tool import HTTPToolSpec


def generate_http_tool(
    tool: HTTPToolSpec,
) -> str:
    """
    Generate a Python function that acts as an HTTP tool.
    """

    method = tool.method.lower()

    description = (
        tool.description
        or f"Calls the {tool.name} HTTP service."
    )

    return f'''async def {tool.name}(payload: dict) -> dict:
    """
    {description}
    """

    async with httpx.AsyncClient(
        base_url="{tool.base_url}",
        timeout=30.0,
    ) as client:

        response = await client.{method}(
            {tool.path!r},
            json=payload,
        )

        response.raise_for_status()

        return response.json()
'''