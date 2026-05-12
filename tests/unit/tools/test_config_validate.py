"""Unit tests for config_validate tool."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from litex_verify.core.context import ServerContext
from litex_verify.core.exceptions import StateError
from litex_verify.core.state import WorkflowState
from litex_verify.models.project import ProjectState
from litex_verify.models.soc_config import (
    BusConfig,
    CPUConfig,
    ClockConfig,
    MemoryConfig,
    PeripheralConfig,
    SoCConfig,
)
from litex_verify.tools.config_validate import ConfigValidateInput, ConfigValidateTool


def _setup_project(ctx: ServerContext, config: SoCConfig) -> Path:
    proj = ctx.workspace / "proj"
    meta = proj / ".litex_verify"
    cfg_dir = proj / "config"
    meta.mkdir(parents=True)
    cfg_dir.mkdir(parents=True)
    state = ProjectState(
        project_name="proj",
        workflow_state=WorkflowState.S1_CONFIG,
    )
    (meta / "state.json").write_text(
        json.dumps(state.model_dump(mode="json")), encoding="utf-8"
    )
    (cfg_dir / "soc_config.json").write_text(
        config.model_dump_json(), encoding="utf-8"
    )
    ctx.set_active_project(proj)
    return proj


@pytest.mark.asyncio
async def test_valid_config_passes(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    config = SoCConfig(cpu=CPUConfig(type="vexriscv"))
    _setup_project(ctx, config)
    tool = ConfigValidateTool(ctx)
    result = await tool.execute(ConfigValidateInput())
    assert result.valid
    assert not result.errors


@pytest.mark.asyncio
async def test_duplicate_addresses_flagged(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    config = SoCConfig(
        cpu=CPUConfig(type="vexriscv"),
        peripherals=[
            PeripheralConfig(type="uart", name="uart0", base_addr="0x82000000"),
            PeripheralConfig(type="spi", name="spi0", base_addr="0x82000000"),
        ],
    )
    _setup_project(ctx, config)
    tool = ConfigValidateTool(ctx)
    result = await tool.execute(ConfigValidateInput())
    assert not result.valid
    assert any("ADDR-001" in e for e in result.errors)


@pytest.mark.asyncio
async def test_unaligned_address_flagged(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    config = SoCConfig(
        cpu=CPUConfig(type="vexriscv"),
        peripherals=[
            PeripheralConfig(type="uart", name="uart0", base_addr="0x82000001"),
        ],
    )
    _setup_project(ctx, config)
    tool = ConfigValidateTool(ctx)
    result = await tool.execute(ConfigValidateInput())
    assert any("ADDR-002" in e for e in result.errors)


@pytest.mark.asyncio
async def test_no_active_project_raises(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    tool = ConfigValidateTool(ctx)
    with pytest.raises(StateError):
        await tool.execute(ConfigValidateInput())


@pytest.mark.asyncio
async def test_state_transitions_to_s2_when_valid(tmp_path: Path) -> None:
    ctx = ServerContext(tmp_path)
    config = SoCConfig(cpu=CPUConfig(type="vexriscv"))
    _setup_project(ctx, config)
    # Force the state machine to S1 so the conditional transition to S2 fires
    assert ctx.state_machine is not None
    await ctx.state_machine.transition(WorkflowState.S1_CONFIG, "test", force=True)
    tool = ConfigValidateTool(ctx)
    await tool.execute(ConfigValidateInput())
    assert ctx.state_machine.current_state == WorkflowState.S2_RTL
