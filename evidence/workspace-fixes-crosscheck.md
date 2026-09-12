# Workspace fixes cross-checked against gdoc

**Neither implementation is a safe universal oracle for the other.** Reverse testing found a distinct Unicode-indexing defect in gdoc, alongside the already identified Workspace Markdown defect. Workspace is better protected against oversized spreadsheet reads; gdoc is better protected against inherited heading styles in native Markdown edits. Several apparent wins simply reflect features the other tool does not offer.

Scope: Workspace `54b1c56f7f9912ce32681460d7ca38f9c2a37564` and gdoc `dbfa4c34bfa699ee8dd9839da85eea1fac177d44`. GitHub PR states checked 2026-09-12. The full PR responses, including head and merge commits, are in [workspace-prs.json](workspace-prs.json). Merged patches listed below were checked as ancestors of the pinned Workspace revision, not merely assumed present because GitHub calls them merged. An open/closed PR may have equivalent code in main under another commit; this audit checks the code too.

The [runnable probe](../probes/workspace-fixes-crosscheck.py) produces [31 offline observations](workspace-fixes-probes.json) from real converter/helper calls and mocked Google-service boundaries. These are request-shape and local-behavior checks, not live API or rendered-document tests. Assertions intentionally reproduce defects: a passing probe is not a certificate of correctness.

## A new gdoc bug discovered by transferring the Unicode concern

Workspace's converter uses Python character counts where Google Docs expects UTF-16 units. gdoc's Markdown converter handles that correctly, including repeated emoji and a woman-technologist ZWJ sequence. But gdoc's **case-insensitive phrase search** has a different index-expansion bug: `İ` (U+0130, Latin capital I with dot above) becomes two code points when lowercased, while gdoc keeps its original character-to-document-index map.

| Operation/input | Expected native range | Actual gdoc result |
|---|---|---|
| Find `cat` in `İ cat\n` | `[3, 6)` | `[4, 7)` |
| Find `cat` in `İİ cat\n` | `[4, 7)` | `IndexError` |
| Find `cat` in `😀 İ cat\n` | `[6, 9)` | `[7, 10)` |
| Replace `cat` in `İ cat sat\n` | Delete `cat` | Generates a delete range covering `at ` |

The last observation follows the output into gdoc's actual replacement-request builder; it is stronger evidence than finding suspicious `lower()` code. This offline probe did not execute the remaining Google requests; the coordinator subsequently reproduced wrong text live in [the feature checks](live-feature-checks.json). With the final-newline examples, Google's own deletion constraints can turn a wrong range into an error instead of visible corruption.

`--case-sensitive` is a demonstrated workaround for these inputs. The shared search function is used by editing and other phrase-location paths, including insertion and anchored-comment location; those callers deserve regressions too, but only the shared search and replacement builder were directly exercised here. Workspace's plain replacement emits Google's native `replaceAllText`, so it does not construct this erroneous local index map. That does not prove every case-insensitive semantic difference is absent from the service.

