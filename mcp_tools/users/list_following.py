"""list_following tool – GET /users/{username}/following"""

from __future__ import annotations
import os
from pydantic import BaseModel, Field
from llama_index.core.tools import FunctionTool
from mcp_tools.common import github_request

class ListFollowingInput(BaseModel):
    page: int | None = Field(None, ge=1)
    perPage: int | None = Field(None, ge=1, le=100)

def _list_following(*, page=None, perPage=None):
    # Always use the authenticated user's username
    username = os.getenv("GITHUB_USERNAME")
    if not username:
        raise RuntimeError("GITHUB_USERNAME env-var required.")
    params = {}
    if page:    params["page"]     = page
    if perPage: params["per_page"] = perPage
    return github_request("GET", f"/users/{username}/following", params=params)

list_following_tool = FunctionTool.from_defaults(
    fn=_list_following,
    name="list_following",
    description="List accounts the authenticated user is following",
    # input_type=ListFollowingInput,
)

__all__ = ["list_following_tool"]
