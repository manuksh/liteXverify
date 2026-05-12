"""Sandboxed file system operations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import aiofiles
import aiofiles.os

from litex_verify.core.exceptions import SecurityError


class SandboxedFileSystem:
    def __init__(self, workspace: Path, allowed_paths: list[Path] | None = None) -> None:
        self.workspace = workspace.resolve()
        self.allowed_paths = [self.workspace]
        for path in allowed_paths or []:
            self.allowed_paths.append(path.resolve())

    def _validate_path(self, path: Path) -> Path:
        resolved = path.resolve()
        for allowed in self.allowed_paths:
            try:
                resolved.relative_to(allowed)
                return resolved
            except ValueError:
                continue
        raise SecurityError(f"Path {resolved} is outside workspace")

    async def exists(self, path: Path) -> bool:
        validated = self._validate_path(path)
        return await aiofiles.os.path.exists(validated)

    async def mkdir(self, path: Path, parents: bool = True) -> None:
        validated = self._validate_path(path)
        if parents:
            await aiofiles.os.makedirs(validated, exist_ok=True)
        else:
            await aiofiles.os.mkdir(validated)

    async def write_text(self, path: Path, content: str) -> None:
        validated = self._validate_path(path)
        await self.mkdir(validated.parent, parents=True)
        tmp = validated.with_suffix(validated.suffix + ".tmp")
        async with aiofiles.open(tmp, "w", encoding="utf-8") as file:
            await file.write(content)
        await aiofiles.os.replace(tmp, validated)

    async def read_text(self, path: Path) -> str:
        validated = self._validate_path(path)
        async with aiofiles.open(validated, "r", encoding="utf-8") as file:
            return await file.read()

    async def write_json(self, path: Path, payload: dict[str, Any]) -> None:
        await self.write_text(path, json.dumps(payload, indent=2))

    async def read_json(self, path: Path) -> dict[str, Any]:
        text = await self.read_text(path)
        return json.loads(text)
