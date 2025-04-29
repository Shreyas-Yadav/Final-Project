"""create_issue tool – POST /repos/{owner}/{repo}/issues"""

from __future__ import annotations
import os
from pydantic import BaseModel, Field
from llama_index.core.tools import FunctionTool
from mcp_tools.common import github_request

class CreateIssueInput(BaseModel):
    repo:  str = Field(...)
    title: str = Field(..., description="Issue title")
    body:  str | None = Field(None, description="Markdown body")
    labels: list[str] | None = Field(None)
    assignees: list[str] | None = Field(None)

def _create_issue(repo, title, *, body=None,
                   labels=None, assignees=None):
    # Always use the authenticated user's username
    owner = os.getenv("GITHUB_USERNAME")
    if not owner:
        raise RuntimeError("GITHUB_USERNAME env-var required.")
    body_json = {"title": title, "body": body,
                 "labels": labels, "assignees": assignees}
    body_json = {k: v for k, v in body_json.items() if v}
    return github_request("POST", f"/repos/{owner}/{repo}/issues", json=body_json)

create_issue_tool = FunctionTool.from_defaults(
    fn=_create_issue,
    name="create_issue",
    description="Open a new issue in the authenticated user's repository only",
    # input_type=CreateIssueInput,
)

__all__ = ["create_issue_tool"]
