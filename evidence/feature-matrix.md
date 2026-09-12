# Practical feature parity, command by command

Pinned public upstreams: gdoc `dbfa4c34bfa699ee8dd9839da85eea1fac177d44` (0.21.0), Workspace `54b1c56f7f9912ce32681460d7ca38f9c2a37564` (1.26.0). This is source-verified interface coverage, not a successful live run of every operation. Local gdoc forks are not credited to public upstream.

**Workspace covers far more office apps; gdoc exposes several document-review operations that Workspace cannot perform through its named tools.** “Unavailable” below means unavailable through the inspected interface. Writing an Apps Script, calling Google directly, or adding code changes that boundary and is not counted as feature parity.

Workspace comparison assumes complete tool tier with relevant services enabled. “Direct” means a named operation supports the intention; it does not promise identical defaults, output, fidelity, or Google request count. “Compose” means existing named operations plus client processing. “Absent” means no equivalent exposed operation. CLI setup commands are compared separately from document capabilities.

## Every public gdoc command

Aliases are grouped, internal `_sync-hook`/`_pull-hook` excluded: **39 commands**, including four setup/transport commands. gdoc MCP exposes **30**: 13 classified read-only and 17 write. See [CLI parser][g-cli] and [MCP allowlist][g-mcp].

| gdoc command | Meaningful office capability | Workspace equivalent and boundary | gdoc MCP |
|---|---|---|---|
| `update` | Update installed application | Package-manager upgrade; no equivalent office tool | Absent |
| `mcp` | Serve commands locally over stdio; allowlist/read-only/account options | `workspace-mcp` serves stdio or HTTP; service/tier/individual-tool filters | Server entrypoint |
| `auth` | Login, named account list/remove/default; organization setup URL | `start_google_auth`; broader OAuth/service-account deployment options; different credential administration | Absent; authenticate outside MCP |
| `config` | Default paged/pageless document mode | Server environment configuration; no matching per-user page-mode preference tool | Absent |
| `ls` | Folder listing, Docs/Sheets/all filters | **Direct:** `list_drive_items` with folder/drive controls | Yes |
| `find` | Full-text/title search; `--raw` Google Drive query | **Direct:** `search_drive_files`; richer parameterized controls | Yes |
| `cat` | Markdown/plain/JSON; selected/all tabs; annotated comments; Sheets ranges; past revision | **Direct partly:** `get_doc_as_markdown`, `get_doc_content`, `read_sheet_values`; past revisions absent; all-sheet read requires info + reads | Yes |
| `revisions` (`history`) | Retained milestone IDs, timestamps, recent limit | **Absent:** no retained-revision listing tool | Yes |
| `tabs` | Docs tab tree or workbook worksheets | **Direct:** document content/structure; `get_spreadsheet_info` | Yes |
| `cells` | Rectangular CSV/TSV/stdin writes; ordinary range append; RAW default/formula option | **Direct write:** `modify_sheet_values` accepts 2D arrays and clear; **different append:** `append_table_rows` requires native table ID | **One row per invocation**; file/stdin removed |
| `toc` | Heading outline with deep links; tab selection | **Compose:** retrieve structure and derive headings/links; no dedicated ready-made TOC command | Yes |
| `add-tab` | Add document tab | **Direct:** `manage_doc_tab(create)`; also placement and parent nesting on creation | Yes |
| `edit` | Phrase replacement; Markdown replacement; all/case/typography matching; table cell by label/coordinates; tab selection | **Direct plain global:** `find_and_replace_doc`. **Compose formatted/cell:** inspect ranges + typed operations. No matching normalize/ambiguity abstraction | Yes; old/new file inputs removed |
| `suggest` | Inline Markdown suggested edit; matching/tab controls; never silently direct-edits | **Absent:** no suggestion-write operation; gdoc requires Developer Preview-enrolled OAuth client | Yes, same preview gate |
| `diff` | Current-vs-local or retained-revision word diff; time/revision selectors; HTML/JSON/comments | **Absent history:** no revision retrieval/diff. Current-vs-local can be composed with export + external diff | Revision/time diff only; no local file or HTML output |
| `write` | Replace whole Doc via Markdown import or selected tab; stale-baseline and multi-tab-collapse guards | **Direct differing semantics:** `update_drive_file` content upload or `manage_doc_tab(populate_from_markdown)`; lacks matching stale-baseline guard | Yes, inline Markdown replaces file |
| `insert` | Markdown at selected tab start/end, stale-baseline guard | **Compose/direct subset:** `modify_doc_text`/batch for text/styles; native Markdown tab append path, but converter supports less Markdown | Yes, inline Markdown |
| `pull` | Save Markdown with document/frontmatter metadata; past revision; hooks | **Compose download:** read/export + local write; no corresponding sync metadata/hook system | Absent |
| `push` | Upload frontmatter-linked local file; conflict and tab-collapse controls | **Compose upload:** import/update, but caller implements document binding and baseline checks | Absent |
| `comments` | Open/all resolved threads, formatting | **Direct:** `list_document_comments`; also Sheets/Slides tools | Yes |
| `comment` | Document-level comment; quoted selection with preview/fallback status | **Direct unanchored only:** `manage_document_comment(create)` has no quote/range parameter | Yes |
| `reply` | Reply to thread | **Direct:** `manage_document_comment(reply)` | Yes |
| `resolve` | Resolve thread, optional reply content | **Direct resolve:** manager creates a fixed “This comment has been resolved.” reply; custom accompanying reply is another call | Yes |
| `reopen` | Reopen resolved thread | **Absent:** manager accepts only create/reply/resolve | Yes |
| `delete-comment` | Permanently delete comment with confirmation/force | **Absent:** manager accepts only create/reply/resolve | Yes; true `force` required |
| `comment-info` | One comment by ID | **Compose:** list threads and select ID; no dedicated get-one tool | Yes |
| `images` | Enumerate images/charts/drawings; inspect object; download images | **Compose/subset:** native structure/content exposes objects; caller organizes download; no equivalent image inventory/download abstraction | Inventory only; download removed |
| `export` | PDF/DOCX/HTML/ODT/EPUB etc.; local file or stdout | **Direct/compose:** `export_doc_to_pdf`, Drive download/export URL; getting a URL is not saving the artifact | Absent |
| `insert-image` | Local/public image; anchor/end/raw index; tab; size | **Direct public/Drive source:** `insert_doc_image` takes index; batch `insert_image` adds tab/segment targeting. Local upload + access management separate | Absent |
| `replace-image` | Replace object content in place, preserve size and center-crop | **Absent equivalent:** no replaceImage operation. Delete+insert changes identity and may change layout | Absent |
| `structure` | Native JSON, UTF-16 indices, style/segment/tab filters | **Direct:** `get_doc_content`/`inspect_doc_structure`; outputs and filtering differ | Yes |
| `info` | Title, identity, modified metadata | **Direct/compose:** Drive/document metadata; exact compact output differs | Yes |
| `share` | One person/domain/anyone; reader/commenter/writer; discoverability | **Direct and broader:** `manage_drive_access`, permission inspection, batch grants/revocation/updates | Yes |
| `mkdir` | Create folder, optional parent | **Direct:** `create_drive_folder` | Yes |
| `mv` (`move`) | Move file to folder | **Direct:** `update_drive_file` parent changes | Yes |
| `rename` | Rename file | **Direct:** `update_drive_file(name)` | Yes |
| `drives` | List shared drives | **Direct:** `list_drive_items` shared-drive listing mode | Yes |
| `new` | Blank or Markdown document; folder; page mode | **Direct:** `create_doc` blank/plain or `import_to_google_doc` Markdown; layout mode via additional native operation | Yes; inline content, no local images |
| `cp` | Native file copy, optional folder | **Direct:** `copy_drive_file` | Yes |

