"""Fifteen synthetic gdoc Markdown contracts; optional authorized scratch live checks.

Run with the workspace-mcp Python for MarkdownIt and Google dependencies.
Default: offline only. --live adds three private personal-account scratch Docs.
No collection writes, sharing, deletion, or upstream changes.
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "repos/gdoc"))
from gdoc.mdparse import parse_markdown
from gdoc.api.docs import get_tab_text
from markdown_it import MarkdownIt

HERE = Path(__file__).parent
OUT = HERE / "links-results.json"
CASES = [
    ("raw-ampersand-control", "R&D costs < 5% of revenue.", "R&D costs < 5% of revenue.", [], "control"),
    ("named-entities", "R&amp;D costs &lt; 5% of revenue.", "R&D costs < 5% of revenue.", [], "convention-gap"),
    ("numeric-entities", "Budget &#163;125; variance &#x2212;5%.", "Budget £125; variance −5%.", [], "convention-gap"),
    ("literal-angle-limit-control", "Target <5%; ceiling >10%.", "Target <5%; ceiling >10%.", [], "control"),
    ("plain-query-link-control", "Open [Budget](https://example.com/report?a=1&b=2).", "Open Budget.", ["https://example.com/report?a=1&b=2"], "control"),
    ("entity-query-link", "Open [Budget](https://example.com/report?a=1&amp;b=2).", "Open Budget.", ["https://example.com/report?a=1&b=2"], "candidate"),
    ("bracket-link-label", "Read [Finance [Q3]](https://example.com/q3).", "Read Finance [Q3].", ["https://example.com/q3"], "candidate"),
    ("escaped-bracket-label-control", r"Read [Finance \[Q3\]](https://example.com/q3).", "Read Finance [Q3].", ["https://example.com/q3"], "control"),
    ("simple-linked-label-control", "Read [Finance Q3](https://example.com/q3).", "Read Finance Q3.", ["https://example.com/q3"], "control"),
    ("closing-heading-marker", "# Revenue forecast #", "Revenue forecast", [], "candidate"),
    ("escaped-heading-hash-control", r"# Revenue forecast \#", "Revenue forecast #", [], "control"),
    ("ten-digit-account", "1234567890. Revenue account", "1234567890. Revenue account", [], "candidate"),
    ("nine-digit-list-control", "123456789. Revenue account", "Revenue account", [], "control"),
    ("iso-date-control", "2026-09-12. Review budget.", "2026-09-12. Review budget.", [], "control"),
    ("plain-email-control", "Contact finance@example.com by Friday.", "Contact finance@example.com by Friday.", [], "control"),
]

def reference(source):
    tokens = MarkdownIt("commonmark").parse(source)
    text, urls = [], []
    for token in tokens:
        if token.type != "inline":
            continue
        for child in token.children or []:
            if child.type in {"text", "code_inline", "html_inline"}:
                text.append(child.content)
            elif child.type == "link_open":
                urls.append(child.attrGet("href"))
    return {"text": "".join(text), "links": urls}

def summarize(document):
    rows = []
    for element in document["tabs"][0]["documentTab"]["body"]["content"]:
        p = element.get("paragraph")
        if not p:
            continue
        runs = [{"text": e["textRun"].get("content", ""), "style": e["textRun"].get("textStyle", {})}
                for e in p.get("elements", []) if "textRun" in e]
        rows.append({"runs": runs, "paragraph_style": p.get("paragraphStyle", {}),
                     "bullet": bool(p.get("bullet"))})
    return {"text": "".join(r["text"] for p in rows for r in p["runs"]), "paragraphs": rows}

def main():
    results = {"pin": "dbfa4c34bfa699ee8dd9839da85eea1fac177d44", "offline": [], "live": []}
    if OUT.exists():
        results["live"] = json.loads(OUT.read_text()).get("live", [])
    for key, source, text, urls, classification in CASES:
        parsed = parse_markdown(source)
        actual = {"text": parsed.plain_text.rstrip("\n"), "links": [
            s.style["link"]["url"] for s in parsed.styles if "link" in s.style]}
        expected = {"text": text, "links": urls}
        ref = reference(source)
        assert ref == expected, (key, ref, expected)
        results["offline"].append({"id": key, "markdown": source, "classification": classification,
                                   "expected": expected, "actual": actual, "reference": ref,
                                   "pass": actual == expected,
                                   "styles": [{"type": s.type, "style": s.style} for s in parsed.styles]})
    # Also establish that the bracket-label syntax can come from gdoc itself.
    tab = {"body": {"content": [{"paragraph": {"elements": [
        {"textRun": {"content": "Read "}}, {"textRun": {"content": "Finance [Q3]",
        "textStyle": {"link": {"url": "https://example.com/q3"}}}},
        {"textRun": {"content": ".\n"}}]}}]}}
    results["bracket_label_export"] = get_tab_text(tab, markdown=True)
    assert results["bracket_label_export"].rstrip("\n") == next(c[1] for c in CASES if c[0] == "bracket-link-label")
    results["summary"] = {"offline_cases": len(CASES), "passes": sum(x["pass"] for x in results["offline"])}
    OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    print(results["summary"], flush=True)
    if "--live" not in sys.argv:
        return
    spec = importlib.util.spec_from_file_location("hunt_live", ROOT / "hunt/live.py")
    b = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(b)
    ledger_path = b.LOCAL / "r2-links-ledger.json"
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {}
    for key in ["bracket-link-label", "ten-digit-account", "entity-query-link"]:
        row = next(x for x in results["offline"] if x["id"] == key)
        if any(x["id"] == key for x in results["live"]):
            continue
        doc = ledger.get(key)
        if not doc:
            doc = b.new("Synthetic gdoc R2 links — " + key)
            ledger[key] = doc
            b.save("r2-links-ledger.json", ledger)
        before = b.state(doc)
        tab_id = before["tabs"][0]["tabProperties"]["tabId"]
        b.save("r2-links-" + key + "-before.json", before)
        mdfile = b.LOCAL / ("r2-links-" + key + ".md")
        mdfile.write_text(row["markdown"])
        mdfile.chmod(0o600)
        assert b.cli(["cat", doc, "--tab", tab_id])["returncode"] == 0
        response = b.cli(["write", doc, str(mdfile), "--tab", tab_id])
        attempts = [response["returncode"]]
        for _ in range(2):
            if response["returncode"] != 3 or "doc changed since last read" not in response["stderr"]:
                break
            assert b.cli(["cat", doc, "--tab", tab_id])["returncode"] == 0
            response = b.cli(["write", doc, str(mdfile), "--tab", tab_id])
            attempts.append(response["returncode"])
        after = b.state(doc)
        b.save("r2-links-" + key + "-after.json", after)
        native = summarize(after)
        links = [r["style"]["link"]["url"] for p in native["paragraphs"] for r in p["runs"] if "link" in r["style"]]
        actual = {"text": native["text"].rstrip("\n"), "links": links}
        live = {"id": key, "markdown": row["markdown"], "expected": row["expected"],
                "before": summarize(before), "after": native, "actual": actual,
                "returncode": response["returncode"], "attempt_returncodes": attempts,
                "stderr": "\n".join(line for line in response["stderr"].splitlines() if line.startswith("ERR:")),
                "pass": actual == row["expected"],
                "command": "gdoc write DOC specimen.md --tab TAB --account PERSONAL"}
        results["live"].append(live)
        OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
        print(key, response["returncode"], actual, flush=True)

if __name__ == "__main__":
    main()
