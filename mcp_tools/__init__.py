"""Entry-point that aggregates all GitHub MCP **repo** FunctionTools."""

from importlib import import_module
from pathlib import Path

_pkg_path = Path(__file__).parent / "repos"
for _file in _pkg_path.glob("*.py"):
    if _file.name == "__init__.py":
        continue
    import_module(f"mcp_tools.repos.{_file.stem}")

# Re-export every *_tool object for convenience:
from mcp_tools.repos import *  # noqa: F401,F403