Source map: [gdoc CLI][g-cli], [gdoc MCP restrictions][g-mcp], [Workspace Docs][w-docs], [typed batch operation union][w-ops], [Drive][w-drive], [Sheets][w-sheets], [comment dispatcher][w-comments].

## Differences hidden behind apparently shared features

| Concrete intention | gdoc | Workspace | Consequence |
|---|---|---|---|
| Replace a repeated phrase once, or fail if ambiguous | Default edit rejects multiple matches | Find/replace globally replaces matches | Set intentions explicitly; the same text arguments are not equivalent tests |
| Match straight quotes against curly quotes | `edit --normalize` | No corresponding switch | Agent must inspect actual text or supply alternatives |
| Replace with `**approved**` | Parses Markdown and formats replacement | Plain replacement inserts literal asterisks | Equivalent outcome requires a format operation and accurate range |
| Fill cell beside “Budget” | `edit --cell Budget ...` resolves label | Inspect table structure, identify cell, update indexed range | Workspace can achieve ordinary cells, but needs more targeting work |
| Replace ten unrelated placeholders | Ten commands | One `batch_update_doc` call | One shell script can still package gdoc commands into one agent turn |
| Read Doc and comments in one view, selected tab | `cat --comments` cannot combine tab selection | Markdown reader supports comments and selected tab | Workspace has the more direct combined view |
| Create tab under another tab | No exposed parent control in `add-tab` | Parent on `manage_doc_tab(create)` | Workspace-only creation capability |
| Move/reparent an existing Doc tab | No dedicated operation | `rename` and typed `update_doc_tab` change title only | **Neither exposes this**; do not describe Workspace as a general tab-reorganization tool |
| Preserve image object identity during replacement | `replace-image` | No corresponding typed operation | Remove/reinsert is not semantic parity |
| Feed identifiers `00123` or `=SUM(A1:A3)` to Sheets | RAW/literal default | USER_ENTERED default | Defaults can change IDs or execute formulas; choose input mode explicitly |
| Read formulas, notes, and hyperlink metadata | Basic displayed cell values only | Explicit reader flags | gdoc cannot offer an equivalent structural spreadsheet inspection |
| Append to an ordinary populated range | Native Sheets values.append via `cells --append` | Named append requires a native Sheets table | Reading last row then writing is multi-step and races with other appenders |
| Clear a range without resetting formatting | Empty values are possible; no clear command | Native clear operation | Workspace directly expresses clear semantics |
| Review earlier retained revisions | Listing, retrieval, time selectors, rendered diffs | No revision tools | This is a substantive gdoc exclusive, not merely shorter syntax |
| Create a highlighted comment | Preview-based path with explicit unanchored fallback | Create body contains only comment text | Workspace's comments on Sheets/Slides likewise do not take a cell/element anchor |

