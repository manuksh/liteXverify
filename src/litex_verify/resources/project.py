"""Project resources."""

from __future__ import annotations

from litex_verify.core.context import ServerContext


async def read_project_resource(context: ServerContext, uri: str) -> dict:
    if not context.active_project:
        return {"error": "No active project. Run project_init first."}
    state = await context.load_project_state()
    if uri == "project://state":
        return {
            "project_name": state.project_name,
            "workflow_state": state.workflow_state.value,
            "verification_tier": state.verification_tier,
            "tools": {name: info.model_dump(mode="json") for name, info in state.tools.items()},
        }
    if uri == "project://config":
        return state.config.model_dump(mode="json") if state.config else {}
    if uri == "project://runs":
        return {"runs": [run.model_dump(mode="json") for run in state.runs]}
    raise ValueError(f"Unsupported resource URI: {uri}")
