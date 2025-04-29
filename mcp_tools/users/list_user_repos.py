"""list_user_repos tool – GET /users/{username}/repos"""

from __future__ import annotations
import os
from pydantic import BaseModel, Field
from llama_index.core.tools import FunctionTool
from mcp_tools.common import github_request

class ListUserReposInput(BaseModel):
    type: str | None = Field(None, description="all, owner, member")
    sort: str | None = Field(None, description="created, updated, pushed, full_name")
    direction: str | None = Field(None, description="asc or desc")
    page: int | None = Field(None, ge=1)
    perPage: int | None = Field(None, ge=1, le=100)

def _list_repos(*, type=None, sort=None,
                 direction=None, page=None, perPage=None):
    # Always use the authenticated user's username
    username = os.getenv("GITHUB_USERNAME")
    if not username:
        raise RuntimeError("GITHUB_USERNAME env-var required.")
    params = {}
    if type:      params["type"]      = type
    if sort:      params["sort"]      = sort
    if direction: params["direction"] = direction
    if page:      params["page"]      = page
    if perPage:   params["per_page"]  = perPage
    return github_request("GET", f"/users/{username}/repos", params=params)

list_user_repos_tool = FunctionTool.from_defaults(
    fn=_list_repos,
    name="list_user_repos",
    description="List repositories owned by the authenticated user only",
    # input_type=ListUserReposInput,
)

__all__ = ["list_user_repos_tool"]
