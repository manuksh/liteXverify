# LiteX MCP Server — Architecture

## Core Components

### 1. Authentication Layer (`auth/`)

- **ApiKeyMiddleware**: Validates `Authorization: Bearer litex-sk-<key>`
- **ContextVar**: `current_tenant_id` for tenant isolation
- **Store**: SQLite-based tenant/key management

### 2. MCP Server (`server.py`)

- **FastMCP** on port 8003
- **Streamable HTTP** transport at `/mcp`
- **Resources**: Read-only template/config fetching
- **Tools**: State-modifying actions (SoC gen, sim, synthesis)

### 3. SoC Generation Pipeline

```
L0 CSR Def → L1 Unit Sim → L2 SoC Sim → L3 Synthesis → L4 Timing → L5 Hardware
     [HUMAN_GATE]                                              [HUMAN_GATE]
```

### 4. Verification Flow

1. `analyze_soc_config()` — Parse LiteX Python SoC definition
2. `generate_verification_env()` — Auto-create testbenches
3. `build_gateware()` — Generate RTL from LiteX
4. `run_verification()` — Execute sims, collect coverage

## Key Design Patterns

- **Tenant Isolation**: Per-tenant `state/tenants/<id>/socs/` directories
- **Evidence-Gated Stages**: Structured JSON evidence required for stage advancement
- **Self-Correction**: Tools attempt auto-fix before escalation (max 3 retries)
- **RAG Integration**: `ask_litex_rag()` queries LiteX documentation

## Data Flow

```
User (Cline/Cursor)
       │
       ▼ HTTP POST /mcp
ApiKeyMiddleware ──► 401 if invalid
       │
       ▼ (sets tenant context)
server.py (FastMCP)
       │
       ├──► resources/ — fetch templates
       └──► tools/ — execute actions
              │
              ├──► data/ — read templates
              └──► state/ — update SoC status
```
