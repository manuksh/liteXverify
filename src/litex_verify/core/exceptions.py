"""Custom exception hierarchy for LiteXVerify."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ErrorEnvelope:
    code: int
    category: str
    message: str
    details: str | None = None
    recovery: str | None = None


class LiteXVerifyError(Exception):
    """Base exception for all LiteXVerify errors."""

    code: int = 9000
    category: str = "system"

    def __init__(
        self,
        message: str,
        details: str | None = None,
        recovery: str | None = None,
    ) -> None:
        self.message = message
        self.details = details
        self.recovery = recovery
        super().__init__(message)

    def to_mcp_error(self) -> dict[str, object | None]:
        return {
            "code": self.code,
            "category": self.category,
            "message": self.message,
            "details": self.details,
            "recovery": self.recovery,
        }


class ProjectError(LiteXVerifyError):
    category = "project"


class ConfigError(LiteXVerifyError):
    category = "config"


class RTLError(LiteXVerifyError):
    category = "rtl"


class TestbenchError(LiteXVerifyError):
    category = "testbench"


class SimulationError(LiteXVerifyError):
    category = "simulation"


class AnalysisError(LiteXVerifyError):
    category = "analysis"


class StateError(LiteXVerifyError):
    code = 1002
    category = "project"


class ToolError(LiteXVerifyError):
    """Generic execution error carrying explicit code/category."""

    def __init__(
        self,
        code: int,
        message: str,
        category: str = "system",
        details: str | None = None,
        recovery: str | None = None,
    ) -> None:
        self.code = code
        self.category = category
        super().__init__(message, details=details, recovery=recovery)


class ProjectExistsError(ProjectError):
    code = 1010


class ProjectNotFoundError(ProjectError):
    code = 1011


class InvalidConfigError(ConfigError):
    code = 2001


class AddressConflictError(ConfigError):
    code = 2002


class ToolNotFoundError(LiteXVerifyError):
    code = 9001
    category = "system"


class SecurityError(LiteXVerifyError):
    code = 9002
    category = "system"


class InvalidTransitionError(StateError):
    code = 1002


class ToolTimeoutError(SimulationError):
    code = 5002
