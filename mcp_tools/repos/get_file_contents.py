from __future__ import annotations
from pydantic import BaseModel, Field
from llama_index.core.tools import FunctionTool
from mcp_tools.common import github_request
import os
from mcp_tools.common import GITHUB_USERNAME

class GetFileContentsInput(BaseModel):
    repo:  str = Field(...)
    path:  str = Field(..., description="File path in repo")
    ref:   str | None = Field(None, description="Branch/tag/SHA")

def _get_file(repo, path, *, ref=None):
    # Always use the authenticated user's username
    owner = os.getenv("GITHUB_USERNAME")
    if not owner:
        raise RuntimeError("GITHUB_USERNAME env-var required.")
    params = {"ref": ref} if ref else None
    return github_request("GET",
                          f"/repos/{owner}/{repo}/contents/{path}",
                          params=params)

get_file_contents_tool = FunctionTool.from_defaults(
    fn=_get_file,
    name="get_file_contents",
    description="Retrieve file metadata + Base64 content from authenticated user's repositories only",
    # input_type=GetFileContentsInput,
)

__all__ = ["get_file_contents_tool"]
