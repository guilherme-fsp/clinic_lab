from transpiler.generators.mcp_generator import (
    generate_mcp_tool,
)
from transpiler.schemas.tool import MCPToolSpec


def test_generate_mcp_tool():

    tool = MCPToolSpec(
        type="mcp",
        name="ocr",
        description="OCR service.",
        transport="sse",
        url="http://localhost:8001/sse",
    )

    code = generate_mcp_tool(tool)

    assert "ocr_toolset" in code
    assert "McpToolset" in code
    assert "SseConnectionParams" in code
    assert "http://localhost:8001/sse" in code

    compile(
        code,
        "<generated-mcp-tool>",
        "exec",
    )