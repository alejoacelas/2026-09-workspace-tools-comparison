# Google Workspace MCP vs gdoc for everyday office work

**Choose Workspace MCP as the general office connector; choose gdoc as a document-review companion to a shell-capable agent.** If email and calendar are already covered by another integration, gdoc's revision diffs, concise output, and text-oriented editing become more valuable. If the agent must handle inboxes, meetings, spreadsheets, and presentations through one connector, Workspace MCP covers much more.

Both repositories were cloned and inspected on **12 September 2026**. This evaluates the public upstreams, not any local fork or installed version.

| Snapshot | Workspace MCP | gdoc |
|---|---|---|
| Repository | [taylorwilsdon/google_workspace_mcp][w-repo] | [LucaDeLeo/gdoc][g-repo] |
| Checked-out revision | `54b1c56`, v1.26.0, September 6 | `dbfa4c3`, v0.21.0, August 27 |
| Main interface | MCP server over stdio or HTTP; CLI client connects to that server | Direct CLI; optional local stdio MCP server |
| Tool surface | 122 entries in the tier configuration; importing all service modules registers 123 including a diagnostic tool | 30 MCP tools; additional CLI commands for local files and setup |
| Scope | 12 service groups, including Apps Script and Custom Search | Google Docs, Drive, and basic Sheets |
| Runtime dependencies declared | 18 | 4 |
| Public project size at inspection | 3,146 stars; 982 forks | 17 stars; 5 forks |

Tool and dependency counts come from [Workspace's tier file][w-tiers], [package metadata][w-package], [gdoc's MCP registry][g-mcp], and [package metadata][g-package]. Stars and forks describe adoption, not reliability. The tier file includes an authentication tool, and its service counts are not perfectly comparable to gdoc's command counts.

## Feature coverage

| Office task | Workspace MCP | gdoc |
|---|---|---|
| Find, read, create, copy and share documents | Yes; rich Drive queries, imports, permissions and batch sharing | Yes; short commands, URLs accepted, Markdown/file workflows |
| Read documents with comments | Markdown with inline references or comment appendix; all tabs or a selected tab | Line-numbered Markdown with inline threads; `--comments` cannot be combined with `--tab` or `--all-tabs` |
| Change ordinary wording | Plain global find/replace; indexed and batched edits; text/heading anchors for insertions | Find/replace with Markdown formatting; optional smart-quote/dash normalization; rejects ambiguous matches unless `--all` |
| Edit native layout | Extensive text/paragraph styles, headers/footers, page/section properties, tables, rows/columns and cell styles | Markdown formatting, native tables, named/coordinate cell replacement, page/pageless mode; narrower layout controls |
| Manage document tabs | Create, rename, delete, nest, populate from Markdown | List/read, add, and insert/replace content by tab; fewer topology controls |
| Review revisions | No dedicated retained-revision listing/diff workflow found | Revision selectors, word diffs, HTML diff artifacts, past-revision reads |
| Make suggested edits | Reads suggestion views; no exposed suggest-write operation found | `suggest`, gated on Developer Preview; verifies returned suggestions |
| Comments and discussion | List, add, reply, resolve and delete on Docs/Sheets/Slides; new comments are document-level | Docs-oriented comment/reply/resolve/reopen; quote-based anchoring with preview access and explicit fallback status |
| Spreadsheet values | Read/write/clear ranges; formula reads, notes/hyperlinks, error reporting | Read tabs/ranges/all tabs; CSV/TSV imports; append rows; formula writes with `--user-entered` |
| Spreadsheet structure and formatting | Create workbooks/tabs; duplicate/move/resize; formatting, conditional rules, native table rows | No first-class workbook creation, cell formatting, conditional formatting or chart tools |
| Presentations | Create/read, raw batch updates, geometry, speaker notes, slide thumbnails, comments; import PPTX | No dedicated presentation tools |
| Email and meetings | Gmail search/read/draft/send/reply/forward/attachments/labels/filters; Calendar events, recurrence, free/busy, Meet links | Not supported |
| Other office services | Contacts, Tasks, Forms, Chat, Apps Script, Custom Search | Not supported |
| Local document workflow | Import files through server-accessible paths, URLs or content | Pull/edit/diff/push, local PDF/DOCX exports, image downloads and insertion |

