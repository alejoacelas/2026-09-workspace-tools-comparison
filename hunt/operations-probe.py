"""Pure native-Doc-tab -> Markdown contract probes; no Google/authentication calls.

Run: ~/.local/share/uv/tools/workspace-mcp/bin/python hunt/operations-probe.py
Synthetic fixtures only. Differences are candidates or known representation
limits, not live-write corruption. Exit 0 means all cases ran, not all passed.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "repos/gdoc"))
from gdoc.api.docs import get_tab_text
from gdoc.mdparse import parse_markdown

def run(text, **style):
    return {"textRun": {"content": text, "textStyle": style}}

def para(text=None, *, elements=None, list_id=None, level=0):
    p = {"elements": elements if elements is not None else [run(text)]}
    if list_id is not None:
        p["bullet"] = {"listId": list_id, "nestingLevel": level}
    return {"paragraph": p}

def table(rows):
    return {"table": {"tableRows": [{"tableCells": [
        {"content": [para(cell)] if isinstance(cell, str) else cell}
        for cell in row]} for row in rows]}}

def definition(start=1, glyph="DECIMAL"):
    return {"listProperties": {"nestingLevels": [{"glyphType": glyph,
             "startNumber": start}, {"glyphType": "DECIMAL", "startNumber": 1}]}}

cases = []
def add(name, content, expected, *, lists=None, mode="exact", classification="candidate"):
    cases.append({"id": name, "native_tab": {"body": {"content": content},
                  "lists": lists or {}}, "expected": expected, "mode": mode,
                  "classification": classification})

# Punctuation controls avoid the previously documented literal emphasis defects.
for name, text in [
    ("office-punctuation", "Budget: £1,250.50; tax (20%) — approved!\n"),
    ("curly-quotes", "“Friday’s review” — don’t postpone.\n"),
    ("windows-path", r"Open C:\reports\2026\final.txt" + "\n"),
    ("comparison-symbols", "Actual < forecast; 3 > 2; x = 4.\n"),
]:
    add(name, [para(text)], text, classification="control")

# URL brackets in the LABEL, rather than the already known balanced-URL defect.
for name, label, url in [
    ("url-query-control", "Budget", "https://example.com/report?a=1&b=2"),
    ("link-square-bracket-label", "Budget [draft]", "https://example.com/report"),
    ("link-email-control", "Email finance", "mailto:finance@example.com"),
]:
    add(name, [para(elements=[run(label, link={"url": url}), run("\n")])],
        {"text": label + "\n", "url": url}, mode="roundtrip_link",
        classification="candidate" if "bracket" in name else "control")

# Ordered-list numbering is meaningful office content (steps, references).
add("ordered-start-seven", [para("Approve\n", list_id="a"), para("Publish\n", list_id="a")],
    "7. Approve\n8. Publish\n", lists={"a": definition(7)})
add("adjacent-distinct-lists", [para("Checklist A\n", list_id="a"), para("Checklist B\n", list_id="b")],
    "1. Checklist A\n1. Checklist B\n", lists={"a": definition(), "b": definition()})
add("same-list-after-note", [para("Approve\n", list_id="a"), para("Note: obtain sign-off.\n"),
    para("Publish\n", list_id="a")], "1. Approve\nNote: obtain sign-off.\n2. Publish\n",
    lists={"a": definition()})
add("ordinary-numbering-control", [para("Approve\n", list_id="a"), para("Publish\n", list_id="a")],
    "1. Approve\n2. Publish\n", lists={"a": definition()}, classification="control")
add("new-list-after-note-control", [para("Approve\n", list_id="a"), para("Another checklist.\n"),
    para("Publish\n", list_id="b")], "1. Approve\nAnother checklist.\n1. Publish\n",
    lists={"a": definition(), "b": definition()}, classification="control")

# Table read paths: compare visible content preservation, and distinguish the
# documented TSV representation from outright omitted content.
add("ordinary-table-tsv-control", [table([["Item\n", "Cost\n"], ["Pens\n", "100\n"]])],
    "Item\tCost\nPens\t100\n", classification="control")
add("table-linked-cell", [table([[[para(elements=[run("Budget", link={"url": "https://example.com/budget"}), run("\n")])], "100\n"]])],
    "https://example.com/budget", mode="contains", classification="representation-gap")
add("table-bold-cell", [table([[[para(elements=[run("Approved", bold=True), run("\n")])], "100\n"]])],
    "**Approved**", mode="contains", classification="representation-gap")
add("nested-table-content", [table([[ [para("Breakdown\n"), table([["Materials\n", "475\n"]]), para("Total\n")], "500\n"]])],
    ["Breakdown", "Materials", "475", "Total", "500"], mode="contains_all")
add("multiline-cell-content-control", [table([["North\nSouth\n", "100\n"]])],
    ["North", "South", "100"], mode="contains_all", classification="control")

# Native visible chips are paragraph elements, not ordinary text runs.
add("person-chip-visible-name", [para(elements=[run("Owner: "),
    {"person": {"personProperties": {"name": "Alex Example", "email": "alex@example.com"}}}, run("\n")])],
    "Owner: Alex Example\n")
add("file-chip-visible-title", [para(elements=[run("See "),
    {"richLink": {"richLinkProperties": {"title": "Budget 2026", "uri": "https://example.com/budget"}}}, run(" today.\n")])],
    ["See", "Budget 2026", "today."], mode="contains_all")
add("soft-line-break-visible-text", [para(elements=[run("First line"),
    {"textRun": {"content": "\u000bSecond line\n", "textStyle": {}}}])],
    "First line\u000bSecond line\n", classification="control")

results = []
for case in cases:
    actual = get_tab_text(case["native_tab"], markdown=True)
    mode, expected = case["mode"], case["expected"]
    observed = actual
    if mode == "contains":
        passed = expected in actual
    elif mode == "contains_all":
        passed = all(item in actual for item in expected)
    elif mode == "roundtrip_link":
        parsed = parse_markdown(actual.rstrip("\n"))
        urls = [r.style["link"]["url"] for r in parsed.styles if "link" in r.style]
        observed = {"markdown": actual, "text": parsed.plain_text, "urls": urls}
        passed = parsed.plain_text == expected["text"] and expected["url"] in urls
    else:
        passed = actual == expected
    results.append({**case, "passed": passed, "actual": observed})

report = {"pin": "dbfa4c34bfa699ee8dd9839da85eea1fac177d44",
          "scope": "20 pure export cases; no Google API calls; expectation definitions explicit",
          "summary": {"cases": len(results), "passed": sum(r["passed"] for r in results),
                      "differences": sum(not r["passed"] for r in results)}, "results": results}
destination = Path(__file__).with_name("operations-results.json")
destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(report["summary"]))
for result in results:
    if not result["passed"]:
        print(result["id"], repr(result["actual"]))
