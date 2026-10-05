from pydantic import BaseModel, ConfigDict, Field, field_validator

from transpiler.schemas.tool import ToolSpec


class AgentSpec(BaseModel):
    """
    Declarative specification used to generate a Google ADK agent.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    name: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$",
        description="Valid Python-compatible name for the generated agent.",
    )

    description: str = Field(
        min_length=1,
        description="Human-readable description of the agent.",
    )

    instruction: str = Field(
        min_length=1,
        description="System instruction that defines agent behavior.",
    )

    model: str = Field(
        min_length=1,
        description="Model identifier used by Google ADK.",
    )

    tools: list[ToolSpec] = Field(
        default_factory=list,
        description="Tools available to the generated agent.",
    )

    @field_validator("tools")
    @classmethod
    def validate_unique_tool_names(
        cls,
        tools: list[ToolSpec],
    ) -> list[ToolSpec]:

        names = [tool.name for tool in tools]

        if len(names) != len(set(names)):
            raise ValueError(
                "Tool names must be unique."
            )

        return tools