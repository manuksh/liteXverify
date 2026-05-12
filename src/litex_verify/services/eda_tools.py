"""EDA tool detection service."""

from __future__ import annotations

import asyncio
import shutil
from pathlib import Path

from litex_verify.core.exceptions import ToolNotFoundError
from litex_verify.models.project import ToolInfo
from litex_verify.utils.subprocess import ProcessResult, run_command


class EDAToolAdapter:
    name: str = ""
    tier: int = 1
    detect_cmd: list[str] = []
    capabilities: list[str] = []

    async def detect(self) -> ToolInfo | None:
        executable = self.detect_cmd[0]
        path = shutil.which(executable)
        if not path:
            return None
        result = await run_command(self.detect_cmd, timeout=30)
        if result.returncode != 0:
            return None
        version = _parse_first_version_line(result)
        return ToolInfo(
            name=self.name,
            version=version,
            path=Path(path),
            tier=self.tier,
            capabilities=list(self.capabilities),
        )

    async def run(self, command: list[str], cwd: Path | None = None, timeout: int = 300) -> ProcessResult:
        return await run_command(command, cwd=cwd, timeout=timeout)


class VerilatorTool(EDAToolAdapter):
    name = "verilator"
    tier = 1
    detect_cmd = ["verilator", "--version"]
    capabilities = ["simulation", "lint", "coverage"]


class IcarusTool(EDAToolAdapter):
    name = "icarus"
    tier = 1
    detect_cmd = ["iverilog", "-V"]
    capabilities = ["simulation"]


class QuestaTool(EDAToolAdapter):
    name = "questa"
    tier = 2
    detect_cmd = ["vsim", "-version"]
    capabilities = ["simulation", "coverage", "uvm", "debug"]


class SynopsysVCSTool(EDAToolAdapter):
    name = "synopsys_vcs"
    tier = 2
    detect_cmd = ["vcs", "-ID"]
    capabilities = ["simulation", "coverage", "uvm", "debug"]


class VivadoTool(EDAToolAdapter):
    name = "vivado"
    tier = 3
    detect_cmd = ["vivado", "-version"]
    capabilities = ["synthesis", "implementation", "fpga_test"]


def _parse_first_version_line(result: ProcessResult) -> str:
    text = (result.stdout + "\n" + result.stderr).strip()
    first = text.splitlines()[0] if text else "unknown"
    return first[:120]


class EDAToolService:
    TOOL_CLASSES = [VerilatorTool, IcarusTool, QuestaTool, SynopsysVCSTool, VivadoTool]

    def __init__(self) -> None:
        self._detected: dict[str, ToolInfo] = {}
        self._adapters: dict[str, EDAToolAdapter] = {}

    async def detect_all(self, force: bool = False) -> dict[str, ToolInfo]:
        if self._detected and not force:
            return dict(self._detected)
        adapters = [cls() for cls in self.TOOL_CLASSES]
        self._adapters = {adapter.name: adapter for adapter in adapters}
        results = await asyncio.gather(*(adapter.detect() for adapter in adapters), return_exceptions=True)
        self._detected = {}
        for result in results:
            if isinstance(result, ToolInfo):
                self._detected[result.name] = result
        return dict(self._detected)

    def get_verification_tier(self) -> int:
        if not self._detected:
            return 0
        return max(info.tier for info in self._detected.values())

    def get_tool(self, name: str) -> EDAToolAdapter:
        adapter = self._adapters.get(name)
        if adapter is None:
            raise ToolNotFoundError(f"Tool {name} not available")
        return adapter
