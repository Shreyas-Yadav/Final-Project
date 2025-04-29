from __future__ import annotations
import os
from pydantic import BaseModel, Field
from llama_index.core.tools import FunctionTool
from mcp_tools.common import github_request

class ListBranchesInput(BaseModel):
    repo:  str = Field(...)
    page: int | None = Field(None, ge=1)
    perPage: int | None = Field(None, ge=1, le=100)

def _list_branches(repo, *, page=None, perPage=None):
    # Always use the authenticated user's username
    owner = os.getenv("GITHUB_USERNAME")
    if not owner:
        raise RuntimeError("GITHUB_USERNAME env-var required.")
    params = {}
    if page:     params["page"]     = page
    if perPage:  params["per_page"] = perPage
    return github_request("GET",
                           f"/repos/{owner}/{repo}/branches", params=params)

list_branches_tool = FunctionTool.from_defaults(
    fn=_list_branches,
    name="list_branches",
    description="List branches in the authenticated user's repository only",
    # input_type=ListBranchesInput,
)

__all__ = ["list_branches_tool"]
