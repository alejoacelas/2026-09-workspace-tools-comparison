# Run log

## Inspect and compare [est 25m | actual 8m]

1. [x] [est 5m | actual 1m] Cloned both upstreams and pinned their revisions; counted configured tools and runtime registrations.
   a. [Inventory](inventory.json) — 122 configured Workspace tools plus one diagnostic registration, and 30 gdoc MCP tools.
2. [x] [est 15m | actual 4m] Traced office workflows and ran selected upstream tests and synthetic probes.
   a. [Call probes](probe-calls.py) — 25 cases separating API executions from agent invocations.
   b. [Markdown probe](probe-markdown.py) — reproducible UTF-16 indexing defect in Workspace's native Markdown converter.
   c. Unexpected: gdoc MCP accepts only one spreadsheet row per write; Workspace advertises Code Mode without an implementation found in this snapshot.
3. [x] [est 5m | actual 3m] Wrote and checked the source-linked comparison and reproduction instructions.
   a. [Comparison](COMPARISON.md) — feature matrix, workflow call counts, collaboration limits and recommendations.
   b. Live Google API behavior, latency and client onboarding remain outside this source-based review.

## Expanded evidence gathering [est 40m | actual 24m, overlapping synthesis]

1. [x] [est 30m | actual 8m] Cross-checked 12 public patch families in each direction, distinguishing open proposals from released code.
   a. [gdoc → Workspace](evidence/gdoc-fixes-crosscheck.md) and [Workspace → gdoc](evidence/workspace-fixes-crosscheck.md) — runnable transferred-bug evidence.
2. [x] [est 30m | actual 10m] Mapped all 39 public commands, ran both full offline suites, and added 36 adversarial converter specimens.
   a. [Feature matrix](evidence/feature-matrix.md), [regression assessment](evidence/regression-assessment.md), and [Markdown corpus](evidence/markdown-corpus.md).
3. [x] [est 40m | actual 24m] Measured CLI and persistent MCP routes and validated synthetic Docs, comments, tabs, tables and Sheets.
   a. [Methodology](evidence/performance.md) — raw timings, native-state checks and excluded harness errors.
   b. Unexpected: gdoc lost unrelated bold and misindexed Turkish İ; Workspace inspector returned HTTP400; both flattened nested lists. Changing only the native bullet request grouping restored nesting.

## Expanded synthesis [est 20m | actual 12m, overlapping evidence gathering]

1. [x] [est 15m | actual 10m] Wrote the measured report and three campaign-convention Pillow illustrations.
   a. [Report](COMPARISON.md) — concrete routing recommendations, observed failures and limits.
2. [x] [est 5m | actual 2m] Two agents reviewed the report and figures; checked local links, JSON, script syntax and upstream cleanliness before committing.
   a. Corrected prior claims about comment deletion, existing-tab reparenting, and broad gdoc editing reliability; kept all private credentials/resource ledgers untracked.

## Parallel follow-up hunt

- Started three independent investigations: tables/blocks, inline Markdown, and document operations/export. Root handles independent confirmation, live fixtures, and progressive Google Doc publication.
- Findings must state the exact execution route and distinguish previously known families from additional candidates; passing controls and discarded hypotheses remain in the evidence.

- Completed 68 offline specimens across three agents, then independently confirmed seven incorrect native writes and two selected-tab read failures against real synthetic Google Docs. Read cases also match a rendered Google PDF; default cat is a passing content control.
- Published nine reviewed Pillow illustrations progressively into a personal Google Doc. Verified 10 tabs and 9 images; two agents inspected all 10 exported content pages. Google adds 10 tab-divider pages to its 20-page export.
- Stale-read protection refused some fresh-fixture writes; fresh-read retries resolved setup state without forcing writes. These refusals are excluded from content-failure counts. Additional offline candidates remain outside the live-confirmed collection.
