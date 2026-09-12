# Session record

## Compare Google office tools for AI agents

The human wanted both repositories cloned and compared side by side for ordinary office work, including feature coverage and operation call counts.

- Inspected pinned upstream Workspace MCP v1.26.0 and gdoc v0.21.0; found substantially broader office coverage in Workspace and specialized document-review workflows in gdoc.
- Reproduced 25 synthetic request-count cases: a warm gdoc phrase edit executes six Google methods versus one Workspace plain replacement; ten Workspace replacements batch into three executions.
- Identified a consequential interface difference: gdoc CLI imports multi-row CSV/TSV in one command, while its MCP wrapper only accepts one row per write; Workspace accepts a two-dimensional range directly.
- Ran 459 selected gdoc tests and 144 selected Workspace tests successfully; reproduced a UTF-16 indexing defect confined to Workspace's native Markdown converter. No live Google account operations were performed, so real document fidelity and latency remain unmeasured.
- Published the comparison, pinned source links and reproduction scripts; retained both upstream clones in `repos/`. Moved the completed project from `~/best/once/2026-09-workspace-tools-comparison` to `~/best/archive/2026-09-workspace-tools-comparison` under the shared one-off lifecycle rule.

Agent session 01a09580-cd9e-7c92-8257-3f4e20733d15 · Commits 8835f8b (scope and plan), 82d38ab (comparison and evidence)

## Install Workspace MCP and compare command names

The human wanted Workspace MCP installed using existing Google credentials and a table comparing its tools with the gdoc CLI's main commands.

- Installed Workspace MCP 1.26.0 and registered `workspace-google` in both Codex homes, Claude Code and Claude Desktop; preserved pre-existing configurations in owner-only local backups.
- Verified both Google identities and reused their existing Docs/Drive OAuth grants; live Drive calls through the actual MCP transport passed for both, with 99 office tools registered.
- Prepared Google consent for the additional services. Infrastructure-only gcloud scopes cannot grant Workspace data access; the personal flow requires handling an unverified-app warning and the work flow requires browser sign-in. Full Gmail/Calendar authorization remains pending.
- Added a side-by-side command table, the complete 122-entry Workspace tier inventory, all 39 public gdoc CLI commands, and setup/reauthorization instructions. Local credentials and private Drive results were not committed.

Agent session 01a09580-cd9e-7c92-8257-3f4e20733d15 · Commits 3b47168 (command comparison and setup record; local client configuration changes are outside Git)

## Restore the active office tools project

The human wanted the comparison project moved back here from the archive for continued work.

- Moved `~/best/archive/2026-09-workspace-tools-comparison` to `~/best/once/2026-09-workspace-tools-comparison`, preserving both upstream clones and the project Git history.
- Updated the Workspace MCP installation to use the restored source location and recorded successful personal and work Gmail/Calendar authorization checks.

Agent session 01a09580-cd9e-7c92-8257-3f4e20733d15 · Commits workspace-tools-comparison: 627d2a6

## Measure office workflows and transfer bug regressions

The human wanted a comprehensive gdoc-versus-Workspace report, including agents cross-checking public bug patches, feature gaps, speed, reliability, regression protection, and campaign-style Pillow illustrations.

- Mapped all 39 public gdoc commands and investigated 12 public patch families in each direction; separated open proposals, released behavior, missing operations and executable findings.
- Ran complete offline suites: 1,563 gdoc tests and 2,114 Workspace tests passed; two live Workspace integration tests were deliberately excluded. Added 36 adversarial Markdown specimens and retained their observer limitations.
- Measured synthetic live workflows: plain replacement medians were 2.83 seconds for gdoc CLI, 2.25 seconds for persistent gdoc MCP, and 0.69 seconds for Workspace MCP. A single ten-placeholder comparison took 28.13 versus 2.27 seconds; runtime and sample limits are explicit.
- Confirmed silent gdoc bold loss, Unicode misindexing, link/underscore conversion defects, Workspace's rejected inspector field mask, and shared native-list flattening. Holding gdoc text/style requests fixed while grouping its bullet requests restored nesting in a native reference replay; neither upstream was patched.
- Independent review caught and excluded harness baseline/parameter errors and an offline nesting false positive. Published raw synthetic evidence, three reviewed Pillow figures, reproduction scripts, and revised routing recommendations; retained 38 synthetic resources in one personal-account test folder with its ledger untracked.
- Kept the active project in `~/best/once/2026-09-workspace-tools-comparison` as requested. No private office document was changed and no credentials were committed.

