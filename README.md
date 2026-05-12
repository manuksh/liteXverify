# LiteXVerify

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Protocol](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

**AI-Assisted Verification Platform for LiteX SoC Designs**

LiteXVerify is a local Model Context Protocol (MCP) server that enables AI coding agents to automate the verification of LiteX-based System-on-Chip designs. It provides natural language interaction for RTL generation, testbench creation, simulation execution, and coverage analysis.

## Key Features

- **Local Execution** - All processing happens on your machine; no cloud dependencies
- **IP Protection** - Design data never leaves your infrastructure
- **Multi-Tool Support** - Works with Verilator, Questa, Synopsys VCS, and Vivado
- **AI Agent Compatible** - Integrates with Cursor, Cline, and OpenCode
- **Tiered Verification** - Adapts to available EDA tools automatically

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Git
- At least one simulator:
  - **Tier 1 (Basic):** Verilator or Icarus Verilog
  - **Tier 2 (UVM):** Questa or Synopsys VCS
  - **Tier 3 (FPGA):** Vivado

### Installation

```bash
# Create workspace
mkdir litex_workspace && cd litex_workspace

# Clone LiteX framework
git clone https://github.com/enjoy-digital/litex.git
cd litex && pip install -e . && cd ..
python litex/litex_setup.py --init --install

# Clone LiteXVerify
git clone https://github.com/<org>/litex_verify.git
cd litex_verify && pip install -e . && cd ..
```

### Configure Your AI Agent

**For Cursor/Cline** (`.vscode/mcp.json`):

```json
{
  "mcpServers": {
    "litex_verify": {
      "command": "python",
      "args": ["-m", "litex_verify.server"],
      "cwd": "/path/to/litex_verify"
    }
  }
}
```

**For OpenCode** (`.opencode/mcp.json`):

```json
{
  "mcpServers": {
    "litex_verify": {
      "command": "python",
      "args": ["-m", "litex_verify.server"],
      "cwd": "/path/to/litex_verify"
    }
  }
}
```

## Usage Examples

Once configured, interact with LiteXVerify through natural language:

```
"Initialize a new LiteX project called my_soc"

"Create a VexRiscv SoC with UART, SPI, and 64KB SRAM"

"Generate RTL and run lint checks"

"Generate a UVM testbench for my design"

"Run the full regression suite"

"Show me the coverage report"
```

## Architecture

```
┌─────────────────┐     stdio/JSON-RPC     ┌──────────────────┐
│    AI Agent     │◄──────────────────────►│   LiteXVerify    │
│ (Cursor/Cline)  │                        │   MCP Server     │
└─────────────────┘                        └────────┬─────────┘
                                                    │
                    ┌───────────────────────────────┼───────────────┐
                    │                               │               │
                    ▼                               ▼               ▼
             ┌─────────────┐              ┌─────────────┐   ┌─────────────┐
             │   LiteX     │              │  EDA Tools  │   │  Workspace  │
             │  Framework  │              │             │   │  (Projects) │
             └─────────────┘              └─────────────┘   └─────────────┘
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `project_init` | Initialize new verification project |
| `tool_discover` | Detect available EDA tools |
| `config_create` | Create SoC configuration |
| `config_validate` | Validate configuration against design rules |
| `rtl_generate` | Generate RTL from LiteX configuration |
| `tb_generate` | Generate UVM or cocotb testbench |
| `sim_run` | Execute simulation regression |
| `report_parse` | Parse simulation logs |
| `coverage_analyze` | Analyze coverage metrics |
| `report_generate` | Generate verification reports |
| `workflow_state` | Query or transition workflow state |

## Verification Workflow

```
S0 (Init) → S1 (Config) → S2 (RTL) → S3 (TB) → S4 (Sim) → S5 (Analysis) → S6 (Report) → DONE
     │           │                                  ▲            │
     │           └──────────────────────────────────┼────────────┘
     │                     (iterate on coverage)    │
     └─────────────────────────────────────────────►ERROR
                          (fail)
```

## Project Structure

```
litex_verify/
├── server.py           # MCP server entry point
├── tools/              # MCP tool implementations
│   ├── project_init.py
│   ├── config.py
│   ├── rtl.py
│   ├── testbench.py
│   ├── simulation.py
│   └── analysis.py
├── resources/          # MCP resources
│   ├── templates/      # UVM/cocotb templates
│   └── scripts/        # EDA tool scripts
├── data/               # Static data
│   └── scaffolds/      # Project scaffolds
└── tests/              # Unit tests
```

## Documentation

| Document | Description |
|----------|-------------|
| [Functional Specification](functional_specification.md) | Complete system specification |
| [Implementation Specification](implementation_specification.md) | Technical implementation details |
| [Initial Idea](initial_idea.md) | Project concept and use model |

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Running the Server Standalone

```bash
python -m litex_verify.server
```

### Adding New Tools

1. Create tool implementation in `tools/`
2. Register in `server.py`
3. Add tests in `tests/`
4. Update documentation

## Verification Tiers

| Tier | Tools | Capabilities |
|------|-------|--------------|
| 1 | Verilator, Icarus | Basic functional simulation, cocotb tests |
| 2 | Questa, Synopsys VCS | Full UVM verification, coverage analysis |
| 3 | Vivado | FPGA-in-the-loop validation |

The server automatically detects available tools and adjusts verification capabilities accordingly.

## Security

- **No Network Access** - Server makes no outbound connections
- **Sandboxed** - Only accesses configured workspace directories
- **No Telemetry** - No usage data collection
- **Auditable** - Open source, all operations logged locally

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [LiteX](https://github.com/enjoy-digital/litex) - The excellent SoC builder framework
- [Model Context Protocol](https://modelcontextprotocol.io/) - AI agent integration standard
- [cocotb](https://www.cocotb.org/) - Python-based verification framework
- [UVM](https://www.accellera.org/activities/working-groups/uvm) - Universal Verification Methodology

## Support

- **Issues**: [GitHub Issues](https://github.com/<org>/litex_verify/issues)
- **Discussions**: [GitHub Discussions](https://github.com/<org>/litex_verify/discussions)

---

**Note**: This project is under active development. APIs may change between versions.
