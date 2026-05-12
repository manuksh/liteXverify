# Skill: SoC Initialization

## When to use
User requests to initialize a new LiteX SoC project or configure SoC topology.

## Workflow

1. **Gather Requirements**
   - Ask for: `soc_name`, `target_board`, `cpu_type`
   - Optional: `cpu_variant`, `interconnect`, `with_ethernet`, `with_sdram`

2. **Call `init_soc` Tool**
   ```json
   {
     "soc_name": "<name>",
     "target_board": "<board>",
     "cpu_type": "<cpu>",
     "cpu_variant": "standard",
     "interconnect": "crossbar",
     "with_ethernet": false,
     "with_sdram": false,
     "l2_size": 8192
   }
   ```

3. **Scaffold Project Structure**
   ```
   socs/<soc_name>.py
   software/
   sim/
   build/
   constraints/
   docs/
   ```

4. **Generate CSR Map**
   - Call `generate_csr_map` with format `markdown`
   - Save to `docs/csr_map.md`

5. **Validate Addresses**
   - Call `validate_csr_addresses`
   - Ensure no conflicts

6. **Update State**
   - Set stage to `L0`
   - Record in `state/tenants/<id>/socs/<soc_name>/status.json`

## Resources
- `litex://soc/templates` — Available SoC templates
- `litex://soc/template/<name>` — Specific template source
- `data/soc_templates/` — Local template files

## Output
Return to user:
- SoC Python class source
- CSR map summary
- Next steps (L0→L1 gate requirements)
