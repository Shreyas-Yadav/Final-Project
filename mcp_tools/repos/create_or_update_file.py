from __future__ import annotations
import os
from pydantic import BaseModel, Field
from llama_index.core.tools import FunctionTool
from mcp_tools.common import put_file

class CreateOrUpdateFileInput(BaseModel):
    repo:    str = Field(...)
    path:    str = Field(...)
    message: str = Field(...)
    content: str = Field(...)
    branch:  str | None = Field(None)
    sha:     str | None = Field(None)

def _create_or_update(repo, path, message, content, *,
                       branch=None, sha=None):
    # Always use the authenticated user's username
    owner = os.getenv("GITHUB_USERNAME")
    if not owner:
        raise RuntimeError("GITHUB_USERNAME env-var required.")
    return put_file(owner, repo, path, message, content,
                     branch=branch, sha=sha)

create_or_update_file_tool = FunctionTool.from_defaults(
    fn=_create_or_update,
    name="create_or_update_file",
    description="Create or update a single file in the authenticated user's repository only",
    # input_type=CreateOrUpdateFileInput,
)

__all__ = ["create_or_update_file_tool"]
