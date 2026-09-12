# Suggestion preview gate and explicit-case control

Preview enabled: two suggested replacements succeeded; native read-only previews preserve originals or show proposed text as appropriate.

The synthetic document starts with `draft`, `review`, and `ΟΣ` on separate paragraphs. The executed command was `gdoc suggest DOC draft final --tab TAB --account PERSONAL`. Full native before/after snapshots remain in ignored `.local-hunt/r2-suggestions*`; sanitized command results and text states are in [suggestions.json](suggestions.json).

The H17 control uses `gdoc edit DOC Σ X --all --case-sensitive --tab TAB --account PERSONAL`. It passes: `ΟΣ` becomes `ΟX`. This flag is a workaround for this exact-character specimen, not a claim that default contextual Unicode matching is repaired.

Source inspection: [`cmd_suggest`](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/cli.py#L1278) rejects structural Markdown and overlapping existing suggestions. [`suggest_replacement`](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/api/docs.py#L2035) pins revision and token identity, performs a non-mutating preview-enrollment read, and requires saved suggestion IDs plus native readback; it has no direct-edit fallback. These source-level protections do not substitute for testing successful suggestion creation in a preview-enrolled environment.

Exactly one new personal scratch Doc; no project enrollment, auth changes, sharing, deletion, collection writes, or acceptance/rejection mutations. Read-only accepted/rejected preview requests run only if creation succeeds. The reproducible probe is [suggestions.py](suggestions.py).

Live verification: the first operation creates one native pending suggestion; accepted preview contains `final`, while without-suggestions preview retains `draft`. The second creates a separate pending suggestion for `review` → `approved`; the accepted preview has native `textStyle.bold: true` on exactly `approved`. Subsequent exact-case editing leaves both pending suggestions present. Inline native text contains proposed and original runs together (for example, `finaldraft`); that is the API’s inline suggestion representation, not duplicated accepted text. Successful creation was tested here; refusal on a non-enrolled project was only source-inspected.

## Additional suggestion controls

Five further controls use the same synthetic document without accepting or rejecting any suggestion. The overlapping pending `final` target refused without mutation. Disjoint `--all` on two `Review token` occurrences created pending changes: accepted preview has two `Reviewed token` strings while the original preview retains two `Review token` strings. Heading, bulleted-list and table replacements all refused without native mutation. Each case has full native before/after and both preview snapshots in ignored local scratch. This brings coverage to seven suggestion command attempts plus one ordinary exact-case edit control; the two initial preview reads are observations, not extra operations.

Two final boundary controls: empty replacement passes as a pending deletion, retaining its source in the without-suggestions preview; `**Ready 😀**` passes with the whole replacement natively bold in accepted preview and the original source retained in without-suggestions preview. Total: nine suggestion command attempts and one ordinary exact-case edit control on one scratch document. No new regression family found.

| Executed command control | Result |
|---|---|
| suggest_plain | pass |
| suggest_bold_inline | pass |
| H17_case_sensitive_workaround | pass |
| overlap_pending | pass |
| disjoint_all | pass |
| reject_heading | pass |
| reject_bullets | pass |
| reject_table | pass |
| empty_deletion | pass |
| unicode_bold | pass |

Six pending suggestions remain in the synthetic document. To reproduce the complete sequence on a new scratch document, run `suggestions.py`, then `suggestions.py --extend`, then `suggestions.py --extra` with `repos/gdoc/.venv/bin/python`. Extension flags use the locally recorded scratch identity and append synthetic paragraphs; they are not read-only replay modes.
