# Parallel gdoc regression hunt

**Nine illustrated examples reproduce against real Google Docs:** seven successful writes produce incorrect content or formatting; two successful selected-tab reads omit content or numbering. See the [Google Doc](https://docs.google.com/document/d/1H-p2wLRxdc3u8GEdfhpWODd5HZ_NKDzFv4Ap7DnFDt8/edit).

Three agents tested 68 offline specimens. The live examples were independently checked against native Google state, and the two read cases against a rendered Google PDF. This is a deliberately adversarial collection, not an estimate of normal-work failure frequency. Eight examples extend the previous comparison; H01 confirms its escaped-pipe case live. These triggers overlap broader campaign repair areas and should not be counted as nine unrelated, globally novel bugs.

| Case | Operation and trigger | Confirmed outcome |
|---|---|---|
| H01 | Native Markdown table with escaped pipe `A\|B` | Row becomes `A\` and `B`; value `100` disappears. |
| H02 | Native table with empty first cell `||100|` | `100` shifts into the first column. |
| H03 | Code block contains a fence-like line with trailing text | Line disappears; following literal asterisks become bold formatting. |
| H04 | Hyperlink has an optional Markdown title | Title becomes part of the actual URL; visible label still looks right. |
| H05 | Code span uses double-backtick delimiters | Code text and delimiter characters are corrupted. |
| H06 | Inline code ends in a backslash | Final backslash and code formatting are lost. |
| H07 | Bold surrounds code containing literal asterisks | Code text changes and emphasis closes too early. |
| H08 | Read selected tab containing nested table | Inner `Materials` and `475` disappear from output. |
| H09 | Read selected tab containing imported numbered steps | Visible steps 7/8 become unordered bullets. |

H01–H07 use `gdoc write --tab`, not whole-document Drive import. H08–H09 leave the source document unchanged; `gdoc cat` without `--tab` preserves the specific values/numbers lost by selected-tab reads. This passing control does not establish complete formatting fidelity.

## Evidence and ground truth

- [Confirmed cases and exact illustration data](confirmed.json), [native live write readback](live-results.json), and [live read results](export-extra-results.json).
- [Tables/blocks: 24 specimens](tables-results.md), [inline Markdown: 24 specimens](inline-results.md), [native export: 20 specimens](operations-results.md). Each includes controls and exclusions. Counts refer to specimens, not independent defects.
- [Additional live read checks](export-extra-results.md): actual nested-table structure, CLI outputs, Google PDF text and digest.
- [Publication verification](publication-checks.json): native tab/image checks and exported-page QA.
- [Pillow renderer](render.py) and [figures](figures/): reconstructed Before / Expected / Observed panels independently reviewed against actual outputs.

Expected Markdown meaning follows explicit synthetic assertions checked against [CommonMark](https://spec.commonmark.org/0.31.2/) and [GFM tables](https://github.github.com/gfm/#tables-extension-). These are conventions for judging advertised Markdown operations; gdoc does not claim full CommonMark compliance. The independent parser and Workspace provide useful cross-checks, but Workspace uses that same parser, so their agreement is not two independent votes. Live native readback—not agreement between implementations—establishes what Google actually stored.

The best additional office-content lead is missing smart-chip labels in offline native-shaped fixtures. It remains outside the live-confirmed collection. Other ordinal variants, representation gaps, malformed input, and unsupported table shapes retain their original classifications. No upstream fix or PR was made in this run.

## Reproduce

Pinned sources: gdoc `dbfa4c34bfa699ee8dd9839da85eea1fac177d44` (v0.21.0); Workspace `54b1c56f7f9912ce32681460d7ca38f9c2a37564`. The ignored clones and environments from the parent comparison are required.

```sh
python3 hunt/tables-probe.py
repos/google-workspace-mcp/.venv/bin/python hunt/inline-probe.py
repos/gdoc/.venv/bin/python hunt/operations-probe.py
python3 hunt/build-confirmed.py
uv run --with pillow python hunt/render.py
```

The offline probes compare outputs and record differences; a zero exit status means the probe ran, not that gdoc passed every case. `build-confirmed.py` asserts the captured live mismatches. These are investigation fixtures, not tests already integrated into upstream gdoc CI.

Live `confirm.py` and `export-extra-probe.py` create or rewrite synthetic personal-account fixtures. `live.py` explicitly verifies the selected personal identity before writes. Raw snapshots, PDF exports, account-specific logs, and resource IDs remain in ignored, owner-only `.local-hunt/`. No resources are shared or permanently deleted by these probes.

The publication scripts write only the locally recorded collection. Synthetic diagrams are hosted in this public repository; the Google Doc's sharing was not changed. The primary seven write fixtures, one extra read fixture, and the collection remain available in the personal account.
