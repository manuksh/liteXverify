import pytest

from litex_verify.server import LiteXVerifyServer


@pytest.mark.asyncio
async def test_invoke_tool_reports_unknown(tmp_path) -> None:
    server = LiteXVerifyServer(workspace_path=tmp_path)
    result = await server.invoke_tool("does_not_exist", {})
    assert "error" in result
