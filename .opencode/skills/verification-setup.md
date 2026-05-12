# Skill: Verification Environment Setup

## When to use
User requests to generate verification environment for an existing SoC configuration.

## Workflow

1. **Analyze SoC Configuration**
   - Call `analyze_soc_config` with:
     - `soc_file_path`: Path to SoC Python file
     - `extract_csr`: true
     - `identify_critical_paths`: true

2. **Extract Requirements**
   From analysis result, identify:
   - Peripherals needing unit tests
   - DMA-capable blocks
   - Interrupt sources
   - Critical timing paths

3. **Generate Verification Files**
   - Call `generate_verification_env` with:
     - `soc_name`: SoC identifier
     - `analysis_result`: JSON from step 1
     - `include_coverage`: true
     - `include_formal`: false (unless requested)

4. **Generated Files**
   ```
   sim/unit/test_<peripheral>.py   (one per peripheral)
   sim/soc/test_bios_boot.py
   sim/soc/test_all_peripherals.py
   sim/Makefile
   tb/assertions/csr_check.sv
   coverage/coverage_plan.md
   ```

5. **Build Gateware**
   - Call `build_gateware` with:
     - `soc_name`: SoC identifier
     - `platform`: Target board
     - `build_bios`: true
     - `gateware_format`: "verilog"

6. **Verify Generation**
   - Check all files exist
   - Validate test syntax (Python compile check)
   - Confirm gateware RTL generated

## Resources
- `litex://sim/templates` — Simulation templates
- `data/sim/` — Local testbench templates
- `build/` — Generated gateware directory

## Output
Return to user:
- List of generated files
- Verification summary (test count, estimated sim time)
- Command to run verification
