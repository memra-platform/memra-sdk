# Changelog

All notable changes to the Memra SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.2] - 2025-05-28

### Fixed
- **MCP Integration**: Fixed broken MCP tool execution after repository separation
- **Tool Registry**: Updated MCP tool routing to use correct endpoints
- **Bridge Server**: Added working MCP bridge server implementation
- **Real Work Detection**: Improved detection of real vs mock work for MCP tools

### Added
- Complete MCP bridge server with DataValidator and PostgresInsert tools
- Health check endpoint for MCP bridge monitoring
- Better error handling and fallback for MCP tool execution

### Changed
- MCP tools now perform real database operations instead of mock responses
- Improved logging and debugging for MCP tool execution flow

## [0.2.1] - 2025-05-27

## [0.2.0] - 2024-01-17

### Added
- **MCP (Model Context Protocol) Integration**: Execute operations on local infrastructure while leveraging cloud AI processing
  - New `mcp_bridge_server.py` for local resource bridging
  - HMAC authentication for secure cloud-to-local communication
  - Support for `hosted_by: "mcp"` in agent tool configurations
  - PostgreSQL integration via MCP bridge
  - Tool-level configuration support in execution engine
  - New MCP tools: `PostgresInsert`, `DataValidator`

### Enhanced
- **Execution Engine**: Updated to support tool-level configuration and MCP routing
- **Tool Registry Client**: Enhanced API client with better error handling and MCP support
- **Agent Configuration**: Added support for tool-specific configuration alongside agent-level config

### Examples
- `examples/accounts_payable_mcp.py` - Complete invoice processing with MCP database integration
- `test_mcp_success.py` - Simple MCP integration test

### Documentation
- `docs/mcp_integration.md` - Comprehensive MCP integration guide
- Updated README with MCP overview and quick start

### Dependencies
- Added `aiohttp>=3.8.0` for MCP bridge server
- Added `aiohttp-cors>=0.7.0` for CORS support
- Added `psycopg2-binary>=2.9.0` for PostgreSQL integration

## [0.1.0] - 2024-01-01

### Added
- Initial release of Memra SDK
- Core agent and department framework
- API client for Memra cloud services
- Basic tool registry and execution engine
- Examples for accounts payable and propane delivery workflows 