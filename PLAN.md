# Measured comparison plan

Compare the pinned public upstreams across the full useful gdoc surface, distinguish unavailable features from awkward workflows, and establish reliability claims through reproducible evidence.

1. Audit public fixes and PRs in both directions, reproducing analogous defects in the other implementation where possible and distinguishing proposed patches from merged behavior.
2. Inventory all gdoc commands and consequential flags against Workspace, and assess upstream regression tests, CI, concurrency, retries, and error reporting.
3. Measure representative live operations on synthetic personal-account specimens, using native Google reads as the independent oracle, plus offline probes for deterministic failures.
4. Present the results in a navigable report with source links, raw measurements, explicitly bounded claims, and occasional Pillow Before / Expected / Observed diagrams following the campaign convention.
5. Review evidence and illustrations, rerun only affected checks, and commit the report and reproduction artifacts without credentials or private document contents.

Live tests create synthetic files in a dedicated personal Drive folder, never send messages or grant access to others, and retain or trash only files created by this run. No permanent deletion. Compare the pinned public upstream code, not the user's modified gdoc campaign branch. Pin timestamps and clearly label any historical PR evidence. Latency measurements are local samples, not universal service SLAs.
