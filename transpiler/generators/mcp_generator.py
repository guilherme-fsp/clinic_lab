from transpiler.schemas.tool import MCPToolSpec


def generate_mcp_tool(tool: MCPToolSpec) -> str:
    """
    Generate the Python code required to instantiate
    an MCP toolset using SSE transport.
    """

    variable_name = f"{tool.name}_toolset"

    return f'''{variable_name} = McpToolset(
    connection_params=SseConnectionParams(
        url="{tool.url}"
    )
)'''