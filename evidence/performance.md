# Performance, live correctness, and reproduction

**The measured Workspace advantage is real for these local routes and fixtures, not a universal speed/reliability score.** Fresh gdoc CLI invocations include process startup; persistent gdoc MCP narrows the gap. Tool choice also changes the number of Google requests and the checks performed.

## Runtime and method

- Public source pins: gdoc `dbfa4c34bfa699ee8dd9839da85eea1fac177d44`, Workspace `54b1c56f7f9912ce32681460d7ca38f9c2a37564`.
- Live gdoc CLI and MCP: clone Python **3.12.13**, Google API client **2.189.0**. `PYTHONPATH` selects the pinned clone; automatic updating is disabled.
- Live Workspace: installed Python **3.11.16**, FastMCP **4.0.3**, MCP **2.2.0**, Google API client **2.200.0**. Key installed source files hash-match the clone. The offline Workspace tests used its separate clone environment: FastMCP **3.4.7**, MCP **1.28.1**, Google API client **2.194.0**.
- Host: macOS **26.6.2**, ARM64. Existing authenticated local account and network; no global/cloud/remote-client latency claim.
- Main run began **2026-09-12 17:13 UTC**. Timings use `time.perf_counter`; trials are sequential and main tool order alternates. Service construction/document-awareness warmups precede timed trials. No artificial network delays or failures were injected into timed live operations.
- Workspace transport exposes complete Drive/Docs/Sheets tiers: **50 tools**. The office installation's 99-tool configuration is broader. Its startup measurement includes opening stdio and listing tools, not first API authentication/service construction.
- gdoc MCP exposes 30 tools and invokes gdoc commands inside its persistent process. It is not a shell-subprocess benchmark disguised as MCP.

[Runtime metadata](runtime.json) records source identity and package versions. Raw results retain individual durations, output text byte counts, reported success/error, and selected native observations. The script excludes setup/oracle API calls from timing. Built-in tool preflight/readback work remains inside timing.

## Live results

| Operation | gdoc CLI median [min,max] | Workspace MCP median [min,max] | n each |
|---|---|---|---:|
| 4 KB Doc read |1.4402 [1.4196,1.5093]s|0.6503 [0.6104,0.7760]s|5|
| Comment-enabled read, empty thread list |1.6323 [1.5025,1.7039]s|0.9060 [0.8336,0.9568]s|5|
| Plain phrase replacement |2.8348 [2.5588,3.0511]s|0.6916 [0.6389,0.7199]s|5|
|100 × 4 Sheets read|1.3347 [1.2746,1.6857]s|0.3939 [0.3876,0.4096]s|5|
|Ten distinct placeholder replacements|28.1344s|2.2745s|1|

The original same-value spreadsheet writes measured medians 1.3770 s and 0.4395 s, but unchanged state cannot independently prove a write occurred. The additional changed-value series measured **1.3540s gdoc vs 0.4705 s Workspace** (three each); every trial started with different cell values and ended with the exact requested rectangle. Leading zeros remained strings because both routes explicitly used RAW.

The actual-comment follow-up used a small one-sentence Doc with one comment, not the original4 KB fixture: medians **1.6491s gdoc vs 0.8881 s Workspace**, three each. Returned content contained the actual comment text in all six samples. Do not subtract these timings from the empty-comment/4 KB series to estimate comment overhead: document sizes differ.

### Persistent gdoc MCP control

| Operation | Persistent gdoc MCP median [min,max] | n |
|---|---|---:|
|4 KB Doc read|**1.1975 [1.0547,2.8145]s**|5|
|Plain phrase replacement|**2.2450 [1.8088,2.4139]s**|5|

Startup and tool listing: one observation of **0.0772s gdoc MCP**, **0.8342s Workspace MCP**. Both had locally cached packages; these are not installation times. gdoc's faster startup is consistent with a smaller implementation/dependency surface, but this measurement does not isolate its cause.

The persistent gdoc series uses similar synthetic text in a new Doc, with VALUE rather than PLACEHOLDER lines and no initial bold style. It was run later, not interleaved with Workspace. The first edit can still initialize a Docs service after a Drive-export read warmup. These limits prevent assigning all differences to transport overhead or reporting a rigorous cross-service confidence interval. They do establish that keeping gdoc alive does not make every extra Google call disappear.

## What the correctness checks assert

