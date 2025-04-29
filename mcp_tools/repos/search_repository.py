from __future__ import annotations
import os
from pydantic import BaseModel, Field
from llama_index.core.tools import FunctionTool
from mcp_tools.common import github_request

class SearchRepositoriesInput(BaseModel):
    query: str = Field(..., description="Search keywords")
    sort: str | None = Field(None)
    order: str | None = Field(None)
    page: int | None = Field(None, ge=1)
    perPage: int | None = Field(None, ge=1, le=100)

def _search_repos(query, *,org = None, sort=None, order=None, page=None, perPage=None):
    username = os.getenv("GITHUB_USERNAME")
    if not username:
        raise RuntimeError("GITHUB_USERNAME env-var required.")
    # Always restrict search to the authenticated user's repositories
    params = {"q": f"{query} user:{username}"}
    if org: params["org"] = org
    if sort: params["sort"] = sort
    if order: params["order"] = order
    if page: params["page"] = page
    if perPage: params["per_page"] = perPage
    return github_request("GET", "/search/repositories", params=params)

search_repositories_tool = FunctionTool.from_defaults(
    fn=_search_repos,
    name="search_repositories",
    description="Search repositories owned by the authenticated user only",
    # input_type=SearchRepositoriesInput,
)

__all__ = ["search_repositories_tool"]
