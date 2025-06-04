# Goose MCP Extension Debug Log

## Problem
Goose is not loading MCP extensions (computer control tools and unstuck visual helper) despite various configuration attempts.

## Environment
- **Goose Version**: Block's Goose (installed via download script)
- **Model**: Claude Opus 4 (`claude-opus-4-20250514`)
- **Container**: Docker Ubuntu 22.04 with VNC
- **MCP Server**: fastmcp available at `/usr/local/bin/fastmcp`

## Attempted Solutions

### ❌ Attempt 1: mcp_servers.json Configuration (FAILED)
**Date**: 2025-06-04  
**Approach**: Used Claude Desktop style `mcp_servers.json` configuration  
**Location**: `~/.config/goose/mcp_servers.json`  
**Result**: Goose didn't load any extensions - showed "no extensions available"  
**Reason**: Block's Goose doesn't use this configuration format

### ❌ Attempt 2: CLI Flags with --with-builtin computer (FAILED)
**Date**: 2025-06-04  
**Approach**: Used CLI flags to load extensions:
```bash
goose session --with-builtin computer --with-extension "fastmcp run /home/goose/mcp_server/unstuck_ai/server.py:mcp --transport stdio"
```
**Result**: Error - "Unknown server requested computer"
**Error Details**:
```
Failed to start builtin extension: Failed to start builtin extension: Failed to start the MCP server from configuration `Builtin(computer)` 
thread 'main' panicked at /home/runner/work/goose/goose/crates/goose-cli/src/commands/mcp.rs:50:55:
Unknown server requested computer
```
**Reason**: `computer` is not a valid built-in extension name for this version of Goose

## Current Status
- ✅ Docker container builds successfully
- ✅ VNC and desktop environment working
- ✅ Unstuck MCP server imports successfully
- ✅ fastmcp available in PATH
- ❌ Goose built-in `computer` extension not available
- ❌ No MCP extensions loading

### 🧪 Attempt 3: Only Unstuck Extension (TESTING)
**Date**: 2025-06-04  
**Approach**: Remove built-in computer extension, load only unstuck:
```bash
goose session --with-extension "fastmcp run /home/goose/mcp_server/unstuck_ai/server.py:mcp --transport stdio"
```
**Status**: Testing now...

## Next Steps to Try
1. ✅ Try loading only the unstuck extension without built-in computer
2. Find valid built-in extension names for Goose  
3. Check if there's a different computer control extension
4. Investigate Goose documentation for proper MCP setup
5. Try alternative computer control methods

## Key Files Modified
- `agents/goose-docker/config/goose_config.yaml` - Updated to Claude Opus 4
- `agents/goose-docker/entrypoint.sh` - Updated model references
- `agents/goose-docker/scripts/goose_api.py` - Changed to use CLI flags
- `agents/goose-docker/Dockerfile` - Fixed MCP config location

## Logs & Evidence
- Container shows: `goose-mcp-server not found in PATH`
- Goose help shows: `--with-builtin <NAME>` option exists
- Error indicates `computer` is not a recognized built-in name