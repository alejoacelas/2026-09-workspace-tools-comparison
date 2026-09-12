"""Three live Workspace MCP controls for existing gdoc findings; synthetic only.
Uses the actual installed stdio tool, then independent native Google readback.
Run with ~/.local/share/uv/tools/workspace-mcp/bin/python.
"""
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "hunt"))
import live as b
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

OUT = Path(__file__).with_suffix(".json")

def summarize(doc):
    paragraphs = []
    for element in doc["tabs"][0]["documentTab"]["body"]["content"]:
        p = element.get("paragraph")
        if not p:
            continue
        runs = [{"text": e["textRun"].get("content", ""), "style": e["textRun"].get("textStyle", {})}
                for e in p.get("elements", []) if "textRun" in e]
        paragraphs.append({"runs": runs, "bullet": bool(p.get("bullet"))})
    text = "".join(r["text"] for p in paragraphs for r in p["runs"])
    urls = [r["style"]["link"]["url"] for p in paragraphs for r in p["runs"] if "link" in r["style"]]
    return {"text": text, "links": urls, "paragraphs": paragraphs}

async def main():
    inputs = json.loads(Path(__file__).with_name("links-results.json").read_text())
    report = {"workspace_pin": "54b1c56f7f9912ce32681460d7ca38f9c2a37564", "workspace_version": "1.26.0",
              "route": "actual installed Workspace stdio manage_doc_tab populate_from_markdown",
              "scope": "three new personal scratch Docs; no collection/sharing/deletion", "cases": []}
    if OUT.exists():
        report = json.loads(OUT.read_text())
    ledger_path = b.LOCAL / "r2-workspace-markdown-ledger.json"
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {}
    log = b.LOCAL / "r2-workspace-markdown-mcp.log"
    log.touch(mode=0o600, exist_ok=True); log.chmod(0o600)
    transport = StdioTransport(command=str(Path.home() / ".local/bin/workspace-mcp"),
        args=["--transport", "stdio", "--tool-tier", "complete", "--tools", "drive", "docs"],
        env={"GOOGLE_CLIENT_SECRET_PATH": str(Path.home() / ".config/gdoc/credentials.json"),
             "WORKSPACE_MCP_CREDENTIALS_DIR": str(Path.home() / ".google_workspace_mcp/credentials"),
             "WORKSPACE_MCP_LOG_LEVEL": "ERROR"}, log_file=log.open("a"))
    async with Client(transport) as client:
        for key in ["ten-digit-account", "bracket-link-label", "entity-query-link"]:
            if any(r["id"] == key for r in report["cases"]):
                continue
            source = next(r for r in inputs["offline"] if r["id"] == key)
            gdoc = next(r for r in inputs["live"] if r["id"] == key)
            doc = ledger.get(key)
            if not doc:
                doc = b.new("Synthetic Workspace control — " + key)
                ledger[key] = doc; b.save("r2-workspace-markdown-ledger.json", ledger)
            before = b.state(doc)
            tab = before["tabs"][0]["tabProperties"]["tabId"]
            b.save("r2-workspace-markdown-" + key + "-before.json", before)
            b.identity()
            result = await client.call_tool("manage_doc_tab", {
                "user_google_email": b.ACCOUNT, "document_id": doc, "action": "populate_from_markdown",
                "tab_id": tab, "markdown_text": source["markdown"], "replace_existing": True},
                raise_on_error=False)
            response = "\n".join(getattr(c, "text", "") for c in result.content)
            after = b.state(doc)
            b.save("r2-workspace-markdown-" + key + "-after.json", after)
            native = summarize(after)
            actual = {"text": native["text"].rstrip("\n"), "links": native["links"]}
            row = {"id": key, "markdown": source["markdown"], "expected": source["expected"],
                   "gdoc_actual": gdoc["actual"], "workspace_actual": actual,
                   "workspace_native": native, "mcp_is_error": result.is_error,
                   "response": response.replace(doc, "DOC").replace(tab, "TAB").replace(b.ACCOUNT, "PERSONAL"),
                   "pass": actual == source["expected"] and not result.is_error}
            report["cases"].append(row)
            OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
            print(key, row["pass"], actual, flush=True)
    report["summary"] = {"cases": len(report["cases"]), "passes": sum(r["pass"] for r in report["cases"]),
                         "normalization": "only trailing paragraph newlines ignored; exact text and hyperlink URLs otherwise"}
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    asyncio.run(main())
