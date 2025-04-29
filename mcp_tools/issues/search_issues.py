"""search_issues tool – GET /search/issues (scoped to a repo or org)"""

from __future__ import annotations
import os
from pydantic import BaseModel, Field
from llama_index.core.tools import FunctionTool
from mcp_tools.common import github_request

class SearchIssuesInput(BaseModel):
    query: str = Field(..., description="Search keywords")
    repo:  str | None = Field(None, description="owner/name to scope search")
    inTitle: bool | None = Field(False, description="restrict to title text")
    state: str | None = Field(None, description="open, closed")
    page: int | None = Field(None, ge=1)
    perPage: int | None = Field(None, ge=1, le=100)

def _search_issues(query, *, repo=None, inTitle=False,
                    state=None, page=None, perPage=None):
    # Always use the authenticated user's username
    username = os.getenv("GITHUB_USERNAME")
    if not username:
        raise RuntimeError("GITHUB_USERNAME env-var required.")
    
    qs = query
    
    # Always restrict to the authenticated user's repositories
    qs += f" user:{username}"
    
    if repo:
        # If repo is provided, ensure it's in the format "username/repo"
        if "/" not in repo:
            repo = f"{username}/{repo}"
        # Verify that the owner matches the authenticated user
        repo_owner = repo.split("/")[0]
        if repo_owner.lower() != username.lower():
            raise ValueError(f"Cannot access repositories not owned by {username}")
        qs += f" repo:{repo}"
    
    if inTitle:
        qs += " in:title"
    if state:
        qs += f" state:{state}"
    params = {"q": qs}
    if page:    params["page"]     = page
    if perPage: params["per_page"] = perPage
    return github_request("GET", "/search/issues", params=params)

search_issues_tool = FunctionTool.from_defaults(
    fn=_search_issues,
    name="search_issues",
    description="Search issues/pull-requests in the authenticated user's repositories only",
    # input_type=SearchIssuesInput,
)

__all__ = ["search_issues_tool"]