Sources: [Docs tools and operation schemas][w-docs], [Workspace services][w-tiers], [Sheets implementation][w-sheets], [Slides implementation][w-slides], [gdoc commands][g-cli], [gdoc Docs implementation][g-docs], and [revision implementation][g-revisions].

**Breadth does not imply polished authoring in every app.** Workspace's Slides tool takes native Google API batch requests: an agent still needs to construct a layout or import a prepared presentation. Its Sheets tools do not expose every Sheets API feature; a custom Apps Script is an additional programming workflow, not equivalent to a ready-made chart/pivot tool. gdoc's basic Sheets support is useful for reading trackers and updating values, but does not replace a spreadsheet authoring integration.

## How many agent calls?

These are **successful tool invocations or CLI command executions**, with authentication complete and identifiers/content already available unless the row says otherwise. They exclude help/schema discovery, model reasoning, retries and human review. Counts are inferred from supported interfaces; several underlying request paths were also exercised with synthetic API responses.

| Operation | Workspace MCP | gdoc CLI | gdoc MCP |
|---|---:|---:|---:|
| Read a known document | 1 | 1 | 1 |
| Read a known document with comments | 1 | 1 | 1 |
| Create a formatted document from prepared Markdown, without images | 1: `import_to_google_doc` | 1: `new --file` | 1: `gdoc_new` with inline text |
| Replace one phrase everywhere, without adding formatting | 1: `find_and_replace_doc` | 1: `edit --all` | 1 |
| Replace 10 different template placeholders | 1: `batch_update_doc` with 10 `find_replace` operations | 10 edits | 10 edits |
| Share one file with five people | 1: `manage_drive_access`, `grant_batch` | 5 shares | 5 shares |
| Read one known spreadsheet range, up to 1,000 rows | 1 | 1 | 1 |
| Write a rectangular 100-row spreadsheet dataset | 1 | 1, from CSV/TSV | **100**, one row per call |
| Read 5,000 rows from one known worksheet | 5 range reads | 1 | 1, possibly large output |
| Read all worksheets of an unknown workbook with three small tabs | 4: workbook info + 3 range reads | 1: `cat --all-tabs` | 1 |
| Search, read, change one phrase, then read back | 4 | 4 | 4 |
| Copy a template, fill 10 placeholders, share with five reviewers | 3; add 1 for content read-back | 16; add 1 for read-back | 16; add 1 for read-back |
| Compare a document's latest two retained revisions | No dedicated operation | 1: `diff --rev prev` | 1 |
| Search and read 20 emails | 2: search + batch content read | Unsupported | Unsupported |
| Check several calendars for availability, then create an event | 2: free/busy + create | Unsupported | Unsupported |
| Create a deck from a prepared PPTX | 1 import | Unsupported | Unsupported |

The **100-row gdoc MCP difference is real interface narrowing**: the MCP wrapper hides `--file` and `--stdin`; its remaining `value` parameter becomes exactly one row in `_read_cell_rows`. The CLI has no such restriction. Likewise, gdoc MCP omits export, pull/push, image insertion and image replacement tools. See [wrapper restrictions][g-mcp] and [row input handling][g-rows].

