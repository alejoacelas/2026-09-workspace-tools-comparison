"""Ten bounded review-command checks on one personal synthetic Doc; no deletion.
Run with workspace-mcp Python. Creates comments/replies only on its scratch Doc.
Raw IDs and account-bearing receipts remain in owner-only .local-hunt/r2-review*.
"""
import csv
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "hunt"))
import live as b
from gdoc.revdiff import build_hunks

OUT = Path(__file__).with_suffix(".json")
ledger_file = b.LOCAL / "r2-review-ledger.json"
ledger = json.loads(ledger_file.read_text()) if ledger_file.exists() else {}
results = {"pin": "dbfa4c34bfa699ee8dd9839da85eea1fac177d44", "cases": []}
COMMENT = 'Question A\tBudget\nIs **100** final? Keep <5% and "quotes".'
REPLY = 'Answer B\nUse **120**; literal [draft] and R&D.'

def record(key, passed, **details):
    results["cases"].append({"id": key, "pass": passed, **details})
    OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    print(key, passed, flush=True)

def state(doc, comment):
    raw = b.drive.comments().get(fileId=doc, commentId=comment,
        fields="id,content,resolved,replies(id,content,action)").execute()
    b.save("r2-review-native.json", raw)
    return {"content": raw.get("content", ""), "resolved": raw.get("resolved", False),
            "replies": [{"content": r.get("content", ""), "action": r.get("action", "")}
                        for r in raw.get("replies", [])]}

def call(args):
    r = b.cli(args)
    assert r["returncode"] == 0, {"returncode": r["returncode"],
        "errors": [l for l in r["stderr"].splitlines() if l.startswith("ERR:")]}
    return r

def main():
    if OUT.exists() and len(json.loads(OUT.read_text()).get("cases", [])) == 10:
        print("Ten cases already recorded; refusing to duplicate comment mutations.")
        return
    doc = ledger.get("doc")
    if not doc:
        doc = b.new("Synthetic gdoc review-command checks")
        ledger["doc"] = doc; b.save("r2-review-ledger.json", ledger)
        tab = b.state(doc)["tabs"][0]["tabProperties"]["tabId"]
        text = "Review plan\nCosts\nAssumptions\n"
        req = [{"insertText": {"location": {"index": 1, "tabId": tab}, "text": text}}]
        start = 1
        for level, line in enumerate(text.splitlines(keepends=True), 1):
            req.append({"updateParagraphStyle": {"range": {"tabId": tab, "startIndex": start,
                       "endIndex": start + len(line)}, "paragraphStyle": {"namedStyleType": f"HEADING_{level}"},
                       "fields": "namedStyleType"}})
            start += len(line)
        b.update(doc, req)
        b.save("r2-review-doc-before.json", b.state(doc))
    cid = ledger.get("comment")
    if not cid:
        made = call(["comment", doc, COMMENT, "--json"])
        cid = json.loads(made["stdout"])["id"]
        ledger["comment"] = cid; b.save("r2-review-ledger.json", ledger)
    current = state(doc, cid)
    record("literal-multiline-comment", current["content"] == COMMENT,
           returncode=0, expected=COMMENT, native=current)

    if not any(r["content"] == REPLY for r in current["replies"]):
        call(["reply", doc, cid, REPLY])
    current = state(doc, cid)
    record("literal-multiline-reply", any(r["content"] == REPLY for r in current["replies"]),
           returncode=0, expected=REPLY, native=current)
    comments = json.loads(call(["comments", doc, "--json"])["stdout"])["comments"]
    selected = next(c for c in comments if c["id"] == cid)
    record("comments-json-thread", selected["content"] == COMMENT and any(r.get("content") == REPLY for r in selected.get("replies", [])),
           content=selected["content"], reply_contents=[r.get("content", "") for r in selected.get("replies", [])])

    message = "Resolved: checked 120; no other reviewer."
    response = call(["resolve", doc, cid, "--message", message, "--json"])
    current = state(doc, cid)
    record("resolve-with-message", current["resolved"] and any(r["action"] == "resolve" and r["content"] == message for r in current["replies"]),
           returncode=response["returncode"], native=current)
    default = json.loads(call(["comments", doc, "--json"])["stdout"])["comments"]
    all_comments = json.loads(call(["comments", doc, "--all", "--json"])["stdout"])["comments"]
    record("resolved-list-filter", not any(c["id"] == cid for c in default) and any(c["id"] == cid for c in all_comments),
           default_count=len(default), all_count=len(all_comments))
    response = call(["reopen", doc, cid, "--json"])
    current = state(doc, cid)
    record("reopen-retains-thread", not current["resolved"] and current["content"] == COMMENT and any(r["content"] == REPLY for r in current["replies"]),
           returncode=response["returncode"], native=current)

    info = json.loads(call(["comment-info", doc, cid, "--json"])["stdout"])["comment"]
    record("comment-info-json-detail", info["content"] == COMMENT and not info.get("resolved", False)
           and len(info.get("replies", [])) == len(current["replies"]),
           content=info["content"], native_reply_count=len(current["replies"]), cli_reply_count=len(info.get("replies", [])))

    plain = call(["comments", doc, "--plain"])["stdout"]
    b.save("r2-review-plain-receipt.json", {"stdout": plain})
    scrubbed = plain.replace(cid, "COMMENT").replace(doc, "DOC").replace(b.ACCOUNT, "PERSONAL")
    for c in all_comments:
        for v in c.get("author", {}).values():
            if isinstance(v, str) and v:
                scrubbed = scrubbed.replace(v, "AUTHOR")
    parsed_records = list(csv.reader(io.StringIO(plain), delimiter="\t"))
    columns = [len(row) for row in parsed_records]
    record("comments-plain-row-contract", len(parsed_records) == 1 and columns == [5]
           and parsed_records[0][3] == COMMENT,
           native_comment_count=1, parsed_record_count=len(parsed_records), tab_fields_per_record=columns,
           parsed_redacted_records=list(csv.reader(io.StringIO(scrubbed), delimiter="\t")),
           expected_redacted_records=[["COMMENT", "open", "AUTHOR", COMMENT, ""]],
           redacted_stdout=scrubbed,
           classification="machine-readable TSV contract candidate; native comment is intact and JSON is correct")

    hunks = build_hunks("Budget is 100 pounds.\n", "Budget is 120 pounds.\n")
    record("revision-diff-amount-control", any(h["kind"] != "equal" for h in hunks),
           scope="offline actual diff builder, no retained revisions required", hunks=hunks)
    toc = json.loads(call(["toc", doc, "--max-depth", "2", "--json"])["stdout"])
    headings = toc.get("headings", toc.get("items", []))
    record("toc-depth-control", [h.get("text") for h in headings] == ["Review plan", "Costs"],
           headings=[{"text": h.get("text"), "level": h.get("level")} for h in headings])
    results["summary"] = {"cases": len(results["cases"]), "passes": sum(r["pass"] for r in results["cases"]),
        "scope": "nine live review/TOC cases and one offline diff control; no anchored-comment or preview paths"}
    OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    b.save("r2-review-doc-after.json", b.state(doc))

if __name__ == "__main__":
    main()
