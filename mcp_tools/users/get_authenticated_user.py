"""get_authenticated_user tool – GET /user"""

from __future__ import annotations
from llama_index.core.tools import FunctionTool
from mcp_tools.common import github_request

def _me():
    """Return the authenticated account profile (requires GITHUB_TOKEN)."""
    return github_request("GET", "/user")

get_authenticated_user_tool = FunctionTool.from_defaults(
    fn=_me,
    name="get_authenticated_user",
    description="Fetch the profile of the token-owner (login, id, email, etc.)",
    # input_type=None,          # no parameters
    return_direct=True,       # let caller consume directly if desired
)

__all__ = ["get_authenticated_user_tool"]
