# Reliability and regression evidence

**Both complete local suites pass, but neither suite demonstrates general document fidelity.** gdoc has more purpose-built document-review guards; Workspace has a visible automated PR test workflow and more infrastructure/security coverage. Those are different strengths, not a numeric reliability ranking.

Public upstream snapshots: gdoc `dbfa4c3` (0.21.0), Workspace `54b1c56` (1.26.0). Tests ran on 12 September 2026 in the existing clone virtual environments. No upstream sources or installed dependencies were changed for these runs. No authenticated Google writes were performed.

## Reproduction and results

| Run | Result | Runtime context | Evidence |
|---|---|---|---|
| gdoc complete configured test suite | **1,563 passed** | Python 3.12; 11.69 seconds | [Raw output](gdoc-full-tests.log) |
| Workspace complete non-integration suite | **2,114 passed, 2 deselected** | Python 3.11; 17.23 seconds | [Raw output](workspace-full-tests.log) |

Commands, from each clone:

```sh
# repos/gdoc
GDOC_AUTO_UPDATE=0 .venv/bin/python -m pytest -q -o addopts=

# repos/google-workspace-mcp
.venv/bin/python -m pytest -q -m 'not integration'
```

The two deselected Workspace tests intentionally mutate a real Google Doc. An Apps Script manual E2E script is excluded by upstream's pytest configuration. Different suite durations, Python versions and test inventories are **not application speed measurements**. Test count is an amount of evidence, not a quality score; many parameterized assertions can cover one narrow behavior.

## What runs automatically

| Question | gdoc public upstream | Workspace public upstream |
|---|---|---|
| Checked-in pytest suite | Yes, configured in pyproject | Yes, configured in pyproject |
| Visible GitHub Actions test workflow at pinned commit | **None**: no `.github` directory | PR-triggered pytest on Ubuntu/Python 3.11 |
| Dependency reproducibility in CI | No checked-in CI to assess | `uv sync --extra test --frozen`, checked-in lock |
| Multiple Python versions/OSes exercised by checked-in test CI | Not established | Test workflow only Python 3.11/Ubuntu |
| Live Google test credentials provided by workflow | No workflow | No; integration fixture skips without document ID/email/token cache |
| Lint/format automation | Ruff configuration; no visible enforcement workflow | Ruff PR/main workflow, pinned Ruff version |
| Required merge checks | Not established by repository files | Workflow exists; branch-protection enforcement not established |
| License declaration | No license file or package license declaration found | MIT in package metadata and license file |

“None checked in” does not prove the author never runs tests or has no external CI. “Workflow exists” does not prove a failing check blocks merge. [Workspace pytest workflow][w-ci], [Ruff workflow][w-ruff], [Workspace metadata][w-package], [gdoc metadata][g-package]. License is a reuse/maintenance distinction, not a correctness measure or legal opinion.

## Useful regression protection actually present

| Failure class | gdoc evidence | Workspace evidence | What remains unproved |
|---|---|---|---|
| UTF-16/index arithmetic | Explicit emoji cleanup-position and table-offset assertions; Markdown/tab request tests | UTF-16 helpers, non-BMP batch snapshot tests and anchor tests | Separate Markdown writer still generated wrong offsets in our earlier probe; shared helpers do not guarantee every path uses them |
| Wrong tab or unintended multi-tab collapse | Tab selection tests, per-tab read/write, multi-tab whole-write refusal | Tab targeting and management tests | Combined long edit sequences and all native objects are not covered by a live differential corpus |
| Concurrent changes | Tests assert revision from fetched document reaches write; stale-baseline refusal tests | Batch metadata/revision reporting tests | Reporting a revision is not enforcing it; Workspace batch lacks requiredRevisionId |
| Inherited bullets/paragraph style drift | Cleanup request tests; nested-list/tab-removal ordering tests | Paragraph/text/table style request tests | Most assertions inspect requests or mocks rather than resulting Google's native document state |
| Suggestions silently become direct edits | Dedicated tests for preview capability, bad responses, transport/verification failures; explicit never-direct-edit semantics | No matching suggestion writer | Account eligibility and live Google behavior remain external dependencies |
| MCP input or account confusion | Schema derived from parser; file/stdin blocking, account restored on errors, unknown arguments, diff exit semantics | FastMCP integration, OAuth/session/auth scope tests, golden Docs/Contacts schemas | Protocol/schema correctness does not imply office-task correctness |
| Spreadsheet data semantics | Range/value/error translation and command routing tests | Range bounds, formula/notes/hyperlinks, formatting and native table tests | Locale-sensitive date/formula interpretation and live contention require API-level tests |
| Infrastructure / remote-server robustness | Small local transport/auth surface | OAuth, SSRF restrictions, file size/download streaming, permissions, auth persistence, retry and logging tests | Deployment-specific proxies, concurrent users and long-running service behavior need representative deployments |

Examples: [gdoc emoji cleanup tests][g-api-tests], [gdoc Markdown tests][g-md-tests], [gdoc MCP tests][g-mcp-tests], [gdoc suggestion tests][g-suggest-tests], [Workspace Docs tests][w-doc-tests], [Workspace test tree][w-tests].

A scan found **no Hypothesis/`@given` property-testing suite** in either pinned tests tree. Workspace has golden **tool-schema** snapshots; these protect the API surface, not rendered document output. Neither pinned suite is an exhaustive executable-reference comparison of Docs mutations against native Google outcomes.

