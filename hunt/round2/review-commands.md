# Review commands: lifecycle passes, plain output breaks records

**Nine of ten bounded checks passed.** Native comment text and replies survived the tested lifecycle, and JSON reads retained their content. The additional failure is in `comments --plain`: one multiline comment becomes two logical records even with a quoting-aware TSV parser, so the advertised stable tab-separated output is not safe for ordinary multiline review notes.

[Executable checks](review-commands.py) · [Results and redacted output](review-commands.json). Pin: public gdoc `dbfa4c34bfa699ee8dd9839da85eea1fac177d44`. Nine checks used one newly created personal-account synthetic Google Doc; one exercised the actual diff builder offline. No other reviewers, mentions, anchored comments, sharing, deletion, or collection changes were involved.

## Checks

| Case | Independent check | Result |
|---|---|---|
| Create a multiline comment containing a tab, literal Markdown and punctuation | Native Drive comment equals the supplied string | Pass |
| Add a multiline reply with literal asterisks/brackets/ampersand | Native reply equals supplied string | Pass |
| List the thread as JSON | Comment and reply content remain exact | Pass |
| Resolve with an explanatory message | Native `resolved=true`; resolve action carries message | Pass |
| Read resolved comments with default versus `--all` | Default excludes it; `--all` includes it | Pass |
| Reopen the comment | Native `resolved=false`; original question and reply retained | Pass |
| `comment-info --json` | Content, state, and reply count agree with native Drive state | Pass |
| `comments --plain` on the multiline comment | One native comment should form one stable five-field TSV record | **Fails:** `csv.reader(delimiter='\t')` returns two logical records with five and two fields |
| Revision-diff builder compares budget 100 versus 120 | At least one changed hunk | Pass, offline |
| TOC with maximum depth 2 on native H1/H2/H3 paragraphs | Returns only `Review plan` and `Costs` | Pass, live |

All tested CLI calls returned exit 0. These controls do not establish every comment, revision, or TOC workflow is correct, and the selected-case ratio is not a reliability estimate.

## The plain-output failure

The native question is deliberately ordinary review content with pasted tabular text:

```text
Question A<TAB>Budget
Is **100** final? Keep <5% and "quotes".
```

The actual native text retains a literal tab and newline. `comments --json` preserves both correctly. `comments --plain` writes them directly into its record stream:

```text
COMMENT<TAB>open<TAB>AUTHOR<TAB>Question A<TAB>Budget
Is **100** final? Keep <5% and "quotes".<TAB>
```

`COMMENT` and `AUTHOR` replace resource/account identifiers in this illustration. Parsing the actual output with `csv.reader(io.StringIO(output), delimiter='\t')` returns `['COMMENT', 'open', 'AUTHOR', 'Question A', 'Budget']`, followed by a second two-field record. The pasted `Budget` value has moved into the quoted-context column, and the remainder of the comment is disconnected from its record.

Physical line count alone would not prove a defect: properly quoted TSV can contain multiline fields. The independent control serializes one five-field record using `csv.writer(delimiter='\t')`; the same reader correctly returns one record containing the complete tab/newline-bearing comment. The actual gdoc output supplies no such quoting. The native comment itself remains intact; this is not a comment mutation or anchoring defect.

The source directly prints `content` inside the TSV row. It already replaces tabs in `quotedFileContent`, but does not apply a consistent serialization policy to the comment body. Existing plain-output tests use simple content; a separate test checks quoted-context tabs. The missing regression is main-comment content containing tabs/newlines. A safe contract could quote fields consistently or provide a clearly specified escaped representation; JSON is the demonstrated workaround.

Reproduce on a separate synthetic document:

```sh
gdoc comment DOC $'Question A\tBudget\nIs **100** final?' --account PERSONAL
gdoc comments DOC --plain --account PERSONAL
gdoc comments DOC --json --account PERSONAL
```

The shell syntax here explicitly supplies the tab/newline. Our executable harness uses subprocess argument arrays instead.

Sources: [comment listing and TSV output](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/cli.py#L2199), [comment lifecycle API](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/api/comments.py#L125), [upstream comment-command tests](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/tests/test_comments_cmd.py).

## Coverage boundaries, not invented defects

- `comment-info` returns JSON thread details correctly in the tested state. Its terser display modes intentionally contain less detail; that alone is not a failure.
- Review of revision tests found intentional normalization, including treating changed ordered-list ordinals as equal. That is a review limitation when numbers matter, but the explicit test shows it is existing policy rather than a newly discovered regression.
- A newly created scratch document is not a good oracle for retained historical revisions. This run therefore tested amount-change detection in the actual diff builder rather than pretending to establish old-version retrieval or revision-retention guarantees.
- Ambiguous anchors, cross-account collaboration, suggestion preview, concurrent writes and Unicode location mapping were excluded because they belong to already reviewed families.

No upstream fix or PR was made. The script refuses to repeat completed ten-case mutations; raw account-bearing receipts, document IDs and the native before/after snapshots remain in owner-only `.local-hunt/r2-review*` files.
