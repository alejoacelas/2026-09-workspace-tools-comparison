# Round 2: links, literal identifiers, and symbols

**Three selected cases failed against real Google Docs while gdoc returned success:** a bracketed hyperlink label became literal Markdown; a ten-digit account identifier disappeared into list formatting; and an encoded ampersand became part of the wrong hyperlink destination. Fifteen offline cases produced nine passes and six differences. This is an adversarial set, not a prevalence estimate.

Source pin: gdoc `dbfa4c34bfa699ee8dd9839da85eea1fac177d44`. [Runnable probe](links.py) · [Full synthetic inputs and native before/after summaries](links-results.json). The three live cases used separate, newly created personal-account scratch documents. No collection, existing office document, permissions, or upstream source was changed. Raw native snapshots and identifiers are kept in owner-only `.local-hunt/r2-links*` files.

## Live results

| Input / intended result | Actual native Google state | CLI result |
|---|---|---|
| `Read [Finance [Q3]](https://example.com/q3).` should show `Read Finance [Q3].`, with the label linked. | Entire Markdown expression is visible text; no hyperlink exists. | Exit 0, first attempt |
| `1234567890. Revenue account` should retain the literal ten-digit identifier. | Text run contains only `Revenue account`; paragraph now has native list membership. | Exit 0, first attempt |
| `Open [Budget](https://example.com/report?a=1&amp;b=2).` should link to `...?a=1&b=2`. | Visible label is correct, but stored link URL remains `...?a=1&amp;b=2`. | Exit 0, first attempt |

The number case establishes lost literal text and added list membership. We did not export its PDF to certify the displayed replacement ordinal, so this report does **not** invent a particular visible list number.

The bracket-label input is especially relevant to a normal edit cycle: `get_tab_text(markdown=True)` itself produces this exact Markdown from a native hyperlink labeled `Finance [Q3]`. The exporter/parse compatibility check ran offline; the CLI/native write failure ran live. Thus this is not just an unsupported hand-authored syntax surprise. Backslash-escaping the label brackets passed the offline control.

For the query case, the URL difference is substantive: parsing the actual query produces parameter `amp;b` rather than `b`. Native readback confirms the wrong URL, independently of whether the visible label looks right. The test does not fetch the destination or claim a particular remote website response.

## All fifteen offline checks

Expectations were explicitly specified, then independently checked with MarkdownIt’s CommonMark parser before comparing gdoc. That parser is a convention oracle, not a second live Google implementation; gdoc does not advertise complete CommonMark compliance.

| Case | Expected | gdoc result |
|---|---|---|
| Raw `R&D costs < 5%` | Preserve literal business text | Pass |
| `R&amp;D costs &lt; 5%` | Decode entities to `R&D costs < 5%` | Entity spellings remain visible; offline convention gap |
| `Budget &#163;125; variance &#x2212;5%` | `Budget £125; variance −5%` | Numeric entity spellings remain visible; offline convention gap |
| `Target <5%; ceiling >10%` | Preserve literal comparison symbols | Pass |
| Link query with raw `&` | Preserve `?a=1&b=2` | Pass |
| Link query with `&amp;` | Decode URL entity | Wrong native URL; live confirmed |
| Link label `Finance [Q3]` | Preserve text and hyperlink | Literal Markdown and no link; live confirmed |
| Escaped `Finance \[Q3\]` label | Preserve text and hyperlink | Pass |
| Simple `Finance Q3` label | Preserve text and hyperlink | Pass |
| `# Revenue forecast #` | Heading text `Revenue forecast` | Closing `#` remains; offline only |
| `# Revenue forecast \#` | Heading text with literal final `#` | Pass |
| Ten-digit `1234567890.` prefix | Literal text; CommonMark list markers allow only 1–9 digits | Identifier removed and list created; live confirmed |
| Nine-digit `123456789.` prefix | Recognize a valid ordered-list marker | Pass for text/recognition; start ordinal not tested |
| `2026-09-12. Review budget.` | Preserve ISO date | Pass |
| Plain `finance@example.com` | Preserve email address | Pass |

## Mechanisms and regression boundaries

1. **Balanced brackets in link labels.** `_LINK_RE` ends its label at the first closing bracket, so it cannot consume the exporter’s valid balanced-bracket output. This differs from the already known parentheses-in-destination bug, although both belong to a link grammar repair area. A regression should begin with a native linked label, export it, parse it, and verify both label and destination; the live write should then preserve that result.
2. **Overbroad numbered-list recognition.** `_NUMBERED_RE` accepts arbitrarily many digits. A ten-digit account identifier followed by period and space becomes a list even though the reference grammar excludes it. This is a write-side recognition failure, separate from the previously found selected-tab ordinal read failures. Test the 9/10-digit boundary with unchanged suffixes and verify native list membership as well as text.
3. **Missing entity decoding.** Text and URL entities remain encoded. The live URL case is stronger than a text-only mismatch because it changes the query parameter name while preserving a convincing label. Test raw/encoded equivalents in both text and destinations, with code spans excluded from entity interpretation.
4. **Closing heading markers.** The parser recognizes the opening heading marker but keeps an optional unescaped closing marker as visible text. This case remains offline-only and should not be counted as another live-confirmed failure.

The campaign’s already documented underscore, balanced-URL-parenthesis, style-reset and newline failures were excluded. Round 1’s bracket-label offline lead is now live-confirmed; this is an evidence upgrade, not an independent new discovery. None of these findings has been submitted upstream.

Sources: [inline parsing and `_LINK_RE`](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/mdparse.py#L54), [native-tab hyperlink exporter](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/api/docs.py#L291), [block parsing](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/mdparse.py#L258).

## Run

```sh
# Offline only; refreshes deterministic results and keeps existing live receipts.
~/.local/share/uv/tools/workspace-mcp/bin/python hunt/round2/links.py

# Creates only missing personal scratch cases; records native before/after.
~/.local/share/uv/tools/workspace-mcp/bin/python hunt/round2/links.py --live
```

The live runner records successful or failed attempts and only retries explicit stale-baseline refusals after a fresh read. A zero process exit means the probe completed, not that gdoc passed its test cases.
