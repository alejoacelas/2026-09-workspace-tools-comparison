# Continued office-work regression hunt

[Google Doc: 19 illustrated cases](https://docs.google.com/document/d/1H-p2wLRxdc3u8GEdfhpWODd5HZ_NKDzFv4Ap7DnFDt8/edit). This round added ten live-confirmed cases, each with a reviewed Pillow Before / Expected / Observed diagram. These are adversarial examples, not a measured everyday failure rate or ten unrelated bug families.

| Case | Concrete failure | Evidence |
|---|---|---|
| H10 | Selected-tab reads omit native person, date and file chip labels. | [Chip reads](chips-results.md) |
| H11 | Windows TSV imports retain hidden carriage returns in cells, breaking exact comparisons. | [Sheet import results](sheets-results.json) |
| H12 | A ten-digit account number becomes list marker 1 and loses its identifier. | [Markdown links and blocks](links-results.md) |
| H13 | A link with brackets inside its label becomes literal Markdown. | [Markdown links and blocks](links-results.md) |
| H14 | An HTML entity in a link destination changes the stored query key. | [Markdown links and blocks](links-results.md) |
| H15 | Editing the value beside a merged label appends to the label instead. | [Native table cases](structure-results.md) |
| H16 | Text matching across an omitted person/file chip deletes that chip. | [Native edit evidence](chips-edits-results.json) |
| H17 | Replacing the exact character `Σ` in `ΟΣ` refuses as absent; `--case-sensitive` works. | [Unicode comparisons](unicode-matching.md) |
| H18 | Tabs/newlines in comments or file titles corrupt plain-output records. | [Comment checks](review-commands.md), [title checks](plain-output.md) |
| H19 | A CSV UTF-8 signature becomes part of the first header. Native Google import consumes it correctly. | [Native CSV control](native-csv-control.json) |

**H16 has demonstrated pending patch coverage in [PR #66](https://github.com/LucaDeLeo/gdoc/pull/66).** Actual search functions from its immutable head reject the synthetic chip-spanning matches. That is narrower than a live patched-CLI test; the tested installation remains v0.21.0. The other nine cases are not corrected by the eleven reviewed open PR heads. [Fix coverage](fix-coverage.md) records the exact revisions and overlaps with existing repair areas.

## What worked

- [Navigation and images](navigation.md): 15 controls passed, including nested tabs, selected reads, headings, image inventory and replacement geometry.
- [Drive operations](drive-operations.md): 15 controls passed, including scoped listing/search, unusual names, copying, moving and source preservation.
- [Local pull/edit/push](local-roundtrip.md): ten expected outcomes passed, including a safe multi-tab refusal and frontmatter-based document identity.
- [Suggestions](suggestions.md): nine suggestion attempts plus one ordinary edit control passed their expected outcomes. The enrolled personal client created real pending plain, bold, Unicode, deletion and multi-match suggestions; overlap and structural replacements refused without mutation.
- [Sheet follow-ups](sheet-followups.md) distinguish import defects from unsupported TSV quoting and documented formatted-value behavior. [Unicode pairs](unicode-matching.md) retain normalization-policy differences without calling every disagreement a bug.

These counts describe separate probe sets, some of which reuse inputs. They must not be added into an independent-case denominator.

## Independent checks and limitations

Native Google state, exact values/URLs, suggestion previews and selected PDF exports establish the stored results. Actual Workspace calls pass the targeted H12–H14 assertions, but add trailing paragraphs; see [Workspace controls](workspace-markdown.md). Default gdoc reads and Workspace retain the chip labels lost by selected-tab reads. On the person-chip control, native Google and Workspace both report zero matches without deleting the chip.

Matching another application is not a proof of equivalence. The implementations can share a parser or disagree legitimately about normalization. Regression fixtures should assert the intended contract and native state, and preserve passing controls. These probes and receipts are committed investigation artifacts, **not tests already added to upstream gdoc CI**.

Run the named Python probes with `repos/gdoc/.venv/bin/python` from the project root unless their source specifies the Workspace environment. Read each script before running: live probes create or edit synthetic personal-account resources, and some extension flags reuse a local fixture. Identity is explicitly checked; raw resources and snapshots remain in ignored `.local-hunt/`. The [manifest](confirmed.json) and [promotion assertions](promote.py) collect reviewed failures. No upstream patch was made.
