# Workspace controls for three gdoc Markdown failures

All three inputs produced the expected content through the installed Workspace MCP stdio tool. Independent Google Docs API readback confirmed the text, link destinations, and paragraph bullet state. These are controls for existing findings, not three additional gdoc bugs.

| Same Markdown input | gdoc native result | Workspace native result |
| --- | --- | --- |
| `1234567890. Revenue account` | Text becomes `Revenue account` with list formatting; separate Google PDF verification renders `1. Revenue account`. | Literal `1234567890. Revenue account`, with no bullet/list property. |
| `Read [Finance [Q3]](https://example.com/q3).` | Literal Markdown remains, with no hyperlink. | `Read Finance [Q3].`, with `Finance [Q3]` linked to `https://example.com/q3`. |
| `Open [Budget](https://example.com/report?a=1&amp;b=2).` | Visible label is correct, but destination retains `&amp;` and therefore has an `amp;b` query parameter. | Visible label is correct and destination is `https://example.com/report?a=1&b=2`. |

The operation was `manage_doc_tab(action="populate_from_markdown", tab_id=..., markdown_text=..., replace_existing=True)` with an explicit personal account, on three newly created synthetic scratch Docs. All three actual MCP responses reported `success: true` and `is_error: false`; the server reported 2, 3, and 3 applied native requests respectively. Each case used one MCP population call; fixture creation and independent readback are additional calls. No destination URLs were visited.

Workspace also left two extra blank paragraphs after the content in each fixture: raw body text ends with three newlines. The pass condition ignores trailing paragraph newlines only, so these results establish the targeted text/link behavior, not exact document equivalence or perfect whitespace preservation.

Workspace version 1.26.0 corresponds to the comparison pin `54b1c56f7f9912ce32681460d7ca38f9c2a37564`; gdoc controls use pin `dbfa4c34bfa699ee8dd9839da85eea1fac177d44`. Inputs, expected values, and gdoc controls are in [links-results.json](links-results.json). Full anonymized Workspace readbacks and tool responses are in [workspace-markdown.json](workspace-markdown.json). Account-bearing fixture IDs and snapshots remain under ignored `.local-hunt/r2-workspace-markdown-*`.

Reproduction: run `~/.local/share/uv/tools/workspace-mcp/bin/python hunt/round2/workspace-markdown.py` from the project root, with the installed tools and configured personal credentials. The script reuses its private fixture ledger and skips cases already recorded in its output file. It verifies personal identity before each write. It does not write the report collection, share files, or delete files.
