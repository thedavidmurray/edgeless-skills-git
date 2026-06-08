#!/usr/bin/env python3
"""
MCP Bridge: tradingview
Auto-generated proxy for Hermes skill interface.
"""

import subprocess
import json
import os
from typing import Any, Dict, List

MCP_NAME = "tradingview"
MCP_COMMAND = 'node'
MCP_ARGS = ['/Users/djm/claude-projects/mcp-servers/tradingview-mcp/src/server.js']
MCP_ENV = {}


class TradingviewMCPBridge:
    """Bridge between Hermes skill interface and tradingview MCP server."""
    
    def __init__(self):
        self._tools = None
        self._proc = None
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Lazy-load tools from MCP server."""
        if self._tools is None:
            self._tools = self._fetch_tools()
        return self._tools
    
    def _fetch_tools(self) -> List[Dict[str, Any]]:
        """Fetch tool schema from MCP server via stdio."""
        env = os.environ.copy()
        env.update(MCP_ENV)
        
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "hermes-mcp-bridge", "version": "1.0.0"}
            }
        }
        
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        proc = subprocess.Popen(
            [MCP_COMMAND] + MCP_ARGS,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        
        try:
            # Initialize
            proc.stdin.write(json.dumps(init_request) + "\n")
            proc.stdin.flush()
            # Read init response robustly (skip notifications/initialized)
            for _ in range(10):
                line = proc.stdout.readline()
                if not line:
                    break
                try:
                    msg = json.loads(line)
                    if msg.get("id") == 1:
                        break
                except json.JSONDecodeError:
                    continue
            
            # Get tools
            proc.stdin.write(json.dumps(tools_request) + "\n")
            proc.stdin.flush()
            response = json.loads(proc.stdout.readline())
            
            return response.get("result", {}).get("tools", [])
        finally:
            proc.stdin.close()
            proc.wait(timeout=5)
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool call via MCP."""
        if self._proc is None or self._proc.poll() is not None:
            self._start_session()
        
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        self._proc.stdin.write(json.dumps(request) + "\n")
        self._proc.stdin.flush()
        response = json.loads(self._proc.stdout.readline())
        
        if "error" in response:
            raise RuntimeError(f"Tool call failed: {response['error']}")
        
        return response.get("result", {})
    
    def _start_session(self):
        """Start persistent MCP session for tool calls."""
        env = os.environ.copy()
        env.update(MCP_ENV)
        
        self._proc = subprocess.Popen(
            [MCP_COMMAND] + MCP_ARGS,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        
        # Initialize session
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "hermes-mcp-bridge", "version": "1.0.0"}
            }
        }
        
        self._proc.stdin.write(json.dumps(init_request) + "\n")
        self._proc.stdin.flush()
        # Read init response (some servers send notifications/initialized first, skip those)
        for _ in range(10):
            line = self._proc.stdout.readline()
            if not line:
                break
            try:
                msg = json.loads(line)
                if msg.get("id") == 1:
                    break
            except json.JSONDecodeError:
                continue


# Singleton instance
_bridge = None

def get_bridge():
    """Get or create bridge instance."""
    global _bridge
    if _bridge is None:
        _bridge = TradingviewMCPBridge()
    return _bridge


def list_tools():
    """List available tools (called by skill_view)."""
    return get_bridge().get_tools()


def call_tool(tool_name: str, **kwargs):
    """Call a tool with arguments."""
    return get_bridge().call_tool(tool_name, kwargs)
