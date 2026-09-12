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
