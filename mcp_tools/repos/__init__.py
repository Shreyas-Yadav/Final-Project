# =========================================
# mcp_tools/repos/__init__.py
# =========================================
"""Expose all repo tools for `from mcp_tools.repos import *`."""

from importlib import import_module
from pathlib import Path

_pkg_path = Path(__file__).parent
for _file in _pkg_path.glob("*.py"):
    if _file.name == "__init__.py":
        continue
    mod = import_module(f"mcp_tools.repos.{_file.stem}")
    globals().update({k: v for k, v in mod.__dict__.items() if k.endswith("_tool")})

__all__ = [k for k in globals() if k.endswith("_tool")]

