"""Offline reverse bug-transfer probes against the two unmodified snapshots.

Run with the installed workspace-mcp Python (which supplies both dependencies):
  ~/.local/share/uv/tools/workspace-mcp/bin/python probes/workspace-fixes-crosscheck.py

Assertions characterize these revisions, including known defects. PASS means
the observation reproduced, not that the tool is correct. No network or tokens.
"""
import ast
import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "repos/gdoc"), str(ROOT / "repos/google-workspace-mcp")]
from gdoc.api import docs, drive, sheets
from gdoc.mdparse import parse_markdown, to_docs_requests
from gdoc.cli import _format_sheet_tsv, build_parser
from gdocs.docs_markdown_writer import markdown_to_docs_requests
from gdocs.docs_helpers import extract_text_from_elements, create_find_replace_request
from gsheets.sheets_helpers import _clamp_a1_read_rows, _column_to_index
from core.cli import _coerce_cli_value
from gdrive.drive_helpers import _resolve_import_media, GOOGLE_SHEETS_IMPORT_FORMATS

observations = []

def record(case, **details):
    observations.append({"case": case, **details})

def paragraph(text, index):
    end = index + len(text.encode("utf-16-le")) // 2
    return {"startIndex": index, "endIndex": end, "paragraph": {"elements": [
        {"startIndex": index, "endIndex": end, "textRun": {"content": text}}
    ]}}

# Native Markdown index convention: BMP, astral, ZWJ, and combining sequences.
for heading in ["Plan", "Plan 😀", "Plan 😀😀", "Plan 👩‍💻", "Plan é"]:
    markdown = f"# {heading}\n\nNext"
    expected = 1 + len((heading + "\n").encode("utf-16-le")) // 2
    ws = markdown_to_docs_requests(markdown)
    gd = to_docs_requests(parse_markdown(markdown), 1)
    ends = [next(r["updateParagraphStyle"]["range"]["endIndex"]
                 for r in requests if "updateParagraphStyle" in r) for requests in [ws, gd]]
    assert ends[1] == expected
    assert ends[0] == 1 + len(heading + "\n")
    record("unicode_heading", heading=heading, expected=expected,
           workspace_end=ends[0], gdoc_end=ends[1], workspace_correct=ends[0] == expected)

# PR850: inserted ordinary paragraphs need an explicit NORMAL_TEXT reset.
for source in ["Plain body paragraph.", "# Heading\n\nBody", "```\ncode\n```"]:
    ws = markdown_to_docs_requests(source, start_index=12)
    gd = to_docs_requests(parse_markdown(source), 12)
    def resets(requests):
        return sum(r.get("updateParagraphStyle", {}).get("paragraphStyle", {}).get(
            "namedStyleType") == "NORMAL_TEXT" for r in requests)
    assert resets(ws) == 0 and resets(gd) > 0
    record("body_style_reset", markdown=source, workspace_resets=resets(ws), gdoc_resets=resets(gd))

# PR1109: inspect actual gdoc request kwargs; inspect Workspace constant without
# importing its decorated/authenticated tools. This is a request-shape check,
# NOT an independent live confirmation that Google's service rejects the mask.
source = (ROOT / "repos/google-workspace-mcp/gdocs/docs_tools.py").read_text()
tree = ast.parse(source)
assignments = [n for n in tree.body if isinstance(n, ast.Assign) and any(
    isinstance(t, ast.Name) and t.id in {"_STRUCTURE_CONTENT_FIELDS", "_STRUCTURE_FIELDS"}
    for t in n.targets)]
scope = {}
exec(compile(ast.Module(body=assignments, type_ignores=[]), "mask_constants", "exec"), scope)
mask = scope["_STRUCTURE_FIELDS"]
legacy = mask.split("tabs(", 1)[0]
assert "headers" in legacy and "body(" in legacy
svc = MagicMock()
svc.documents().get().execute.return_value = {"tabs": []}
with patch.object(docs, "get_docs_service", return_value=svc):
    docs.get_document_structure("synthetic")
kwargs = svc.documents().get.call_args.kwargs
assert kwargs == {"documentId": "synthetic", "includeTabsContent": True}
record("tab_field_mask", workspace_legacy_fields=True, gdoc_default_request=kwargs)

# PR976: no legacy body, only populated tab content; gdoc must find the text.
tab_doc = {"tabs": [{"tabProperties": {"tabId": "t1", "title": "First", "index": 0},
                    "documentTab": {"body": {"content": [paragraph("Present\n", 1)]}}}]}
svc.documents().get().execute.return_value = tab_doc
with patch.object(docs, "get_docs_service", return_value=svc):
    tabs = docs.get_document_tabs("synthetic")
assert docs.get_tab_text(tabs[0]) == "Present\n"
record("tab_only_body", gdoc_read="Present\n")

# PR986: bounded fetch vs unbounded range forwarding; no large allocation needed.
for requested in ["A:Z", "A1:Z50000", "A1001:Z50000", "A1:B120"]:
    svc = MagicMock()
    svc.spreadsheets().values().get().execute.return_value = {"values": []}
    with patch.object(sheets, "get_sheets_service", return_value=svc):
        sheets.get_values("synthetic", requested)
    sent = svc.spreadsheets().values().get.call_args.kwargs["range"]
    clamped, note = _clamp_a1_read_rows(requested)
    assert sent == requested
    record("sheet_fetch_bound", requested=requested, workspace_fetch=clamped,
           workspace_discloses_clamp=bool(note), gdoc_fetch=sent)

