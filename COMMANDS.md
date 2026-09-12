# Workspace MCP tools vs gdoc CLI commands

Workspace exposes **named MCP tools**; gdoc exposes **shell subcommands**. The names below are the actual interfaces, not invented workflow labels. This comparison uses Workspace MCP 1.26.0 and gdoc 0.21.0.

Workspace's word **core** is also a specific launch tier: **C** below means core, **E** extended, and **F** complete. Extended includes core; complete includes both. gdoc has no tiers. Some essential office operations, including drafting email, replacing text and sharing files, are outside Workspace's core tier.

## Everyday command equivalents

Arguments are abbreviated: `DOC` and `SHEET` are IDs or URLs in gdoc. Workspace uses named parameters such as `document_id`, `spreadsheet_id`, and `user_google_email`.

| What you want to do | Workspace MCP tool(s) | gdoc CLI |
|---|---|---|
| Search Drive files | `search_drive_files` **C** | `gdoc find QUERY` |
| List a folder / shared drives | `list_drive_items` **E** | `gdoc ls FOLDER`; `gdoc drives` |
| Read a document | `get_doc_content` **C**; `get_doc_as_markdown` **E** | `gdoc cat DOC` |
| Read a document with its comments | `get_doc_as_markdown` **E**, comments included by default | `gdoc cat DOC --comments` |
| Inspect native document structure | `inspect_doc_structure` **F** | `gdoc structure DOC` |
| Get document metadata / outline | `get_doc_content` **C** and `inspect_doc_structure` **F**, depending on information needed | `gdoc info DOC`; `gdoc toc DOC` |
| Create a document | `create_doc` **C**, initial content is plain text | `gdoc new TITLE` |
| Create from Markdown | `import_to_google_doc` **C** | `gdoc new TITLE --file draft.md` |
| Import Word/HTML/other office files | `import_to_google_doc` **C** | No general DOCX/HTML import command; Markdown input is the supported route |
| Replace a phrase | `find_and_replace_doc` **E**, global text replacement | `gdoc edit DOC OLD NEW`; `--all` for multiple matches |
| Replace many different phrases together | `batch_update_doc` **F**, list of `find_replace` operations | Multiple `gdoc edit` commands; one `--all` only repeats the same replacement |
| Insert text / apply inline formatting | `modify_doc_text` **C**; `batch_update_doc` **F** for compound changes | `gdoc edit DOC OLD '**new**'`; `gdoc insert DOC file.md --tab NAME` |
| Change paragraph/native layout | `update_paragraph_style` **E**; `batch_update_doc` / `update_doc_headers_footers` **F** | Markdown-based edits and page/pageless options; no comparable general style command |
| Edit/create a native table | `create_table_with_data`, `batch_update_doc` **F** | `gdoc edit DOC --cell LABEL VALUE`; Markdown tables in replacements |
| Read/manage document tabs | `get_doc_content` **C**; `manage_doc_tab` **F** creates/renames/deletes/populates | `gdoc tabs DOC`; `gdoc cat DOC --all-tabs`; `gdoc add-tab DOC TITLE`; `gdoc write DOC file.md --tab NAME` |
| Overwrite document content | `update_drive_file` **E**; `manage_doc_tab` **F** for one tab | `gdoc write DOC file.md` |
| Copy a template | `copy_drive_file` **E** | `gdoc cp DOC TITLE` |
| Share with a person / several people | `manage_drive_access` **E**, including `grant_batch` | `gdoc share DOC EMAIL`; one target per command |
| Inspect/revoke/change permissions | `get_drive_file_permissions` **F**; `manage_drive_access` **E** | No equivalent permission-list/revoke workflow |
| Create folders / move / rename files | `create_drive_folder` **C**; `update_drive_file` **E** | `gdoc mkdir TITLE`; `gdoc mv DOC FOLDER`; `gdoc rename DOC TITLE` |
| List comments | `list_document_comments` **E** | `gdoc comments DOC`; `gdoc comment-info DOC ID` |
| Add/reply/resolve comments | `manage_document_comment` **E**, action parameter | `gdoc comment`; `gdoc reply`; `gdoc resolve`; also `reopen`, `delete-comment` |
| Suggest an edit for acceptance | No exposed equivalent | `gdoc suggest DOC OLD NEW` — requires Google Developer Preview |
| Review version history / changes | No dedicated equivalent | `gdoc revisions DOC`; `gdoc diff DOC --rev prev`; `gdoc cat DOC --revision REV` |
| Download/edit/upload local Markdown | Separate read/import/update tools; no matching sync abstraction | `gdoc pull DOC file.md`; `gdoc diff DOC file.md`; `gdoc push file.md` |
| Export a rendered document | `export_doc_to_pdf` **E**; `get_drive_file_download_url` **C** with export format | `gdoc export DOC --out report.pdf` or `.docx`, `.html`, etc. |
| Insert/replace/inspect images | `insert_doc_image` **F**; native structure inspection; no matching dedicated image-replacement tool | `gdoc images`; `gdoc insert-image`; `gdoc replace-image` |
| Read spreadsheet cells | `read_sheet_values` **C** | `gdoc cat SHEET --tab Data --range A1:D20` |
| Write/clear spreadsheet cells | `modify_sheet_values` **C** | `gdoc cells SHEET A1 --file rows.csv`; literal values by default, `--user-entered` for formulas |
| Append spreadsheet rows | `append_table_rows` **F**, for a native Sheets table | `gdoc cells SHEET A1 --append --file rows.csv`, ordinary range append |
| Create a workbook / manage worksheets | `create_spreadsheet` **C**; `create_sheet` / `manage_sheet_tab` **F** | No equivalent workbook/worksheet creation command (`add-tab` is for Docs) |
| Format spreadsheet cells | `format_sheet_range` **E**; `manage_conditional_formatting`, `resize_sheet_dimensions` **F** | No equivalent |
| Create/read/edit slide decks | `create_presentation`, `get_presentation` **C**; `batch_update_presentation` **E** | No dedicated Slides commands |
| Import a prepared spreadsheet/deck | `import_to_google_sheets`, `import_to_google_slides` **C** | No XLSX/PPTX import command |
| Search/read email | `search_gmail_messages`, `get_gmail_message_content`, `get_gmail_messages_content_batch` **C** | Not supported |
| Draft/send/reply/forward email | `draft_gmail_message` **E**; `send_gmail_message` **C** | Not supported |
| Manage email labels/filters | `modify_gmail_message_labels`, `manage_gmail_label`, `manage_gmail_filter` **E**; batch label updates **F** | Not supported |
| Read/create/change calendar events | `list_calendars`, `get_events`, `manage_event` **C** | Not supported |
| Check availability | `query_freebusy` **E** | Not supported |
| Manage tasks and contacts | `list_tasks`, `manage_task`, `search_contacts`, `manage_contact` **C** | Not supported |
| Create/read forms and responses | `create_form`, `get_form` **C**; `list_form_responses` **E**; `batch_update_form` **F** | Not supported |

