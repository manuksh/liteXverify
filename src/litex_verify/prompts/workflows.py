"""Prompt definitions for guided workflows."""

FULL_VERIFICATION_PROMPT = (
    "Full verification workflow:\n"
    "1) Validate environment\n"
    "2) Create/validate configuration\n"
    "3) Generate RTL and lint\n"
    "4) Generate testbench\n"
    "5) Run regression\n"
    "6) Analyze results\n"
    "7) Generate report\n"
)

QUICK_CHECK_PROMPT = (
    "Quick check workflow:\n"
    "1) Generate RTL\n"
    "2) Run sanity tests\n"
    "3) Summarize pass/fail\n"
)

COVERAGE_CLOSURE_PROMPT = (
    "Coverage closure workflow:\n"
    "1) Analyze holes\n"
    "2) Generate targeted tests\n"
    "3) Run incremental regression\n"
    "4) Re-analyze coverage\n"
)


def get_prompt(uri: str) -> str:
    mapping = {
        "workflow://full_verification": FULL_VERIFICATION_PROMPT,
        "workflow://quick_check": QUICK_CHECK_PROMPT,
        "workflow://coverage_closure": COVERAGE_CLOSURE_PROMPT,
    }
    if uri not in mapping:
        raise KeyError(uri)
    return mapping[uri]
