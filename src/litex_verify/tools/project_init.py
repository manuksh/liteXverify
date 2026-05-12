"""project_init tool."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from litex_verify.core.exceptions import ProjectExistsError, ToolError
from litex_verify.core.state import WorkflowState
from litex_verify.models.project import ProjectState
from litex_verify.tools.base import BaseTool
from litex_verify.tools.tool_discover import ToolDiscoverInput, ToolDiscoverTool


class ProjectInitInput(BaseModel):
    project_name: str = Field(..., description="Project identifier")
    target_dir: str | None = None
    template: Literal["minimal", "standard", "full"] = "standard"


class ProjectInitOutput(BaseModel):
    success: bool
    project_path: str
    structure: dict[str, Any]
    next_steps: list[str]


class ProjectInitTool(BaseTool[ProjectInitInput, ProjectInitOutput]):
    name = "project_init"
    description = "Initialize a new LiteX verification project"
    input_schema = ProjectInitInput
    output_schema = ProjectInitOutput
    allowed_states = frozenset(WorkflowState)

    async def execute(self, input_data: ProjectInitInput) -> ProjectInitOutput:
        state = ProjectState(project_name=input_data.project_name)
        target = Path(input_data.target_dir).resolve() if input_data.target_dir else self.context.projects_root.resolve()
        try:
            target.relative_to(self.context.workspace)
        except ValueError as exc:
            raise ToolError(
                code=9002,
                category="system",
                message="target_dir must be inside workspace",
                details=str(target),
            ) from exc
        project_path = target / input_data.project_name
        if project_path.exists():
            raise ProjectExistsError(
                f"Project {input_data.project_name} already exists",
                recovery="Choose a different project name",
            )

        scaffold = self.context.get_scaffold(input_data.template)
        structure = await self._create_structure(project_path, scaffold)

        state.workflow_state = WorkflowState.S1_CONFIG
        await self.context.fs.write_json(project_path / ".litex_verify" / "state.json", state.model_dump(mode="json"))

        self.context.set_active_project(project_path)
        if self.context.state_machine:
            await self.context.state_machine.load()

        tool_discover = ToolDiscoverTool(self.context)
        tools_result = await tool_discover.execute(ToolDiscoverInput())

        state.tools = {
            key: value for key, value in tools_result.tools.items()
        }
        state.verification_tier = tools_result.verification_tier or 1
        state.workflow_state = WorkflowState.S1_CONFIG
        await self.context.save_project_state(state)

        if self.context.state_machine:
            await self.context.state_machine.transition(WorkflowState.S1_CONFIG, "project_init", force=True)

        return ProjectInitOutput(
            success=True,
            project_path=str(project_path),
            structure=structure,
            next_steps=[
                "Create SoC configuration with config_create",
                "Validate configuration with config_validate",
                f"Detected verification tier: {tools_result.verification_tier}",
            ],
        )

    async def _create_structure(self, project_path: Path, scaffold: dict[str, list[str]]) -> dict[str, Any]:
        created: dict[str, Any] = {}
        await self.context.fs.mkdir(project_path, parents=True)
        for root, children in scaffold.items():
            root_path = project_path / root
            await self.context.fs.mkdir(root_path, parents=True)
            created[root] = []
            for child in children:
                child_path = root_path / child
                await self.context.fs.mkdir(child_path, parents=True)
                created[root].append(child)
        await self.context.fs.write_text(project_path / "README.md", f"# {project_path.name}\n")
        return created
