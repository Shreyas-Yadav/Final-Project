"""close_issue tool – PATCH /repos/{owner}/{repo}/issues/{number}"""

from __future__ import annotations
import os
from pydantic import BaseModel, Field
from llama_index.core.tools import FunctionTool
from mcp_tools.common import github_request

class CloseIssueInput(BaseModel):
    repo:   str = Field(...)
    number: int = Field(..., ge=1)

def _close_issue(repo, number):
    # Always use the authenticated user's username
    owner = os.getenv("GITHUB_USERNAME")
    if not owner:
        raise RuntimeError("GITHUB_USERNAME env-var required.")
    return github_request("PATCH",
                           f"/repos/{owner}/{repo}/issues/{number}",
                           json={"state": "closed"})

close_issue_tool = FunctionTool.from_defaults(
    fn=_close_issue,
    name="close_issue",
    description="Close (or re-open) an issue in the authenticated user's repository only",
    # input_type=CloseIssueInput,
)

__all__ = ["close_issue_tool"]