# PR955: verify gdoc neither API-wrapper nor TSV rendering truncates row 120.
svc = MagicMock()
rows = [[f"row-{i}"] for i in range(1, 121)]
svc.spreadsheets().values().get().execute.return_value = {"values": rows}
with patch.object(sheets, "get_sheets_service", return_value=svc):
    returned = sheets.get_values("synthetic", "A1:A120")["values"]
assert len(returned) == 120 and "row-120" in _format_sheet_tsv(returned)
record("sheet_display_truncation", gdoc_rows_returned=len(returned), gdoc_last_row_rendered=True)

# PR930: the inline CSV route still needs an explicit format or filename extension.
for hint in [None, "csv"]:
    try:
        _, mime, _ = asyncio.run(_resolve_import_media(
            tool_name="import_to_google_sheets", file_name="Spend Summary",
            content="item,cost\nPens,4", file_path=None, file_url=None,
            source_format=hint, format_map=GOOGLE_SHEETS_IMPORT_FORMATS))
        actual = {"mime": mime}
    except ValueError as error:
        actual = {"error": str(error)}
    assert ("error" in actual) == (hint is None)
    record("workspace_csv_format_hint", source_format=hint, result=actual)

# PR1051: gdoc rename targets the shortcut resource ID itself, with no resolver.
svc = MagicMock()
svc.files().update().execute.return_value = {"id": "shortcut", "version": "2"}
with patch.object(drive, "get_drive_service", return_value=svc):
    drive.rename_file("shortcut", "Renamed")
assert svc.files().update.call_args.kwargs["fileId"] == "shortcut"
assert not svc.files().get.called
record("shortcut_rename", gdoc_target=svc.files().update.call_args.kwargs["fileId"])

# PR983: quotes survive the argument parser (shell tokenization is outside it).
for query in ['"exact phrase"', '"123"', "ordinary text"]:
    gdoc_value = build_parser().parse_args(["find", query]).query
    workspace_value = _coerce_cli_value(query)
    assert gdoc_value == workspace_value == query
    record("cli_quote_preservation", input=query, gdoc=gdoc_value, workspace=workspace_value)

# PR964: Workspace now rejects dangerous cell-like column labels. gdoc has no
# column deletion operation; absence is documented separately, not a passing test.
for column in ["B2", "A:B", "A\n", "AA"]:
    actual = _column_to_index(column)
    assert actual == (26 if column == "AA" else None)
    record("workspace_column_validation", input=column, actual=actual)

# PR1087: both now preserve blank paragraphs for reads; gdoc locates real native
# text-run indices even across inline objects. Flat text offsets are not its oracle.
object_paragraph = paragraph("Bravo\n", 9)
object_paragraph["startIndex"] = 8
object_paragraph["paragraph"]["elements"].insert(0, {
    "startIndex": 8, "endIndex": 9, "inlineObjectElement": {"inlineObjectId": "img"}})
elements = [paragraph("Alpha\n", 1), paragraph("\n", 7), object_paragraph]
text = extract_text_from_elements(elements)
assert text == "Alpha\n\n\ufffcBravo\n"
matches = docs.find_text_in_document({"body": {"content": elements}}, "Bravo")
assert matches == [{"startIndex": 9, "endIndex": 14}]
record("blank_and_object_indices", workspace_extracted=text, gdoc_matches=matches)

# A fresh analogous Unicode-indexing defect in gdoc's default case-insensitive
# search: lower() expands U+0130, but its doc-index mapping remains unexpanded.
for original in ["İ cat\n", "İİ cat\n", "😀 İ cat\n", "İ cat sat\n"]:
    doc = {"body": {"content": [paragraph(original, 1)]}}
    expected_start = 1 + len(original[:original.index("cat")].encode("utf-16-le")) // 2
    try:
        found = docs.find_text_in_document(doc, "cat")
    except IndexError as error:
        found = {"exception": type(error).__name__, "message": str(error)}
    exact = docs.find_text_in_document(doc, "cat", match_case=True)
    assert exact == [{"startIndex": expected_start, "endIndex": expected_start + 3}]
    assert found != exact
    record("gdoc_lowercase_expansion", text=original, expected=exact, actual=found)

original = "İ cat sat\n"
matches = docs.find_text_in_document({"body": {"content": [paragraph(original, 1)]}}, "cat")
_, requests = docs._build_replacement_requests(parse_markdown("dog"), matches)
deletion = requests[0]["deleteContentRange"]["range"]
assert deletion == {"startIndex": 4, "endIndex": 7}
assert original[deletion["startIndex"] - 1:deletion["endIndex"] - 1] == "at "
reference = create_find_replace_request("cat", "dog")
assert reference["replaceAllText"]["containsText"] == {"text": "cat", "matchCase": False}
record("unicode_wrong_delete_request", text=original, intended_delete="cat",
       actual_delete="at ", gdoc_delete_range=deletion, workspace_request=reference)

print(json.dumps({"network_used": False, "observations": observations}, indent=2, ensure_ascii=False))
