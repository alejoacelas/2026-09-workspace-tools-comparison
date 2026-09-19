---
agent_context:
  version: 1
  groups:
  - once
  visibility: public
---
<!-- agent-context:begin sha256=c9028887b1d8442f7c5b08b8aef9d2fc72f5dc14cc0bb704501be77757ff182b -->
<!-- shared group: once -->
# One-off projects

- Name each folder `YYYY-MM-project-name`; separate words with dashes.
- Give every one-off its own Git repository and GitHub remote when creating it.
- Make it public unless it contains employer information, others' private information, or credentials.
- Give its `AGENTS.md` one to three sentences stating its scope or goal and declare the `once` group.
- Keep instructions in `AGENTS.md`; do not create a duplicate `CLAUDE.md` unless an older or restricted Claude runtime needs an import shim.
- When finished, suggest a durable home using `~/best/projects/AGENTS.md`: maintained tools, reference material, personal or work folders, or the shared archive.
- Park unfinished or insubstantial work in its project topic's `archive/`. Record the old path and reason in that archive's `REPLICATE.md`.
<!-- agent-context:end -->


Compare the public upstream google_workspace_mcp and gdoc repositories for everyday office work with AI agents. Keep conclusions tied to pinned source revisions and distinguish static call estimates from live tests.