## The existing live tests are smoke tests, not fidelity oracles

Workspace's two `populate_from_markdown` integration tests create temporary tabs and check success, request count, structural-element count, text length, and changed length after overwrite. They do not assert that every source character survives, that bold/link ranges are exact, or that surrounding content remains unchanged. Their fixtures skip unless an explicit test document, email and cached OAuth token exist. The checked-in PR workflow does not configure those prerequisites. [Actual integration assertions][w-integration]

This distinction matters for the Unicode bug: a document can contain “more than 50 characters” and still put a paragraph in the wrong place. Adding more smoke inputs would not necessarily catch that; the assertion needs a structural or semantic oracle.

## Error handling, partial writes and concurrency

**gdoc's strongest guards are operation-specific.** Phrase replacement reads native content/revision and pins its principal batch with `writeControl.requiredRevisionId`. Per-tab operations also have revision-aware helpers. Whole-file overwrite compares local awareness/baseline state and refuses stale input unless forced. These lower the chance of overwriting an intervening edit. However, its post-edit cleanup and table insertion can require additional batches; the principal batch's revision guard does not make the entire command transactional. A failed follow-up can leave a partial edit. [Docs mutation implementation][g-docs], [CLI guards][g-cli]

**Workspace's general Docs batch reports revisions but does not enforce a revision precondition.** Its batch manager reads before and after writing, builds typed requests, and submits one Docs batch. That is useful evidence and can reduce network work, but does not prevent a collaborator from changing indexed content between the initial read and submission. Its high-level table-writing path can also use multiple API batches. [Batch manager][w-batch], [table manager][w-table]

**Neither app has a universal exactly-once or automatic-rollback guarantee.** Network loss after a server accepts an append/comment/create can make the outcome uncertain. Retrying such operations blindly may duplicate work. gdoc's suggested-edit path explicitly reports unknown outcome/failed verification and advises inspection; do not generalize that special handling to every command. [Suggested-edit errors][g-docs]

**Workspace's general retry wrapper is narrower than “automatic retries.”** For operations declared read-only, it retries `ssl.SSLError` with one- and two-second waits (three attempts total). Ordinary HTTP errors are translated and raised; the wrapper is not a universal 429/5xx retry engine. Individual service paths can implement their own retries, such as Gmail batches. gdoc's normal Google API wrappers generally call `.execute()` without a custom retry policy; they translate HTTP errors into CLI errors. [Workspace wrapper][w-utils], [gdoc Sheets wrapper][g-sheets]

## What application-speed claims these sources support

1. Workspace native plain replacement is one Google request; gdoc's formatted/revision-aware replacement does more reads and may need cleanup. This predicts a network-latency advantage for the simpler Workspace path, not identical semantics.
2. Workspace can put ten unrelated replacements in one batch; ten gdoc CLI edits repeat preflight/content/postflight work. Batching a shell script reduces model round trips, not Google requests.
3. Persistent MCP processes can amortize imports/service construction; cold standalone CLI invocations cannot be compared with an already-running server without reporting that distinction.
4. An extra read for conflict detection or verification is useful work, not inherently waste. Conversely, a “success” string without verification does not establish correctness.

The existing [synthetic request-count probes](../probe-calls.py) count Google API method executions, not HTTP retries, OAuth refreshes, payload size, quota units or model latency. A defensible latency benchmark should separately report cold/warm startup, Google network time, request size, repeated trials, and whether the requested output and safeguards actually match.

## Highest-value gdoc regression additions

- Add **native-operation differential integration tests** for plain replacement: identical generated Docs, gdoc on one, native `replaceAllText` on the other; compare normalized native structure and unchanged regions.
- Add **request-model property tests** without credentials: generate Unicode/paragraph/table inputs; assert UTF-16 boundaries, valid ranges, correct tab IDs and request ordering. A faithful model needs independently defined semantics rather than replaying gdoc's own parser.
- Replay **minimized anonymous real-document fixtures** for bugs found in local fidelity work; keep them separate from the public upstream score until merged.
- Add **fault injection after each write boundary**, checking honest partial-success/unknown-outcome reporting and no blind duplicate retry.
- Add a visible **PR test workflow** to run those regressions. Strong tests that are optional local practice provide weaker continuing assurance than checks that run on every change.

[w-ci]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/.github/workflows/pytest.yml
[w-ruff]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/.github/workflows/ruff.yml
[w-package]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/pyproject.toml
[g-package]: https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/pyproject.toml
[g-api-tests]: https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/tests/test_api_docs.py#L380
[g-md-tests]: https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/tests/test_mdparse.py
[g-mcp-tests]: https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/tests/test_mcp.py
[g-suggest-tests]: https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/tests/test_suggest.py
[w-doc-tests]: https://github.com/taylorwilsdon/google_workspace_mcp/tree/54b1c56f7f9912ce32681460d7ca38f9c2a37564/tests/gdocs
[w-tests]: https://github.com/taylorwilsdon/google_workspace_mcp/tree/54b1c56f7f9912ce32681460d7ca38f9c2a37564/tests
[w-integration]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/tests/integration/test_update_tab_from_markdown.py#L164
[g-docs]: https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/api/docs.py
[g-cli]: https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/cli.py
[w-batch]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/gdocs/managers/batch_operation_manager.py
[w-table]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/gdocs/managers/table_operation_manager.py
[w-utils]: https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/core/utils.py#L859
[g-sheets]: https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/api/sheets.py
