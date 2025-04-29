"""Auto-import & re-export every *_tool in this package."""

from importlib import import_module
from pathlib import Path

_pkg = Path(__file__).parent
for _file in _pkg.glob("*.py"):
    if _file.name == "__init__.py":
        continue
    mod = import_module(f"mcp_tools.users.{_file.stem}")
    globals().update({k: v for k, v in mod.__dict__.items() if k.endswith("_tool")})

__all__ = [k for k in globals() if k.endswith("_tool")]