gdoc's everyday commands are `find`, `cat`, `edit`, `new`, `write`, `diff`, `comments`, `share`, and `cells`. Workspace uses separate tool families for each app, with management tools taking an `action` and batch tools taking operation lists.

## Invocation

An MCP-connected agent calls Workspace tools directly:

```text
get_doc_as_markdown(user_google_email="you@example.com", document_id="DOC")
find_and_replace_doc(user_google_email="you@example.com", document_id="DOC", find_text="old", replace_text="new")
```

The installed native CLI is a client for a **running HTTP MCP server**:

```sh
workspace-cli list
workspace-cli call get_doc_as_markdown user_google_email=you@example.com document_id=DOC
```

Those commands do not themselves start an HTTP server. A stdio MCP registration lets the agent launch Workspace on demand without running a background daemon. gdoc connects to Google directly:

```sh
gdoc cat DOC --account you@example.com
gdoc edit DOC 'old' 'new' --account you@example.com
```

## Complete Workspace tool inventory

The following table is generated from the upstream tier configuration, preserving every configured name. The local office setup exposes the complete tiers for Gmail, Drive, Calendar, Docs, Sheets, Slides, Forms, Tasks and Contacts: **99 tools**. Chat, Custom Search and Apps Script remain available in the installed package but are not enabled in that registration; they have additional setup or specialized use cases.

