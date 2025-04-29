from __future__ import annotations
import os
from pydantic import BaseModel, Field
from llama_index.core.tools import FunctionTool
from mcp_tools.common import delete_file

class DeleteFileInput(BaseModel):
    repo:    str = Field(..., description="The name of the repository.")
    path:    str = Field(..., description="The path to the file to delete within the repository.")
    message: str = Field(..., description="The commit message for the deletion.")
    sha:     str = Field(..., description="The SHA of the file to delete. This is required by the GitHub API for deletion.")
    branch:  str | None = Field(None, description="The branch the file is on. Defaults to the default branch.")

def _delete_file(repo: str, path: str, message: str, sha: str, *,
                 branch: str | None = None):
    """Deletes a file in the authenticated user's repository."""
    owner = os.getenv("GITHUB_USERNAME")
    if not owner:
        raise RuntimeError("GITHUB_USERNAME env-var required.")
    return delete_file(owner, repo, path, message, sha, branch=branch)

delete_file_tool = FunctionTool.from_defaults(
    fn=_delete_file,
    name="delete_file",
    description="Delete a single file from the authenticated user's repository. Requires the file's SHA.",
    # input_type=DeleteFileInput, # Optional: uncomment to enforce input schema validation
)

__all__ = ["delete_file_tool"]