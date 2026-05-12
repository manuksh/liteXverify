"""CLI entrypoint for LiteXVerify."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from litex_verify.core.logging import configure_logging
from litex_verify.server import LiteXVerifyServer


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LiteXVerify MCP server")
    parser.add_argument("--workspace", type=Path, default=None, help="Workspace path")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    parser.add_argument("--log-json", action="store_true", help="Emit JSON logs")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    configure_logging(level=args.log_level, json_output=args.log_json)
    server = LiteXVerifyServer(workspace_path=args.workspace)
    asyncio.run(server.run())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