| Service | Core | Added by extended | Added by complete |
|---|---|---|---|
| gmail | `search_gmail_messages`; `get_gmail_message_content`; `get_gmail_messages_content_batch`; `send_gmail_message` | `get_gmail_attachment_content`; `get_gmail_thread_content`; `modify_gmail_message_labels`; `list_gmail_labels`; `manage_gmail_label`; `draft_gmail_message`; `list_gmail_filters`; `manage_gmail_filter` | `get_gmail_threads_content_batch`; `batch_modify_gmail_message_labels`; `start_google_auth` |
| drive | `search_drive_files`; `get_drive_file_content`; `get_drive_file_download_url`; `create_drive_file`; `create_drive_folder`; `import_to_google_doc`; `import_to_google_slides`; `import_to_google_sheets`; `get_drive_shareable_link` | `list_drive_items`; `copy_drive_file`; `update_drive_file`; `manage_drive_access`; `set_drive_file_permissions` | `get_drive_file_permissions`; `check_drive_file_public_access` |
| calendar | `list_calendars`; `get_events`; `manage_event` | `create_calendar`; `query_freebusy`; `manage_out_of_office`; `manage_focus_time` | — |
| docs | `get_doc_content`; `create_doc`; `modify_doc_text` | `export_doc_to_pdf`; `search_docs`; `find_and_replace_doc`; `list_docs_in_folder`; `insert_doc_elements`; `update_paragraph_style`; `get_doc_as_markdown`; `list_document_comments`; `manage_document_comment` | `insert_doc_image`; `update_doc_headers_footers`; `batch_update_doc`; `inspect_doc_structure`; `create_table_with_data`; `debug_table_structure`; `manage_doc_tab` |
| sheets | `create_spreadsheet`; `read_sheet_values`; `modify_sheet_values` | `list_spreadsheets`; `get_spreadsheet_info`; `format_sheet_range`; `list_sheet_tables` | `create_sheet`; `manage_sheet_tab`; `append_table_rows`; `resize_sheet_dimensions`; `move_sheet_rows`; `list_spreadsheet_comments`; `manage_spreadsheet_comment`; `manage_conditional_formatting` |
| chat | `send_message`; `get_messages`; `search_messages`; `create_reaction` | `list_spaces`; `download_chat_attachment` | — |
| forms | `create_form`; `get_form` | `list_form_responses` | `set_publish_settings`; `get_form_response`; `batch_update_form` |
| slides | `create_presentation`; `get_presentation` | `batch_update_presentation`; `get_page`; `get_page_thumbnail` | `list_presentation_comments`; `manage_presentation_comment` |
| tasks | `get_task`; `list_tasks`; `manage_task` | — | `list_task_lists`; `get_task_list`; `manage_task_list` |
| contacts | `search_contacts`; `get_contact`; `list_contacts`; `manage_contact` | `list_contact_groups`; `get_contact_group` | `manage_contacts_batch`; `manage_contact_group` |
| search | `search_custom` | — | `get_search_engine_info` |
| appscript | `list_script_projects`; `get_script_project`; `get_script_content`; `create_script_project`; `update_script_content`; `run_script_function`; `generate_trigger_code` | `manage_deployment`; `list_deployments`; `delete_script_project`; `list_versions`; `create_version`; `get_version`; `list_script_processes`; `get_script_metrics` | — |

`debug_docs_runtime_info` is an additional diagnostic registration outside this tier file.

## Complete public gdoc CLI inventory

Aliases are grouped with the primary command. Internal `_sync-hook` and `_pull-hook` commands are omitted.

| Command | Purpose |
|---|---|
| `update` | Update gdoc to the latest version |
| `mcp` | Serve gdoc to desktop chat clients over MCP (stdio) |
| `auth` | Authenticate with Google |
| `config` | Get or set gdoc configuration (applies to all accounts) |
| `ls` | List files in Drive |
| `find` | Search files by name/content |
| `cat` | Export doc as markdown (spreadsheets print as a table) |
| `revisions` (alias: `history`) | List retained revisions (milestones) of a doc |
| `tabs` | List tabs in a doc (or worksheets in a spreadsheet) |
| `cells` | Write values into a spreadsheet range |
| `toc` | Extract table of contents with deep links |
| `add-tab` | Add a new tab to a document |
| `edit` | Find and replace text |
| `suggest` | Find and replace text as a suggested edit (review, not commit) |
| `diff` | Compare doc with a local file, or between revisions |
| `write` | Overwrite doc (or one tab) from local file |
| `insert` | Insert local markdown into an existing tab |
| `pull` | Download doc as local markdown |
| `push` | Upload local markdown to doc |
| `comments` | List comments on a doc |
| `comment` | Add a comment to a doc |
| `reply` | Reply to a comment |
| `resolve` | Resolve a comment |
| `reopen` | Reopen a resolved comment |
| `delete-comment` | Delete a comment |
| `comment-info` | Get a single comment by ID |
| `images` | List images, charts, and drawings in a doc |
| `export` | Export a doc to PDF, DOCX, HTML, and more |
| `insert-image` | Insert an image into an existing doc |
| `replace-image` | Replace an existing image's content by object ID |
| `structure` | Native document JSON (structure, styles, UTF-16 ranges) |
| `info` | Show document metadata |
| `share` | Share a document |
| `mkdir` | Create a Drive folder |
| `mv` (alias: `move`) | Move a file into a folder |
| `rename` | Rename a file |
| `drives` | List shared drives |
| `new` | Create a blank document |
| `cp` | Duplicate a document |

Sources: [Workspace tier configuration](https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/core/tool_tiers.yaml), [Workspace tool implementations](https://github.com/taylorwilsdon/google_workspace_mcp/tree/54b1c56f7f9912ce32681460d7ca38f9c2a37564), and [gdoc CLI parser](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/cli.py#L3673).