Agent session 01a09580-cd9e-7c92-8257-3f4e20733d15 · Commits workspace-tools-comparison: f19c463 (plan), 6b04f1b (initial harness), e15a3cb (review corrections), 36cdfbd (report and evidence)

## Distinguish known bugs from new comparison evidence

The human asked whether the gdoc findings were already recorded or covered by upcoming fixes.

- Cross-checked existing bug-hunt records and current public PR scopes; distinguished proposed repair work from code already present in open PRs.
- Corrected the comparison's novelty wording: several findings, including the Unicode family, were independent reproductions of known bugs. No private campaign specimens were copied into the public report.

Agent session 01a09580-cd9e-7c92-8257-3f4e20733d15 · Commits workspace-tools-comparison: ca97dbc

## Illustrate the escaped-pipe table failure

The human wanted a Pillow diagram of the gdoc escaped-pipe table case.

- Rendered Before / Expected / Observed panels from the saved corpus: intended key `A|B` and value `100` become parsed cells `A` plus backslash and `B`, dropping `100`.
- Labeled the observation as offline parser output, reviewed the actual PNG independently, and added it to the main report with reproduction instructions.

Agent session 01a09580-cd9e-7c92-8257-3f4e20733d15 · Commits workspace-tools-comparison: 6223905

## Parallel regression ideas, live confirmation, and illustrated collection

The human wanted agents to invent and test additional failure cases, collecting confirmed results progressively in a Google Doc with Pillow illustrations.

- Three agents executed 68 synthetic offline specimens with controls and exclusions; nine examples were confirmed through live gdoc operations and independent Google state checks. Selected-tab reads omitted nested-table values and converted numbered steps to bullets, while default cat retained the tested content.
- Created a personal Google Doc with a guide and nine illustrated case tabs, including commands, setup, evidence limits, and known-family overlap. Two agents reviewed every exported content page; native checks verified ten tabs and nine embedded images.
- Kept scratch resource IDs and raw exports local. Published synthetic evidence and reusable probes; no upstream fixes or PRs were made. Stale-read refusals were resolved by fresh reads and excluded from content failures.

Agent session 01a09580-cd9e-7c92-8257-3f4e20733d15 · Commits workspace-tools-comparison: 0b7b99c (plan), 1b312c9 (live write evidence), 4dbc545 (publication), e9eb933 (review refinements and extra probe), 7b78965 (live read findings), a9571b4 (report and final verification)

## Continue the hunt across office workflows

The human wanted continued parallel idea generation and live testing, with confirmed errors collected in the existing illustrated Google Doc.

- Added ten live-confirmed cases, bringing the collection to 19: native chip omission/deletion, merged-label targeting, Unicode matching, Markdown links/account numbers, spreadsheet encoding/line endings and malformed plain output. Kept related triggers within their existing repair families rather than claiming ten unrelated discoveries.
- Checked actual native state and selected Workspace operations. Workspace passed the targeted link/account-number assertions; native Google and Workspace preserved a person chip where gdoc's phantom match deleted it. Native CSV import handled the UTF-8 signature that gdoc retained as header content.
- Broadened passing controls across Drive, navigation/images, local pull/edit/push and real pending suggestions. Unsupported inputs, Unicode policy differences and a failed native tab-title setup remain distinguished from confirmed defects.
- Inspected all eleven open gdoc PR heads. Executed search functions from PR #66 block the destructive chip match; the patch is pending and was not installed or tested through the live CLI. The other nine additional cases are not corrected by the reviewed patches.
- Published 19 Pillow diagrams in 20 Google Doc tabs. Three agents reviewed the exported content pages; native image/tab checks, Python/JSON checks and local-link checks passed. Raw account resources remain local; no upstream fixes or regression tests were added.

Agent session 01a09580-cd9e-7c92-8257-3f4e20733d15 · Commits workspace-tools-comparison: a85b16a (continued plan), 32390ad (seven additional cases), 83d2639 (three cases and broader controls), 71579d6 (repair coverage, final controls and verified publication)
