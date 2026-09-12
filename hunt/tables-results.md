# Native table and fenced-code bug hunt

**Two new repair families reproduced offline:** empty-edge table cells are erased or shifted; opening and closing fence information strings are parsed with the wrong grammar. These are invented specimens, not copied campaign documents.

The 24 cases run the pinned gdoc parser and native request generator. A separate markdown-it CommonMark parser with its table extension provides readable reference HTML; explicit cell/text expectations remain in the fixture definitions. This tests parser output and generated requests, not Google acceptance or final rendering.

| Case | Result | Finding |
|---|---|---|
| table_regular | pass | selected assertions pass |
| empty_first_data_compact | candidate | table rows/cell mapping differ |
| empty_first_data_spaced | pass | selected assertions pass |
| empty_first_header_compact | candidate | table rows/cell mapping differ |
| empty_last_header_compact | candidate | table rows/cell mapping differ |
| empty_middle_data | pass | selected assertions pass |
| empty_last_data | pass | selected assertions pass |
| empty_two_prefix_cells | candidate | table rows/cell mapping differ |
| one_column_empty_row | candidate | table rows/cell mapping differ |
| short_data_row | pass | selected assertions pass |
| long_data_row | pass | selected assertions pass |
| escaped_pipe_known | known-duplicate | table rows/cell mapping differ |
| bold_unicode_cells | pass | selected assertions pass |
| no_outer_pipes | scope-gap | table rows/cell mapping differ |
| mismatched_header_separator | excluded-malformed-table | table rows/cell mapping differ |
| fence_basic | pass | selected assertions pass |
| fence_language | pass | selected assertions pass |
| fence_multiword_info | candidate | literal code text differs; code style coverage differs; literal Markdown acquired bold |
| fence_false_close_backtick | candidate | literal code text differs; code style coverage differs; literal Markdown acquired bold |
| fence_false_close_tilde | candidate | literal code text differs; code style coverage differs; literal Markdown acquired bold |
| fence_close_trailing_spaces | pass | selected assertions pass |
| fence_longer_close | pass | selected assertions pass |
| fence_short_inner | pass | selected assertions pass |
| fence_unclosed | pass | selected assertions pass |

## Candidate T1: empty edge cells move or delete data

Input `|A|B|` / `|---|---|` / `||100|` should have an empty first data cell and `100` in the second. gdoc creates `["100", ""]`. With header `||B|`, it infers one column instead of two and drops the second data value. Spaces inside the empty cell avoid this: `| |100|` passes. Empty middle/trailing data cells and short-row padding controls pass. The single-column empty row `||` is not recognized as a row at all.

Root causes are edge stripping with `line.strip("|")` before splitting and `_TABLE_ROW_RE` requiring a nonempty interior. The shared repair boundary is preserving empty-cell identity, not treating each manifestation as a separate bug. Empty-header width loss is the strongest content-loss specimen. Native route: `write --tab` / `insert` / formatted table insertion call `parse_markdown`, and `_insert_table` consumes these rows.

## Candidate T2: fence info strings expose literal code to Markdown parsing

Inside a fenced code block, the line `````not-a-close`` is literal code: a closing fence may only be followed by spaces/tabs. gdoc treats it as a closing delimiter, discards that line and then renders `**literal**` as bold prose. The same issue occurs with tilde fences. Conversely, the valid opening info string `python title=demo.py` is rejected by gdoc, leaving the opening marker visible and parsing the body as Markdown. Both arise from reusing `_FENCE_RE` with one optional nonspace token for opening and closing lines.

Workspace’s native converter retained the exact intended literal code text for all nine fence specimens, including all three gdoc failures (offline request inspection only). Simple/language fences, whitespace-only closing suffixes, longer closing delimiters, shorter internal delimiters and unterminated fences pass these assertions. The opening and closing failures need distinct regression cases but belong to one fence grammar repair.

## Exclusions and deduplication

Escaped-pipe corruption is already in the comparison corpus, so its replay is a known duplicate. Missing outer table pipes is valid GFM but absent from this parser’s recognized table grammar; recorded as a scope gap rather than a new corruption family. A mismatched header/separator column count is not a GFM table and is excluded from positive table expectations even though gdoc recognizes it.

The campaign consolidated family headings/root-cause summaries were reviewed for deduplication. Existing broad Markdown export/parser and balanced-link families overlap the area, but the reviewed report does not identify these empty-edge-cell or fenced-info subcases. This is a new concrete trigger/root-cause claim, not proof no earlier private test ever covered them. No private specimen or private report excerpt is reproduced here.

## Sources and reproduction

- [gdoc native parser](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/mdparse.py#L323).
- [gdoc native table insertion](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/api/docs.py#L764).
- [CommonMark fenced-code grammar](https://spec.commonmark.org/0.31.2/#fenced-code-blocks): opening info strings and closing-fence suffixes have different rules.
- [GFM table grammar](https://github.github.com/gfm/#tables-extension-): cells may be empty; optional exterior pipes and uneven body rows have defined handling.
- Run `python3 hunt/tables-probe.py`; [raw inputs, outputs and request evidence](tables-results.json).
