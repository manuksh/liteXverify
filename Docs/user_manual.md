# LiteXVerify — User Manual

**Version:** 0.1.0  
**Date:** May 2026  
**Audience:** FPGA Engineers, Verification Engineers, Hardware Architects

---

## Table of Contents

1. [What Is LiteXVerify?](#1-what-is-litexverify)
2. [System Requirements](#2-system-requirements)
3. [Installation](#3-installation)
4. [Configuring AI Coding Agents](#4-configuring-ai-coding-agents)
   - 4.1 [Cursor](#41-cursor)
   - 4.2 [VS Code with Cline](#42-vs-code-with-cline)
   - 4.3 [OpenCode](#43-opencode)
   - 4.4 [OpenAI Codex / Claude CLI](#44-openai-codex--claude-cli)
5. [Environment Configuration](#5-environment-configuration)
   - 5.1 [EDA Tool Setup](#51-eda-tool-setup)
   - 5.2 [LiteX Framework Path](#52-litex-framework-path)
   - 5.3 [Workspace Layout](#53-workspace-layout)
6. [Generating a LiteX SoC](#6-generating-a-litex-soc)
   - 6.1 [Initializing a Project](#61-initializing-a-project)
   - 6.2 [Describing Your SoC in Natural Language](#62-describing-your-soc-in-natural-language)
   - 6.3 [Validating the Configuration](#63-validating-the-configuration)
   - 6.4 [Generating RTL](#64-generating-rtl)
7. [Generating the Verification Platform](#7-generating-the-verification-platform)
   - 7.1 [Choosing a Framework](#71-choosing-a-framework)
   - 7.2 [Generating a UVM Testbench](#72-generating-a-uvm-testbench)
   - 7.3 [Generating a cocotb Testbench](#73-generating-a-cocotb-testbench)
8. [Running Verification](#8-running-verification)
   - 8.1 [Starting a Full Regression](#81-starting-a-full-regression)
   - 8.2 [Running Targeted Tests](#82-running-targeted-tests)
   - 8.3 [Enabling Waveform Dumps](#83-enabling-waveform-dumps)
9. [Analyzing Results](#9-analyzing-results)
   - 9.1 [Parsing Simulation Logs](#91-parsing-simulation-logs)
   - 9.2 [Analyzing Coverage](#92-analyzing-coverage)
   - 9.3 [Generating Reports](#93-generating-reports)
   - 9.4 [Coverage Closure Loop](#94-coverage-closure-loop)
10. [Workflow State Machine](#10-workflow-state-machine)
11. [MCP Tools Reference](#11-mcp-tools-reference)
12. [MCP Resources Reference](#12-mcp-resources-reference)
13. [Verification Tiers](#13-verification-tiers)
14. [Troubleshooting](#14-troubleshooting)
15. [Glossary](#15-glossary)

---

## 1. What Is LiteXVerify?

LiteXVerify is a **local Model Context Protocol (MCP) server** that connects your AI coding agent directly to the LiteX SoC build and verification toolchain. It acts as a structured bridge between natural language instructions and real EDA tool invocations, keeping all design data on your local machine.

### What It Does

| Capability | Description |
|-----------|-------------|
| **SoC Configuration** | Describe your CPU, peripherals, memory, and bus topology in plain English; LiteXVerify creates the LiteX Python config |
| **RTL Generation** | Drives LiteX to produce synthesizable Verilog or VHDL, then runs lint checks automatically |
| **Testbench Generation** | Auto-generates UVM environments (agents, driver, monitor, RAL model) or cocotb test modules directly from the RTL interface |
| **Simulation** | Compiles and launches Verilator, Questa, or Synopsys VCS; manages seeds, timeouts, and waveform capture |
| **Coverage Analysis** | Merges coverage databases and identifies uncovered code/functional holes with actionable suggestions |
| **Reporting** | Produces HTML, Markdown, or JSON verification summary reports |

### What It Does Not Do

- **Send data to the cloud.** Every operation runs locally. No RTL, logs, or coverage data leave your machine.
- **Replace EDA tools.** LiteXVerify orchestrates your existing simulators; it does not bundle them.
- **Require a continuous internet connection.** After initial installation, the server runs fully offline.

### Supported AI Agents

LiteXVerify works with any MCP-capable AI coding client:

- **Cursor** (native MCP support)
- **VS Code + Cline extension** (community MCP support)
- **OpenCode** (built-in MCP support)
- **OpenAI Codex CLI / Claude Code CLI** (via `mcpServers` config)

---

## 2. System Requirements

### Software

| Component | Minimum Version | Notes |
|-----------|----------------|-------|
| Python | 3.10 | 3.11 or 3.12 recommended |
| Git | Any recent version | Required for LiteX installation |
| LiteX Framework | Latest stable | Must be installed and importable |
| pip | 22+ | For package installation |

### Operating Systems

| OS | Support Level |
|----|--------------|
| Linux (Ubuntu, Debian, RHEL, Arch) | Primary — fully supported |
| Windows with WSL2 | Supported — run everything inside WSL2 |
| macOS (Apple Silicon / Intel) | Supported |
| Windows (native) | Partial — EDA tools may require WSL2 |

### EDA Tools (at least one required)

| Tool | Tier | Open Source? | Notes |
|------|------|-------------|-------|
| Verilator 4.x / 5.x | 1 | Yes | Free, fast, cocotb support |
| Icarus Verilog | 1 | Yes | Lightweight functional sim |
| Questa / ModelSim 2021+ | 2 | No (license required) | Full UVM, coverage |
| Synopsys VCS 2021+ | 2 | No (license required) | Full UVM, coverage |
| Vivado 2020+ | 3 | Free edition available | FPGA-in-the-loop |

---

## 3. Installation

### Step 1 — Install the LiteX Framework

```bash
# Create a dedicated workspace
mkdir ~/litex_workspace && cd ~/litex_workspace

# Clone and bootstrap LiteX
git clone https://github.com/enjoy-digital/litex.git
cd litex
pip install -e .
python litex_setup.py --init --install
cd ..
```

The `--init --install` flags download and install all standard LiteX IP cores (Migen, LiteDRAM, LiteEth, etc.). This step may take several minutes.

### Step 2 — Install LiteXVerify

**From PyPI (once published):**

```bash
pip install litex-verify
```

**From source (current method):**

```bash
git clone https://github.com/<org>/litex_verify.git
cd litex_verify
pip install -e .
```

For development or contribution work, install with dev extras and activate pre-commit hooks:

```bash
pip install -e ".[dev]"
pre-commit install
```

### Step 3 — Verify the Installation

```bash
python -m litex_verify --help
```

Expected output:

```
usage: litex_verify [-h] [--workspace WORKSPACE] [--log-level LOG_LEVEL] [--log-json]
LiteXVerify MCP server
```

Run a quick health check by starting the server in the foreground (press Ctrl+C to stop):

```bash
python -m litex_verify --workspace ~/litex_workspace
```

---

## 4. Configuring AI Coding Agents

LiteXVerify communicates with AI agents over **stdio using the JSON-RPC 2.0 / MCP protocol**. Each agent needs to know how to launch the server process. The configuration is a JSON snippet that you add to the agent's settings file.

### Core Server Command

All configurations use the same underlying command:

```
python -m litex_verify --workspace /path/to/your/workspace
```

Replace `/path/to/your/workspace` with the absolute path to the directory that will contain your LiteX projects.

---

### 4.1 Cursor

Cursor has first-class MCP support since Cursor 0.40+. Add LiteXVerify to Cursor's MCP server list using one of these methods.

#### Method A — Project-Level Configuration (recommended)

Create or edit `.cursor/mcp.json` in your workspace root:

```json
{
  "mcpServers": {
    "litex_verify": {
      "command": "python",
      "args": [
        "-m", "litex_verify",
        "--workspace", "/path/to/your/workspace",
        "--log-level", "INFO"
      ],
      "env": {
        "LITEX_PATH": "/path/to/litex_workspace/litex",
        "PATH": "/usr/local/bin:/usr/bin:/bin:/path/to/eda/tools/bin"
      }
    }
  }
}
```

#### Method B — User-Level Configuration

Open **Cursor Settings → MCP** and paste:

```json
{
  "litex_verify": {
    "command": "python",
    "args": ["-m", "litex_verify", "--workspace", "/path/to/your/workspace"],
    "env": {
      "LITEX_PATH": "/path/to/litex_workspace/litex"
    }
  }
}
```

#### Verifying in Cursor

1. Open the **Cursor Chat** panel (Cmd/Ctrl+L).
2. Type: `What MCP tools are available?`
3. Cursor will list all 11 LiteXVerify tools if the server is running correctly.

---

### 4.2 VS Code with Cline

The [Cline](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev) extension (formerly Claude Dev) supports MCP servers through its settings panel.

#### Step 1 — Install the Cline Extension

Search for **Cline** in the VS Code Extensions marketplace and install it.

#### Step 2 — Add the MCP Server

Open the Cline sidebar panel, navigate to **MCP Servers → Edit MCP Settings**, and add the following to `cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "litex_verify": {
      "command": "python",
      "args": [
        "-m", "litex_verify",
        "--workspace", "/path/to/your/workspace"
      ],
      "env": {
        "LITEX_PATH": "/path/to/litex_workspace/litex",
        "PATH": "/usr/local/bin:/usr/bin:/bin:/path/to/eda/tools/bin"
      },
      "disabled": false,
      "autoApprove": [
        "project_init",
        "tool_discover",
        "config_validate",
        "workflow_state",
        "report_parse",
        "coverage_analyze",
        "report_generate"
      ]
    }
  }
}
```

> **Tip:** The `autoApprove` list lets Cline invoke read-only and non-destructive tools without prompting you for confirmation each time. Tools that write files (`config_create`, `rtl_generate`, `tb_generate`, `sim_run`) are intentionally excluded from auto-approval so you stay in control.

#### Step 3 — Restart Cline

Click the **Reconnect** button in the MCP Servers panel or reload the VS Code window (Ctrl+Shift+P → `Developer: Reload Window`).

---

### 4.3 OpenCode

[OpenCode](https://opencode.ai) is a terminal-first AI coding assistant with native MCP support.

#### Configuration File Location

The MCP configuration lives in your project's `.opencode/` directory or your global OpenCode config:

```
# Project-level (preferred)
<workspace>/.opencode/mcp.json

# Global
~/.config/opencode/mcp.json
```

#### Configuration Content

```json
{
  "mcpServers": {
    "litex_verify": {
      "command": "python",
      "args": [
        "-m", "litex_verify",
        "--workspace", "/path/to/your/workspace"
      ],
      "env": {
        "LITEX_PATH": "/path/to/litex_workspace/litex",
        "PATH": "/usr/local/bin:/usr/bin:/bin"
      }
    }
  }
}
```

#### The `.opencode/rules/` Directory

LiteXVerify ships with OpenCode-compatible rule files in `.opencode/rules/`. These teach OpenCode the conventions for this project:

| File | Purpose |
|------|---------|
| `architecture.md` | Explains the MCP server architecture |
| `project-conventions.md` | Naming and file structure conventions |
| `testing.md` | Testing approach and pytest usage |

These are loaded automatically when you open the workspace in OpenCode.

---

### 4.4 OpenAI Codex / Claude CLI

Both the OpenAI Codex CLI and Anthropic's Claude Code CLI support MCP servers through a `--mcp-config` flag or a config file.

#### Using a Config File

Create `~/.config/codex/mcp.json` (Codex) or `~/.config/claude/mcp.json` (Claude):

```json
{
  "mcpServers": {
    "litex_verify": {
      "command": "python",
      "args": [
        "-m", "litex_verify",
        "--workspace", "/path/to/your/workspace"
      ],
      "env": {
        "LITEX_PATH": "/path/to/litex_workspace/litex"
      }
    }
  }
}
```

#### Passing Config Inline

```bash
# Codex CLI
codex --mcp-config ./litex_mcp.json "Initialize a new LiteX SoC project"

# Claude Code CLI
claude --mcp-config ./litex_mcp.json "Initialize a new LiteX SoC project"
```

---

## 5. Environment Configuration

### 5.1 EDA Tool Setup

LiteXVerify uses the `tool_discover` tool to auto-detect simulators by looking for them on the system `PATH`. The simplest approach is to ensure your EDA tools are available before launching the server.

#### Linux / macOS

Add your EDA tool bin directories to `PATH` in your shell profile (`~/.bashrc`, `~/.zshrc`):

```bash
# Verilator (usually installed via package manager)
# apt install verilator  OR  brew install verilator

# Questa (commercial)
export PATH=$PATH:/opt/questasim/bin

# Synopsys VCS (commercial)
export PATH=$PATH:/opt/synopsys/vcs/bin
source /opt/synopsys/vcs/bin/setup.sh

# Vivado
source /opt/Xilinx/Vivado/2023.2/settings64.sh
```

Then reload your shell:

```bash
source ~/.bashrc
```

#### Windows (WSL2)

Run all commands inside your WSL2 terminal. Add EDA tool paths to `~/.bashrc` inside WSL as shown above. When configuring the AI agent on Windows, use the WSL path prefix:

```json
"command": "wsl",
"args": ["python", "-m", "litex_verify", "--workspace", "/home/<user>/litex_workspace"]
```

#### Passing the PATH via the Agent Config

If you do not want to modify your shell profile system-wide, pass the EDA tool directories through the `env.PATH` key in the MCP server config:

```json
"env": {
  "PATH": "/usr/local/bin:/usr/bin:/bin:/opt/questasim/bin:/opt/synopsys/vcs/bin"
}
```

#### Verifying Tool Detection

Ask your AI agent:

```
Run tool_discover to check what EDA tools are available.
```

A successful response looks like:

```json
{
  "tools": {
    "verilator": { "version": "5.006", "path": "/usr/bin/verilator", "tier": 1 },
    "questa": { "version": "2023.1", "path": "/opt/questasim/bin/vsim", "tier": 2 }
  },
  "verification_tier": 2,
  "capabilities": ["simulation", "coverage", "uvm", "debug"]
}
```

---

### 5.2 LiteX Framework Path

LiteXVerify invokes LiteX as a Python library. As long as LiteX is installed in the same Python environment (virtual env or system Python), it will be found automatically.

If you use a virtual environment, **activate it before launching the server or the AI agent**:

```bash
source ~/litex_venv/bin/activate
python -m litex_verify --workspace ~/litex_workspace
```

To confirm LiteX is importable:

```bash
python -c "import litex; print(litex.__version__)"
```

You can also pass `LITEX_PATH` as an env variable in the MCP config to point to a non-default location. LiteXVerify will add that directory to `sys.path` at startup.

---

### 5.3 Workspace Layout

LiteXVerify organizes all work under a single workspace directory. Each project lives in its own subdirectory:

```
~/litex_workspace/
├── litex/                  ← LiteX framework clone
├── my_soc/                 ← Your first project (created by project_init)
│   ├── .litex_verify/
│   │   └── state.json      ← Workflow state (auto-managed)
│   ├── rtl/
│   │   └── src/            ← Generated Verilog files
│   ├── tb/
│   │   ├── unit/           ← Unit testbenches
│   │   └── regression/
│   ├── sim/
│   │   └── questa/         ← Simulation run artifacts
│   ├── logs/
│   │   └── sim/            ← Simulation logs
│   ├── reports/            ← Generated HTML/Markdown reports
│   └── build/              ← LiteX build artifacts
└── another_project/
```

You do not need to create this structure manually — `project_init` does it for you.

---

## 6. Generating a LiteX SoC

This section walks through the complete SoC creation workflow from a blank slate to synthesizable RTL.

### 6.1 Initializing a Project

Tell your AI agent to initialize a project. Natural language examples:

```
Initialize a new LiteX verification project called "uart_soc" in my workspace.
```

```
Create a new project called "ethernet_fpga" using the full template.
```

Behind the scenes, the agent calls `project_init` with:

```json
{
  "project_name": "uart_soc",
  "template": "standard"
}
```

**Available templates:**

| Template | Description |
|----------|-------------|
| `minimal` | Bare-bones structure (rtl/, tb/, logs/) |
| `standard` | Full structure with scripts, reports, docs directories |
| `full` | Standard + pre-populated script templates for all supported tools |

After initialization, the agent reports:
- The absolute path to your project
- Which EDA tools were detected and at what tier
- Suggested next steps

The workflow advances to **State S1 (Configuration)** automatically.

---

### 6.2 Describing Your SoC in Natural Language

With the project initialized, describe the SoC you want to build. Be as specific as you like:

**Minimal SoC:**
```
Create a VexRiscv SoC with a single UART peripheral running at 100 MHz.
```

**Full-featured SoC:**
```
Create a LiteX SoC with:
- VexRiscv CPU (full variant with FPU)
- Wishbone bus at 100 MHz
- UART at base address 0x82000000
- SPI flash controller at 0x82100000
- GPIO (32 pins) at 0x82200000
- 256KB SRAM
- I2C bus at 0x82300000
```

The agent calls `config_create` and stores a validated JSON configuration file in your project. The configuration includes:

- CPU type and variant
- Bus standard (Wishbone / AXI / AXI-Lite)
- System clock frequency
- Memory type and size
- Peripheral list with base addresses (auto-allocated if not specified)

**Supported CPU types:** `vexriscv`, `picorv32`, `minerva`, `none` (no CPU, peripheral-only SoC)

**Supported peripherals:** `uart`, `spi`, `i2c`, `gpio`, `timer`, `ethernet`, `custom`

---

### 6.3 Validating the Configuration

Before generating RTL, validate the configuration to catch design rule violations:

```
Validate the SoC configuration.
```

or

```
Run a strict validation on the current config.
```

The agent calls `config_validate` and reports:

| Check | ID | Severity |
|-------|----|---------|
| No overlapping memory addresses | ADDR-001 | Error |
| Addresses aligned to peripheral requirements | ADDR-002 | Error |
| Clock frequency within peripheral limits | CLK-001 | Error |
| CDC paths identified for multi-clock | CLK-002 | Warning |
| Bus width compatibility | BUS-001 | Error |
| BRAM usage estimate within device limits | RSC-001 | Warning |

If errors are found, the agent will describe each violation and suggest how to fix it. You can ask it to fix them automatically:

```
Fix all address alignment errors in the config.
```

---

### 6.4 Generating RTL

Once validation passes, generate the RTL:

```
Generate RTL from the current SoC configuration.
```

```
Generate Verilog RTL and run lint checks.
```

The agent calls `rtl_generate`. This step:

1. Invokes LiteX to build the SoC and export Verilog/VHDL
2. Runs lint analysis on the generated files
3. Extracts module hierarchy and interface signals
4. Identifies CSR (Control and Status Register) definitions for RAL model generation
5. Stores interface metadata for testbench generation

The workflow advances to **State S2 (RTL Generation)** and then **State S3 (TB Generation)**.

**Sample agent output:**
```
RTL generation complete.
Top module: soc_top
Generated files:
  - rtl/src/soc_top.v
  - rtl/src/vexriscv_cpu.v
  - rtl/include/csr.vh

Lint: 0 errors, 2 warnings (INFO: undriven signal in debug module)
```

---

## 7. Generating the Verification Platform

### 7.1 Choosing a Framework

LiteXVerify supports two testbench frameworks. The choice is made automatically based on your verification tier, but you can override it:

| Framework | Tier Required | Language | Best For |
|-----------|--------------|----------|---------|
| **cocotb** | Tier 1+ | Python | Fast setup, Python-native tests, CI-friendly |
| **UVM** | Tier 2+ | SystemVerilog | Full methodology, reusable agents, functional coverage |

If you have Questa or VCS installed (Tier 2), UVM is the default. With only Verilator or Icarus (Tier 1), cocotb is used automatically.

---

### 7.2 Generating a UVM Testbench

```
Generate a UVM testbench for the current SoC design.
```

```
Generate a complete UVM environment including RAL model and sanity tests.
```

The agent calls `tb_generate` with `framework: "uvm"` and produces:

```
tb/
├── top_tb.sv               ← Top-level testbench with DUT instantiation
├── env.sv                  ← UVM environment
├── wishbone_agent/
│   ├── wishbone_agent.sv
│   ├── wishbone_driver.sv
│   ├── wishbone_monitor.sv
│   ├── wishbone_sequencer.sv
│   ├── wishbone_seq_item.sv
│   ├── wishbone_interface.sv
│   └── wishbone_agent_pkg.sv
├── ral_model.sv            ← Register Abstraction Layer (auto-generated from CSRs)
├── sequences/
│   ├── base_sequence.sv
│   └── reg_access_seq.sv
└── tests/
    ├── test_base.sv
    ├── test_sanity.sv
    └── test_register_access.sv
```

**Requesting specific components:**

```
Generate only the UVM agent for the UART interface.
```

```
Generate the UVM testbench but skip the RAL model.
```

**Generated test types:**

| Test | Description |
|------|-------------|
| `sanity` | Basic reset and bus connectivity check |
| `register` | Reads/writes all CSRs via RAL model |
| `random` | Randomized stimulus for coverage exploration |

---

### 7.3 Generating a cocotb Testbench

```
Generate a cocotb testbench for the SoC.
```

The agent produces:

```
tb/
├── test_soc_sanity.py      ← Basic connectivity test
├── test_uart.py            ← UART-specific tests
├── tb_utils.py             ← BFM helpers and common utilities
└── Makefile                ← Verilator/Icarus build file
```

cocotb tests use Python `async/await` syntax. The generated files are immediately runnable:

```bash
cd tb/
make SIM=verilator
```

---

## 8. Running Verification

### 8.1 Starting a Full Regression

```
Run the full regression suite.
```

```
Run all tests with coverage enabled.
```

The agent calls `sim_run` with default parameters. It:

1. Compiles the RTL and testbench for your simulator
2. Runs every test in the test list sequentially (or in parallel if configured)
3. Collects code, functional, toggle, and FSM coverage per test
4. Saves logs to `logs/sim/` and coverage databases to `sim/<tool>/`

**Progress reporting:** The agent will report a live status as tests complete:

```
Running regression (12 tests)...
  ✓ test_sanity          [1.2s]
  ✓ test_register_access [4.7s]
  ✗ test_uart_rx_timeout [2.1s] FAILED
  ✓ test_gpio_toggle     [0.9s]
  ...
Summary: 11 passed, 1 failed
```

---

### 8.2 Running Targeted Tests

```
Run only the UART tests.
```

```
Re-run the failed test from the last run with seed 42.
```

```
Run tests test_sanity and test_register_access with high verbosity.
```

The agent maps these requests to `sim_run` parameters:

```json
{
  "tests": ["test_uart_tx", "test_uart_rx"],
  "seed": 42,
  "verbosity": "high",
  "coverage": true
}
```

**Simulator override:** If you need to use a specific simulator instead of the auto-detected one:

```
Run the regression using Synopsys VCS.
```

---

### 8.3 Enabling Waveform Dumps

```
Run the failing UART test with waveform capture enabled.
```

The agent calls `sim_run` with `waves: true`. The waveform file path is included in the response:

```json
{
  "wave_file": "sim/questa/test_uart_rx/vsim.vcd"
}
```

Open the waveform in your preferred viewer:

```bash
# GTKWave (free)
gtkwave sim/questa/test_uart_rx/vsim.vcd

# Questa GUI
vsim -view sim/questa/test_uart_rx/vsim.wlf
```

---

## 9. Analyzing Results

### 9.1 Parsing Simulation Logs

After a run, ask the agent to extract the key information:

```
Parse the simulation logs from the last run.
```

```
What errors occurred in the last regression?
```

The agent calls `report_parse` and presents:

- Pass / fail / error / timeout counts
- Full per-test result table
- Extracted UVM severity counts (FATAL, ERROR, WARNING, INFO)
- Error messages with surrounding context (not just bare log lines)

**Example output:**

```
Simulation run: run_20260512_183045
  Passed:  11 / 12
  Failed:   1 / 12
  Errors:   0

Failed test: test_uart_rx_timeout
  [1800ns] UVM_ERROR @ test_uart_rx_timeout.sv:88
  Expected response within 500ns timeout, got none.
  Recovery hint: Check UART baud rate divider in CSR.
```

---

### 9.2 Analyzing Coverage

```
Analyze coverage across all runs.
```

```
Show me the coverage holes and how to fix them.
```

```
Check if we meet the 90% coverage threshold.
```

The agent calls `coverage_analyze` and reports:

```
Overall coverage: 84.3%  (target: 90%)
⚠ Threshold not met.

Coverage breakdown:
  Code coverage:       88.1%
  Functional coverage: 79.4%
  Toggle coverage:     91.2%
  FSM coverage:        72.0%

Top coverage holes:
  ① uart0.rx_fifo_overflow_flag — never toggled
     Suggestion: Add test_uart_rx_overflow to exercise FIFO full condition

  ② SoC FSM state SLEEP — never entered
     Suggestion: Send WFI instruction sequence via CPU test
```

---

### 9.3 Generating Reports

```
Generate an HTML verification report.
```

```
Create a Markdown report for the project wiki.
```

```
Generate a full report with coverage trends and recommendations.
```

The agent calls `report_generate`. Available formats:

| Format | Use Case |
|--------|---------|
| `html` | Standalone browser-viewable report with charts |
| `markdown` | GitHub / Confluence / wiki embedding |
| `json` | Machine-readable for CI dashboards |

The report includes:

- **Executive Summary** — One-line status, coverage number, pass rate
- **Test Results** — Full per-test table with duration and seed
- **Coverage Summary** — Metrics by type and by RTL module
- **Coverage Holes** — Uncovered items with suggested tests
- **Regression History** — Coverage trend across recent runs
- **Recommendations** — AI-generated next steps

Open the HTML report:

```bash
xdg-open reports/verification_report_20260512.html   # Linux
open reports/verification_report_20260512.html        # macOS
```

---

### 9.4 Coverage Closure Loop

When coverage is below target, use the built-in workflow prompt to run the closure loop automatically:

```
Start the coverage closure workflow.
```

This activates the `workflow://coverage_closure` guided sequence:

1. **Analyze** — Identify the top coverage holes
2. **Generate** — Create targeted tests for each hole
3. **Run** — Execute the new tests (incrementally, not full regression)
4. **Re-analyze** — Check if holes are now covered
5. **Repeat** — Until threshold is met or no further progress

You can also drive this loop manually:

```
We're at 84% coverage and need 90%. Generate tests to cover the UART RX overflow and FSM SLEEP state holes.
```

```
Run the new tests I just added without re-running the full regression.
```

```
Re-analyze coverage and tell me if we now meet the 90% threshold.
```

---

## 10. Workflow State Machine

LiteXVerify tracks every project through a structured workflow state machine to prevent invalid operations (e.g., running a simulation before RTL exists).

```
START
  │
  ▼
S0 — Init & Discovery
  │   (tool_discover runs automatically)
  ▼
S1 — Config Validation
  │   (config_create + config_validate)
  ▼
S2 — RTL Generation
  │   (rtl_generate + lint)
  ▼
S3 — Testbench Generation
  │   (tb_generate)
  ▼
S4 — Simulation
  │   (sim_run)
  ▼
S5 — Analysis
  │   (report_parse + coverage_analyze)
  ▼
S6 — Reporting
  │   (report_generate)
  ├──► DONE   (coverage met, all tests pass)
  └──► S4     (iterate: coverage gaps found)
```

### Checking the Current State

```
What is the current workflow state?
```

The agent calls `workflow_state` with `action: "get"` and returns the current state, available transitions, and recent history.

### Forcing a State Transition

In normal operation you should never need to force a transition. If you need to restart from a specific point (e.g., your RTL changed outside of LiteXVerify):

```
Force the workflow back to S2 so I can regenerate the RTL.
```

The agent calls `workflow_state` with `action: "transition"` and `force: true`.

### Resetting a Project

```
Reset the project state back to the beginning.
```

This returns to S0 and clears all run history. Use with caution.

---

## 11. MCP Tools Reference

All tools are available from within your AI agent using natural language. This table provides the precise tool names and key parameters for reference.

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `project_init` | Create a new verification project | `project_name`, `target_dir`, `template` |
| `tool_discover` | Detect installed EDA tools and set verification tier | `force_rescan` |
| `config_create` | Create or update the SoC configuration | `cpu`, `bus_standard`, `clock_freq`, `peripherals`, `memory` |
| `config_validate` | Run design rule checks on the config | `config_path`, `check_level` |
| `rtl_generate` | Generate RTL from the LiteX configuration | `output_format`, `output_dir`, `run_lint` |
| `tb_generate` | Generate UVM or cocotb testbench | `framework`, `components`, `include_ral`, `test_templates` |
| `sim_run` | Compile and run simulation | `tests`, `simulator`, `seed`, `timeout`, `coverage`, `waves`, `verbosity` |
| `report_parse` | Extract structured results from simulation logs | `run_id`, `log_path` |
| `coverage_analyze` | Aggregate and analyze coverage metrics | `run_ids`, `coverage_types`, `threshold` |
| `report_generate` | Generate HTML/Markdown/JSON report | `format`, `include_sections`, `output_path` |
| `workflow_state` | Query or transition the workflow state | `action` (`get` / `transition` / `reset`), `target_state`, `force` |

---

## 12. MCP Resources Reference

Resources are read-only data served by LiteXVerify. Your agent can read these at any time to inspect templates, scripts, or project state.

### Template Resources

| URI | Content |
|-----|---------|
| `templates://uvm/agent` | UVM agent template (Jinja2/SystemVerilog) |
| `templates://uvm/env` | UVM environment template |
| `templates://uvm/test` | UVM base test template |
| `templates://uvm/sequence` | UVM base sequence template |
| `templates://cocotb/test` | cocotb test module template |
| `templates://cocotb/bfm` | cocotb Bus Functional Model template |

### Script Resources

| URI | Content |
|-----|---------|
| `scripts://questa/compile.do` | Questa compile script |
| `scripts://questa/run.do` | Questa simulation run script |
| `scripts://vcs/compile.sh` | VCS compile script |
| `scripts://vcs/run.sh` | VCS simulation run script |
| `scripts://vcs/coverage.sh` | VCS coverage merge script |
| `scripts://verilator/Makefile` | Verilator build Makefile |
| `scripts://vivado/synth.tcl` | Vivado synthesis TCL script |

### Project State Resources

| URI | Content |
|-----|---------|
| `project://state` | Current workflow state, detected tools, and project metadata |
| `project://config` | Active SoC JSON configuration |
| `project://runs` | Simulation run history with pass/fail/coverage |

---

## 13. Verification Tiers

LiteXVerify automatically selects the richest workflow available based on the tools it detects.

### Tier 1 — Basic Functional Verification

**Detected tools:** Verilator and/or Icarus Verilog  
**Testbench framework:** cocotb (Python)  
**Coverage types:** Line coverage (Verilator), toggle coverage  
**Typical use:** Open-source FPGA development, students, CI pipelines  

```
What you get:
  ✓ RTL generation and lint
  ✓ Python-native cocotb tests
  ✓ Basic functional coverage
  ✗ UVM methodology
  ✗ Functional coverage groups
  ✗ FPGA-in-the-loop
```

### Tier 2 — Full UVM Verification

**Detected tools:** Questa 2021+ or Synopsys VCS 2021+  
**Testbench framework:** UVM 1.2 (SystemVerilog)  
**Coverage types:** Code, functional, toggle, FSM, branch  
**Typical use:** ASIC tape-out, commercial FPGA signoff  

```
What you get:
  ✓ Everything from Tier 1
  ✓ Auto-generated UVM environments
  ✓ Register Abstraction Layer (RAL)
  ✓ Functional coverage groups
  ✓ Full coverage merging across runs
  ✓ Debug waveforms
  ✗ FPGA-in-the-loop
```

### Tier 3 — FPGA-in-the-Loop

**Detected tools:** Vivado 2020+  
**Additional capability:** Synthesize and implement the SoC for hardware-connected test  
**Typical use:** Board bring-up acceleration, hardware validation  

```
What you get:
  ✓ Everything from Tier 1 and 2
  ✓ Vivado synthesis and implementation
  ✓ Bitstream generation scripts
  ✓ FPGA-in-the-loop test capability
```

---

## 14. Troubleshooting

### The server does not start

**Symptom:** Agent reports the MCP server is not responding or tool list is empty.

**Checks:**
1. Run `python -m litex_verify --help` in a terminal — if this fails, your Python environment is wrong.
2. Confirm `litex` is importable: `python -c "import litex"` — if it fails, LiteX is not installed.
3. Check the `command` path in your MCP config points to the correct Python executable.
4. On Windows, ensure you are using WSL2 and the `wsl python` invocation.

---

### Tool discover finds no tools

**Symptom:** `tool_discover` returns an empty tools map and `verification_tier: 0`.

**Fix:** Ensure your EDA tools are on the `PATH` that the MCP server process sees. The server does not inherit your interactive shell profile automatically. Add the `env.PATH` key to your MCP config as described in [Section 5.1](#51-eda-tool-setup).

```json
"env": {
  "PATH": "/usr/local/bin:/usr/bin:/bin:/opt/questasim/bin"
}
```

---

### RTL generation fails

**Symptom:** `rtl_generate` returns an error with code 3001.

**Checks:**
1. Run `config_validate` first — RTL generation requires a valid configuration.
2. Confirm LiteX is importable in the server's Python environment.
3. Check that the `target_dir` has write permission.
4. Look at the full error `details` field for the underlying Python traceback.

---

### UVM testbench generation fails

**Symptom:** `tb_generate` fails with code 4001 or `framework: "uvm"` is not available.

**Fix:** UVM requires Tier 2 tools (Questa or VCS). If `tool_discover` only found Tier 1 tools, use `framework: "cocotb"` or install a Tier 2 simulator.

---

### Simulation hangs or times out

**Symptom:** `sim_run` returns code 5002 (timeout).

**Fix:** Increase the per-test timeout:
```
Run the regression with a 600 second timeout per test.
```
Or ask the agent to investigate the hang:
```
The simulation hung. Parse the partial log and tell me what happened.
```

---

### Coverage stays below threshold despite passing tests

**Symptom:** `coverage_analyze` reports `meets_threshold: false` even after many runs.

**Checks:**
1. Ensure coverage collection was enabled: `sim_run` must be called with `coverage: true` (the default).
2. The coverage database path must exist — check `sim/<tool>/` subdirectory.
3. Ask for specific holes and generate targeted tests as described in [Section 9.4](#94-coverage-closure-loop).

---

### Workflow state is stuck or wrong

**Symptom:** A tool fails with "Tool cannot execute in current state".

**Fix:** Check the current state and either proceed normally or force a transition:
```
What is the current workflow state and what transitions are available?
```
```
Force the workflow state back to S1 so I can recreate the configuration.
```

---

## 15. Glossary

| Term | Definition |
|------|------------|
| **MCP** | Model Context Protocol — open standard for connecting AI agents to tools via JSON-RPC over stdio |
| **LiteX** | Open-source Python SoC builder framework by enjoy-digital |
| **SoC** | System on Chip — an integrated circuit containing a processor, memory, and peripherals |
| **RTL** | Register Transfer Level — hardware description at the level of registers and logic operations |
| **UVM** | Universal Verification Methodology — IEEE 1800.2 standard verification methodology for SystemVerilog |
| **cocotb** | Coroutine-based Co-simulation Test Bench — Python framework for hardware verification |
| **RAL** | Register Abstraction Layer — UVM component for abstract register access |
| **BFM** | Bus Functional Model — behavioral model of a bus protocol |
| **CSR** | Control and Status Register — memory-mapped register for hardware configuration |
| **EDA** | Electronic Design Automation — software tools for IC design |
| **CDC** | Clock Domain Crossing — signal paths that cross between different clock domains |
| **DRC** | Design Rule Check — automated check of design against manufacturing or logical rules |
| **FSM** | Finite State Machine — sequential logic circuit with defined states and transitions |
| **Verification Tier** | Capability level determined by available EDA tools (1=basic, 2=UVM, 3=FPGA) |
| **Workspace** | Root directory that contains all LiteXVerify projects |

---

*End of LiteXVerify User Manual*

---

**Feedback and Issues:** [GitHub Issues](https://github.com/<org>/litex_verify/issues)  
**Source Code:** [GitHub Repository](https://github.com/<org>/litex_verify)  
**MCP Protocol:** [modelcontextprotocol.io](https://modelcontextprotocol.io)  
**LiteX Framework:** [github.com/enjoy-digital/litex](https://github.com/enjoy-digital/litex)
