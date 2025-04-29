"""get_issue tool – GET /repos/{owner}/{repo}/issues/{number}"""

from __future__ import annotations
import os
from pydantic import BaseModel, Field
from llama_index.core.tools import FunctionTool
from mcp_tools.common import github_request

class GetIssueInput(BaseModel):
    repo:   str = Field(...)
    number: int = Field(..., ge=1, description="Issue number")

def _get_issue(repo, number):
    # Always use the authenticated user's username
    owner = os.getenv("GITHUB_USERNAME")
    if not owner:
        raise RuntimeError("GITHUB_USERNAME env-var required.")
    return github_request("GET", f"/repos/{owner}/{repo}/issues/{number}")

get_issue_tool = FunctionTool.from_defaults(
    fn=_get_issue,
    name="get_issue",
    description="Retrieve a single issue by number from the authenticated user's repository only",
    # input_type=GetIssueInput,
)

__all__ = ["get_issue_tool"]
