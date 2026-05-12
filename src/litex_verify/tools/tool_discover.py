"""tool_discover tool."""

from __future__ import annotations

from pydantic import BaseModel

from litex_verify.core.state import WorkflowState
from litex_verify.models.project import ToolInfo
from litex_verify.tools.base import BaseTool


class ToolDiscoverInput(BaseModel):
    force_rescan: bool = False


class ToolDiscoverOutput(BaseModel):
    tools: dict[str, ToolInfo]
    verification_tier: int
    capabilities: list[str]
    missing_recommended: list[str]


class ToolDiscoverTool(BaseTool[ToolDiscoverInput, ToolDiscoverOutput]):
    name = "tool_discover"
    description = "Detect available EDA tools and capabilities"
    input_schema = ToolDiscoverInput
    output_schema = ToolDiscoverOutput
    allowed_states = frozenset(WorkflowState)

    async def execute(self, input_data: ToolDiscoverInput) -> ToolDiscoverOutput:
        tools = await self.context.eda_tools.detect_all(force=input_data.force_rescan)
        tier = self.context.eda_tools.get_verification_tier()
        capabilities = sorted({cap for tool in tools.values() for cap in tool.capabilities})
        recommended = {"verilator", "icarus", "questa", "synopsys_vcs", "vivado"}
        missing = sorted(recommended.difference(tools.keys()))
        return ToolDiscoverOutput(
            tools=tools,
            verification_tier=tier if tier > 0 else 1,
            capabilities=capabilities,
            missing_recommended=missing,
        )
