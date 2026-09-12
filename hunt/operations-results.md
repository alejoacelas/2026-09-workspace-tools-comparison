# Additional gdoc native-tab export probes

**Twenty pure conversion cases produced eleven passes and nine differences.** The strongest new leads are missing smart-chip labels, omitted nested-table contents, and incorrect ordered-list ordinals. These are deliberately selected tests, not a real-world failure rate. No Google requests, credentials, or private specimens were used.

Pinned public source: `dbfa4c34bfa699ee8dd9839da85eea1fac177d44`. Run [operations-probe.py](operations-probe.py) to regenerate [all fixtures and results](operations-results.json):

```sh
~/.local/share/uv/tools/workspace-mcp/bin/python hunt/operations-probe.py
```

The probe invokes `get_tab_text(tab, markdown=True)` on invented native-shaped dictionaries. The three hyperlink cases also run the actual gdoc Markdown parser on the export. Thus these observations establish converter behavior; they do **not** establish that a live Google Doc containing each fixture was created or rewritten successfully. The ordinal expectations follow the supplied native list identity and `startNumber` metadata; live native-list controls should confirm those particular display expectations before publication as live bugs.

| Case | Expected content/contract | Actual result | Assessment |
|---|---|---|---|
| Office punctuation | `Budget: £1,250.50; tax (20%) — approved!` | Same text | Pass |
| Curly quotes | `“Friday’s review” — don’t postpone.` | Same text | Pass |
| Windows path | Literal `C:\reports\2026\final.txt` in export | Same text | Pass; parser round trip not tested here |
| Comparison symbols | `Actual < forecast; 3 > 2; x = 4.` | Same text | Pass |
| Link with query parameters | Label `Budget`, complete `?a=1&b=2` URL | Label and URL retained after parse | Pass |
| Link label contains square brackets | Label `Budget [draft]` and its URL remain a hyperlink after export/parse | Parser returns literal `[Budget [draft]](https://example.com/report)` with no link | New input variant of the export/parser contract family; not the known URL-parenthesis defect |
| Email hyperlink | `Email finance`, complete `mailto:` URL | Label and URL retained | Pass |
| Ordered list starts at 7 | `7. Approve`, `8. Publish` | `1. Approve`, `2. Publish` | Ignores native `startNumber` |
| Adjacent distinct ordered lists | Each native list starts at 1 | Second list rendered `2.` | Counter ignores native list identity |
| Same native ordered list resumes after prose | First item `1.`, second item `2.` | Second item rendered `1.` | Counter clears on non-list paragraph |
| Ordinary two-item numbered list | `1.`, `2.` | Same | Pass |
| Different list after a note | New list starts at 1 | Same | Pass |
| Ordinary 2×2 table | All cells retained in documented TSV representation | `Item\tCost\nPens\t100\n` | Pass; no claim TSV reconstructs a native table |
| Hyperlinked table cell | Retain the cell hyperlink destination | `Budget\t100\n`; URL absent | Representation gap: table path deliberately uses plain text even in Markdown mode |
| Bold table cell | Retain supported bold markup in Markdown mode | `Approved\t100\n`; bold absent | Representation gap, related to previously known style-loss families |
| Nested table inside a cell | Retain outer `Breakdown`, inner `Materials / 475`, outer `Total / 500` | `Breakdown\nTotal\t500\n`; inner text and value absent | Content omission in recursive native-shaped fixture; backend fixture not live-established |
| Multiline table cell | Retain `North`, `South`, `100` | All present | Pass on content; TSV cell boundaries not round-trip-certified |
| Person chip | `Owner: Alex Example` | `Owner: ` | Visible name omitted because it is not a text run |
| File chip | `See Budget 2026 today.` | `See  today.` | Visible title omitted because it is not a text run |
| Soft line break | Preserve supplied U+000B and following text | Same sequence | Pass on raw export; not a live backend fixture |

## Minimal reproductions and repair boundaries

All imports below are from the pinned gdoc clone. The checked-in probe supplies the complete synthetic native dictionaries, making each example independently editable.

**Numbered lists:** `_paragraph_markdown` increments a dictionary keyed solely by nesting level. It never reads `startNumber`, and a non-list paragraph clears all counters. These are three manifestations of one ordinal-state problem, not three unrelated bugs. A regression should include native list identity, start ordinal, nesting level, and interrupted continuation.

```python
from gdoc.api.docs import get_tab_text
tab = {
    "body": {"content": [{"paragraph": {
        "elements": [{"textRun": {"content": "Approve\n"}}],
        "bullet": {"listId": "steps"},
    }}]},
    "lists": {"steps": {"listProperties": {"nestingLevels": [
        {"glyphType": "DECIMAL", "startNumber": 7}
    ]}}},
}
assert get_tab_text(tab, markdown=True) == "1. Approve\n"  # expected ordinal: 7
```

**Smart chips:** `_runs_markdown` skips every non-`textRun` paragraph element, even when `person.personProperties.name` or `richLink.richLinkProperties.title` supplies visible text. These two specimens are one missing-element-rendering family. At minimum, a plain read should retain a recognizable label rather than silently joining the surrounding words.

```python
tab = {"body": {"content": [{"paragraph": {"elements": [
    {"textRun": {"content": "Owner: "}},
    {"person": {"personProperties": {
        "name": "Alex Example", "email": "alex@example.com"
    }}},
    {"textRun": {"content": "\n"}},
]}}]}}
assert get_tab_text(tab, markdown=True) == "Owner: \n"
```

**Nested tables:** the top-level exporter enters table cells, but `_extract_paragraphs_text` processes only their direct paragraphs and skips any table element inside a cell. A recursive text-preservation oracle would detect missing `Materials` and `475` even without judging table formatting. Whether the backend admits the synthetic nested structure should be established before calling it an ordinary live-document defect.

**Square-bracket link labels:** the exporter produces `[Budget [draft]](https://example.com/report)`. gdoc's importer does not recognize that link and inserts the entire Markdown syntax as visible text. The test is of compatibility between its own output and input, not a claim that all Markdown readers reject the serialization. A live twin-document test can distinguish the supported Google import route from gdoc's native tab-writing route.

Source boundaries: [native tab exporter, lists, run renderer](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/api/docs.py#L275), [nonrecursive table-cell text extraction](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/api/docs.py#L214), [inline link parser](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/mdparse.py#L54).

The campaign's consolidated family descriptions were checked only to avoid counting established issues as new discoveries; no campaign specimen or private evidence was copied. Table style loss and the bracket-label case belong to broader known export/parse fidelity concerns, while the exact ordinal and chip specimens are new probes for this report. Existing COMPARISON.md specimens—Turkish-I mapping, emoji offsets, balanced destination parentheses, underscores, escaped table pipes, and nested bullet writes—were not repeated.
