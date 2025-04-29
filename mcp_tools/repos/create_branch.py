from __future__ import annotations
import os
from pydantic import BaseModel, Field
from llama_index.core.tools import FunctionTool
from mcp_tools.common import github_request

class CreateBranchInput(BaseModel):
    repo:   str = Field(...)
    branch: str = Field(..., description="New branch name")
    sha:    str = Field(...,  description="Base commit SHA")

def _create_branch(repo, branch, sha):
    # Always use the authenticated user's username
    owner = os.getenv("GITHUB_USERNAME")
    if not owner:
        raise RuntimeError("GITHUB_USERNAME env-var required.")
    body = {"ref": f"refs/heads/{branch}", "sha": sha}
    return github_request("POST",
                           f"/repos/{owner}/{repo}/git/refs",
                           json=body)

create_branch_tool = FunctionTool.from_defaults(
    fn=_create_branch,
    name="create_branch",
    description="Create a new branch from a SHA in the authenticated user's repository only",
)

__all__ = ["create_branch_tool"]
