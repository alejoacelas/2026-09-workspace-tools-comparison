# Spreadsheet follow-ups: invisible characters and value-copy boundaries

**The CRLF discrepancy is independently confirmed in live Google cells, and ordinary lookup formulas expose its practical effect.** Ten additional live cases distinguish import defects from unsupported TSV dialects and deliberately lossy display/value-copy interfaces. Source: public gdoc `dbfa4c34bfa699ee8dd9839da85eea1fac177d44`.

[Executable follow-ups](sheet-followups.py) · [Native values, formula results and CLI receipts](sheet-followups.json). Only the existing synthetic personal-account spreadsheet was used. Original rows 7–14 were read without modification; new evidence occupies Data rows 200–280. No collection, permissions, or existing office data was changed.

## CRLF: one family, independently checked

Native reads, rather than captured CLI text, returned:

```text
TSV CRLF A7:B8:  [["Item", "Value\r"], ["Budget", "100\r"]]
CSV CRLF A13:B14:[["Item", "Value"],   ["Budget", "100"]]
```

The TSV parser opens with `newline=""`, retaining original terminators, and strips only `"\n"` before splitting cells. CSV uses `csv.reader`, which consumes CRLF correctly. The remaining carriage return is actual cell content, not an artifact of printing JSON.

| Live formula | TSV CRLF cell | Clean CSV control |
|---|---:|---:|
| `EXACT(cell,"100")` | FALSE | TRUE |
| `MATCH("Value",header_range,0)` | Not found | Column 2 |
| `LEN(cell)` | 4 | 3 |

The lookup uses `IFERROR(...,"not found")` to record a readable result. These formulas are in D200:H201 and refer to the original imported cells. The original BOM header also fails `EXACT(A25,"Item")` and has length 5 rather than 4.

CRLF and bare-CR manifestations are **one newline-handling family**, not separate independent bugs. The BOM issue is a separate encoding boundary, already detected in the coordinator's sweep; this run adds confirmation and a formula-level consequence rather than another discovery count.

## Ten additional cases

| Case | Observed outcome | Classification |
|---|---|---|
| UTF-8 BOM CSV | First header is `\ufeffItem`; CLI exits 0. | Reconfirmed encoding artifact; `.csv` is opened as `utf-8`, not BOM-aware `utf-8-sig`. |
| Quoted TSV field containing a tab | `"North\tSouth"` becomes two cells; `100` shifts into a third column. | Unsupported quoted-TSV dialect. The tool treats TSV as literal tab-separated lines. |
| Quoted TSV field containing a newline | One intended row becomes two rows, retaining quote characters. | Same quoted-TSV limitation; do not count twice. |
| CSV field containing a quoted tab | One cell retains `North\tSouth`, with `100` beside it. | Passing CSV control. |
| RAW identifier/formula-like text | `00123` and literal `=1+2` are preserved. | Passing default-input control. |
| Explicit USER_ENTERED | `00123` displays as `123`; `=1+2` evaluates to `3`. | Passing requested-coercion control, not corruption. |
| JSON read of embedded newline/tab | Retains `North\nSouth`, `A\tB`, and `00123`. | Passing text-preservation control. |
| Plain read → TSV write | Becomes `North South`, `A B`, `00123`. | Documented display loss: `_format_sheet_tsv` replaces embedded separators with spaces. It is unsuitable as a lossless export. |
| Formula read → RAW write | Source `formulaValue: "=1+2"` becomes destination `stringValue: "3"`. | Capability boundary: the reader returns formatted values, not formulas. |
| Typed value read → RAW write | Number `1234.5` displayed as `$1,234.50` and boolean TRUE become strings; string `00123` remains intact. | Capability boundary: JSON structure does not imply native spreadsheet value types. |

All final CLI calls completed successfully. Four controls explicitly passed; the other rows have the classifications above rather than being combined into a misleading overall bug rate.

The initial USER_ENTERED control accidentally omitted its flag in the harness. That was corrected, and just that control was rerun successfully. The first RAW result was excluded as an application failure; the correction is recorded in the JSON receipt.

## What this means for office work and regression tests

Use CSV when transferring cells that may contain tabs or multiline notes. JSON reads retain those characters, whereas `--plain` is a readable presentation. Neither default formatted-value output nor a JSON wrapper makes a full worksheet backup: formulas, number formats, and native numeric/boolean types require a different structured read/write route.

Useful independent regressions are small:

1. Import equivalent LF, CRLF and BOM-prefixed files, then compare actual cell strings. Follow with `EXACT` and `MATCH` so invisible differences have an observable contract.
2. Pair accepted CSV quoting with unsupported TSV quoting; either document/refuse the latter or implement an explicit dialect, instead of silently treating all delimited files as equivalent.
3. Keep separate assertions for displayed text, cell-internal separators, formula source, effective values, and native input types. A displayed `3` can be a formula result, a number, or a string.

Sources: [file parser](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/cli.py#L727), [plain TSV formatter](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/cli.py#L79), [Sheets value reader/writer](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/api/sheets.py#L69).

Run with `~/.local/share/uv/tools/workspace-mcp/bin/python hunt/round2/sheet-followups.py`. This is a live investigation script with explicit personal-identity checks before every write; it is not an upstream offline test.
