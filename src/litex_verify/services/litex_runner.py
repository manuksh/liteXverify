"""LiteX invocation service."""

from __future__ import annotations

import structlog
from pathlib import Path

from litex_verify.core.exceptions import RTLError
from litex_verify.models.soc_config import SoCConfig
from litex_verify.utils.subprocess import run_command

logger = structlog.get_logger(__name__)


class LiteXRunner:
    """LiteX invocation wrapper with auto-detect fallback to stub mode.

    When ``stub_mode`` is ``None`` (default), the runner probes whether the
    ``litex`` Python package is importable.  If it is, real RTL generation is
    attempted; otherwise the runner falls back to a synthetic stub and emits a
    warning so operators are never silently misled.
    """

    _litex_available: bool | None = None  # class-level cache after first probe

    async def _check_litex(self) -> bool:
        """Return True if the litex package is importable in the current env."""
        if LiteXRunner._litex_available is not None:
            return LiteXRunner._litex_available
        probe = await run_command(
            ["python", "-c", "import litex; print(litex.__version__)"],
            timeout=15,
        )
        LiteXRunner._litex_available = probe.returncode == 0
        if LiteXRunner._litex_available:
            version = probe.stdout.strip().splitlines()[0] if probe.stdout else "unknown"
            logger.info("litex_detected", version=version)
        else:
            logger.warning("litex_not_found", hint="RTL generation will use stub output")
        return LiteXRunner._litex_available

    async def generate_rtl(
        self,
        config: SoCConfig,
        output_dir: Path,
        output_format: str = "verilog",
        stub_mode: bool | None = None,
    ) -> list[Path]:
        """Generate RTL for *config* into *output_dir*.

        Parameters
        ----------
        stub_mode:
            ``True``  — always use the synthetic stub.
            ``False`` — always invoke real LiteX (raises on failure).
            ``None``  — auto-detect: use real LiteX when available, else stub.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        ext = "v" if output_format == "verilog" else "vhd"
        top_name = "soc_top"
        rtl_path = output_dir / f"{top_name}.{ext}"

        use_real = stub_mode is False or (stub_mode is None and await self._check_litex())

        if use_real:
            cmd = [
                "python",
                "-m",
                "litex.soc.integration.soc_core",
                "--cpu-type",
                config.cpu.type,
                "--output-dir",
                str(output_dir),
                "--no-compile-software",
            ]
            result = await run_command(cmd, cwd=output_dir, timeout=120)
            if result.returncode != 0:
                if stub_mode is False:
                    raise RTLError("LiteX RTL generation failed", details=result.stderr)
                # Auto-detect mode: LiteX found but failed — fall through to stub
                logger.warning(
                    "litex_rtl_failed",
                    returncode=result.returncode,
                    stderr=result.stderr[:400],
                    hint="Falling back to stub RTL",
                )
            else:
                # Gather all generated RTL files; if LiteX wrote them, return them
                generated = list(output_dir.glob(f"**/*.{ext}"))
                if generated:
                    return generated

        content = self._render_stub(top_name, config, output_format)
        rtl_path.write_text(content, encoding="utf-8")
        return [rtl_path]

    def _render_stub(self, top_name: str, config: SoCConfig, output_format: str) -> str:
        if output_format != "verilog":
            return f"-- Auto-generated stub for {top_name}\nentity {top_name} is end;\narchitecture rtl of {top_name} is begin end;\n"
        return (
            f"// Auto-generated LiteXVerify stub\n"
            f"module {top_name} (\n"
            f"    input wire clk,\n"
            f"    input wire rst\n"
            f");\n"
            f"  // CPU: {config.cpu.type}\n"
            f"  // Bus: {config.bus.standard}\n"
            f"endmodule\n"
        )
