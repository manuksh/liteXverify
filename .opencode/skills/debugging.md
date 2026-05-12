# Skill: Debugging SoC Issues

## When to use
User reports simulation failures, timing violations, or unexpected behavior.

## Workflow

1. **Gather Context**
   - SoC name and current stage
   - Error message or symptom
   - Recent changes (if any)

2. **Fetch Logs**
   - Read simulation logs from `sim/`
   - Check synthesis reports from `build/`
   - Review timing reports if at L3+

3. **Parse Errors**
   - Call `parse_sim_log` with log content
   - Call `parse_utilization_report` for synth issues
   - Call `parse_timing_report` for timing violations

4. **Categorize Issue**

   **Simulation Failures:**
   - Testbench bug → Fix test
   - RTL bug → Update SoC definition
   - Constraint issue → Regenerate constraints

   **Timing Violations:**
   - Unconstrained path → Add constraint
   - Critical path → Pipeline or optimize
   - Clock domain crossing → Add CDC synchronizer

   **Resource Overutilization:**
   - Reduce L2 cache size
   - Remove unused peripherals
   - Optimize interconnect

5. **Apply Fix**
   - Update SoC Python file
   - Regenerate verification env
   - Re-run affected tests

6. **Verify Fix**
   - Re-run simulation/synthesis
   - Confirm issue resolved
   - Ensure no regressions

7. **Document**
   - Add note to `reports/debug_log.md`
   - Update CSR map if registers changed

## Common Issues & Fixes

| Issue | Likely Cause | Fix |
|-------|--------------|-----|
| BIOS boot timeout | DDR calibration failure | Check SDRAM timing params |
| UART no output | Wrong baudrate | Verify `uart_baudrate` in SoC |
| Address conflict | Overlapping CSR regions | Adjust peripheral base addresses |
| WNS negative | Timing path unconstrained | Add false path or pipeline |
| Verilator error | RTL syntax issue | Check custom peripheral RTL |

## Resources
- `litex://csr/schema` — CSR validation rules
- `ask_litex_rag` — Query LiteX documentation
- `state/tenants/<id>/socs/<soc>/status.json` — Current state

## Output
Return to user:
- Root cause analysis
- Applied fix description
- Verification results
- Prevention recommendations