## Office controls beyond gdoc's surface

Workspace directly exposes native paragraph spacing/alignment, text style ranges, headers/footers, margins/page properties, named ranges, table row/column insertion/deletion, merging/unmerging, column widths, row sizing and pinned header rows. gdoc can create Markdown tables and replace their content, but does not expose those general geometry controls. [Typed operation schemas][w-ops]

Workspace also creates/manages workbooks and worksheets, formats cells and conditional rules, moves/resizes sheet dimensions, and manages native table rows. Neither inspected Sheets interface is a general chart/pivot authoring API. Workspace's Apps Script escape hatch requires writing and running a program; it is not a direct chart command. [Sheets source][w-sheets]

Workspace handles Gmail, Calendar, Contacts, Tasks, Forms, Slides, Chat, Apps Script, and Custom Search. gdoc does not. Slides and Forms batch updates expose native Google request structures; an agent must still construct correct layouts/question operations. Count an API primitive as available, but do not equate it with a polished document/deck-design workflow. [Tier inventory][w-tiers]

## Boundaries that matter for an office agent

- **CLI and MCP are different products in gdoc.** Its no-local-files restriction is deliberate isolation, but removes bulk cell-file input, image editing, exports, and local revision artifacts. A shell-equipped agent regains those capabilities through the CLI.
- **Neither Markdown round trip is a universal preservation mechanism.** Re-importing document content can discard topology or native objects outside the conversion format. Native copy followed by small indexed changes is a different operation from export/edit/import.
- **gdoc's local image insertion temporarily publishes the uploaded image.** Its parser explicitly documents a temporary public-read Drive file deleted after insertion. This convenience is not suitable for every confidential image policy without changing the upload route. Workspace's image insertion accepts a Google-retrievable URL/Drive source; it does not solve arbitrary private-image hosting automatically. [gdoc image options][g-cli], [Workspace image tool][w-docs]
- **Permissions are not comments.** Workspace can revoke file access; that does not mean it can delete/reopen a discussion thread. The previous comparison incorrectly credited comment deletion to Workspace.

[g-cli]: https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/cli.py#L3673
[g-mcp]: https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/mcp.py
[w-docs]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/gdocs/docs_tools.py
[w-ops]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/gdocs/operation_schemas.py
[w-drive]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/gdrive/drive_tools.py
[w-sheets]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/gsheets/sheets_tools.py
[w-comments]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/core/comments.py#L37
[w-tiers]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/core/tool_tiers.yaml
