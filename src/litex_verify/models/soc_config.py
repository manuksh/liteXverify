"""SoC configuration models."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class CPUConfig(BaseModel):
    type: Literal["vexriscv", "picorv32", "minerva", "none"]
    variant: str | None = None
    features: list[str] = Field(default_factory=list)


class BusConfig(BaseModel):
    standard: Literal["wishbone", "axi", "axi-lite"] = "wishbone"
    data_width: Literal[32, 64] = 32
    address_width: int = 32


class ClockConfig(BaseModel):
    sys_clk_freq: int = 100_000_000


class MemoryConfig(BaseModel):
    type: Literal["sram", "sdram", "ddr3"] = "sram"
    size: int = 64 * 1024
    base_addr: str = "0x40000000"


class PeripheralConfig(BaseModel):
    type: Literal["uart", "spi", "i2c", "gpio", "timer", "ethernet", "custom"]
    name: str
    base_addr: str
    params: dict[str, Any] = Field(default_factory=dict)


class SoCConfig(BaseModel):
    cpu: CPUConfig
    bus: BusConfig = Field(default_factory=BusConfig)
    clock: ClockConfig = Field(default_factory=ClockConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    peripherals: list[PeripheralConfig] = Field(default_factory=list)
