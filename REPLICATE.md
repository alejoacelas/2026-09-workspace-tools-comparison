# Session record

## Compare Google office tools for AI agents

The human wanted both repositories cloned and compared side by side for ordinary office work, including feature coverage and operation call counts.

- Inspected pinned upstream Workspace MCP v1.26.0 and gdoc v0.21.0; found substantially broader office coverage in Workspace and specialized document-review workflows in gdoc.
- Reproduced 25 synthetic request-count cases: a warm gdoc phrase edit executes six Google methods versus one Workspace plain replacement; ten Workspace replacements batch into three executions.
- Identified a consequential interface difference: gdoc CLI imports multi-row CSV/TSV in one command, while its MCP wrapper only accepts one row per write; Workspace accepts a two-dimensional range directly.
- Ran 459 selected gdoc tests and 144 selected Workspace tests successfully; reproduced a UTF-16 indexing defect confined to Workspace's native Markdown converter. No live Google account operations were performed, so real document fidelity and latency remain unmeasured.
- Published the comparison, pinned source links and reproduction scripts; retained both upstream clones in `repos/`. Moved the completed project from `~/best/once/2026-09-workspace-tools-comparison` to `~/best/archive/2026-09-workspace-tools-comparison` under the shared one-off lifecycle rule.

Agent session 01a09580-cd9e-7c92-8257-3f4e20733d15 · Commits 8835f8b (scope and plan), 82d38ab (comparison and evidence)
