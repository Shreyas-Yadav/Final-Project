from __future__ import annotations
import os
from pydantic import BaseModel, Field
from llama_index.core.tools import FunctionTool
from mcp_tools.common import github_request

class ForkRepositoryInput(BaseModel):
    repo:  str = Field(...)
    organization: str | None = Field(None, description="Target org")

def _fork_repo(repo, *, organization=None):
    # Always use the authenticated user's username
    owner = os.getenv("GITHUB_USERNAME")
    if not owner:
        raise RuntimeError("GITHUB_USERNAME env-var required.")
    body = {"organization": organization} if organization else None
    return github_request("POST",
                           f"/repos/{owner}/{repo}/forks",
                           json=body)

fork_repository_tool = FunctionTool.from_defaults(
    fn=_fork_repo,
    name="fork_repository",
    description="Fork a repository owned by the authenticated user only",
    # input_type=ForkRepositoryInput,
)

__all__ = ["fork_repository_tool"]
