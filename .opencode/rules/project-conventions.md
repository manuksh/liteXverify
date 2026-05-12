# LiteX MCP Server — Coding Conventions

## Language & Style

- **Python 3.10+** with type hints
- **FastAPI/FastMCP** for MCP server implementation
- **Async-first** where applicable
- No comments unless explaining "why", not "what"

## File Organization

```
mcpserver_litex/
├── server.py           # Main MCP entry point
├── admin.py            # CLI admin utility
├── config.py           # Configuration loading
├── auth/               # Authentication middleware
├── resources/          # MCP resource handlers
├── tools/              # MCP tool implementations
├── data/               # Static templates & configs
└── state/              # Runtime state (gitignored)
```

## Naming Conventions

- **Files**: snake_case (`soc_generator.py`)
- **Classes**: PascalCase (`AuroraSoC`)
- **Functions**: snake_case (`validate_csr_addresses`)
- **Constants**: UPPER_SNAKE_CASE (`MCP_PORT`)
- **Private**: Leading underscore (`_build_parser`)

## Error Handling

- Return structured JSON errors: `{"status": "error", "message": "..."}`
- Use HTTP-style status semantics in tool responses
- Log errors with full stack traces to stderr

## Testing

- Unit tests alongside code (future)
- Simulation evidence required for verification tools
- All tools must return parseable JSON
