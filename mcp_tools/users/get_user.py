"""get_user tool – GET /users/{username}"""

from __future__ import annotations
import os
from pydantic import BaseModel, Field
from llama_index.core.tools import FunctionTool
from mcp_tools.common import github_request

# No input needed as we'll always use the authenticated user
class GetUserInput(BaseModel):
    pass

def _get_user():
    # Always use the authenticated user's username
    username = os.getenv("GITHUB_USERNAME")
    if not username:
        raise RuntimeError("GITHUB_USERNAME env-var required.")
    return github_request("GET", f"/users/{username}")

get_user_tool = FunctionTool.from_defaults(
    fn=_get_user,
    name="get_user",
    description="Fetch the authenticated user's profile only",
    # input_type=GetUserInput,
)

__all__ = ["get_user_tool"]
