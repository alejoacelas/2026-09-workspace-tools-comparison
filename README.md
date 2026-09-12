# Google office tools comparison

**[Read the measured comparison](COMPARISON.md).** It covers every public gdoc command, practical Workspace equivalents, live speed/correctness checks, and bugs transferred between the repositories.

Workspace is the broader and faster sampled office connector; gdoc supplies exclusive review and local-file workflows. Both have confirmed document-fidelity defects. The report explains which routes passed, which failed, and which claims remain source-only.

## What to inspect

| Artifact | Contents |
|---|---|
|[Main report](COMPARISON.md)|Recommendations, feature gaps, timings, live failures and four Pillow illustrations|
|[Feature matrix](evidence/feature-matrix.md)|All 39 public gdoc commands, consequential flags and CLI/MCP differences|
|[Command names](COMMANDS.md)|Actual Workspace tools and gdoc subcommands|
|[gdoc fixes → Workspace](evidence/gdoc-fixes-crosscheck.md)|12 public patch families cross-checked against the other implementation|
|[Workspace fixes → gdoc](evidence/workspace-fixes-crosscheck.md)|12 reverse patch families, PR states, ancestry and executable observations|
|[Markdown corpus](evidence/markdown-corpus.md)|36 adversarial specimens, explicit expectations and observer limitations|
|[Regression assessment](evidence/regression-assessment.md)|Full upstream tests, CI enforcement limits, concurrency and retry behavior|
|[Live methodology](evidence/performance.md)|Timing samples, native-state checks, runtime versions and harness corrections|
|[Installation](SETUP.md)|Local Workspace MCP registration and completed account authorization|

The active project is `~/best/once/2026-09-workspace-tools-comparison`; it was restored from the archive for continued evaluation. Both upstream Git clones are retained in ignored `repos/`. Public evidence uses synthetic content; credentials, live resource IDs and transport logs remain Git-ignored in `.local-benchmark/`.

## Reproduce

Pinned public upstreams:

- gdoc 0.21.0: `dbfa4c34bfa699ee8dd9839da85eea1fac177d44`.
- Workspace MCP 1.26.0: `54b1c56f7f9912ce32681460d7ca38f9c2a37564`.

```sh
mkdir -p repos
git clone https://github.com/LucaDeLeo/gdoc.git repos/gdoc
git -C repos/gdoc checkout dbfa4c34bfa699ee8dd9839da85eea1fac177d44
git clone https://github.com/taylorwilsdon/google_workspace_mcp.git repos/google-workspace-mcp
git -C repos/google-workspace-mcp checkout 54b1c56f7f9912ce32681460d7ca38f9c2a37564
(cd repos/gdoc && uv sync --frozen --extra dev)
(cd repos/google-workspace-mcp && uv sync --frozen --extra test)
```

[Full reproduction instructions](evidence/performance.md#run-the-evidence) distinguish offline checks from live scripts that create synthetic Google files. The live install uses a different dependency resolution from the clone's frozen test environment; [runtime metadata](evidence/runtime.json) records that distinction.

The original synthetic API-call counts remain reproducible with `probe-calls.py` and each clone's Python; `probe-markdown.py` characterizes the initial emoji-index finding. Later native-state checks are stronger evidence than those first request-only observations. Historical first-pass conclusions remain in Git history rather than being silently treated as current findings.

[Plan](PLAN.md) · [Overview](OVERVIEW.md) · [Run log](RUN-LOG.md) · [Session record](REPLICATE.md)
