# Office connector comparison decisions

## Core decisions

### Fair comparisons

- [Pin source and runtime identities separately](#decision-1).
- [Distinguish CLI, persistent MCP and native API costs](#decision-2).

### Correctness evidence

- [Use independent native state to confirm document failures](#decision-3).
- [Separate defects from stale reads and unsupported inputs](#decision-4).

### Claims and publication

- [Describe repair families and pending patches accurately](#decision-5).
- [Publish synthetic evidence while keeping account resources local](#decision-6).

## Details

<a id="decision-1"></a>

### Pin source and runtime identities separately

Retain the inspected upstream revisions and runtime metadata. The installed Workspace environment and frozen offline clone had different dependency resolutions; report which one produced each result rather than equating them. See [evidence/runtime.json](evidence/runtime.json).

<a id="decision-2"></a>

### Distinguish CLI, persistent MCP and native API costs

Count Google methods separately from user-visible tool calls. Include each route’s own preflight/readback work in timing, exclude setup and oracle calls, and preserve sample sizes. A single batched workload or local median is not a universal speed ranking. See [evidence/performance.md](evidence/performance.md).

<a id="decision-3"></a>

### Use independent native state to confirm document failures

Request inspection and Markdown parsing can miss or misclassify fidelity failures. Keep passing route controls and native readback beside a reproducer. The nested-list investigation corrected an offline false positive and isolated bullet grouping without claiming that upstream was patched. See [probes/live-list-oracle.py](probes/live-list-oracle.py).

<a id="decision-4"></a>

### Separate defects from stale reads and unsupported inputs

Refresh stale read baselines and repair invalid harness parameters before labeling content failures. Keep Unicode policy differences and failed setup distinct from demonstrated corruption; preserve both controls and exclusions in the hunt. See [hunt/README.md](hunt/README.md).

<a id="decision-5"></a>

### Describe repair families and pending patches accurately

Independent reproduction is not proof of novelty. Group related triggers and distinguish a reviewed PR function from a fix installed through the live CLI. The saved PR coverage describes those inspected heads, not today’s upstream state. See [evidence/gdoc-fixes-crosscheck.md](evidence/gdoc-fixes-crosscheck.md).

<a id="decision-6"></a>

### Publish synthetic evidence while keeping account resources local

Fixtures and illustrations may be shared; credentials, live resource identifiers, raw account exports and transport logs remain ignored. Neither this record nor historical access checks authorize running cloud-writing probes. See [README.md](README.md). History inspected: [36cdfbd](https://github.com/alejoacelas/2026-09-workspace-tools-comparison/commit/36cdfbd).
