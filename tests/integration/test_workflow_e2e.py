import pytest

from litex_verify.server import LiteXVerifyServer


@pytest.mark.asyncio
async def test_workflow_minimal(tmp_path) -> None:
    server = LiteXVerifyServer(workspace_path=tmp_path)
    result = await server.invoke_tool("project_init", {"project_name": "e2e_test", "template": "minimal"})
    assert result.get("success") is True
