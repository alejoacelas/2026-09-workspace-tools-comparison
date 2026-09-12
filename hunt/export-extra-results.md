# Live native-table and numbering read checks

**`gdoc cat DOC --tab TAB` silently omitted a genuine inner table and changed a visibly numbered list into bullets. Plain `gdoc cat DOC` preserved the inner words and the list's 7/8 numbering.** Both commands exited successfully. This is a route-specific read-fidelity finding, not a failure of every gdoc read.

One synthetic scratch document was imported from HTML through Google Drive. Before testing gdoc, the native Docs API response confirmed an outer 1×1 table containing an inner 1×2 table with `Materials` and `475`. The same response exposed the first list level's `startNumber: 7`. We then exported the document directly from Google as PDF, extracted its text, rendered page one, and visually checked it: the inner table is present, and the two items visibly read **7. Review budget** and **8. Approve purchase**.

| Native document fact | Plain `gdoc cat DOC` | `gdoc cat DOC --tab TAB` |
|---|---|---|
| Inner table contains `Materials` and `475` | Both values appear, flattened into the outer Markdown cell | Both values are completely absent |
| Procedure is visibly numbered 7 and 8 | Outputs `7. Review budget` and `8. Approve purchase` | Outputs `- Review budget` and `- Approve purchase` |
| CLI outcome | Exit 0 | Exit 0 |

The API reported `GLYPH_TYPE_UNSPECIFIED` on the imported list. That alone would be insufficient to establish its visible numbering; the independently exported and visually inspected PDF resolves the ambiguity. This specimen demonstrates numbering changing to bullets, not a 7→1 renumbering.

Pinned implementation: gdoc 0.21.0, `dbfa4c34bfa699ee8dd9839da85eea1fac177d44`. The [sanitized results](export-extra-results.json) contain the synthetic HTML, native table dimensions/depth, relevant list metadata, exact CLI output, and PDF text/hash. The [probe](export-extra-probe.py) creates a new scratch document if rerun; it does not share or delete files. Resource IDs, full native snapshots and PDF remain in the ignored `.local-hunt` directory. Preflight identity notices were excluded from public evidence.

No Workspace operation was tested in this follow-up. The result confirms an actual native nested-table read failure in gdoc's selected-tab exporter; it does not establish comparative behavior for Workspace or loss during writes. The scratch document and its existing content were not modified during the read/PDF verification.
