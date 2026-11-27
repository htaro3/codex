#!/usr/bin/env python3
"""Check public GitHub Actions workflow state from runner network."""
import json
import os
import urllib.error
import urllib.request

for url in [
    "https://api.github.com/repos/htaro3/codex/actions/workflows",
    "https://api.github.com/repos/htaro3/codex/actions/workflows/pc-watch-live.yml",
]:
    try:
        headers={"User-Agent":"MiniPCWatch/0.2","Accept":"application/vnd.github+json"}
        if os.environ.get("GITHUB_TOKEN"):
            headers["Authorization"]="Bearer "+os.environ["GITHUB_TOKEN"]
        req=urllib.request.Request(url,headers=headers)
        with urllib.request.urlopen(req,timeout=15) as r:
            obj=json.load(r)
        if "workflows" in obj:
            print("WORKFLOW_STATES", [(w.get("name"),w.get("state"),w.get("path")) for w in obj["workflows"]],flush=True)
        else:
            print("LIVE_STATE", obj.get("name"),obj.get("state"),obj.get("path"),flush=True)
    except Exception as e:
        print("ERROR_WORKFLOW_STATE",type(e).__name__,str(e)[:200],flush=True)
