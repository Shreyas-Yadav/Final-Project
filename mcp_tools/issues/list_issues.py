"""list_issues tool – GET /repos/{owner}/{repo}/issues"""

from __future__ import annotations
import os
from pydantic import BaseModel, Field
from llama_index.core.tools import FunctionTool
from mcp_tools.common import github_request

class ListIssuesInput(BaseModel):
    repo:  str = Field(...)
    state: str | None = Field(None, description="open, closed, all")
    assignee: str | None = Field(None)
    labels: str | None = Field(None, description="CSV list of label names")
    page: int | None = Field(None, ge=1)
    perPage: int | None = Field(None, ge=1, le=100)

def _list_issues(repo, *, state=None, assignee=None,
                  labels=None, page=None, perPage=None):
    # Always use the authenticated user's username
    owner = os.getenv("GITHUB_USERNAME")
    if not owner:
        raise RuntimeError("GITHUB_USERNAME env-var required.")
    params = {}
    if state:    params["state"]    = state
    if assignee: params["assignee"] = assignee
    if labels:   params["labels"]   = labels
    if page:     params["page"]     = page
    if perPage:  params["per_page"] = perPage
    return github_request("GET", f"/repos/{owner}/{repo}/issues", params=params)

list_issues_tool = FunctionTool.from_defaults(
    fn=_list_issues,
    name="list_issues",
    description="List issues in the authenticated user's repository only",
    # input_type=ListIssuesInput,
)

__all__ = ["list_issues_tool"]
