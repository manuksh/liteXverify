# LiteX MCP Server — Testing & Verification

## Verification Levels

| Level | Scope | Tools | Evidence |
|-------|-------|-------|----------|
| L0 | CSR Validation | LiteX CSR scanner | `csr_map_valid`, `no_address_conflicts` |
| L1 | Unit Simulation | Verilator | `unit_tests_passed`, `no_verilator_errors` |
| L2 | SoC Simulation | Verilator + BIOS | `bios_boots`, `uart_console_responds` |
| L3 | Synthesis | Vivado/Quartus | `synth_clean`, `resource_utilization_ok` |
| L4 | Timing Closure | Vivado/Quartus STA | `wns_positive`, `all_clocks_constrained` |
| L5 | Hardware | JTAG/UART tests | `hardware_boot_ok`, `peripherals_functional` |

## Tool Commands

### Initialize SoC Project
```bash
python server.py --init_soc --name aurora_soc --board arty_a7_100 --cpu vexriscv
```

### Run Verification
```bash
python server.py --run_sim --soc aurora_soc --level L2
```

### Generate Documentation
```bash
python server.py --gen-csr-doc --soc aurora_soc --format markdown
```

## CI/CD Integration

- Nightly regression runs all SoC configs
- Failures reported via webhook (Slack/Teams)
- Artifacts archived: logs, waveforms, utilization reports

## Coverage Requirements

- **Line**: ≥95%
- **Branch**: ≥90%
- **Toggle**: ≥98%
- **Functional**: ≥95%
