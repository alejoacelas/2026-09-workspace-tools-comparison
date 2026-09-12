# Drive file operations: bounded live check

**All 15 checks passed.** Within this small synthetic workspace, gdoc preserved punctuation and Unicode in names, copied the intended document into a distinct file, moved only the copy, and listed/searched the expected files. No new bug was found in this area.

The [probe](drive-operations.py) used pinned gdoc 0.21.0 (`dbfa4c34bfa699ee8dd9839da85eea1fac177d44`) against the authorized personal account. It created one dedicated test folder, one child folder, one simple document and one copy. Google Drive metadata supplied the exact-name, parent and identity oracle; native Docs body text supplied the copy-content oracle. [All results](drive-operations.json)

| Checks | Inputs or operation | Result |
|---|---|---|
| 1–3: ordinary setup and folder naming | Standard root folder; child `Owner's archive (Σ)`; document `Budget draft` | Exact names and intended parents verified |
| 4–5: apostrophe | Rename to `Director's notes`, then scoped exact-name search | Name preserved; search finds precisely the source file |
| 6–7: backslash | Rename to `Archive\2026`, then scoped exact-name search | Literal backslash preserved; correct file found |
| 8–9: parentheses | Rename to `Plan (Q4)`, then scoped exact-name search | Name preserved; correct file found |
| 10–11: Unicode | Rename to `Café Σ budget`, then scoped exact-name search | Accented letter and Greek sigma preserved; correct file found |
| 12: copy | Copy to a name combining apostrophe, backslash, parentheses and sigma | New identity; exact requested name; body equals source; source name unchanged; copy initially in source folder |
| 13: move | Move copy into child folder | Copy has exactly the destination parent; source remains in root test folder |
| 14: repeated move | Move same copy to same destination again | Succeeds and retains destination parent |
| 15: scoped listings | List both test folders | Returned identity sets equal native Drive's folder-scoped results |

## CLI contracts and limits

- `mkdir TITLE --parent FOLDER` and `new TITLE --folder FOLDER` accept an explicit containing folder.
- `rename DOC TITLE`, `cp DOC TITLE`, and `mv DOC FOLDER` address the source by ID or URL. These tests supplied known IDs, so duplicate display names were not used as identity selectors.
- `ls FOLDER` scopes the listing to that folder.
- Normal `find` and `find --title` have **no folder-selection argument** in this pinned version. To avoid scanning unrelated files, the probe used `find QUERY --raw` with an explicit parent condition and exact `name = ...`. It exercised gdoc's actual `_escape_query_value` helper when constructing the name literal. This tests literal escaping and the exposed raw-query route, **not** an invocation of ordinary unscoped `find --title`.
- `cp` exposes no destination-folder argument. The copy inherited the source folder in this fixture; `mv` then moved it explicitly.

These are case-specific checks, not a reliability rate or proof for all filenames. They do not cover shared drives, permissions, shortcuts, huge folders or pagination, concurrent moves, duplicate-name search selection, or every possible Unicode normalization. We deliberately did not treat Drive's `contains` token/prefix behavior as a bug: all name-search comparisons used exact equality.

Every mutation selected and verified the authorized account. Every list/search query was restricted to the dedicated root or child folder. No permissions, sharing, permanent deletion, collection changes or real office documents were involved. IDs stay in the ignored `.local-hunt/r2-drive-ledger.json`; public evidence contains only synthetic names and normalized scope labels.

Run with Workspace's installed Python:

```sh
~/.local/share/uv/tools/workspace-mcp/bin/python hunt/round2/drive-operations.py
```

Rerunning creates another dedicated synthetic folder and its fixtures; it does not delete previous ones. The bounded hypotheses are exhausted, so this area should be recorded as passing rather than expanded merely to search for a failure.