- Main plain replacement trials verify old wording is absent and new wording present through a native Docs read; they do not certify every original style. A separate style fixture explicitly inspects text-run formatting and catches gdoc's unrelated bold loss.
- Batch placeholder workflow verifies all ten replacement values. It does not measure sharing; the copy/fill/share call count in the main report is interface-derived.
- Changed Sheets writes verify the entire100 × 4 returned rectangle and ensure it differs from pre-write state.
- Comments are created only on synthetic Docs. Create/reply/resolve/reopen checks read the actual Drive comment state; no quote-anchored or preview suggestion claim is made.
- The simple native-table case asserts one 2 × 2 table and expected text, not arbitrary merged/nested-table fidelity.
- Tab isolation checks both tabs' native text, then checks both appear in each tool's all-tab output.
- Markdown cases retain native paragraph and run styles. Two independent reviewers inspected the evidence/illustrations. Heading/Unicode and link differences are distinct from intentional spacer newlines.
- Nested-list checks inspect child `nestingLevel` and indentation. A grouped native Google request serves as the positive reference. The offline request observer's list-intent pass is explicitly not accepted as a live correctness pass.
- PDF export verifies a `%PDF` header. Revision/TOC/info/tab commands are smoke checks on synthetic Docs; retained-history diff quality and exported page layout are not certified.

No aggregate “reliability success rate” is computed. A CLI exit/MCP result flag can say success while content is wrong; Workspace's non-image insertion validation even returns textual `Error:` with `isError=false` on the tested route. Error latency is not a fast successful operation.

## Harness corrections retained for auditability

The independent benchmark review found setup issues and the run retained their evidence rather than counting them as product failures:

1. The original `live-benchmark.py` invoked gdoc tab write/insert without first recording a gdoc read baseline, and its insert command omitted explicit `--position end`. Those two gdoc refusals are excluded. Corrected native-write cases appear in `live-feature-checks.json`; append succeeded after a later fresh read in `live-followups.json`.
2. One append attempt after a read saw Drive version 3 advance to 4 and correctly refused the stale baseline. A fresh-read retry succeeded. We did not establish why that metadata advanced; it is not classified as a gdoc content-loss bug.
3. The first Workspace comment reply used `reply_content` instead of the actual `comment_content` parameter. That schema failure is excluded; the corrected call is verified in `live-followups.json`.
4. A follow-up image-error probe initially supplied `image_uri` instead of `image_source`, so it stopped at local schema validation. The dedicated `live-mcp-benchmark.py` supplied a known synthetic Doc as an image source and recorded the actual textual-error/false-isError behavior, then completed the persistent gdoc timing control.
5. The original same-value Sheets writes were supplemented with changed sentinels before any correctness claim.

Harness history is in commits `6b04f1b` (initial) and `e15a3cb` (first review corrections); later correction/probe commits are recorded in the session log. Current scripts include the corrected arguments. Raw earlier records still contain the excluded setup failures. `successes` in raw timing summaries means tool-reported success, not validated document fidelity.

## Run the evidence

The source-only suites and local probes need no Google credentials:

```sh
(cd repos/gdoc && GDOC_AUTO_UPDATE=0 .venv/bin/python -m pytest -q -o addopts=)
(cd repos/google-workspace-mcp && .venv/bin/python -m pytest -q -m 'not integration')
python3 probes/markdown-corpus.py
~/.local/share/uv/tools/workspace-mcp/bin/python probes/gdoc-fixes-crosscheck.py
~/.local/share/uv/tools/workspace-mcp/bin/python probes/workspace-fixes-crosscheck.py
```

The cross-check scripts assume the cloned repositories and an installed Workspace Python with its dependencies. The Markdown corpus spawns the existing clone interpreters and includes independent observer self-checks. Clone/bootstrap instructions are in [README](../README.md).

The live scripts **create and mutate synthetic Google files**. Choose an explicitly authorized account; authenticate both tools first. They verify its identity through Drive's account endpoint, keep account selection explicit, and create their own folder/specimens. Credentials must stay outside this repository. The `.local-benchmark` directory is Git-ignored, owner-only, and contains resource IDs and private transport logs for resumption; it must be retained until follow-ups finish.

```sh
PYTHON=~/.local/share/uv/tools/workspace-mcp/bin/python
"$PYTHON" probes/live-benchmark.py --account you@example.com --trials 5
"$PYTHON" probes/live-feature-checks.py --account you@example.com
"$PYTHON" probes/live-followups.py --account you@example.com
"$PYTHON" probes/live-mcp-benchmark.py --account you@example.com
"$PYTHON" probes/live-list-oracle.py --account you@example.com
```

Each first run creates a new dedicated folder. Later scripts use its ledger and prior fixtures, so execute in order and do not mix accounts or rerun stages against altered fixtures without inspecting their prerequisites. They do not automatically delete files or grant permissions. Timing scripts are an audit harness, not a production workload generator or an unattended recurring job. Re-running changes the dated evidence; preserve the old run if comparing versions.

Raw results: [main](live-benchmark.json), [feature follow-up](live-feature-checks.json), [corrected cases/native oracle](live-followups.json), [MCP transport/error contract](live-mcp-benchmark.json), [controlled list-request variant](live-list-oracle.json).
