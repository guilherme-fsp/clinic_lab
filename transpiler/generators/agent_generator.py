from transpiler.generators.http_generator import (
    generate_http_tool,
)
from transpiler.generators.mcp_generator import (
    generate_mcp_tool,
)
from transpiler.schemas.agent import AgentSpec
from transpiler.schemas.tool import (
    HTTPToolSpec,
    MCPToolSpec,
    LocalToolSpec
)


class AgentCodeGenerator:

    def generate(
        self,
        spec: AgentSpec,
    ) -> str:

        imports = self._generate_imports(
            spec
        )

        tool_definitions, tool_references = (
            self._generate_tools(spec)
        )

        agent_definition = self._generate_agent(
            spec,
            tool_references,
        )

        sections: list[str] = [
            imports,
        ]

        if tool_definitions:
            sections.append(
                "\n\n".join(
                    tool_definitions
                )
            )

        sections.append(
            agent_definition
        )

        return "\n\n".join(
            sections
        )

    def _generate_imports(
        self,
        spec: AgentSpec,
    ) -> str:

        imports: set[str] = {
            "from google.adk.agents import Agent",
        }

        for tool in spec.tools:

            if isinstance(tool, MCPToolSpec):

                imports.add(
                    "from google.adk.tools.mcp_tool."
                    "mcp_toolset import McpToolset"
                )

                imports.add(
                    "from google.adk.tools.mcp_tool."
                    "mcp_session_manager "
                    "import SseConnectionParams"
                )

            elif isinstance(tool, HTTPToolSpec):

                imports.add(
                    "import httpx"
                )

            elif isinstance(tool, LocalToolSpec):

                imports.add(
                    f"from {tool.module} "
                    f"import {tool.function}"
                )

        return "\n".join(
            sorted(imports)
        )

    def _generate_tools(
        self,
        spec: AgentSpec,
    ) -> tuple[list[str], list[str]]:

        tool_definitions: list[str] = []
        tool_references: list[str] = []

        for tool in spec.tools:

            if isinstance(tool, MCPToolSpec):

                tool_definitions.append(
                    generate_mcp_tool(tool)
                )

                tool_references.append(
                    f"{tool.name}_toolset"
                )

            elif isinstance(tool, HTTPToolSpec):

                tool_definitions.append(
                    generate_http_tool(tool)
                )

                tool_references.append(
                    tool.name
                )

            elif isinstance(tool, LocalToolSpec):

                tool_references.append(
                    tool.function
                )

        return (
            tool_definitions,
            tool_references,
        )

    def _generate_agent(
        self,
        spec: AgentSpec,
        tool_references: list[str],
    ) -> str:

        tools_block = self._format_tools(
            tool_references
        )

        return f"""root_agent = Agent(
        name={spec.name!r},
        model={spec.model!r},
        description={spec.description!r},
        instruction={spec.instruction!r},
        tools=[
    {tools_block}
        ],
    )"""

    @staticmethod
    def _get_tool_reference(
        tool: MCPToolSpec
        | HTTPToolSpec
        | LocalToolSpec,
    ) -> str:

        if isinstance(tool, MCPToolSpec):
            return f"{tool.name}_toolset"

        if isinstance(tool, HTTPToolSpec):
            return tool.name

        if isinstance(tool, LocalToolSpec):
            return tool.function

        raise ValueError(
            f"Unsupported tool: {tool}"
        )

    @staticmethod
    def _format_tools(
        tools: list[str],
    ) -> str:

        return "\n".join(
            f"        {tool},"
            for tool in tools
        )