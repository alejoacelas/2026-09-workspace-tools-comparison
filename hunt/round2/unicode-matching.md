# Case-insensitive matching against Google's native operation

**gdoc can refuse to replace an exact uppercase character that visibly occurs in the document.** In live tests, source `ΟΣ`, find `Σ`, replacement `X` produced:

| Operation | Result |
|---|---|
| `gdoc edit DOC 'Σ' 'X' --all --tab TAB --account PERSONAL` | Exit 3, no match; document remains `ΟΣ` |
| Native Google `replaceAllText`, `matchCase:false` | One replacement; document becomes `ΟX` |
| Context control: identical operation on `Budget Σ` | Both produce `Budget X` |

The sigma in the source and query is the **same U+03A3 character**. No visual resemblance or normalization assumption is needed. gdoc lowercases the whole document and the query separately: word-final `Σ` in `ΟΣ` becomes `ς`, while isolated query `Σ` becomes `σ`. The search therefore misses a literal character that was present before normalization. This is a case-insensitive **search-completeness bug**, distinct from the already known Turkish-I index corruption.

## What ran

[The executable](unicode-matching.py) tested **22 source/query pairs** on two reusable synthetic scratch documents: one for pinned gdoc 0.21.0 (`dbfa4c34bfa699ee8dd9839da85eea1fac177d44`), one for the actual Google Docs API. Both bodies were explicitly reset before each case, and their native text was verified identical before either operation. gdoc used `--all` with default case-insensitive matching; Google used `replaceAllText` with `matchCase:false`, the same replacement, and the explicit same single-tab scope. Resulting native text was read after each operation.

Nine pairs ended with identical text; thirteen differed. **Those are compatibility observations, not thirteen independent bugs or a quality score.** Cases were selected to explore Unicode boundaries, not sampled from office usage. A gdoc no-match error and Google's successful zero-replacement result count as matching final text when both leave the document unchanged. The exact return codes, native replacement counts, text, and Unicode code points are in [the evidence](unicode-matching.json).

## Results by family

| Family and selected inputs | Observed behavior | Interpretation |
|---|---|---|
| Greek final sigma: `ς`/`σ`, `ΟΣ`/`οσ`, `ς`/`Σ`, and exact `ΟΣ`/`Σ` | Google replaces; gdoc reports no match | One contextual-case-matching family; exact-character case above is strongest |
| Ordinary uppercase sigma `Σ`/`σ`; isolated `Budget Σ`/`Σ` | Both replace correctly | Context controls bound the failure |
| German `Straße`/`STRASSE` | Google replaces; gdoc reports no match | Native matching supports this expansion; gdoc's lowercasing does not |
| German capital `ẞ`/`ß` | **gdoc replaces; Google reports zero matches** | Reverse-direction semantic difference; do not automatically call gdoc wrong because it differs from the oracle |
| Long s `ſale`/`sale`, micro sign `µg`/`μg`, dotless `ı`/`I` | Google replaces; gdoc reports no match | Additional case/compatibility differences; not independent corruption bugs |
| Composed `José` vs `Jose` + U+0301, in both directions | Google replaces; gdoc reports no match | Canonically equivalent names behave differently; no normalization equivalence was assumed in the harness |
| `Owner’s budget` with query `Owner's` | Google replaces; gdoc reports no match | Default typography behavior differs; gdoc separately offers explicit `--normalize` for smart punctuation |
| NBSP in `Budget draft` with ordinary-space query | Both leave text unchanged | Useful nonmatch: neither operation treats these spaces as equivalent in this specimen |
| ASCII, Cyrillic, accented uppercase/lowercase, Kelvin-sign controls | Both replace correctly | Positive controls |
| Query `absent` against `Budget draft` | Both leave text unchanged | Ordinary negative control |
| `İ` with query `i` | Both replace correctly | Dotted I is not universally broken |
| `İ cat sat` with query `cat` | gdoc produces `İ cMATCHsat`; Google produces `İ MATCH sat` | **Repeat of the known Turkish-I indexing family**, not a new finding |

The native Google operation is an executable reference for **Google's actual semantics**, not proof that every difference is a gdoc defect. In particular, the capital-sharp-S reversal demonstrates why a differential suite must retain both outputs rather than assuming the reference implements every desired Unicode rule. The exact-character sigma counterexample establishes a narrower and stronger defect without that ambiguity.

The punctuation case was tested with default flags. No claim is made that gdoc cannot perform that replacement when explicitly given `--normalize`. Likewise, these runs do not establish gdoc's behavior with `--case-sensitive`, or a universal guarantee across languages.

## Scope and reproducibility

No private office documents, sharing, deletion, or collection updates were involved. Exactly two scratch documents were created for this run and reused. Their IDs and raw native snapshots remain in ignored `.local-hunt/r2-unicode*` files; public outputs contain only synthetic strings. Normal preflight identity notices were excluded from public stderr.

Run with Workspace's installed Python:

```sh
~/.local/share/uv/tools/workspace-mcp/bin/python hunt/round2/unicode-matching.py
```

A normal invocation creates two additional scratch documents. `--resume` reuses the recorded pair and skips cases already recorded; that was used to add the two stronger sigma cases after the initial twenty completed. It is not a retest mode.

The source-level mechanism is in pinned gdoc [`find_text_in_document`](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/api/docs.py#L495): whole-segment and query `lower()` calls precede searching. This report does not substitute a speculative fix for the observed native outcomes.