Sources: [gdoc search mapping](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/api/docs.py#L495), [gdoc replacement builder](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/api/docs.py#L1504), [Workspace native replacement builder](https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/gdocs/docs_helpers.py#L1008).

## Twelve public patch families

| Workspace patch and status | Pinned Workspace behavior | Cross-check in gdoc | Evidence and practical implication |
|---|---|---|---|
| [#850 body paragraphs inherit headings](https://github.com/taylorwilsdon/google_workspace_mcp/pull/850), **open** | Proposed fix absent: plain body, mixed heading/body, and fenced code emit no `NORMAL_TEXT` resets. | All three inputs emit explicit normal-style resets. | **Executed both converters.** When inserting at a heading boundary, Workspace depends on inherited paragraph state; gdoc deliberately controls it. Live rendering claim is the PR author's, not a live reproduction here. |
| [#1109 structure inspector's incompatible field mask](https://github.com/taylorwilsdon/google_workspace_mcp/pull/1109), **open** | Exact reported mask is present: legacy top-level `body/headers/footers` alongside `tabs`, with `includeTabsContent=True`. | Default `get_document_structure` sends `includeTabsContent=True` with no mask. | **Executed gdoc request boundary; evaluated Workspace's actual constants.** Author reports every inspector request returns HTTP 400. This offline audit reproduced the cause's shape; the coordinator subsequently confirmed the exact HTTP400 live in [the main benchmark](live-benchmark.json). Explicit custom gdoc masks can still be invalid. |
| [#976 empty structure for tabbed Docs](https://github.com/taylorwilsdon/google_workspace_mcp/pull/976), **merged, ancestor verified** | First-tab fallback patch present. | A synthetic response containing only tab-body content reads `Present\n` successfully. | **Executed gdoc tab retrieval and extraction.** The earlier fallback fix does not protect Workspace against the separate #1109 request failure. |
| [#1087 read text drifts from native indices](https://github.com/taylorwilsdon/google_workspace_mcp/pull/1087), **closed unmerged** | Equivalent blank-paragraph/object-placeholder implementation **is present** under other history. | Phrase search uses original text-run indices rather than searching exported plain-text offsets. | **Executed both.** Blank line + inline image before `Bravo`: Workspace emits `Alpha\n\n\uFFFCBravo\n`; gdoc finds native `[9,14)`. Workspace helper explicitly says table text is **not** index-aligned: never treat arbitrary flat extraction offsets as native positions. |
| [#955 only 50 rows displayed](https://github.com/taylorwilsdon/google_workspace_mcp/pull/955), **merged, ancestor verified** | Patch returns all fetched rows (subject to newer fetch cap). | 120 supplied rows survive the API wrapper and TSV formatting, including row 120. | **Executed gdoc wrapper and formatter; ran Workspace regression suite.** Both cover the simple truncation failure. |
| [#986 unbounded spreadsheet reads](https://github.com/taylorwilsdon/google_workspace_mcp/pull/986), **merged, ancestor verified** | `A:Z` becomes `A1:Z1000`; `A1:Z50000` also clamps; later windows start at the requested row. Response discloses clamp. | Sends `A:Z` and `A1:Z50000` unchanged and materializes the returned values. | **Executed real clamp helper and gdoc request boundary.** gdoc retains the unbounded-allocation exposure that motivated Workspace's fix; no OOM or memory benchmark was performed here. Conversely, gdoc can return >1,000 rows in one call; Workspace requires paging. |
| [#964 invalid column label deletes wrong column](https://github.com/taylorwilsdon/google_workspace_mcp/pull/964), **merged, ancestor verified** | Rejects `B2`, `A:B`, and trailing newline; accepts `AA` as index 26. | No comparable column-deletion command. | **Executed Workspace validation.** This is a capability gap, not evidence of a superior gdoc deletion implementation. |
| [#1051 shortcut metadata modifies target](https://github.com/taylorwilsdon/google_workspace_mcp/pull/1051), **merged, ancestor verified** | Metadata-only updates retain shortcut ID; content updates follow target. | `rename_file('shortcut', …)` sends `files.update(fileId='shortcut')` with no resolving GET. | **Executed gdoc request boundary.** Same erroneous target substitution is absent for rename. gdoc lacks the matching trash workflow; no claim about deleting shortcuts was tested. |
| [#1002 Shared Drive permissions falsely private](https://github.com/taylorwilsdon/google_workspace_mcp/pull/1002), **merged, ancestor verified** | Uses paginated `permissions.list` for Shared Drive files instead of relying on missing inline permissions. | Grants permissions but lacks an equivalent permission-inspection/public-access-report operation. | **Source/capability assessment only.** gdoc cannot make the same false-private report through a tool it does not expose; it also cannot answer the user's access-audit question. |
| [#999 invalid styling payloads/fractional font sizes](https://github.com/taylorwilsdon/google_workspace_mcp/pull/999), **merged, ancestor verified** | Fixes background color nesting, complete border payloads, fractional point sizes; adds per-edge borders. | No matching general document-background/font-size/table-border command. | **Source/capability assessment only.** gdoc's Markdown authoring is not an equivalent typography/layout control surface. No false "gdoc passes" award for missing features. |
| [#983 CLI strips literal quotes](https://github.com/taylorwilsdon/google_workspace_mcp/pull/983), **merged, ancestor verified** | Coercer now retains JSON-string-looking literal text. | Argparse preserves the same strings. | **Executed both parsers** on `"exact phrase"`, `"123"`, and ordinary text. Shell quoting itself was not under test. |
| [#930 spreadsheet import failure routes](https://github.com/taylorwilsdon/google_workspace_mcp/pull/930), **closed unmerged** | Inline CSV named `Spend Summary` still auto-detects `text/plain` and is rejected; explicit `source_format='csv'` succeeds. | Writes structured values/CSV-derived values to existing sheets through the values API rather than this Drive-import pathway. | **Executed Workspace media resolution** with and without explicit hint. gdoc cannot substitute for every new-file import feature; other PR930 URL/native-MIME allegations were not independently exercised. |

The label “merged” should not be confused with the behavior of an older installed version, nor should a closed PR automatically be treated as either fixed or unfixed. The #1087 case demonstrates why code inspection and runnable checks are necessary.

## What the tests actually guarantee

The [focused Workspace run](workspace-reverse-regressions.txt) passed **88 tests** across Markdown, index alignment, tab reads, Sheets range limits, and CLI coercion. The [focused gdoc run](gdoc-reverse-regressions.txt) passed **142 tests** across phrase finding, Markdown, Sheets wrappers, and tab reading. These are selected upstream tests, not full-suite totals, and overlap other report runs: do not add them to other counts.

Those passing tests coexist with the defects above. Workspace's existing mask test asserts that a mask exists and contains words such as `paragraph`, `table`, and `tabs`; it does not verify that Google accepts their combination. gdoc's find tests do not expose the lowercasing expansion. Neither test count nor mocked API success supplies the external oracle the user wants.

The most useful proposed gdoc regression is therefore not one example with a Turkish character. Generate real text-run mappings from arbitrary Unicode, pick substrings, and verify returned ranges against a separately computed UTF-16 map, including case transformations that change length. For plain replacement, compare the resulting native document with Google's own `replaceAllText` on a twin document. A second implementation can generate leads, but Google index conventions and the intended operation must decide which result is correct.

Run the evidence without credentials:

```sh
~/.local/share/uv/tools/workspace-mcp/bin/python probes/workspace-fixes-crosscheck.py
```

No Google file was created, changed, shared, or deleted for this audit. No upstream source was modified, and no issue or PR was published.
