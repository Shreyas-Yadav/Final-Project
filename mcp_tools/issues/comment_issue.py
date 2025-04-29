"""comment_issue tool – POST /repos/{owner}/{repo}/issues/{number}/comments"""

from __future__ import annotations
import os
from pydantic import BaseModel, Field
from llama_index.core.tools import FunctionTool
from mcp_tools.common import github_request

class CommentIssueInput(BaseModel):
    repo:   str = Field(...)
    number: int = Field(..., ge=1)
    body:   str = Field(..., description="Markdown comment body")

def _comment_issue(repo, number, body):
    # Always use the authenticated user's username
    owner = os.getenv("GITHUB_USERNAME")
    if not owner:
        raise RuntimeError("GITHUB_USERNAME env-var required.")
    return github_request("POST",
                           f"/repos/{owner}/{repo}/issues/{number}/comments",
                           json={"body": body})

comment_issue_tool = FunctionTool.from_defaults(
    fn=_comment_issue,
    name="comment_issue",
    description="Add a comment to an issue in the authenticated user's repository only",
    # input_type=CommentIssueInput,
)

__all__ = ["comment_issue_tool"]
