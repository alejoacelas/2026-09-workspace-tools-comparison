# Offline native Markdown corpus

36 hand-specified specimens, two pinned upstream converters. A pass means the selected assertions passed, not full rendering fidelity. No Google API calls.

gdoc 0.21.0 (`dbfa4c3`) passed the selected assertions in 32 specimens, differed in 3, and had 1 unsupported parser-route specimen. Workspace 1.26.0 (`54b1c56`) passed 21, differed in 12, and had 3 documented unsupported specimens. This deliberately adversarial corpus is not a representative frequency sample; do not turn these counts into an overall quality score.

Three gdoc differences are concrete: a URL ending `Policy_(2026)` is truncated to `Policy_(2026` and leaves a visible closing parenthesis; `office_budget_total` becomes `officebudgettotal` with an italic middle; an escaped pipe in table cell `A\|B` produces cells `A\` and `B`, discarding the intended value `100`. Workspace handles the first two as expected; its native Markdown route does not support tables.

Workspace loses nested list depth, drops the second paragraph inside a list item, and miscalculates UTF-16 positions across nine specimens containing non-BMP characters. gdoc passes these selected assertions. gdoc retaining list continuation text does not certify that it remains semantically attached to the same native list item; that relationship is outside this observer.

**Live cross-check changes the nesting conclusion:** the two-space `nested-bullets` fixture already used here emits one tab in gdoc, but the later [live native snapshot](live-feature-checks.json) shows the child flattened in BOTH tools. A [direct grouped-bullet Google reference](live-followups.json) subsequently preserved child nestingLevel1. This observer counts intended leading-tab nesting; it does not reproduce all Google bullet/list behavior. Therefore its gdoc nesting pass is a request-intent check, not proof that nested lists render correctly. [Complete writer cross-check](nested-list-crosscheck.md).

Sources: [gdoc native parser](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/mdparse.py), [Workspace native converter](https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/gdocs/docs_markdown_writer.py).

| Specimen | gdoc | Workspace | Difference detected |
|---|---|---|---|
| plain | pass | pass | — |
| paragraphs | pass | pass | — |
| heading | pass | pass | — |
| h6 | pass | pass | — |
| bold | pass | pass | — |
| italic | pass | pass | — |
| bold-italic | pass | pass | — |
| nested-emphasis | pass | pass | — |
| link | pass | pass | — |
| link-parentheses | difference | pass | gdoc: visible text differs, link label/URL differs |
| bold-link | pass | pass | — |
| inline-code | pass | pass | — |
| fenced-code | pass | pass | — |
| bullets | pass | pass | — |
| nested-bullets | pass (request intent only) | difference | workspace: list nesting differs |
| numbered | pass | pass | — |
| nested-numbered | pass (request intent only) | difference | workspace: list nesting differs |
| list-continuation | pass | difference | workspace: visible text differs |
| table | pass | unsupported-route | workspace: native table cells differ/missing |
| table-escaped-pipe | difference | unsupported-route | gdoc: native table cells differ/missing; workspace: native table cells differ/missing |
| strike | pass | unsupported-route | workspace: visible text differs, strike target differs |
| image-alt | unsupported-route | pass | gdoc: visible text differs |
| escaped-markers | pass | pass | — |
| intraword-underscore | difference | pass | gdoc: visible text differs |
| blockquote | pass | pass | — |
| horizontal-rule | pass | pass | — |
| emoji-heading | pass | difference | workspace: 2: insertion 8 differs from append frontier 9, 3: insertion 9 differs from append frontier 10, 4: insertion 14 differs from append frontier 15 |
| emoji-before-bold | pass | difference | workspace: 2: insertion 12 differs from append frontier 13, bold target differs |
| emoji-in-bold | pass | difference | workspace: 2: insertion 5 differs from append frontier 6, bold target differs |
| emoji-after-bold | pass | difference | workspace: 2: insertion 12 differs from append frontier 13, 3: insertion 13 differs from append frontier 14, 4: insertion 18 differs from append frontier 19 |
| emoji-link | pass | difference | workspace: 2: insertion 10 differs from append frontier 11, link label/URL differs |
| emoji-list | pass | difference | workspace: 1: insertion 3 differs from append frontier 4, 3: insertion 8 differs from append frontier 9, visible text differs, list nesting differs |
| emoji-code | pass | difference | workspace: 1: updateTextStyle [1,2) splits UTF-16 character, 2: insertion 3 differs from append frontier 4, 3: insertion 4 differs from append frontier 5, 4: insertion 9 differs from append frontier 10, code target differs |
| combining-marks | pass | pass | — |
| zwj-emoji | pass | difference | workspace: 1: updateTextStyle [5,11) splits UTF-16 character, 2: insertion 12 differs from append frontier 14, 3: insertion 13 differs from append frontier 15, 4: insertion 18 differs from append frontier 20, visible text differs, bold target differs |
| astral-cjk | pass | difference | workspace: 2: insertion 10 differs from append frontier 11, 3: insertion 11 differs from append frontier 12, 4: insertion 16 differs from append frontier 17, bold target differs |

## Scope and interpretation

The probe calls gdoc `parse_markdown` + `to_docs_requests` (native edit/tab path) and Workspace `markdown_to_docs_requests` (populate-from-Markdown path). It does not compare either app’s separate Drive HTML/Markdown import route. gdoc native tables require later insertion phases; here their parsed row/cell data is checked, not live table construction. Image rendering is outside this gdoc parser’s native-image contract; Workspace intentionally produces linked alt text. Workspace explicitly excludes GFM tables/strikethrough, so those rows are unsupported-route, not implementation failures.

The independent request replayer starts from a blank body, uses UTF-16 bytes for insertion and style ranges, validates character boundaries and tab targeting, checks that these sequential emitters append at the correct UTF-16 frontier, and models removal of leading list tabs by createParagraphBullets. It records the text targeted when each style request executes. It does not implement Google’s full paragraph-style inheritance, tables, final style coalescing, numbering continuation, or backend sanitization. Range errors are request-level findings, not a claim Google returned a particular HTTP response.

Text comparison normalizes whitespace to avoid classifying intentional blank spacer paragraphs as bugs; consequently it does not certify exact paragraph spacing, line breaks, or code indentation. Nesting is checked independently via leading-tab removal. Style assertions name explicit expected selected text; they are not derived from either parser. No percentage score should be interpreted as real-world failure probability. Common Markdown link/underscore/list semantics are expectations of this corpus, not a claim gdoc promises complete CommonMark compliance.

Reproduce: `python3 probes/markdown-corpus.py`. Full Markdown inputs, native requests, replayed text, target ranges and findings are in [markdown-corpus.json](markdown-corpus.json).


## Controlled live list follow-up

The [native isolation test](live-list-oracle.json) replayed gdoc's exact text and paragraph-style requests. Its three per-item bullet requests flattened the list; replacing only those with one grouped bullet request restored `nestingLevel: 1` and 72-point child indentation. This identifies a concrete grouping interaction and fix direction, without claiming a gdoc patch has been applied. The offline leading-tab observer cannot certify final nesting.
