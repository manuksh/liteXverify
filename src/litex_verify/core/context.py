"""Server context shared across tools/resources/prompts."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from litex_verify.core.state import StateMachine
from litex_verify.models.project import ProjectState
from litex_verify.services.eda_tools import EDAToolService
from litex_verify.utils.filesystem import SandboxedFileSystem


class ServerContext:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace.resolve()
        self.fs = SandboxedFileSystem(self.workspace)
        self.active_project: Path | None = None
        self.state_machine: StateMachine | None = None
        self.eda_tools = EDAToolService()

    def set_active_project(self, project_path: Path) -> None:
        self.active_project = project_path.resolve()
        self.state_machine = StateMachine(self.active_project, self.fs)

    def clear_active_project(self) -> None:
        self.active_project = None
        self.state_machine = None

    @property
    def projects_root(self) -> Path:
        return self.workspace / "projects"

    @property
    def state_file(self) -> Path:
        if not self.active_project:
            raise RuntimeError("No active project")
        return self.active_project / ".litex_verify" / "state.json"

    @property
    def config_file(self) -> Path:
        if not self.active_project:
            raise RuntimeError("No active project")
        return self.active_project / "config" / "soc_config.json"

    async def load_project_state(self) -> ProjectState:
        data = await self.fs.read_json(self.state_file)
        state = ProjectState.model_validate(data)
        if self.state_machine:
            await self.state_machine.load()
            state.workflow_state = self.state_machine.current_state
        return state

    async def save_project_state(self, state: ProjectState) -> None:
        state.updated_at = datetime.now(timezone.utc)
        if self.state_machine:
            state.workflow_state = self.state_machine.current_state
        await self.fs.write_json(self.state_file, state.model_dump(mode="json"))

    def get_scaffold(self, template: str) -> dict[str, list[str]]:
        base = {
            "rtl": ["src", "include"],
            "tb": ["unit", "integration", "regression"],
            "sim": ["logs", "wave"],
            "reports": ["sim", "coverage", "signoff"],
            "config": [],
            ".litex_verify": [],
        }
        if template == "minimal":
            return {k: v for k, v in base.items() if k in {"rtl", "tb", "config", ".litex_verify"}}
        if template == "full":
            base["scripts"] = ["questa", "vcs", "vivado"]
        return base
