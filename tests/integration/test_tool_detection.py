import pytest

from litex_verify.services.eda_tools import EDAToolService


@pytest.mark.asyncio
async def test_tool_detection_returns_dict() -> None:
    result = await EDAToolService().detect_all(force=True)
    assert isinstance(result, dict)
