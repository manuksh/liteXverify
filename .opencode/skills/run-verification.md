# Skill: Run Verification

## When to use
User requests to execute verification tests for an SoC.

## Workflow

1. **Check Prerequisites**
   - Verify SoC exists in state
   - Confirm gateware is built
   - Check simulator availability (Verilator/ModelSim/VCS)

2. **Determine Verification Level**
   Based on user request or SoC stage:
   - `unit` — L1 peripheral tests
   - `soc` — L2 full SoC with BIOS
   - `regression` — All tests

3. **Execute Simulation**
   - Call `run_verification` with:
     - `soc_name`: SoC identifier
     - `test_level`: "unit" | "soc" | "regression"
     - `simulator`: "verilator" (default)
     - `coverage`: true
     - `timeout_minutes`: 60

4. **Monitor Progress**
   - Poll for completion
   - Stream logs if available
   - Watch for errors

5. **Parse Results**
   - Call `parse_sim_log` for each test log
   - Extract pass/fail counts
   - Collect coverage metrics

6. **Handle Failures**
   If tests fail:
   - Parse error with `parse_sim_log`
   - Identify root cause (testbench bug, RTL bug, constraint issue)
   - Attempt fix (max 3 retries)
   - Escalate if unresolved

7. **Update State**
   - If all pass and at L0: advance to L1
   - If all pass and at L1: advance to L2
   - Record evidence in status.json

## Evidence Requirements

### L0→L1
```json
{
  "unit_tests_passed": true,
  "no_verilator_errors": true,
  "coverage_threshold_met": true,
  "all_peripherals_tested": true
}
```

### L1→L2
```json
{
  "bios_boots": true,
  "uart_console_responds": true,
  "ddr_calibration_success": true,
  "max_sim_runtime_minutes": 30
}
```

## Resources
- `sim/unit/*.log` — Unit test logs
- `sim/soc/*.log` — SoC simulation logs
- `sim/waveforms/*.vcd` — Waveform files
- `coverage/` — Coverage reports

## Output
Return to user:
- Test summary (passed/failed/skipped)
- Coverage metrics
- Links to logs and waveforms
- Stage advancement status (if applicable)
