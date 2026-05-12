# LiteXVerify

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Protocol](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

**Local, open verification infrastructure for LiteX-based System-on-Chip designs**

LiteXVerify is an open-source, local verification infrastructure for LiteX-based SoC designs. It provides a reproducible and auditable workflow for RTL generation, testbench creation, simulation, and coverage analysis, while keeping all execution and design data within the user's local environment.

The server implements the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/), which lets coding assistants such as Cursor, Cline, and OpenCode drive the workflow through structured tool calls — but the server runs entirely on your machine and requires no cloud service.

## What It Does

| Stage | What LiteXVerify provides |
|-------|--------------------------|
| **Configuration** | Structured SoC config from CPU, peripheral, and memory specs; design-rule validation |
| **RTL Generation** | Drives LiteX to produce synthesizable Verilog/VHDL; runs lint automatically |
| **Testbench Generation** | Auto-generates UVM environments (agents, RAL model) or cocotb test modules from the RTL interface |
| **Simulation** | Compiles and launches Verilator, Questa, or Synopsys VCS; manages seeds, timeouts, and waveforms |
| **Coverage Analysis** | Merges coverage databases, identifies uncovered code and functional holes |
| **Reporting** | Produces HTML, Markdown, or JSON verification summary reports |

## Design Principles

- **Local-first** — No data leaves the machine; no accounts, no telemetry, no network calls
- **Reproducible** — Workflow state is persisted to a plain JSON file; any run can be resumed or audited
- **Tool-agnostic** — Automatically adapts to whichever EDA tools are installed (see [Verification Tiers](#verification-tiers))
- **Open** — MIT licensed; all templates, scripts, and generated artifacts are plain text

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Git
- LiteX framework (see installation below)
- At least one simulator:
  - **Tier 1 (Basic):** Verilator or Icarus Verilog (free, open source)
  - **Tier 2 (UVM):** Questa or Synopsys VCS (commercial licence required)
  - **Tier 3 (FPGA):** Vivado

### Installation

```bash
# 1. Create a workspace directory
mkdir litex_workspace && cd litex_workspace

# 2. Install the LiteX framework
git clone https://github.com/enjoy-digital/litex.git
cd litex && pip install -e . && cd ..
python litex/litex_setup.py --init --install

# 3. Install LiteXVerify
git clone https://github.com/<org>/litex_verify.git
cd litex_verify && pip install -e . && cd ..
```

Verify the installation:

```bash
python -m litex_verify --help
```

### Connecting a Coding Assistant (optional)

LiteXVerify exposes its workflow as MCP tools, which coding assistants can call directly. Add the following to your assistant's MCP configuration, substituting the correct workspace path.

**Cursor** (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "litex_verify": {
      "command": "python",
      "args": ["-m", "litex_verify", "--workspace", "/path/to/litex_workspace"]
    }
  }
}
```

**VS Code + Cline** (`cline_mcp_settings.json`):

```json
{
  "mcpServers": {
    "litex_verify": {
      "command": "python",
      "args": ["-m", "litex_verify", "--workspace", "/path/to/litex_workspace"]
    }
  }
}
```

**OpenCode** (`.opencode/mcp.json`):

```json
{
  "mcpServers": {
    "litex_verify": {
      "command": "python",
      "args": ["-m", "litex_verify", "--workspace", "/path/to/litex_workspace"]
    }
  }
}
```

See the [User Manual](user_manual.md) for full configuration options, EDA tool PATH setup, and WSL2 guidance.

## Verification Workflow

The server tracks every project through a state machine that prevents operations from running out of order and ensures each artefact is always traceable to a specific configuration and run.

```
S0 (Init) → S1 (Config) → S2 (RTL) → S3 (TB) → S4 (Sim) → S5 (Analysis) → S6 (Report) → DONE
                │                                    ▲              │
                └────────────────────────────────────┴──────────────┘
                              (iterate on coverage gaps)
```

| State | Name | Entry condition |
|-------|------|----------------|
| S0 | Init & Discovery | Project created; EDA tools scanned |
| S1 | Config | SoC configuration created or loaded |
| S2 | RTL Generation | Configuration validated; RTL produced |
| S3 | TB Generation | RTL interface analysed; testbench generated |
| S4 | Simulation | Testbench compiled; regression running |
| S5 | Analysis | Logs parsed; coverage merged |
| S6 | Report | Summary report generated |

## Workflow Tools

Each step in the workflow is exposed as a discrete, documented tool call.

| Tool | Purpose |
|------|---------|
| `project_init` | Create project directory structure and initial state file |
| `tool_discover` | Detect installed simulators and set verification tier |
| `config_create` | Write a validated SoC configuration (CPU, bus, peripherals, memory) |
| `config_validate` | Run design-rule checks (address overlap, clock limits, bus width) |
| `rtl_generate` | Invoke LiteX and produce Verilog/VHDL; run lint |
| `tb_generate` | Generate UVM environment or cocotb test suite from RTL interfaces |
| `sim_run` | Compile and execute simulation; collect coverage |
| `report_parse` | Extract structured pass/fail and error data from simulation logs |
| `coverage_analyze` | Aggregate coverage databases; identify uncovered items |
| `report_generate` | Produce HTML, Markdown, or JSON verification report |
| `workflow_state` | Query or transition the workflow state machine |

## Verification Tiers

The server detects available tools at startup and activates the corresponding capability set.

| Tier | Tools | Testbench framework | Coverage |
|------|-------|---------------------|---------|
| 1 | Verilator, Icarus Verilog | cocotb (Python) | Line, toggle |
| 2 | Questa, Synopsys VCS | UVM 1.2 (SystemVerilog) | Code, functional, toggle, FSM |
| 3 | Vivado (+ Tier 1/2) | UVM or cocotb | Full + FPGA-in-the-loop |

## Project Structure

```
src/litex_verify/
├── server.py               # MCP server entry point
├── core/                   # State machine, config, context, exceptions
├── models/                 # Pydantic data models (project, SoC config, simulation)
├── tools/                  # One module per workflow tool
├── services/               # EDA tool adapters, LiteX runner, log parser, coverage DB
├── generators/             # UVM and cocotb code generators (Jinja2 templates)
├── resources/              # MCP resource handlers (templates, scripts, project state)
├── prompts/                # MCP guided-workflow prompts
└── utils/                  # Sandboxed filesystem, subprocess, validation helpers

data/
├── templates/              # Jinja2 templates for UVM components and cocotb tests
├── scripts/                # EDA tool compile/run/coverage scripts
└── scaffolds/              # Project directory scaffolds (minimal / standard / full)
```

## Documentation

See the [User Manual](user_manual.md) for installation instructions, agent configuration, EDA tool setup, and a complete end-to-end usage guide.

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Running with Coverage

```bash
pytest tests/ --cov=litex_verify --cov-report=term-missing
```

### Running the Server Directly

```bash
python -m litex_verify --workspace /path/to/workspace --log-level DEBUG
```

### Adding a New Tool

1. Create `src/litex_verify/tools/<tool_name>.py` following the `BaseTool` pattern
2. Register the class in `src/litex_verify/tools/__init__.py`
3. Add unit tests in `tests/unit/tools/test_<tool_name>.py`
4. Document the new tool in `user_manual.md`

### Code Quality

```bash
# Lint and format
ruff check src/ tests/
ruff format src/ tests/

# Type checking
mypy src/litex_verify

# Pre-commit hooks (run once after cloning)
pre-commit install
```

## Local Execution and Auditability

All operations run as local subprocess calls. No data is sent to any remote service at any stage.

- Workflow state is written to `<project>/.litex_verify/state.json` — a plain JSON file that can be read, diffed, or committed to version control
- All tool invocations are logged locally via `structlog`; set `--log-json` for machine-readable output
- Generated RTL, testbenches, scripts, and reports are plain text files under the project directory

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-change`)
3. Commit your changes with a clear message
4. Open a pull request against `develop`

Please run `pre-commit` and `pytest` before submitting.

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

## Acknowledgements

- [LiteX](https://github.com/enjoy-digital/litex) — SoC builder framework by enjoy-digital
- [Model Context Protocol](https://modelcontextprotocol.io/) — open standard for tool-augmented AI assistants
- [cocotb](https://www.cocotb.org/) — coroutine-based hardware co-simulation framework
- [UVM](https://www.accellera.org/activities/working-groups/uvm) — Universal Verification Methodology (IEEE 1800.2)

---

> This project is under active development. Tool interfaces may change before the 1.0 release.
