"""list_followers tool – GET /users/{username}/followers"""

from __future__ import annotations
import os
from pydantic import BaseModel, Field
from llama_index.core.tools import FunctionTool
from mcp_tools.common import github_request

class ListFollowersInput(BaseModel):
    page: int | None = Field(None, ge=1)
    perPage: int | None = Field(None, ge=1, le=100)

def _list_followers(*, page=None, perPage=None):
    # Always use the authenticated user's username
    username = os.getenv("GITHUB_USERNAME")
    if not username:
        raise RuntimeError("GITHUB_USERNAME env-var required.")
    params = {}
    if page:    params["page"]     = page
    if perPage: params["per_page"] = perPage
    return github_request("GET", f"/users/{username}/followers", params=params)

list_followers_tool = FunctionTool.from_defaults(
    fn=_list_followers,
    name="list_followers",
    description="List followers of the authenticated user only",
    # input_type=ListFollowersInput,
)

__all__ = ["list_followers_tool"]
