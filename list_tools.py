# list_tools_stdio.py
import os, sys, json, subprocess, textwrap

from rich import print

TOKEN = os.environ["GITHUB_PERSONAL_ACCESS_TOKEN"]        # export GITHUB_PAT=ghp_xxx

cmd = [
    "docker", "run", "-i", "--rm","-p", "3000:3000",
    "-e", f"GITHUB_PERSONAL_ACCESS_TOKEN={TOKEN}",
    "ghcr.io/github/github-mcp-server"
]

# ── start the container and keep its stdio pipes open
proc = subprocess.Popen(
    cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
)

def rpc(method, params=None, id_=1):
    msg = {"jsonrpc": "2.0", "id": id_, "method": method, "params": params or {}}
    proc.stdin.write(json.dumps(msg) + "\n")
    proc.stdin.flush()
    return json.loads(proc.stdout.readline())

# 1⃣ handshake (required by MCP)
rpc("initialize", {"clientInfo": {"name": "demo-list-tools", "version": "0.1"}} , id_=0)

# 2⃣ ask for the tool catalogue
tools_page = rpc("tools/list")

print(f"Total tools are : {len(tools_page['result']['tools'])}" )
print(tools_page)

# print("\nAvailable tools:\n")
# for t in tools_page["result"]:
#     print(f"- {t['name']}: {textwrap.shorten(t.get('description', ''), width=60)}")

proc.terminate()   # be polite
