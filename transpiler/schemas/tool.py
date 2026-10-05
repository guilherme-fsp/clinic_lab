from typing import Annotated, Literal

from pydantic import AnyHttpUrl, BaseModel, Field


class MCPToolSpec(BaseModel):
    """
    Specification for a tool exposed through a MCP server.
    """

    type: Literal["mcp"]

    name: str = Field(
        min_length=1,
        description="Logical name of the MCP tool.",
    )

    description: str | None = Field(
        default=None,
        description="Human-readable description of the tool.",
    )

    transport: Literal["sse"] = Field(
        default="sse",
        description="MCP transport protocol.",
    )

    url: AnyHttpUrl = Field(
        description="SSE endpoint exposed by the MCP server.",
    )


class HTTPToolSpec(BaseModel):
    """
    Specification for an external HTTP API used by the agent.
    """

    type: Literal["http"]

    name: str = Field(
        min_length=1,
        description="Logical name of the HTTP tool.",
    )

    description: str | None = Field(
        default=None,
        description="Human-readable description of the tool.",
    )

    base_url: AnyHttpUrl = Field(
        description="Base URL of the external HTTP service.",
    )

    method: Literal[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ] = Field(
        description="HTTP method used to call the service.",
    )

    path: str = Field(
        min_length=1,
        pattern=r"^/",
        description="Relative path of the HTTP endpoint.",
    )


class LocalToolSpec(BaseModel):
    """
    Specification for a local Python function exposed
    directly to the generated ADK agent.
    """

    type: Literal["local"]

    name: str = Field(
        min_length=1,
        pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$",
        description="Logical name of the local tool.",
    )

    description: str | None = Field(
        default=None,
        description="Human-readable description of the tool.",
    )

    module: str = Field(
        min_length=1,
        pattern=r"^[a-zA-Z_][a-zA-Z0-9_.]*$",
        description="Python module containing the function.",
    )

    function: str = Field(
        min_length=1,
        pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$",
        description="Python function to expose as an ADK tool.",
    )


ToolSpec = Annotated[
    MCPToolSpec
    | HTTPToolSpec
    | LocalToolSpec,
    Field(discriminator="type"),
]