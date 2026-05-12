import pytest

from litex_verify.core.context import ServerContext
from litex_verify.tools.config_create import ConfigCreateInput, ConfigCreateTool


@pytest.mark.asyncio
async def test_config_create_writes_config(tmp_path) -> None:
    context = ServerContext(tmp_path)
    project = tmp_path / "projects" / "demo"
    await context.fs.mkdir(project / ".litex_verify", parents=True)
    await context.fs.mkdir(project / "config", parents=True)
    context.set_active_project(project)
    await context.fs.write_json(project / ".litex_verify" / "state.json", {"project_name": "demo"})

    tool = ConfigCreateTool(context)
    result = await tool.execute(
        ConfigCreateInput(
            cpu="vexriscv",
            peripherals=[{"type": "uart"}],
        )
    )
    assert result.success
