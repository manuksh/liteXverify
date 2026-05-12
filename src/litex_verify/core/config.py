"""Configuration model for server runtime settings."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class ServerConfig(BaseModel):
    workspace: Path
    projects_dir_name: str = "projects"
    state_dir_name: str = ".litex_verify"
    config_filename: str = "soc_config.json"
    default_timeout_seconds: int = Field(default=300, ge=1, le=36000)