Workspace's range reader clamps reads to **1,000 rows**. gdoc's all-worksheet read uses one Sheets `batchGet` internally, after obtaining workbook metadata. These are different optimizations: Workspace bounds output per call; gdoc offers a convenient whole-workbook operation. See [range limit][w-sheet-helpers] and [gdoc's spreadsheet reader][g-sheet-reader].

**A shell call is not the same as an agent round trip.** A coding agent can put ten gdoc commands in one shell script and return only a summary; similarly it can script Workspace's CLI/MCP client. That reduces model interactions, but leaves ten underlying operations. With ordinary MCP tool calling, the differences in the table are much more consequential. Neither side gets credited with arbitrary custom API code as a built-in operation.

## Google requests hidden inside each call

The following counts were reproduced by [a runnable probe](probe-calls.py), substituting synthetic responses at the Google client boundary. They count **API method executions**, not OAuth requests, network connection setup, upload chunks, retries, or quota units. Each comment list fits one page; no errors, images, shortcuts or extra formatting cleanup occur. This is not a latency benchmark.

| One agent operation | Workspace MCP | gdoc, previously seen file | gdoc, first interaction | gdoc `--quiet` |
|---|---:|---:|---:|---:|
| Read Doc as Markdown, no comment content | 1 | 3 | 4 | 2 |
| Read Doc with comment content | 2 | 4 | 5 | 3 |
| Replace one plain phrase | 1 | 6 | 7 | 4 |
| Read a Sheets range | 1 | 4 | 5 | 3 |
| Write a Sheets range | 1 | 4 | 5 | 2 |

Workspace uses `get_doc_as_markdown` with comments disabled for the first row; its separate `get_doc_content` uses two requests on a native Doc. Operation choice matters.

A normal gdoc edit makes these six calls:

1. Fetch Drive version metadata.
2. Fetch comment changes.
3. Fetch document structure and revision to locate the text.
4. Send a revision-pinned formatted replacement batch.
5. Read the result to detect paragraph cleanup needs.
6. Fetch the new Drive version for local awareness state.

A first interaction adds title/owner metadata. Required paragraph cleanup and native-table insertion add more requests. `--quiet` skips awareness reads, but is not a universal “subtract two” switch: reading with `cat` still needs MIME detection, and guarded overwrites still check their baseline. See [awareness implementation][g-notify], [replacement implementation][g-replace], and [probe results](gdoc-call-probes.json).

Workspace's ten-placeholder batch makes **three requests**: revision metadata, one batch update, and a result read. The ten equivalent warm gdoc edits make **60** on the simple path above. They are not semantically identical: gdoc reconstructs formatted replacements and pins the initial write to a revision, whereas Workspace's plain replacements use the native `replaceAllText` operation. See [batch manager][w-batch] and [Workspace probe results](workspace-call-probes.json).

Creating a small Markdown document without images is one Drive upload in gdoc; Workspace's import additionally resolves/checks the destination folder, making two API method executions. For email, searching and reading 20 results takes two agent calls but **21 logical Google operations**: one search plus 20 message gets bundled into one HTTP batch. Workspace chunks content batches at 25. “One batch” does not mean one operation for quota purposes. See [gdoc creation][g-create], [Workspace import][w-import], and [Gmail batching][w-gmail].

## Document fidelity and collaboration

**gdoc provides a better ready-made review workflow, but neither tool guarantees lossless editing.** Its advantages include change banners, refusal of stale whole-document overwrites, native cell targeting by label, retained-revision diffs, and the preview-gated `suggest` command. `edit` warns about changes since the last read and pins its main batch to the revision it just fetched; later cleanup/table batches are not all pinned. Whole-document Markdown import reconstructs content, so it should not be treated as a lossless round trip of an elaborate template. Sources: [gdoc write/edit commands][g-cli], [Docs mutations][g-docs].

Workspace's native Docs controls are substantially broader. It can batch unrelated replacements and formatting operations, manipulate table geometry, and edit headers, footers and section properties. It also has semantic insertion anchors, so not every edit requires the model to calculate indices. Its batch implementation reads revision IDs and returns a post-write snapshot, but **does not submit `requiredRevisionId`** on that batch: revision reporting is not a concurrency guard. Sources: [operation schemas][w-operations], [batch manager][w-batch].

Three limitations materially affect office use:

1. **Suggestions and anchored comments need special access in gdoc.** `suggest` requires the OAuth client project to be enrolled in Google's Developer Preview and fails closed if it cannot establish support. Quoted comments fall back to unanchored Drive comments when the preview path is unavailable. Workspace's exposed comment writer creates document-level comments, not highlighted text anchors. These are the implementations at the pinned revisions, not promises about availability on every Google account. Sources: [suggest implementation][g-suggest], [comment command][g-comment], [Workspace comments][w-comments].
2. **Multi-tab defaults differ.** Workspace's Markdown reader walks document tabs. gdoc's ordinary `cat` uses Drive export; its documentation identifies that as first-tab-only, with `--all-tabs` for the Docs API path. gdoc prevents an ordinary whole-document write from collapsing multiple tabs unless explicitly overridden. Its comment-annotated view cannot be combined with tab selection. Sources: [Workspace reader][w-markdown-reader], [gdoc reader/write commands][g-cli].
3. **Workspace's native Markdown-to-tab converter has a reproducible Unicode-index defect.** For `# Plan 😀` followed by `Next`, it calculates a heading end index of 8, while Google's UTF-16 indexing requires 9; subsequent insertions are also shifted. gdoc's converter uses 9. The [reproducer](probe-markdown.py) and [Workspace output](workspace-markdown-probe.json) demonstrate request generation only, without a live write. This affects `populate_from_markdown`'s converter, not every Workspace editing tool or the separate Drive import path. That same converter documents no GFM-table/strikethrough support and renders images as linked alt text. Use native table/image tools or an appropriate import path instead. Sources: [Workspace converter][w-converter], [gdoc converter][g-converter].

The isolated converter finding is useful evidence against assuming fidelity, not a basis for declaring an overall failure rate. Neither repository was tested against a representative collection of real office documents here.

## Agent ergonomics and deployment

| Consideration | Workspace MCP | gdoc |
|---|---|---|
| Shell-capable agent | Verbose named tools and JSON arguments; CLI requires a running server | Short commands, pipes, Markdown files, CSV/TSV and stable JSON/plain output |
| Local MCP client | Native stdio support | Built-in stdio wrapper with 30 tools |
| Remote connector | HTTP transport and OAuth flows; deployable centrally | No built-in HTTP transport; requires a local process-launching client or an additional bridge |
| Tool discovery/context | 45 core entries, 91 through extended, 122 through complete; service filters and individual disable list | Smaller default surface; `--allow` and `--read-only` narrow it further |
| Large content | Field masks, structure summaries, bounded Sheets reads; file imports avoid putting all bytes into model context | `--max-bytes`, `--no-images`, selected tabs/ranges, terse output, file-based workflows |
| Accounts/team use | Multiple auth/deployment modes, per-user identity, service accounts and gateway support | Named local accounts and a shared OAuth-client onboarding path |
| Read-only controls | Filters tools and requests read-only scopes; per-service permission levels | Filters commands/tools; normal authentication still requests Drive and Docs write scopes |
| Installation footprint | Python plus web/MCP/auth stack, persistent server or hosted deployment | Smaller Python CLI; MCP adds no dependency |
| Declared license | MIT | No license file or package license declaration found in this checkout |

Sources: [Workspace CLI][w-cli], [server flags][w-main], [permission implementation][w-permissions], [gdoc MCP][g-mcp], [gdoc auth scopes][g-auth], and package metadata linked above. Client compatibility here means matching transport capabilities; this was **not** a live Claude Cowork/desktop integration test.

There is no defensible universal token-cost winner from source inspection alone. gdoc has concise prose output and easy local filtering, but Workspace also emits Markdown and offers service/tier filtering. A client with dynamic tool discovery pays a different schema cost from one that loads every tool up front. Long documents and repeated model turns can dominate both. No tokenizer, model-task benchmark, or wall-clock API benchmark was run.

Workspace's README advertises “Code Mode,” but a case-insensitive source search found that phrase only in the README, with no corresponding executable feature in the inspected entrypoints. This report credits the working CLI and batch operations, not that unverified claim.

## Recommendation

1. **One connector for a general office assistant: Workspace MCP.** Gmail, Calendar, Sheets formatting, presentation imports and multi-operation batches outweigh gdoc's stronger document-review conveniences. Expose only the service groups the assistant actually needs.
2. **A coding agent already equipped for mail/calendar: gdoc is a useful addition.** Its best use is reviewing and revising Google Docs with comments, revision diffs, Markdown files and explicit text anchors. Basic spreadsheet value updates also fit well through the CLI.
3. **A chat/desktop workflow without shell access: prefer Workspace MCP.** gdoc's MCP wrapper loses bulk multi-row input and several local-file features, and it cannot itself serve a remote HTTP connector. A local stdio client can still use its document-review tools.
4. **For your likely mixed workflow: keep Workspace for broad office operations and gdoc for document review.** Route tasks explicitly so the agent does not arbitrarily choose between duplicate document tools. Use Workspace's native style/layout tools when the document task exceeds gdoc's editing surface.

## What was verified

- Both upstream repositories were cloned at the revisions above and remain available in `repos/`; no upstream tracked files were changed.
- [Inventory](inventory.json) records configured tools and source test counts; registration checks returned 123 Workspace tools and 30 gdoc tools.
- **459 selected gdoc tests and 144 selected Workspace tests passed.** They cover document edits, comments/suggestions, tab handling, MCP, Sheets, Markdown conversion and selected Gmail paths. These were existing, mostly mocked unit tests, not equal-sized comparative benchmarks or whole-suite certifications. [gdoc output](gdoc-tests.txt), [Workspace output](workspace-tests.txt).
- **25 synthetic call-count scenarios** passed assertions, plus two converter-characterization runs. [Call probe](probe-calls.py), [Markdown probe](probe-markdown.py).
- No private Google data, authenticated Google API operations, permission changes, or live document mutations were used. Real-world fidelity, latency, OAuth onboarding and sustained multi-user operation remain unmeasured.

[Reproduction instructions and project overview](README.md).

[w-repo]: https://github.com/taylorwilsdon/google_workspace_mcp
[g-repo]: https://github.com/LucaDeLeo/gdoc
[w-tiers]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/core/tool_tiers.yaml
[w-package]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/pyproject.toml
[g-package]: https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/pyproject.toml
[g-mcp]: https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/mcp.py
[w-docs]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/gdocs/docs_tools.py
[w-sheets]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/gsheets/sheets_tools.py
[w-slides]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/gslides/slides_tools.py
[g-cli]: https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/cli.py
[g-docs]: https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/api/docs.py
[g-revisions]: https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/api/revisions.py
[g-rows]: https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/cli.py#L726
[w-sheet-helpers]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/gsheets/sheets_helpers.py#L23
[g-sheet-reader]: https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/cli.py#L120
[g-notify]: https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/notify.py#L62
[g-replace]: https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/api/docs.py#L1542
[w-batch]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/gdocs/managers/batch_operation_manager.py
[g-create]: https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/api/drive.py#L231
[w-import]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/gdrive/drive_tools.py#L1332
[w-gmail]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/gmail/gmail_tools.py#L1913
[w-operations]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/gdocs/operation_schemas.py
[g-suggest]: https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/api/docs.py#L1932
[g-comment]: https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/cli.py#L2307
[w-comments]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/core/comments.py
[w-markdown-reader]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/gdocs/docs_tools.py#L2575
[w-converter]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/gdocs/docs_markdown_writer.py
[g-converter]: https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/mdparse.py
[w-cli]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/core/cli.py
[w-main]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/main.py
[w-permissions]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/auth/permissions.py
[g-auth]: https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/auth.py#L25
