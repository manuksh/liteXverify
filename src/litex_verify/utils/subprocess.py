"""Async subprocess utilities."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from pathlib import Path

from litex_verify.core.exceptions import ToolTimeoutError


@dataclass
class ProcessResult:
    returncode: int
    stdout: str
    stderr: str
    duration_ms: int


async def run_command(cmd: list[str], cwd: Path | None = None, timeout: int = 300) -> ProcessResult:
    start = time.monotonic()
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(cwd) if cwd else None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError as exc:
        proc.kill()
        raise ToolTimeoutError(f"Command timed out: {' '.join(cmd)}") from exc

    return ProcessResult(
        returncode=proc.returncode,
        stdout=stdout.decode(errors="replace"),
        stderr=stderr.decode(errors="replace"),
        duration_ms=int((time.monotonic() - start) * 1000),
    )
