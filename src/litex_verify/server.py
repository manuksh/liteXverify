"""LiteXVerify MCP server."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Awaitable, Callable

import structlog

from litex_verify.core.context import ServerContext
from litex_verify.core.exceptions import LiteXVerifyError
from litex_verify.prompts.workflows import get_prompt
from litex_verify.resources.project import read_project_resource
from litex_verify.resources.scripts import read_script_resource
from litex_verify.resources.templates import read_template_resource
from litex_verify.tools import ALL_TOOL_CLASSES

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
except Exception:  # pragma: no cover - fallback for environments without MCP sdk
    Server = None
    stdio_server = None


class LiteXVerifyServer:
    """Main MCP server class."""

    def __init__(self, workspace_path: Path | None = None) -> None:
        self.workspace = (workspace_path or Path.cwd()).resolve()
        self.context = ServerContext(self.workspace)
        self.logger = structlog.get_logger().bind(component="server")
        self.server = Server("litex_verify") if Server is not None else None

        self._tools: dict[str, Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]] = {}
        self._register_tools()
        self._resource_uris = [
            "templates://uvm/agent",
            "templates://uvm/env",
            "templates://uvm/test",
            "templates://uvm/sequence",
            "templates://cocotb/test",
            "templates://cocotb/bfm",
            "scripts://questa/compile.do",
            "scripts://questa/run.do",
            "scripts://vcs/compile.sh",
            "scripts://vcs/run.sh",
            "scripts://vcs/coverage.sh",
            "scripts://verilator/Makefile",
            "scripts://vivado/synth.tcl",
            "project://state",
            "project://config",
            "project://runs",
        ]
        self._prompt_uris = [
            "workflow://full_verification",
            "workflow://quick_check",
            "workflow://coverage_closure",
        ]
        if self.server is not None:
            self._register_mcp_handlers()

    def _register_tools(self) -> None:
        for tool_class in ALL_TOOL_CLASSES:
            tool = tool_class(self.context)
            self._tools[tool.name] = tool

    def _register_mcp_handlers(self) -> None:
        if self.server is None:
            return

        @self.server.list_tools()
        async def _list_tools() -> list[dict[str, Any]]:
            return [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.input_schema.model_json_schema(),
                }
                for tool in self._tools.values()
            ]

        @self.server.call_tool()
        async def _call_tool(name: str, arguments: dict[str, Any] | None = None) -> list[dict[str, str]]:
            result = await self.invoke_tool(name, arguments or {})
            return [{"type": "text", "text": json.dumps(result)}]

        @self.server.list_resources()
        async def _list_resources() -> list[dict[str, str]]:
            return [{"uri": uri, "name": uri, "description": uri} for uri in self._resource_uris]

        @self.server.read_resource()
        async def _read_resource(uri: str) -> str:
            resource = await self.read_resource(uri)
            return json.dumps(resource) if isinstance(resource, dict) else resource

        @self.server.list_prompts()
        async def _list_prompts() -> list[dict[str, str]]:
            return [{"name": uri, "description": uri} for uri in self._prompt_uris]

        @self.server.get_prompt()
        async def _get_prompt(name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
            _ = arguments
            text = await self.get_prompt(name)
            return {
                "description": f"Workflow prompt: {name}",
                "messages": [
                    {
                        "role": "user",
                        "content": {"type": "text", "text": text},
                    }
                ],
            }

    async def invoke_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name not in self._tools:
            return {"error": {"code": 9001, "category": "system", "message": f"Unknown tool: {name}"}}
        try:
            return await self._tools[name](arguments)
        except LiteXVerifyError as exc:
            return {"error": exc.to_mcp_error()}

    async def read_resource(self, uri: str) -> str | dict:
        if uri.startswith("templates://"):
            return read_template_resource(self.workspace, uri)
        if uri.startswith("scripts://"):
            return read_script_resource(self.workspace, uri)
        if uri.startswith("project://"):
            return await read_project_resource(self.context, uri)
        raise ValueError(f"Unsupported resource: {uri}")

    async def get_prompt(self, uri: str) -> str:
        return get_prompt(uri)

    async def run(self) -> None:
        if self.server is None or stdio_server is None:
            self.logger.warning("mcp_sdk_missing", message="mcp package unavailable; invoke tools via API only")
            return
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )
