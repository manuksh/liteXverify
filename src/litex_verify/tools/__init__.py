"""Tool exports."""

from litex_verify.tools.config_create import ConfigCreateTool
from litex_verify.tools.config_validate import ConfigValidateTool
from litex_verify.tools.coverage_analyze import CoverageAnalyzeTool
from litex_verify.tools.project_init import ProjectInitTool
from litex_verify.tools.report_generate import ReportGenerateTool
from litex_verify.tools.report_parse import ReportParseTool
from litex_verify.tools.rtl_generate import RTLGenerateTool
from litex_verify.tools.sim_run import SimRunTool
from litex_verify.tools.tb_generate import TBGenerateTool
from litex_verify.tools.tool_discover import ToolDiscoverTool
from litex_verify.tools.workflow_state import WorkflowStateTool

ALL_TOOL_CLASSES = [
    ProjectInitTool,
    ToolDiscoverTool,
    ConfigCreateTool,
    ConfigValidateTool,
    RTLGenerateTool,
    TBGenerateTool,
    SimRunTool,
    ReportParseTool,
    CoverageAnalyzeTool,
    ReportGenerateTool,
    WorkflowStateTool,
]
