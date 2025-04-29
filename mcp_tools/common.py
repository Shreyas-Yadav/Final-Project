"""Shared helpers for all GitHub MCP repo tools."""

import base64, os
from json import dumps
from typing import Any, Dict
import requests
from dotenv import load_dotenv
load_dotenv()

GITHUB_API_BASE = os.getenv("GITHUB_API_BASE", "https://api.github.com")
API_VERSION_HDR = {"X-GitHub-Api-Version": "2022-11-28"}
TIMEOUT = 15  # s
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "Shreyas-Yadav")


def _get_token() -> str:
    tok = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not tok:
        raise RuntimeError("GITHUB_TOKEN env-var required.")
    return tok

def _headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {_get_token()}",
        "Accept": "application/vnd.github+json",
        **API_VERSION_HDR,
    }

def github_request(method: str, path: str, *,
                   params: Dict[str, Any] | None = None,
                   json:   Dict[str, Any] | None = None) -> Any:
    url = f"{GITHUB_API_BASE}{path}"
    resp = requests.request(
        method, url, headers=_headers(),
        params=params, json=json, timeout=TIMEOUT
    )
    resp.raise_for_status()
    res = resp.json() if resp.content else {"status_code": resp.status_code}
    return dumps(res, indent=2)

def put_file(owner: str, repo: str, path: str, message: str, content: str,
             *, branch: str | None = None, sha: str | None = None):
    """Create / update one file via the Contents API."""
    b64 = base64.b64encode(content.encode()).decode()
    body: Dict[str, Any] = {"message": message, "content": b64}
    if branch: body["branch"] = branch
    if sha:    body["sha"]    = sha
    return github_request("PUT",
                          f"/repos/{owner}/{repo}/contents/{path}",
                          json=body)

def delete_file(owner: str, repo: str, path: str, message: str, sha: str,
                *, branch: str | None = None):
    """Delete one file via the Contents API."""
    body: Dict[str, Any] = {"message": message, "sha": sha}
    if branch: body["branch"] = branch
    return github_request("DELETE",
                          f"/repos/{owner}/{repo}/contents/{path}",
                          json=body)
