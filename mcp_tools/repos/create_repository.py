from __future__ import annotations
from pydantic import BaseModel, Field
from llama_index.core.tools import FunctionTool
from mcp_tools.common import github_request

class CreateRepositoryInput(BaseModel):
    name: str = Field(..., description="Repo name")
    description: str | None = Field(None)
    private: bool | None = Field(False)
    autoInit: bool | None = Field(False, description="Init with README")

def _create_repository(name: str, *, description=None,
                       private=False, autoInit=False):
    body = {"name": name, "description": description,
            "private": private, "auto_init": autoInit}
    body = {k: v for k, v in body.items() if v is not None}
    return github_request("POST", "/user/repos", json=body)

create_repository_tool = FunctionTool.from_defaults(
    fn=_create_repository,
    name="create_repository",
    description="Create a new GitHub repository",
    # input_type=CreateRepositoryInput,
)

__all__ = ["create_repository_tool"]
