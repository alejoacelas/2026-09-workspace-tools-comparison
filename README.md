# Google office tools comparison

[Read the side-by-side comparison](COMPARISON.md) · [Compare actual command names](COMMANDS.md) · [Local installation and authorization status](SETUP.md).

Workspace MCP is the broader office connector; gdoc is a useful document-review companion for shell-capable agents. The report compares feature coverage, agent calls, underlying Google API executions, collaboration behavior and deployment. It uses public source and synthetic tests, with no live Google account operations.

The upstream snapshots are Workspace MCP `54b1c56f7f9912ce32681460d7ca38f9c2a37564` and gdoc `dbfa4c34bfa699ee8dd9839da85eea1fac177d44`, inspected September 12, 2026. Local clones live in the ignored `repos/` directory; their upstream remotes remain intact.

## Evidence

- [Call-count probe](probe-calls.py) and [results for gdoc](gdoc-call-probes.json) / [Workspace](workspace-call-probes.json) distinguish agent operations from Google API executions.
- [Markdown probe](probe-markdown.py) and [gdoc output](gdoc-markdown-probe.json) / [Workspace output](workspace-markdown-probe.json) characterize a UTF-16 indexing difference.
- [Inventory](inventory.json) records configured tool names and pinned revisions.
- [gdoc test output](gdoc-tests.txt) and [Workspace test output](workspace-tests.txt) record 459 and 144 selected passing upstream tests.

## Reproduce

Clone into an empty `repos/` directory and select the inspected revisions:

```sh
mkdir -p repos
git clone https://github.com/taylorwilsdon/google_workspace_mcp.git repos/google-workspace-mcp
git -C repos/google-workspace-mcp checkout 54b1c56f7f9912ce32681460d7ca38f9c2a37564
git clone https://github.com/LucaDeLeo/gdoc.git repos/gdoc
git -C repos/gdoc checkout dbfa4c34bfa699ee8dd9839da85eea1fac177d44
```

Install each checkout's dependencies:

```sh
(cd repos/gdoc && uv sync --frozen --extra dev)
(cd repos/google-workspace-mcp && uv sync --frozen --extra test)
```

Run the synthetic probes from this project directory. They replace Google services with mocks, use invented document data, and do not need credentials:

```sh
repos/gdoc/.venv/bin/python probe-calls.py gdoc
repos/google-workspace-mcp/.venv/bin/python probe-calls.py workspace
repos/gdoc/.venv/bin/python probe-markdown.py gdoc
repos/google-workspace-mcp/.venv/bin/python probe-markdown.py workspace
```

The Markdown assertions characterize these exact snapshots, including Workspace's incorrect heading end index; an upstream fix will require updating that expectation. The call probe excludes OAuth wrappers, retries, pagination beyond one page and resumable-upload exchanges. It is not a performance or integration test.

The selected upstream tests were:

```sh
(cd repos/gdoc && GDOC_AUTO_UPDATE=0 .venv/bin/python -m pytest -q -o addopts= \
  tests/test_edit.py tests/test_edit_cell.py tests/test_suggest.py \
  tests/test_anchored_comment.py tests/test_cat.py tests/test_cat_tabs.py \
  tests/test_write.py tests/test_mcp.py tests/test_sheets_cmd.py \
  tests/test_docs_batch.py tests/test_structure.py tests/test_new_file.py)

(cd repos/google-workspace-mcp && .venv/bin/python -m pytest -q \
  tests/gdocs/test_semantic_anchors.py tests/gdocs/test_batch_metadata.py \
  tests/gdocs/test_docs_markdown_writer.py tests/gdocs/test_read_tab_selection.py \
  tests/gdocs/test_suggestions_view_mode.py tests/gsheets/test_read_sheet_values.py \
  tests/gsheets/test_format_sheet_range.py tests/gmail/test_search_gmail_messages_headers.py \
  tests/gmail/test_batch_modify_label_verification.py)
```

## Plan

1. Clone upstream repositories, pin revisions, and inventory supported services and operations.
2. Trace representative office workflows to count agent interactions and underlying API requests, including batching and verification.
3. Produce a source-linked comparison and practical recommendations, clearly separating inspected behavior from live validation.

[Run overview](OVERVIEW.md) · [Run log](RUN-LOG.md) · [Session record](REPLICATE.md).
