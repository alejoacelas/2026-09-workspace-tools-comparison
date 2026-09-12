# Round 2: live native structure probes

15 cases on fresh personal synthetic documents. Pinned gdoc CLI, verified personal identity before writes; no collection edits, sharing, or deletions.

| Case | Assessment |
|---|---|
| regular_coordinate | pass |
| colspan_rightmost | pass |
| colspan_wrong_column | pass |
| rowspan_wrong_column | pass |
| colspan_unmerged_row_control | pass |
| multiline_cell_edit | pass |
| empty_cell_edit | pass |
| multiline_label_control | pass |
| decimal_control | control-or-known-list-family |
| upper_alpha_known_variant | control-or-known-list-family |
| upper_roman_known_variant | control-or-known-list-family |
| resumed_same_list_known_variant | control-or-known-list-family |
| separate_lists_known_variant | control-or-known-list-family |
| multiline_read_control | pass |
| colspan_label_control | live-confirmed-wrong-target |

## Confirmed: merged label routes into a covered cell

The CLI promises a label replaces “the cell to its right”; `--col` selects an explicit zero-based column. In a one-row native table with Merged A spanning two columns followed by C, `gdoc edit DOC Updated --cell "Merged A" --tab TAB` returns success but changes the left cell to Merged AUpdated and leaves C untouched. A fresh three-column-span replay changes Budget to Budget800 while leaving the intended adjacent value 700 unchanged. An explicit `--col 2` on a pristine two-span control correctly changes C to Updated and preserves Merged A.

Root boundary: resolve_cell_range uses ci + 1 for the default target without accounting for columnSpan. The native array includes a covered empty cell at that physical slot. The resolver selects its editable position; Google incorporates the inserted text into the owning merged cell. It does not skip to the next visible cell. This is a new merged-topology trigger in the broader target-identity repair area, not a claim that merged coordinate addressing generally fails. All four suspect coordinate examples passed.

Evidence is the case colspan_label_control, including separate replication and explicit_column_control captures. Both erroneous edits and the workaround returned exit 0, with native Docs readback. [CLI label promise](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/cli.py#L3996), [cell resolver](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/api/docs.py#L652).

## Controls and known-family observations

Nine table/content scenarios passed their selected checks: normal/merged/rowspan coordinate targets, unmerged row below a span, multiline replacement, empty-cell insertion, multiline label selection, and retention of multiline cell values. These controls do not certify arbitrary merged topology or document style preservation.

Five live list scenarios add real native evidence rather than new families. Decimal 1–3 agrees across default and selected-tab reads. UPPER_ALPHA and UPPER_ROMAN glyph metadata is real, but both exports render decimal markers: a representation limitation affecting both routes. A resumed native DECIMAL list keeps one listId around intervening prose; default cat returns 1 then 2, while selected-tab cat returns 1 then 1. That is the already-known ordinal-state family. Distinct-list controls restart, as intended.

Fifteen main cases were run, plus a fresh merged-label replication and an explicit-column control. Initial list setup used an obsolete preset name, which Google rejected before mutation; the harness corrected it from the discovery enum and reused the same scratch document. That setup error is excluded from app findings.

All HTML-imported table spans were checked in the native Docs response before judging cell coordinates. Expected coordinates refer to the displayed logical row/column; these native physical cell arrays retain covered positions that are not separate visible cells. Full input HTML, native span/cell summaries, commands and results are in [structure-results.json](structure-results.json). IDs and full resource snapshots remain in ignored local scratch.

List probes deliberately revisit known ordinal/marker-state mechanisms as controls; they are not automatically new bug families. Multiline read checks require retained values, not a specific TSV representation.
